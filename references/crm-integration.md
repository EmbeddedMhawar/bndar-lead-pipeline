# CRM Integration & Chrome DevTools Protocol (CDP) Guide

Reference guide for automating `https://espace.lereseau-ma.com` (Laravel-based Conciergerie CRM) via BrowserOS Neo over CDP.

---

## 1. BrowserOS Neo CDP Endpoint

* **Endpoint**: `http://127.0.0.1:9114`
* **Target Listing**: `GET /json` or `GET /json/list`
* **Open Tab**: `PUT /json/new?<url>`
* **Activate Tab**: `GET /json/activate/<targetId>`
* **Close Tab**: `GET /json/close/<targetId>`

---

## 2. Authentication & Session Context

Because BrowserOS Neo is an active, persistent user browser:
* The user is already logged in to `espace.lereseau-ma.com`.
* Any new tab created via `PUT /json/new` inherits full session cookies and credentials.
* No passwords or secret keys need to be hardcoded in scripts.

---

## 3. Form Submission & CSRF Security

### Fast Injection via Web Worker
Instead of rendering heavy Blade templates, scripts can open a single worker tab to `/leads/create`, extract the CSRF token, and execute `fetch()` requests directly:

```javascript
// Extract token
const token = document.querySelector("input[name='_token']")?.value;

// Execute lead creation
const fd = new FormData();
fd.append("_token", token);
fd.append("nom_complet", "[P1-1] Suite Privée");
fd.append("phone_number", "0661000000");
fd.append("ville", "Casablanca");
fd.append("quartier", "Aïn Diab");
fd.append("type_propriete", "Appartement");
fd.append("disponibilite", "Disponible");
fd.append("notes", "https://www.avito.ma/...");

await fetch("/leads", { method: "POST", body: fd });
```

### Lead Status Updates
To update lead status (e.g. to `Non Qualifié` when rejected during review):

```javascript
const fd = new FormData();
fd.append("_token", token);
fd.append("status", "Non Qualifié");
fd.append("notes", "Disqualifié lors de la revue par l'utilisateur.");

await fetch(`/leads/${leadId}/status`, { method: "POST", body: fd });
```

---

## 4. Safety Guardrails

1. **Explicit Form Selectors**:
   * ⚠️ **Never use** `document.querySelector("form")` on edit/show pages!
   * The first `<form>` in the DOM header is frequently the `/logout` action.
   * **Always use** `form#leadForm` or `form[action*="/leads"]`.

2. **Backend Permission Handling**:
   * Regular agents do not have permission to execute `DELETE /leads/<id>` (`403 Forbidden: Seul le super administrateur peut supprimer un lead`).
   * Clean pipeline disqualification must be done by switching status to `Non Qualifié`.

---

## 5. Disqualification Tagging Conventions (`[EXPIRÉ]` vs `[IGNORÉ]`)

When a lead is disqualified, its status is changed to `Non Qualifié` and its name in the CRM is updated to reflect the reason:

1. **`[EXPIRÉ]` (Expired Listings)**:
   * **Trigger**: Ad expired or deleted on the portal (Mubawab 301-redirect to `/sd/...`, or Avito deactivated banner).
   * **Action**: `POST /leads/<id>/status` with `status: "Non Qualifié"` and notes `"Annonce expirée sur le portail"`, then update `nom_complet` via `/leads/<id>/edit` to `[EXPIRÉ] [P...] Nom`.

2. **`[IGNORÉ]` (Competitor / Foreign / Out-of-Scope)**:
   * **Trigger**: Ad is active online, but belongs to a competitor conciergerie (e.g. *Happy Key*), is in a foreign country (e.g. Spain), or is not a residential vacation property (e.g. transport service only).
   * **Action**: `POST /leads/<id>/status` with `status: "Non Qualifié"`, then update `nom_complet` via `/leads/<id>/edit` to `[IGNORÉ] [P...] Nom (Raison)`.

