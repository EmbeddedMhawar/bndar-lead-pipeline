# AGENTS.md - Bndar Lead Pipeline

Guidelines for AI coding agents interacting with the Bndar lead pipeline.

## Critical Rules

1. **Anti-Broker Mandate**: Never approve or ingest real estate brokers (semsara), commercial real estate agencies, or competitor conciergeries (e.g. StayHere, Key Maroc, Amun, Yactis).
2. **Yield Priority Schema**: Always preserve and apply the priority prefix format `[P1-1]` through `[P4]` in `nom_complet`.
3. **Coastal Elevation**: Any property situated along the Atlantic coast outside central Casablanca (Route d'Azemmour, Tamaris, Sidi Rahal, Blanca Beach, El Mansouria, Bouznika, Sidi Bouzid) must be tagged `[P1-1]`.
4. **CRM Form Safety**: Never target generic `document.querySelector("form")` on lead pages because `form[0]` is often `/logout`. Always explicitly target `form#leadForm` or `form[action*="/leads"]`.
5. **No Destructive Deletion**: Standard CRM backend returns `403 Forbidden` on lead deletion. Always reject leads via `POST /leads/<id>/status` with status `"Non Qualifié"`.
6. **Location Ground-Truthing**: The location explicitly stated in the ad's title and description text strictly overrides Avito or Mubawab category metadata.
7. **Disqualification Tags**: Expired listings (Mubawab 301 redirects to `/sd/...` or Avito deletion banners) must be tagged `[EXPIRÉ]`. Reserve `[IGNORÉ]` strictly for competitor conciergeries (e.g. *Happy Key*), foreign listings, or out-of-scope services.

