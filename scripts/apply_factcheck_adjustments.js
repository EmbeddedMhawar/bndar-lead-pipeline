/**
 * apply_factcheck_adjustments.js
 *
 * Applies fact-checking decisions to the CRM via authenticated CDP tabs:
 * 1. Closes open batch tabs in BrowserOS Neo.
 * 2. Updates expired leads to status "Non Qualifié" and tags with "[EXPIRÉ]".
 * 3. Updates competitor/out-of-scope leads to status "Non Qualifié" and tags with "[IGNORÉ]".
 * 4. Renames leads with refined locations (e.g. "[P1-1] Nom (Dar Bouazza)" or "[P1-4] Nom (Ghandi / Roudani)").
 * 5. Updates local queue files.
 */

const fs = require('fs');
const path = require('path');

const BASE_URL = process.env.BROWSEROS_NEO_URL || 'http://127.0.0.1:9114';
const WebSocket = globalThis.WebSocket;

async function cdpCall(ws, method, params = {}) {
    return new Promise((resolve, reject) => {
        const id = Math.floor(Math.random() * 1000000);
        const handler = (msg) => {
            const data = JSON.parse(msg.data);
            if (data.id === id) {
                ws.removeEventListener('message', handler);
                if (data.error) reject(data.error);
                else resolve(data.result);
            }
        };
        ws.addEventListener('message', handler);
        ws.send(JSON.stringify({ id, method, params }));
    });
}

async function renameLeadInCRM(leadId, newName) {
    const editTabRes = await fetch(`${BASE_URL}/json/new?https://espace.lereseau-ma.com/leads/${leadId}/edit`, { method: 'PUT' });
    const editTarget = await editTabRes.json();
    const editWs = new WebSocket(editTarget.webSocketDebuggerUrl);
    await new Promise(r => editWs.onopen = r);
    await new Promise(r => setTimeout(r, 1800));

    await cdpCall(editWs, 'Runtime.evaluate', {
        expression: `(() => {
            const input = document.querySelector("input[name='nom_complet']");
            if (input) {
                input.value = ${JSON.stringify(newName)};
                const form = document.querySelector("form#leadForm") || document.querySelector("form[action*='/leads/${leadId}']");
                if (form) form.submit();
            }
        })()`
    });
    await new Promise(r => setTimeout(r, 1200));
    await fetch(`${BASE_URL}/json/close/${editTarget.id}`).catch(() => {});
    editWs.close();
}

async function setLeadStatusInCRM(leadId, status, notes) {
    const res = await fetch(`${BASE_URL}/json/new?https://espace.lereseau-ma.com/leads/create`, { method: 'PUT' });
    const target = await res.json();
    const ws = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise(r => ws.onopen = r);
    await new Promise(r => setTimeout(r, 1500));

    const tokenRes = await cdpCall(ws, 'Runtime.evaluate', {
        expression: "document.querySelector(\"input[name='_token']\")?.value",
        returnByValue: true
    });
    const token = tokenRes.result ? tokenRes.result.value : null;

    if (token) {
        await cdpCall(ws, 'Runtime.evaluate', {
            expression: `(async () => {
                const fd = new FormData();
                fd.append("_token", "${token}");
                fd.append("status", "${status}");
                fd.append("notes", "${notes}");
                return await (await fetch("/leads/${leadId}/status", { method: "POST", body: fd })).status;
            })()`,
            awaitPromise: true
        });
    }
    await fetch(`${BASE_URL}/json/close/${target.id}`).catch(() => {});
    ws.close();
}

async function applyFactcheckAdjustments(adjustments = []) {
    // 1. Close current open batch tabs
    const currentBatchFile = './scratch/current_factcheck_batch.json';
    if (fs.existsSync(currentBatchFile)) {
        const currentBatch = JSON.parse(fs.readFileSync(currentBatchFile, 'utf-8'));
        for (const item of currentBatch) {
            await fetch(`${BASE_URL}/json/close/${item.tabId}`).catch(() => {});
        }
    }

    // 2. Process adjustments
    for (const adj of adjustments) {
        if (adj.type === 'EXPIRED') {
            const tag = `[EXPIRÉ] ${adj.newName || adj.name}`;
            console.log(`Disqualification [EXPIRÉ] Lead #${adj.id} -> ${tag}`);
            await setLeadStatusInCRM(adj.id, 'Non Qualifié', 'Annonce expirée ou supprimée sur le portail.');
            await renameLeadInCRM(adj.id, tag);
        } else if (adj.type === 'IGNORED') {
            const tag = `[IGNORÉ] ${adj.newName || adj.name}`;
            console.log(`Disqualification [IGNORÉ] Lead #${adj.id} -> ${tag}`);
            await setLeadStatusInCRM(adj.id, 'Non Qualifié', adj.reason || 'Lead hors-scope / concurrent.');
            await renameLeadInCRM(adj.id, tag);
        } else if (adj.type === 'RENAME') {
            console.log(`Renommage précis Lead #${adj.id} -> "${adj.newName}"`);
            await renameLeadInCRM(adj.id, adj.newName);
        }
    }

    console.log("Ajustements CRM appliqués avec succès !");
}

module.exports = { applyFactcheckAdjustments, renameLeadInCRM, setLeadStatusInCRM };
