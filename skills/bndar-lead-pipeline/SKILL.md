---
name: bndar-lead-pipeline
description: End-to-end methodology and automation pipeline for sourcing, anti-broker filtering, Airbtics yield-ranking, CRM-injecting, and human-in-the-loop batch-reviewing direct property owner leads for premium hospitality conciergerie.
---

# Bndar Lead Pipeline Skill (`bndar-lead-pipeline`)

This skill orchestrates the end-to-end pipeline for building, cleaning, and verifying a high-yield direct property owner CRM database for **Bndar** (Hospitality Conciergerie) in Casablanca and surrounding coastal areas.

It enforces a zero-broker policy, Airbtics-backed revenue tiering, automated CRM injection via Chrome DevTools Protocol (CDP), and an interactive 10-tab batch review workflow in BrowserOS Neo.

---

## 1. Pipeline Architecture

```
[Portals: Avito / Mubawab]
       │
       ▼
[Anti-Broker Filtration] ──► Deduplicate phone numbers, blacklist agencies & brokers
       │
       ▼
[Airbtics Yield Ranking] ──► Map sectors to yield tiers [P1-1] -> [P4]
       │
       ▼
[CRM Direct Injection]   ──► CDP Worker injects verified owners via authenticated API
       │
       ▼
[Interactive Batch Review]─► Opens 10 tabs at a time in BrowserOS Neo in priority order
       │
       ├─► Closed tabs   ──► Automatically marked "Non Qualifié" in CRM
       └─► Kept tabs     ──► Automatically approved + coastal gem re-tagging
       │
       ▼
[Zero-Duplicate Audit]   ──► Multi-level phone collision verification (100% unique)
```

---

## 2. Yield Tiers & Sector Taxonomy

Rankings are established based on Airbtics market performance data for short-term rental revenue compared to city average:

| Priority Code | Sector / Zone | Airbtics Yield Premium | Key Characteristics |
|---|---|---|---|
| **`[P1-1]`** | **Corniche, Aïn Diab, Rte d'Azemmour, Tamaris, Sidi Rahal, El Mansouria, Sidi Bouzid** | **+51% & Coastal** | Beachfront resorts, villas, cabanons, ultra-high ADR |
| **`[P1-2]`** | **Anfa, Anfa Supérieur** | **+21%** | Luxury villas & upscale private apartments |
| **`[P1-3]`** | **Marina, Casa-Port** | **+11%** | Waterfront business & modern tourist residences |
| **`[P1-4]`** | **Maârif, Les Princesses, Val Fleuri** | **+7%** | High booking occupancy, shopping & dining hub |
| **`[P1-5]`** | **Racine** | **+0%** | Trendy urban district, consistent business travelers |
| **`[P2-6]`** | **Gauthier** | **-3%** | Art-deco, central dining & nightlife |
| **`[P2-7]`** | **Palmier** | **-5%** | Business & residential hybrid |
| **`[P2-8]`** | **Habous** | **-6%** | Cultural & artisanal appeal |
| **`[P2-9]`** | **CIL** | **-9%** | Quiet luxury villas & leafy residences |
| **`[P2-10]`** | **Belvédère** | **-10%** | Station proximity (Casa-Voyageurs) |
| **`[P3-11]`** | **Bourgogne, Bourgogne Ouest** | **-11%** | Dense residential, popular rental volume |
| **`[P3-12]`** | **Casablanca Finance City (CFC)** | **-14%** | Modern business towers, corporate stays |
| **`[P3-13]`** | **Oasis** | **-14%** | Residential suburban villas |
| **`[P3-14]`** | **Beauséjour** | **-14%** | Mid-tier residential hub |
| **`[P3-15]`** | **Centre Ville, Roches Noires, Derb Omar** | **-19%** | Budget tourism & commercial travelers |
| **`[P3-16]`** | **Sidi Maarouf, Nearshore** | **-23%** | Tech parks & IT corporate rentals |
| **`[P4]`** | **Californie, 2 Mars, Aïn Sebaâ, Oulfa, etc.** | **Secondary** | Peripheral residential sectors |

