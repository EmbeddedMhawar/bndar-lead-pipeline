const fs = require('fs');
const path = require('path');

const STATE_DIR = process.env.STATE_DIR || process.cwd();

function normalizePhone(p) {
    if (!p) return '';
    let clean = p.replace(/\D/g, '');
    if (clean.startsWith('212')) clean = '0' + clean.slice(3);
    if (clean.length === 9 && (clean.startsWith('6') || clean.startsWith('7'))) clean = '0' + clean;
    return clean;
}

function audit(records) {
    console.log(`Auditing ${records.length} records for phone number collisions...`);

    const fullMap = new Map();
    const last8Map = new Map();

    records.forEach(r => {
        const raw = r.phone_number || r.phone || '';
        const norm = normalizePhone(raw);
        const last8 = norm.slice(-8);

        if (norm) {
            if (!fullMap.has(norm)) fullMap.set(norm, []);
            fullMap.get(norm).push(r);
        }

        if (last8) {
            if (!last8Map.has(last8)) last8Map.set(last8, []);
            last8Map.get(last8).push(r);
        }
    });

    const fullDupes = [...fullMap.entries()].filter(([k, v]) => v.length > 1);
    const last8Dupes = [...last8Map.entries()].filter(([k, v]) => v.length > 1);

    console.log(`\n=== AUDIT SUMMARY ===`);
    console.log(`Total Records: ${records.length}`);
    console.log(`Unique Full Normalized Numbers: ${fullMap.size}`);
    console.log(`Full Duplicates: ${fullDupes.length}`);
    console.log(`Last 8-Digits Suffix Collisions: ${last8Dupes.length}`);

    if (fullDupes.length > 0) {
        console.log(`\n⚠️ Exact Duplicates Found:`);
        fullDupes.forEach(([phone, list]) => {
            console.log(`Phone ${phone} (${list.length} occurrences):`);
            list.forEach(item => console.log(`  - #${item.id || item.leadId}: ${item.nom_complet || item.name} (${item.quartier || item.sector})`));
        });
    } else {
        console.log(`\n✅ 100% UNIQUE: No duplicate phone numbers found!`);
    }

    return { total: records.length, unique: fullMap.size, duplicates: fullDupes.length };
}

// Support CLI run with file argument
if (require.main === module) {
    const fileArg = process.argv[2] || path.join(STATE_DIR, "review_queue.json");
    if (!fs.existsSync(fileArg)) {
        console.error(`File not found: ${fileArg}`);
        process.exit(1);
    }
    const data = JSON.parse(fs.readFileSync(fileArg, 'utf-8'));
    audit(data);
}

module.exports = { audit, normalizePhone };
