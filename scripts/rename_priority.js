const fs = require('fs');
const path = require('path');

const BASE_URL = process.env.CDP_URL || "http://127.0.0.1:9114";
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

async function renameLead(leadId, newName) {
    console.log(`Renaming Lead #${leadId} -> "${newName}"...`);
    const res = await fetch(`${BASE_URL}/json/new?https://espace.lereseau-ma.com/leads/${leadId}/edit`, { method: "PUT" });
    const target = await res.json();
    const ws = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise(r => ws.onopen = r);
    await new Promise(r => setTimeout(r, 1500));

    const evalScript = `(() => {
        const input = document.querySelector("input[name='nom_complet']");
        if (input) {
            input.value = ${JSON.stringify(newName)};
            const form = document.querySelector("form#leadForm") || document.querySelector("form[action*='/leads/${leadId}']");
            if (form) {
                form.submit();
                return { success: true };
            }
        }
        return { error: "Form not found" };
    })()`;

    const resEval = await cdpCall(ws, "Runtime.evaluate", { expression: evalScript, returnByValue: true });
    await new Promise(r => setTimeout(r, 1200));
    await fetch(`${BASE_URL}/json/close/${target.id}`).catch(() => {});
    ws.close();
    return resEval?.result?.value;
}

if (require.main === module) {
    const leadId = process.argv[2];
    const newName = process.argv[3];
    if (!leadId || !newName) {
        console.error("Usage: node rename_priority.js <leadId> <newName>");
        process.exit(1);
    }
    renameLead(leadId, newName).then(console.log).catch(console.error);
}

module.exports = { renameLead };