> [!IMPORTANT]
> **Coastal Elevation Rule**: Whenever an ad mentions beachfront, cabanon, or seaside vacation rental outside Casablanca center (e.g. Route d'Azemmour, Tamaris, Blanca Beach, Sidi Rahal, El Mansouria, Sidi Bouzid), it must be elevated to **`[P1-1]`** due to high summer ADR.

---

## 3. Anti-Broker Filtration Rules

Never inject real estate agents, intermediaries (semsara), or competitor conciergeries:
1. **Badges & Storefronts**: Exclude any advertiser with `Boutique`, `Pro`, or `Agence`.
2. **Keyword Blacklist**: Exclude descriptions with "honoraires d'agence", "frais d'agence", "commission", "notre agence", "bureau immobilier".
3. **Multi-listing Deduplication**: Discard phone numbers associated with multiple unrelated properties across different areas (typical broker behavior).
4. **Competitor Screening**: Identify and immediately flag known hospitality conciergeries (e.g. *StayHere*, *Key Maroc*, *Amun Hospitality*, *Yactis Stays*).

---

## 4. CRM Direct Injection Engine

The CRM runs on Laravel (`https://espace.lereseau-ma.com`). To inject leads without loading heavy UI pages:
- Open a worker CDP tab to `https://espace.lereseau-ma.com/leads/create`.
- Extract the CSRF `_token` from the DOM:
  ```javascript
  const token = document.querySelector("input[name='_token']")?.value;
  ```
- Send a direct `POST` to `/leads` via `fetch()` using `FormData` from within the worker tab:
  ```javascript
  const fd = new FormData();
  fd.append("_token", token);
  fd.append("nom_complet", `[${priorityCode}] ${advertiserName}`);
  fd.append("phone_number", cleanPhoneNumber);
  fd.append("ville", "Casablanca");
  fd.append("quartier", sectorName);
  fd.append("type_propriete", "Appartement");
  fd.append("disponibilite", "Disponible");
  fd.append("notes", originalAdUrl);
  await fetch("/leads", { method: "POST", body: fd });
  ```
- **Execution Speed**: ~150ms per lead.

---

## 5. Interactive Batch Review Workflow

To prevent reviewer fatigue and ensure 100% human verification:

1. **Batch Slicing**:
   - The queue is sorted by descending yield priority (`[P1-1]` down to `[P4]`).
   - Opens **10 tabs at a time** in BrowserOS Neo via CDP (`PUT /json/new?<adUrl>`).
   - The first tab of the batch is brought to focus via `GET /json/activate/<tabId>`.

2. **User Interaction**:
   - The user looks at the listing photos, amenities, and host profile.
   - **If the ad is bad/unsuitable**: User simply **closes the tab**.
   - **If the ad is good**: User **leaves the tab open**.
   - The user types **« ok »** or **« suivant »** in chat.

3. **Automated Synchronization (`sync_batch_and_next.js`)**:
   - The script inspects live targets on CDP endpoint `http://127.0.0.1:9114/json`.
   - Compares open tabs against `current_batch.json` using **both target IDs and normalized ad URLs** (ensures resilience against browser restarts).
   - **Closed Tabs**: Automatically updated in CRM to status **`Non Qualifié`** with notes `"Disqualifié lors de la revue par l'utilisateur"`.
   - **Kept Tabs**: Marked **`Validé`**, and closed cleanly to prepare for the next batch.
   - Automatically opens the next 10 unreviewed leads.

---

## 6. Zero-Duplicate Audit Protocol

Before finishing a lead campaign, execute a two-level collision audit:
1. **Indicatif Normalization**: Strip spaces, hyphens, and convert `+212...` or `00212...` to national format `06...` / `07...`.
2. **Last 8 Digits Match**: Compare subscriber suffixes (`digits.slice(-8)`) to catch any masked duplicates.
3. Every approved lead must be 100% unique.

---

## 7. Safety Rules & Gotchas

> [!CAUTION]
> **Form Targeting Safety**: In the CRM, `document.querySelector("form")` on lead pages often targets `/logout` (which will terminate the session). Always explicitly target `form#leadForm` or `form[action*="/leads"]`.

> [!WARNING]
> **Permission Limitations**: Standard CRM credentials may return `403 Forbidden` on `DELETE /leads/<id>`. Lead rejection must be executed via `POST /leads/<id>/status` with `status: "Non Qualifié"`. This safely archives the lead away from the default active pipeline.
