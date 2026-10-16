const fs = require("fs");
const path = require("path");

const BASE_URL = process.env.CDP_URL || "http://127.0.0.1:9114";
const STATE_DIR = process.env.STATE_DIR || process.cwd();

async function openBatch() {
    const queueFile = path.join(STATE_DIR, "review_queue.json");
    if (!fs.existsSync(queueFile)) {
        console.error("review_queue.json not found in " + STATE_DIR);
        return;
    }

    const queue = JSON.parse(fs.readFileSync(queueFile, "utf-8"));
    const unreviewed = queue.filter(l => !l.reviewed);
    if (unreviewed.length === 0) {
        console.log("All leads have been reviewed!");
        return;
    }

    const batchSize = parseInt(process.env.BATCH_SIZE || "10", 10);
    const batch = unreviewed.slice(0, batchSize);
    console.log(`=== OPENING BATCH OF ${batch.length} LEADS ===`);

    const currentBatchRecord = [];
    let firstTabId = null;

    for (let i = 0; i < batch.length; i++) {
        const item = batch[i];
        console.log(`[${i + 1}/${batch.length}] Opening Lead #${item.id}: ${item.priorityCode} ${item.nom_complet} (${item.quartier})...`);
        try {
            const res = await fetch(`${BASE_URL}/json/new?${encodeURI(item.notes)}`, { method: "PUT" });
            const data = await res.json();
            if (i === 0) firstTabId = data.id;

            currentBatchRecord.push({
                tabId: data.id,
                leadId: item.id,
                nom_complet: item.nom_complet,
                priorityCode: item.priorityCode,
                quartier: item.quartier,
                url: item.notes
            });
        } catch (e) {
            console.error(`Failed to open ${item.notes}:`, e.message);
        }
        await new Promise(r => setTimeout(r, 400));
    }

    // Activate the first tab
    if (firstTabId) {
        await fetch(`${BASE_URL}/json/activate/${firstTabId}`).catch(() => {});
    }

    fs.writeFileSync(
        path.join(STATE_DIR, "current_batch.json"),
        JSON.stringify(currentBatchRecord, null, 2)
    );

    console.log("\nBatch opened successfully!");
    console.log("Rule: Close the tabs for listings you wish to ignore / disqualify.");
    console.log("When finished, say 'ok' or 'suivant' to sync CRM choices and open the next batch!");
}

openBatch().catch(console.error);
