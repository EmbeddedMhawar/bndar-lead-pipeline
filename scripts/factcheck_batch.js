/**
 * factcheck_batch.js
 *
 * Opens 10 approved leads at a time in BrowserOS Neo via Chrome DevTools Protocol (CDP),
 * extracts live ad titles and descriptions, detects expired ads (Mubawab 301 redirects to /sd/
 * or Avito deletion banners), and compares cited ad location against portal metadata.
 */

const fs = require('fs');
const path = require('path');

const BASE_URL = process.env.BROWSEROS_NEO_URL || 'http://127.0.0.1:9114';
const WebSocket = globalThis.WebSocket;

const LOCATION_KEYWORDS = [
    { name: "La Corniche / Aïn Diab", code: "[P1-1]", regex: /\b(corniche|a[iï]n\s*diab|oc[eé]an|phare|sindi?bad)\b/i },
    { name: "Tamaris", code: "[P1-1]", regex: /\btamaris\b/i },
    { name: "Sidi Rahal / Blanca Beach", code: "[P1-1]", regex: /\b(sidi\s*rahal|blanca\s*beach|ola\s*blanca)\b/i },
    { name: "El Mansouria / Bouznika", code: "[P1-1]", regex: /\b(mansouria|bouznika|eden\s*island)\b/i },
    { name: "Sidi Bouzid", code: "[P1-1]", regex: /\bsidi\s*bouzid\b/i },
    { name: "Route d'Azemmour / Dar Bouazza", code: "[P1-1]", regex: /\b(azemmour|dar\s*bouazza|darbouazza)\b/i },
    { name: "Anfa Supérieur", code: "[P1-2]", regex: /\b(anfa|anfa\s*sup[eé]rieur)\b/i },
    { name: "Marina / Casa-Port", code: "[P1-3]", regex: /\b(marina|casa[\s-]*port)\b/i },
    { name: "Maârif / Princesses / Val Fleuri", code: "[P1-4]", regex: /\b(ma[aâ]rif|princesses?|val\s*fleuri|ghandi|roudani)\b/i },
    { name: "Racine / Triangle d'Or", code: "[P1-5]", regex: /\b(racine|triangle\s*d['\s]*or)\b/i },
    { name: "Gauthier", code: "[P2-6]", regex: /\bgauthier\b/i },
    { name: "Palmier", code: "[P2-7]", regex: /\bpalmier\b/i },
    { name: "Habous", code: "[P2-8]", regex: /\bhabous\b/i },
    { name: "CIL", code: "[P2-9]", regex: /\bcil\b/i },
    { name: "Belvédère", code: "[P2-10]", regex: /\bbelv[eé]d[eè]re\b/i },
    { name: "Bourgogne", code: "[P3-11]", regex: /\bbourgogne\b/i },
    { name: "Casablanca Finance City (CFC)", code: "[P3-12]", regex: /\b(cfc|finance\s*city)\b/i },
    { name: "Oasis", code: "[P3-13]", regex: /\boasis\b/i },
    { name: "Beauséjour", code: "[P3-14]", regex: /\bbeaus[eé]jour\b/i },
    { name: "Centre Ville / Casa Voyageurs", code: "[P3-15]", regex: /\b(centre\s*ville|casa[\s-]*voyageurs?|roches?\s*noires?|derb\s*omar|mers\s*sultan)\b/i },
    { name: "Sidi Maarouf / Nearshore", code: "[P3-16]", regex: /\b(sidi\s*maarouf|nearshore)\b/i }
];

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

async function factcheckBatch(queuePath = './scratch/factcheck_queue.json') {
    if (!fs.existsSync(queuePath)) {
        console.error(`Queue file not found at ${queuePath}`);
        return;
    }

    const queue = JSON.parse(fs.readFileSync(queuePath, 'utf-8'));
    const unreviewed = queue.filter(l => !l.factchecked);

    if (unreviewed.length === 0) {
        console.log("All approved leads have been fact-checked!");
        return;
    }

    const batch = unreviewed.slice(0, 10);
    const batchNumber = Math.floor(queue.filter(l => l.factchecked).length / 10) + 1;
    console.log(`\n=== OUVERTURE DU LOT DE FACT-CHECKING #${batchNumber} (10 Leads) ===`);

    const currentBatchRecord = [];
    let firstTabId = null;

    for (let i = 0; i < batch.length; i++) {
        const item = batch[i];
        console.log(`[${i + 1}/${batch.length}] Analyse Lead #${item.id}: ${item.currentPriority} ${item.nom_complet}...`);

        try {
            const res = await fetch(`${BASE_URL}/json/new?${encodeURI(item.url)}`, { method: 'PUT' });
            const target = await res.json();
            if (i === 0) firstTabId = target.id;

            let extractedTitle = "";
            let extractedDesc = "";
            let isExpired = false;
            let detectedLocations = [];

            try {
                const ws = new WebSocket(target.webSocketDebuggerUrl);
                await new Promise(r => ws.onopen = r);
                await new Promise(r => setTimeout(r, 2000));

                const domData = await cdpCall(ws, 'Runtime.evaluate', {
                    expression: `(() => {
                        const currentUrl = window.location.href;
                        const h1 = document.querySelector("h1")?.innerText || "";
                        const heading = Array.from(document.querySelectorAll("h2, h3, div, span")).find(el => el.innerText?.trim() === "Description");
                        let desc = "";
                        if (heading && heading.parentElement) {
                            desc = heading.parentElement.innerText.replace("Description", "").trim();
                        }
                        if (!desc) {
                            const descEl = document.querySelector("p[data-testid='description'], .description, #description, [data-cy='ad-description'], .blockPropContent, p");
                            desc = descEl?.innerText || "";
                        }
                        const bodyText = document.body.innerText;
                        const isMubawabExpired = currentUrl.includes("/sd/") || currentUrl.includes("appartements-vacational");
                        const isAvitoDeleted = bodyText.includes("supprimée") || bodyText.includes("plus disponible") || bodyText.includes("Page introuvable");
                        return { title: h1, desc: desc.slice(0, 2000), isExpired: isMubawabExpired || isAvitoDeleted, currentUrl };
                    })()`,
                    returnByValue: true
                });

                if (domData.result?.value) {
                    extractedTitle = domData.result.value.title;
                    extractedDesc = domData.result.value.desc;
                    isExpired = domData.result.value.isExpired;

                    const fullText = (extractedTitle + " " + extractedDesc).toLowerCase();
                    for (const kw of LOCATION_KEYWORDS) {
                        if (kw.regex.test(fullText)) {
                            detectedLocations.push({ name: kw.name, code: kw.code });
                        }
                    }
                }
                ws.close();
            } catch (err) {
                console.error(`Error reading DOM for #${item.id}:`, err.message);
            }

            currentBatchRecord.push({
                tabId: target.id,
                leadId: item.id,
                nom_complet: item.nom_complet,
                currentPriority: item.currentPriority,
                currentQuartier: item.currentQuartier,
                url: item.url,
                phone: item.phone_number,
                extractedTitle,
                extractedDesc,
                isExpired,
                detectedLocations
            });

        } catch (e) {
            console.error(`Failed to open ${item.url}:`, e.message);
        }
        await new Promise(r => setTimeout(r, 400));
    }

    if (firstTabId) {
        await fetch(`${BASE_URL}/json/activate/${firstTabId}`).catch(() => {});
    }

    fs.writeFileSync(path.join(path.dirname(queuePath), 'current_factcheck_batch.json'), JSON.stringify(currentBatchRecord, null, 2));

    console.log(`\nLot #${batchNumber} inspecté avec succès ! Diagnostic :`);
    console.table(currentBatchRecord.map(r => ({
        ID: r.leadId,
        Nom: r.nom_complet,
        Quartier: r.currentQuartier,
        Expiré: r.isExpired ? "OUI [EXPIRÉ]" : "Non",
        LieuDétecté: r.detectedLocations.map(l => l.code).join(', ') || "-"
    })));
}

if (require.main === module) {
    factcheckBatch().catch(console.error);
}

module.exports = { factcheckBatch, LOCATION_KEYWORDS };
