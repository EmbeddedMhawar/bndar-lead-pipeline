/**
 * unassign_all_leads.js
 *
 * Removes assignment ("Retirer l'assignation") for all leads in the CRM
 * via authenticated CDP in BrowserOS Neo.
 */

const fs = require('fs');
const BASE_URL = process.env.BROWSEROS_NEO_URL || 'http://127.0.0.1:9114';
const WebSocket = globalThis.WebSocket;

async function cdpCall(ws, method, params = {}) {
    return new Promise((resolve, reject) => {
        const id = Math.floor(Math.random() * 1000000);
        const onMsg = (event) => {
            const data = JSON.parse(event.data);
            if (data.id === id) {
                ws.removeEventListener('message', onMsg);
                if (data.error) reject(data.error);
                else resolve(data.result);
            }
        };
        ws.addEventListener('message', onMsg);
        ws.send(JSON.stringify({ id, method, params }));
    });
}

async function unassignLeads(leadIds = []) {
    const tabs = await (await fetch(`${BASE_URL}/json/list`)).json();
    let tab = tabs.find(t => t.url.includes('espace.lereseau-ma.com/leads'));
    if (!tab) {
        throw new Error("No active /leads tab found in BrowserOS Neo");
    }

    const ws = new WebSocket(tab.webSocketDebuggerUrl);
    await new Promise(r => ws.onopen = r);

    const CHUNK_SIZE = 10;
    let success = 0;
    let skipped = 0;

    for (let i = 0; i < leadIds.length; i += CHUNK_SIZE) {
        const chunk = leadIds.slice(i, i + CHUNK_SIZE);
        const res = await cdpCall(ws, 'Runtime.evaluate', {
            expression: `(async () => {
                const token = document.querySelector('input[name="_token"]')?.value || document.querySelector('meta[name="csrf-token"]')?.content;
                const chunkIds = ${JSON.stringify(chunk)};
                return await Promise.all(chunkIds.map(async (id) => {
                    try {
                        const fd = new FormData();
                        fd.append('_token', token);
                        fd.append('_method', 'PATCH');
                        fd.append('assigned_to', '');
                        const r = await fetch('/leads/' + id + '/reassign', {
                            method: 'POST',
                            headers: { 'X-CSRF-TOKEN': token, 'X-Requested-With': 'XMLHttpRequest' },
                            body: fd,
                            redirect: 'manual'
                        });
                        return { id, status: r.status };
                    } catch (e) {
                        return { id, error: e.message };
                    }
                }));
            })()`,
            awaitPromise: true,
            returnByValue: true
        });

        const results = res.result?.value || [];
        for (const r of results) {
            if (r.status === 200 || r.status === 302 || r.status === 0) success++;
            else skipped++;
        }
        await new Promise(r => setTimeout(r, 150));
    }

    // Refresh page to sync DOM
    await cdpCall(ws, 'Page.navigate', { url: 'https://espace.lereseau-ma.com/leads' });
    ws.close();
    return { success, skipped };
}

module.exports = { unassignLeads };
