---
name: bndar-prospection
description: Outbound prospecting workflow and execution playbooks for Bndar Conciergerie. Generates actionable 5-prospect batches with a WhatsApp warmup-first cadence (custom voice notes and listing audits) before escalating to direct phone calls, with ground-truth location auditing and Le Réseau CRM lifecycle tracking.
---

# Bndar Prospection Skill (`bndar-prospection`)

Outbound sales methodology, script execution, and CRM pipeline management tailored for **Bndar** (Hospitality Conciergerie in Casablanca and surrounding coastal areas).

This skill enforces a disciplined **5-prospect batch workflow**, prioritizing **WhatsApp warmup voice notes** before escalating to direct phone calls, with strict ground-truth listing verification and Le Réseau CRM status synchronization.

---

## 1. Cadence & Operating Rules

```
[Batch of 5 Prospects]
        │
        ▼
[Ground-Truth Pre-Flight] ──► Check real address, unit type, and anti-broker status
        │
        ▼
[Touchpoint 1: WhatsApp]  ──► 8–12s personalized voice note (negative-reverse audit offer)
        │
        ├──► Status in CRM: "Nouveau" ──► "Pas répondu relance 1" upon send
        │
        ├──► Prospect replies (Positive) ──► Advance to Steps ②, ③, ④ ("En Discussion")
        ├──► Prospect taken by competitor ─► Mark "Non Qualifié" + 3-6 mo callback note
        │
        ▼ (Wait 24h grace window)
[Touchpoint 2: Phone Call] ──► Direct cold call if no reply to WhatsApp warmup
        │
        └──► Status in CRM: "Pas répondu relance 2"
```

### Why Batches of 5?
* **Zero Spray-and-Pray**: Each prospect gets individual attention and a genuinely customized voice note.
* **Immediate Response Handling**: Staying on top of live WhatsApp notifications without backlog delays.
* **Vocal Quality**: Voice energy stays sharp and relaxed ("feet on desk" posture) without vocal fatigue.

---

## 2. Ground-Truth Pre-Flight Check

Before recording any audio or dialing:
1. **Dismantle Portal Tag Traps**:
   * Portals frequently categorize properties into broad municipal zones (e.g., tagging *Dar Bouazza / Ain Gedid* under generic *"Anfa"*).
   * **Rule**: Always extract the real micro-neighborhood or residence name from the listing description (e.g., *Le 134 Square*, *Twin Center*, *Bourgogne côté Mosquée Hassan II*).
2. **Anti-Broker Filter**:
   * Verify seller type (`PRIVATE`).
   * Blacklist commercial keywords: `airbnb`, `conciergerie`, `immobilière`, `agence`, `luxury suites`.
3. **Property Characteristics**:
   * Identify property type (*Studio*, *Loft*, *Appartement*, *Villa*).
   * Note high-value amenities (*piscine*, *vue mer*, *neuf / rénové*).

---

## 3. The 4-Step Prospection Framework (Moroccan Darija)

### ① DAKHLA (WhatsApp Voice Note: 8–12 Seconds)
*Goal: Disarm sales resistance, establish local context, and ask for permission to share free audit value.*

> « Salam **[Si / Lalla Prénom]**,  
> Cheft l'annonce f **[Avito / Mubawab]** 3la **[le studio / l'appartement]** dialek f **[Quartier / Résidence exact]** — saraha **[zwin / zwina]** bzaf, **[hook: vue mer m3a la piscine / nqi w m-finy]** saraha **[fih / fiha]** potentiel kbir.  
> Dakchi 3lach sbe9t w khedmet 3la 9eblek, fabour: 9addit w 7essent lik t-tsawer, w wejjedt lik un audit fih l-khotowat li t9ed dir bach t-tele3 l-madkhoul dialek b 30% tal 40%.  
> Wach momkin tkoun disponible l chi appel visio wla chi rencontre / goulsa, bach nwerik hadchi li wejjedt lik ? »

*Recording Tip*: Release the WhatsApp microphone button **instantly** on the last syllable to avoid trailing dead air.

---

### ② ILA 9AL IYEH / SI RÉPONSE POSITIVE (Speed Introduction)
*Goal: Position Bndar clearly without bloated corporate jargon.*

