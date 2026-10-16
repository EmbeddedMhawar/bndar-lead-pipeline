# Bndar Lead Pipeline 🏨📊

> End-to-end methodology and automation pipeline for sourcing, anti-broker filtering, Airbtics yield-ranking, CRM-injecting, and human-in-the-loop batch-reviewing direct property owner leads for premium hospitality conciergerie.

---

## 🌟 Overview

The **Bndar Lead Pipeline** was built to solve the core customer acquisition problem for hospitality conciergeries: **how to build a database of 100+ verified direct property owners in premium sectors, strictly free of real estate brokers (semsara) and commercial agencies.**

It combines:
1. **Targeted Scraping & Anti-Semsara Filtration**: Identifying true private landlords and eliminating commercial agencies and intermediaries.
2. **Airbtics Market Yield Hierarchy**: Structuring leads into revenue tiers (`[P1-1]` coastal beachfront down to `[P4]` peripheral).
3. **Automated CRM Direct Injection**: Ingestion into Laravel-based CRM (`espace.lereseau-ma.com`) via authenticated CDP Web Workers.
4. **Interactive 10-Tab Batch Review Protocol**: Human-in-the-loop verification in BrowserOS Neo where closing tabs automatically disqualifies listings in the CRM.
5. **Zero-Duplicate Phone Collision Audit**: Rigorous normalization and multi-level collision checks.

---

## 🚀 Priority Yield Tiers (Casablanca Market)

* **`[P1-1]` Coastline & Beach Resorts (+51%)**: La Corniche, Aïn Diab, Route d'Azemmour, Tamaris, Sidi Rahal, Blanca Beach, El Mansouria, Sidi Bouzid.
* **`[P1-2]` Anfa (+21%)**: Upscale villas and luxury residences.
* **`[P1-3]` Marina & Casa-Port (+11%)**: Modern waterfront business towers.
* **`[P1-4]` Maârif & Les Princesses (+7%)**: Year-round highest occupancy.
* **`[P1-5]` Racine**: Trendy central district.
* **`[P2]` High Yield Heritage & Business**: Gauthier, Belvédère, Palmier.
* **`[P3]` Core Residential & Tech**: Bourgogne, Oasis, Centre Ville, Sidi Maarouf (Nearshore).
* **`[P4]` Peripheral Residential**: Californie, 2 Mars, Oulfa, Aïn Sebaâ.

---

## 🛠️ Repository Structure

```
bndar-lead-pipeline/
├── skills/
│   └── bndar-lead-pipeline/
│       └── SKILL.md            # Agent skill instructions & trigger rules
├── scripts/
│   ├── open_batch.js           # Opens 10 leads in BrowserOS Neo in priority order
│   ├── sync_batch_and_next.js  # Detects closed/kept tabs, updates CRM & opens next batch
│   ├── rename_priority.js      # Updates CRM lead name with [P1-1]..[P4] prefixes
│   └── audit_duplicates.js     # Multi-level phone collision verification
├── references/
│   ├── yield-benchmarks.md     # Airbtics revenue benchmarking and sector taxonomy
│   └── crm-integration.md      # CDP automation, CSRF handling & safety guardrails
├── install.sh                  # Installs skill into Antigravity global config
├── AGENTS.md                   # Operational guidelines for AI coding agents
└── README.md                   # Project overview & documentation
```

---

## 💻 Installation

To register this skill with Google Antigravity / AI Agent:

```bash
chmod +x install.sh
./install.sh
```

Or manually symlink:
```bash
ln -sf "$(pwd)/skills/bndar-lead-pipeline" ~/.gemini/config/skills/bndar-lead-pipeline
```

---

## 📋 Interactive Batch Review Usage

1. **Start Review**:
   ```bash
   node scripts/open_batch.js
   ```
2. **Review in BrowserOS Neo**:
   - Close tabs for listings you reject.
   - Leave tabs open for listings you approve.
3. **Synchronize & Enchain**:
   ```bash
   node scripts/sync_batch_and_next.js
   ```
4. **Audit Uniqueness**:
   ```bash
   node scripts/audit_duplicates.js
   ```

---

## 📄 License

MIT © [Bndar](https://bndar.com) & [Abderrahmane Mhawar](https://github.com/EmbeddedMhawar).
