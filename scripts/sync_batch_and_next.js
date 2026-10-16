const fs = require("fs");
const path = require("path");

const BASE_URL = process.env.CDP_URL || "http://127.0.0.1:9114";
const STATE_DIR = process.env.STATE_DIR || process.cwd();
const WebSocket = globalThis.WebSocket;

async function cdpCall(ws, method, params = {}) {
    return new Promise((resolve, reject) => {
        const id = Math.floor(Math.random() * 1000000);
        const handler = (msg) => {
            const data = JSON.parse(msg.data);
            if (data.id === id) {
                ws.removeEventListener("message", handler);
                if (data.error) reject(data.error);
                else resolve(data.result);
            }
        };
        ws.addEventListener("message", handler);
        ws.send(JSON.stringify({ id, method, params }));
    });
}

function getAdId(url) {
    if (!url) return null;
    const m = url.match(/(\d{6,10})/);
    return m ? m[1] : null;
}

async function syncAndNext() {
    const batchFile = path.join(STATE_DIR, "current_batch.json");
    if (!fs.existsSync(batchFile)) {
        console.log("No active batch found.");
        return;
    }

    const currentBatch = JSON.parse(fs.readFileSync(batchFile, "utf-8"));
    const queueFile = path.join(STATE_DIR, "review_queue.json");
    const queue = JSON.parse(fs.readFileSync(queueFile, "utf-8"));

    // 1. Get currently open tabs in BrowserOS Neo
    const liveTabs = await (await fetch(`${BASE_URL}/json`)).json();
    const livePages = liveTabs.filter(t => t.type === "page");

    const toDisqualify = [];
    const approved = [];

    for (const item of currentBatch) {
        const itemAdId = getAdId(item.url);
        const liveTab = livePages.find(t => {
            if (t.id === item.tabId) return true;
            if (itemAdId && getAdId(t.url) === itemAdId) return true;
            try {
                if (decodeURIComponent(t.url) === decodeURIComponent(item.url)) return true;
            } catch (e) {}
            return false;
        });

        if (!liveTab) {
            // User CLOSED the tab -> Disqualify in CRM
            toDisqualify.push(item);
        } else {
            // User kept the tab open -> Approved
            approved.push(item);
            // Close the live tab to keep browser clean
            await fetch(`${BASE_URL}/json/close/${liveTab.id}`).catch(() => {});
        }
    }

    console.log(`\n=== REVIEW RESULTS ===`);
    console.log(`✅ Approved leads: ${approved.length}`);
    approved.forEach(l => console.log(`   - Lead #${l.leadId} : ${l.priorityCode} ${l.nom_complet} (${l.quartier})`));

    console.log(`❌ Disqualified leads: ${toDisqualify.length}`);
    toDisqualify.forEach(l => console.log(`   - Lead #${l.leadId} : ${l.priorityCode} ${l.nom_complet} (${l.quartier})`));

    // 2. Disqualify closed leads in CRM if any
    if (toDisqualify.length > 0) {
        console.log("\nUpdating 'Non Qualifié' status in CRM...");
        const res = await fetch(`${BASE_URL}/json/new?https://espace.lereseau-ma.com/leads/create`, { method: "PUT" });
        const target = await res.json();
        const ws = new WebSocket(target.webSocketDebuggerUrl);
        await new Promise(r => ws.onopen = r);
        await new Promise(r => setTimeout(r, 1500));

        const tokenRes = await cdpCall(ws, "Runtime.evaluate", {
            expression: "document.querySelector(\"input[name='_token']\")?.value",
            returnByValue: true
        });
        const token = tokenRes.result ? tokenRes.result.value : null;

        for (const item of toDisqualify) {
            console.log(`Disqualifying Lead #${item.leadId}...`);
            const statusScript = `(async () => {
                const fd = new FormData();
                fd.append("_token", "${token}");
                fd.append("status", "Non Qualifié");
                fd.append("notes", "Disqualifié lors de la revue par l'utilisateur.");
                try {
                    await fetch("/leads/${item.leadId}/status", { method: "POST", body: fd });
                    return { success: true };
                } catch(e) { return { error: e.message }; }
            })()`;
            await cdpCall(ws, "Runtime.evaluate", { expression: statusScript, awaitPromise: true });
            await new Promise(r => setTimeout(r, 150));
        }

        await fetch(`${BASE_URL}/json/close/${target.id}`).catch(() => {});
        ws.close();
        console.log("CRM statuses updated successfully!");
    }

    // 3. Mark in review_queue.json
    for (const item of currentBatch) {
        const qItem = queue.find(q => q.id === item.leadId);
        if (qItem) {
            qItem.reviewed = true;
            qItem.status = toDisqualify.some(d => d.leadId === item.leadId) ? "Non Qualifié" : "Validé";
        }
    }
    fs.writeFileSync(queueFile, JSON.stringify(queue, null, 2));

    // 4. Open next batch
    console.log("\nOpening next batch...");
    require("./open_batch.js");
}

syncAndNext().catch(console.error);