> « Parfait ! N9eddem lik rassi : **Abderrahmane**, 3endi conciergerie f **Casablanca**, smitha **Bndar**.  
> Hna kan-optimiziw l-madkhoul dial les propriétaires w kangériw koulchi men A tal Z — l-voyageurs (les clients), le ménage, l-accueil w les arrivées — w hadchi ghir b **pourcentage** men dakchi li kaydkhel lik f l-jib. **Ma kanreb7o 7ta katreba7 nta.**  
> W justement : n9ed n3awnek t-tele3 had les revenus bla ma tebqa mberzet rask b had t-tekhrbiq kamel b ydik. »

---

### ③ DISCOVERY (La Question Clé)
*Goal: Uncover their exact pain point before pitching features.*

> « Bach nwejjed l-rendez-vous dialna b a7san tari9a, 3endi sou'al wa7ed : had l-logement, wach dayro ktar k **investissement locatif** (bach ydkhel l-madkhoul), wla **résidence secondaire** katskoun fiha w katkriha ghi mra mra ? »

* **Si Investissement Locatif (Levier : Rendement & Occupation)** :
  * Mettre en avant le pricing dynamique, le référencement Airbnb/Booking, et le remplissage des nuits creuses en milieu de semaine.
* **Si Résidence Secondaire (Levier : Sérénité & Préservation du bien)** :
  * Mettre en avant le filtrage rigoureux des voyageurs, le ménage pro avec photos après chaque départ, et la couverture d'assurance AirCover.

---

### ④ CLOSING LE RENDEZ-VOUS
*Goal: Lock a concrete 10-minute visual presentation.*

> « Wach ynasbek **[ghedda / be3d ghedda]** ?  
> F had le rendez-vous ghadi nwerik t-tsawer li 9addit w l-audit l-kamel. **Hadchi fabour, w aslan rah déja mwjjed.** »

---

## 4. Objection & Pivot Playbook

| Situation / Objection | Action CRM | Réponse Recommandée |
|---|---|---|
| **Déjà sous contrat avec une autre conciergerie** (ex: Si Mounir) | `Non Qualifié` + note rappel 3–6 mois | *« C'est noté Si [Nom], aucun souci ! Allah ysseker. N'hésite pas à garder mon contact si jamais tu as un autre bien ou si à l'avenir tu souhaites comparer les performances. Belle journée à toi ! »* |
| **Gère lui-même et refuse l'aide** | `Refusé par le propriétaire` | *« Tout à fait normal ! L'essentiel c'est que ça tourne bien. Si jamais tu te retrouves avec des semaines creuses ou besoin d'un dépannage ménage/clés, tu as mon contact. »* |
| **Aucune réponse après 24h** | Passer à `Pas répondu relance 2` | Déclencher l'appel direct (Stage 2) ou relance texte courte : *« Salam [Nom], as-tu pu jeter un œil au petit vocal ? »* |
| **Intéressé mais demande combien ça coûte** | Maintenir `En Discussion` | *« C'est une commission transparente à la performance uniquement sur les réservations effectives (entre 15% et 20% selon la formule). On n'encaisse rien si le bien ne génère rien. »* |

---

## 5. Le Réseau CRM Status Lifecycle

Pour chaque prospect sur `espace.lereseau-ma.com` :
1. **Création / Import** : Statut initial = **`Nouveau`**. Email laissé vide si inconnu (aucun faux email).
2. **Après envoi du vocal WhatsApp** : Statut = **`Pas répondu relance 1`**.
3. **Après relance ou tentative d'appel téléphonique** : Statut = **`Pas répondu relance 2`**.
4. **Dès que le prospect répond** : Statut = **`En Discussion`**.
5. **Rendez-vous validé** : Statut = **`Rendez-vous Planifié`**.
6. **Concurrent identifié / Hors cible** : Statut = **`Non Qualifié`**.

---

## 6. Helper CLI Tooling

Pour générer le prochain lot de 5 prospects qualifiés :

```bash
# Générer le prochain lot de 5 prospects (priorité WhatsApp inbound)
python3 /home/mhawar/Work/bndar-lead-pipeline/scripts/next_prospect_batch.py --size 5

# Voir les statistiques de prospection en cours
python3 /home/mhawar/Work/bndar-lead-pipeline/scripts/next_prospect_batch.py --status

# Marquer un statut après contact
python3 /home/mhawar/Work/bndar-lead-pipeline/scripts/next_prospect_batch.py --mark 12345 "En Discussion" "RDV fixé demain 15h"
```
