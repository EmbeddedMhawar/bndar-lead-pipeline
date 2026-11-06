#!/usr/bin/env python3
"""
prospect_tracker.py - Stateful Conversation & Preparation Engine for Bndar Conciergerie

Tracks:
1. Prospect details, micro-location, and property characteristics.
2. Conversation state machine & event log.
3. "What to Say Next" dynamically generated based on specific prospect replies/events.
4. Preparation checklist (Audit, Before/After photos, Pricing benchmark) before meetings.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"
STATE_FILE = DATA_DIR / "prospection_state.json"
ALL_ADS_FILE = Path("/home/mhawar/.gemini/antigravity/brain/f4e23eb6-ba8e-42dd-a929-0c7cba2369ee/scratch/all_unique_ads.json")

def load_data():
    if not STATE_FILE.exists():
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading state: {e}")
        return {}

def save_data(data):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def clean_phone(phone_str):
    if not phone_str:
        return ""
    digits = "".join(c for c in phone_str if c.isdigit())
    if digits.startswith("0") and len(digits) == 10:
        return "212" + digits[1:]
    return digits

def generate_next_script(prospect, event, event_note=""):
    nom = prospect.get("nom", "Moul Dar")
    first_name = nom.split()[0].replace("[P1-1]", "").replace("[P1-2]", "").replace("[P1-4]", "").strip().title()
    salutation = f"Lalla {first_name}" if first_name.lower() in ["karima", "hajar", "sonia", "fatima", "imane", "ouafaa", "meryem", "sara"] else f"Si {first_name}"
    quartier = prospect.get("quartier", "Casablanca")
    bien = prospect.get("type_bien", "l'appartement")
    adj = "zwin" if "studio" in bien.lower() or "loft" in bien.lower() else "zwina"
    pronoun = "fih" if "studio" in bien.lower() or "loft" in bien.lower() else "fiha"

    current_relance = prospect.get("relance_count", 0)

    # 1. Event: CHKOUN NTOUMA / C'EST QUOI ?
    if event == "asked_identity":
        return (
            f"« C'est tout à fait normal ! M3ak Abderrahmane, 3endi conciergerie hna f Casablanca smitha Bndar.\\n\\n"
            f"En fait, la raison dial l-message diali : cheft {bien} dialek f {quartier} — tbarkellah {adj} bzaf w fih potentiel kbir.\\n"
            f"Hna kan-optimiziw l-madkhoul dial les propriétaires w kan-gériw koulchi men A tal Z (clients, ménage, réservations) bla ma tebqa mberzet rask.\\n\\n"
            f"Dakchi 3lach sbe9t w wejjedt lik un audit fih l-khotowat li t9ed dir bach t-tele3 l-madkhoul dialek b 30% tal 40% w t-3emmer les nuits creuses.\\n"
            f"Wach momkin chi appel visio wla appel khfif dial 10 d9ayeq ghedda wla be3d ghedda, bach n-partager m3ak had l'audit w tchoufo b 3aynik ? »"
        )

    # 2. Event: SEFTO LIA HNA F WHATSAPP (Pushback diplomatic)
    elif event == "asked_whatsapp_send":
        return (
            f"« Mrehba {salutation} ! L'audit fih des calculs de rentabilité personnalisés 3la {bien} dialek m3a des comparaisons dial les prix par nuit f {quartier}, w fiha des photos li khssni nwerihom lik avec explication.\\n\\n"
            f"Ila sefto lik f fichier PDF ghadi ykoun nachef w s3ib y-ban lik l-impact dialo. Ghi 10 d9ayeq f un appel téléphonique wla visio kat-kfi bach nwerik les 3 points essentiels w t-stafed menno 100%.\\n\\n"
            f"Wach ynasbek chi appel khfif ghedda f la matinée wla f l'après-midi ? »"
        )

    # 3. Event: CH7AL KATAXHDO ? (Pricing question)
    elif event == "asked_price":
        return (
            f"« Question légitime ! F Bndar kan-khedmo b le modèle 100% à la performance : ma kan-akhdo 7ta derhem fixe f l'avancement.\\n\\n"
            f"Kan-akhdo ghir une commission (pourcentage) 3la les réservations li kaydkhelhoum l'appartement f l-jib. Ya3ni : ma kanreb7o 7ta katreba7 nta, w ila dar ma khedmatch ma kat-khelles walou.\\n\\n"
            f"Wach mnasbak 10 d9ayeq nwerik l'audit complet w n-fessro les détails ? »"
        )

    # 4. Event: AGREED TO RDV
    elif event == "agreed_rdv":
        return (
            f"« Parfait {salutation} ! C'est noté avec grand plaisir. Je prépare l'audit et les photos optimisées pour notre échange.\\n"
            f"On se cale à [Heure confirmée]. À très vite ! »"
        )

    # 5. Event: COMPETITOR (Taken by another conciergerie)
    elif event == "competitor":
        return (
            f"« C'est noté {salutation}, aucun souci ! Allah ysseker lik m3ahom.\\n"
            f"N'hésite pas à garder mon contact WhatsApp : si jamais tu as un autre bien ou si à l'avenir tu souhaites comparer le taux d'occupation et la rentabilité, je serai ravi d'échanger avec toi. Belle continuation ! »"
        )

    # 6. Event: NO REPLY (Relance calculation)
    elif event == "no_reply":
        next_r = current_relance + 1

        if prospect.get("initial_approach") == "NAME_TOSS" and next_r == 1:
            # Special bridge for Karima (Name toss -> Reveal audit)
            return (
                f"« Salam {salutation},\\n"
                f"Ghi bach n-kemmel lik l-fikra dial le vocal li seft lik : cheft l'annonce dial {bien} dialek f {quartier} — tbarkellah {adj} bzaf w {pronoun} potentiel kbir.\\n"
                f"Dakchi 3lach sbe9t w wejjedt lik un audit fih l-khotowat w les photos améliorées bach t-tele3 l-madkhoul dialek b 30% tal 40% w t-3emmri les nuits creuses f west la semaine.\\n"
                f"Hadchi kamel fabour w déja mwjjed 3endi. Wach momkin chi appel khfif dial 10 d9ayeq [ghedda wla be3d ghedda], bach nwerik hadchi li wejjedt lik ? »"
            )
        elif next_r == 1:
            # Standard Relance 1 (J+2)
            return (
                f"« Salam {salutation},\\n"
                f"Kan-dhen rak machghoul(a). Ghi bghit n-chouf wach wselk le message l-fowqani ?\\n"
                f"T-tsawer li 9addit lik w l-audit rahom déja mwjjdin 3endi.\\n"
                f"Wach momkin chi appel khfif dial 10 d9ayeq [ghedda wla be3d ghedda] bach nwerik had l-khedma ? »"
            )
        elif next_r == 2:
            # Relance 2 (J+7) - Investissement & Nuits vides
            return (
                f"« Salam {salutation},\\n"
                f"Sou'al sarie3 3la {bien} dialek f {quartier} : wach dayro k investissement locatif bach ydkhel l-madkhoul ?\\n"
                f"7it f Avito, kay-di3ou bzaf dial les nuits f west la semaine. Alors que f Airbnb w Booking, m3a des prix optimisés w tsawer pro, dar katkoun dima 3amra b clientèle nqiya li katkhelles mzyan, w t9ed t-tele3 l-madkhoul b 30% tal 40%.\\n"
                f"Hadchi li bghit nwerik f l-audit. Wach mnasbak 10 d9ayeq ghedda n-werik l-arqam ? »"
            )
        elif next_r == 3:
            # Relance 3 (J+14) - Risque Avito vs AirCover
            return (
                f"« Salam {salutation},\\n"
                f"Bzaf dial les propriétaires li kay-kriw f Avito kay-koun 3ndhom khetar kbir : f Avito makayn la contrat, la assurance ila wqe3 chi mochkil.\\n"
                f"Hna f Bndar kan-khdmo b l'assurance AirCover (Airbnb) w Booking, kan-diro filtrage s7i7 dial les profils, w le ménage kay-koun met9oun m3a tsawer mor koul kherja.\\n"
                f"Ila kanti baghi raha dial l-bal bla sda3 r-ras, wach bghiti n-choufo 10 d9ayeq nwerik kifach kan-tehnniw moul dar men had t-tekhrbiq ? »"
            )
        elif next_r == 4:
            # Relance 4 (J+21) - Délégation totale
            return (
                f"« Salam {salutation},\\n"
                f"Ghi sou'al sarie3 : wach keryan {bien} f {quartier} ma kay-akhodch lik bzaf dial l-weqt f t-tebzi3 (les messages f nssat l-lil, l-ménage, w les remises de clés) ?\\n"
                f"F Bndar, kan-gériw koulchi men A tal Z bach t-tele3 les revenus dialek bla ma tebqa mberzet rask b had t-tekhrbiq kamel b ydik.\\n"
                f"Wach bghiti n-werik f 10 d9ayeq kifach kan-tkelmou b kolchi w nta mrte7 ? »"
            )
        elif next_r == 5:
            # Relance 5 (J+30) - Modèle commission
            return (
                f"« Salam {salutation},\\n"
                f"Ghi bach t3ref kifach kan-khedmo f Bndar : ma kan-akhdo 7ta derhem fixe f l'avancement.\\n"
                f"Kan-khdmo ghir b pourcentage men dakchi li kaydkhel lik f l-jib : Ma kanreb7o 7ta katreba7 nta.\\n"
                f"L'audit w t-tsawer li 9addit lik rahom baqyin mwjjdin 3endi. Wach momkin chi appel khfif n-werihom lik ? »"
            )
        elif next_r >= 6:
            # Relance 6 (J+60) - Breakup
            return (
                f"« Salam {salutation},\\n"
                f"Ma jawbtinich, danc kan-dhen que l'optimisation w la conciergerie dial {bien} f {quartier} mabqatch prioritée 3ndek f had l-weqt, w hadchi 3adi jiddan !\\n"
                f"Ghadi n-sedd le dossier dialek men jihti bach ma nbqach n-berztk, w l'audit ghadi n-khebbih f l'archive.\\n"
                f"Ila tbeddel l-projet dialek f l-moustaqbal, rak 3ndek le contact diali. Allah ysseker lik w bon courage ! »"
            )

    return "Pas de script automatique défini pour cet événement."

def ensure_lead_structure(lead_id, lead_data):
    # Ensure default structure
    if "history" not in lead_data:
        lead_data["history"] = []
    if "prep_checklist" not in lead_data:
        lead_data["prep_checklist"] = {
            "listing_audited": True,
            "photos_enhanced": False,
            "revenue_benchmark_ready": False,
            "3_optimization_points_ready": False
        }
    if "relance_count" not in lead_data:
        status = lead_data.get("status", "")
        if "relance 1" in status.lower():
            lead_data["relance_count"] = 1
        elif "relance 2" in status.lower():
            lead_data["relance_count"] = 2
        elif "relance 3" in status.lower():
            lead_data["relance_count"] = 3
        else:
            lead_data["relance_count"] = 0
    if "type_bien" not in lead_data:
        lead_data["type_bien"] = "le studio" if "studio" in lead_data.get("note", "").lower() else "l'appartement"
    if "quartier" not in lead_data:
        lead_data["quartier"] = "Maarif" if "maarif" in lead_data.get("note", "").lower() else "Casablanca"
    return lead_data

def list_prospects(data):
    print("\n" + "="*85)
    print("📋 BNDAR PROSPECTION PIPELINE — TABLEAU DE BORD D'ACTION")
    print("="*85)
    
    active = []
    closed = []
    
    for lid, p in data.items():
        p = ensure_lead_structure(lid, p)
        if p.get("status") in ["Non Qualifié", "Refusé par le propriétaire", "Contrat Signé"]:
            closed.append((lid, p))
        else:
            active.append((lid, p))

    print(f"\n🟢 EN COURS D'ENGAGEMENT ({len(active)} prospects) :")
    print(f"{'ID':<8} | {'Nom':<20} | {'Téléphone':<14} | {'Statut CRM':<22} | {'Relance #':<10} | {'Action Due'}")
    print("-" * 85)
    for lid, p in active:
        nom = p.get("nom", "Inconnu")[:18]
        phone = p.get("phone", "N/A")[:14]
        stat = p.get("status", "Nouveau")[:20]
        rc = str(p.get("relance_count", 0))
        due = p.get("next_due", "À définir")
        print(f"{lid:<8} | {nom:<20} | {phone:<14} | {stat:<22} | {rc:<10} | {due}")

    print(f"\n🔴 CLOS / HORS CIBLE ({len(closed)} prospects) :")
    for lid, p in closed:
        print(f"- #{lid} {p.get('nom', 'Inconnu')}: [{p.get('status')}] - {p.get('note', '')}")
    print("\n" + "="*85 + "\n")

def show_prospect(data, identifier):
    match = None
    for lid, p in data.items():
        if lid == identifier or str(p.get("crm_id")) == identifier or identifier.lower() in p.get("nom", "").lower():
            match = (lid, p)
            break
            
    if not match:
        print(f"❌ Prospect '{identifier}' introuvable.")
        return

    lid, p = match
    p = ensure_lead_structure(lid, p)
    
    phone = p.get("phone", "")
    phone_clean = clean_phone(phone)
    wa_url = f"https://wa.me/{phone_clean}" if phone_clean else "N/A"
    
    print("\n" + "="*70)
    print(f"👤 FICHE PROSPECT : {p.get('nom')} (#{lid})")
    print("="*70)
    print(f"• CRM Lead ID    : #{p.get('crm_id', lid)}")
    print(f"• Téléphone      : {phone} (Lien: {wa_url})")
    print(f"• Localisation   : {p.get('quartier')}")
    print(f"• Type de bien   : {p.get('type_bien')}")
    print(f"• Statut CRM     : {p.get('status')}")
    print(f"• Relances faites: {p.get('relance_count', 0)}")
    print(f"• Prochaine date : {p.get('next_due', 'Aujourd hui')}")
    
    print("\n📦 CHECKLIST DE PRÉPARATION (À avoir sous les yeux pendant l'appel) :")
    chk = p.get("prep_checklist", {})
    for item, done in chk.items():
        mark = "✅" if done else "⬜"
        item_label = {
            "listing_audited": "Annonce analysée & points faibles identifiés",
            "photos_enhanced": "3-5 photos améliorées (lumière/cadrage) prêtes à montrer",
            "revenue_benchmark_ready": "Estimation du revenu mensuel (+30-40%) calculée",
            "3_optimization_points_ready": "3 recommandations concrètes prêtes à dérouler"
        }.get(item, item)
        print(f"  {mark} {item_label}")

    print("\n📜 HISTORIQUE DES INTERACTIONS :")
    hist = p.get("history", [])
    if not hist:
        print(f"  (Note initiale: {p.get('note', 'Aucune')})")
    for h in hist:
        print(f"  - [{h.get('timestamp')}] {h.get('action')}: {h.get('note', '')}")

    print("\n💬 CE QU'IL FAUT DIRE / ENVOYER MAINTENANT :")
    next_script = p.get("pending_script")
    if not next_script:
        # Determine based on status
        if p.get("status") == "Nouveau":
            next_script = generate_next_script(p, "no_reply")
        else:
            next_script = generate_next_script(p, "no_reply")
    print(next_script.replace('\\n', '\n'))
    print("\n" + "="*70 + "\n")

def record_event(data, identifier, event, note=""):
    match = None
    for lid, p in data.items():
        if lid == identifier or str(p.get("crm_id")) == identifier or identifier.lower() in p.get("nom", "").lower():
            match = (lid, p)
            break
            
    if not match:
        print(f"❌ Prospect '{identifier}' introuvable.")
        return

    lid, p = match
    p = ensure_lead_structure(lid, p)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Process event
    if event == "no_reply":
        p["relance_count"] = p.get("relance_count", 0) + 1
        rc = p["relance_count"]
        p["status"] = f"Pas répondu relance {rc}"
        # Set next due date
        delays = {1: 2, 2: 7, 3: 14, 4: 21, 5: 30, 6: 60}
        days_to_add = delays.get(rc, 7)
        next_date = (datetime.now() + timedelta(days=days_to_add)).strftime("%Y-%m-%d")
        p["next_due"] = next_date
        action_name = f"Relance #{rc} envoyée (Sans réponse)"
        p["pending_script"] = generate_next_script(p, "no_reply")

    elif event == "asked_identity":
        p["status"] = "En Discussion"
        action_name = "Le prospect demande l'identité / de quoi il s'agit"
        p["pending_script"] = generate_next_script(p, "asked_identity")

    elif event == "asked_whatsapp_send":
        p["status"] = "En Discussion"
        action_name = "Le prospect demande d'envoyer l'audit sur WhatsApp"
        p["pending_script"] = generate_next_script(p, "asked_whatsapp_send")

    elif event == "asked_price":
        p["status"] = "En Discussion"
        action_name = "Le prospect demande les tarifs / commission"
        p["pending_script"] = generate_next_script(p, "asked_price")

    elif event == "agreed_rdv":
        p["status"] = "Rendez-vous Planifié"
        action_name = "Rendez-vous téléphonique/visio accepté !"
        p["pending_script"] = generate_next_script(p, "agreed_rdv")

    elif event == "competitor":
        p["status"] = "Non Qualifié"
        p["note"] = f"Déjà avec un concurrent. {note}"
        action_name = "Prospect sous contrat conciergerie concurrente"
        p["pending_script"] = generate_next_script(p, "competitor")

    else:
        action_name = event

    p["history"].append({
        "timestamp": now_str,
        "action": action_name,
        "note": note
    })

    save_data(data)
    print(f"\n✅ Événement '{event}' enregistré pour {p.get('nom')} (#{lid}) !")
    print(f"📊 Nouveau statut CRM : {p.get('status')}")
    print("\n🎯 CE QUE TU DOIS DIRE / RÉPONDRE MAINTENANT :")
    print(p.get("pending_script", "").replace('\\n', '\n'))
    print("\n")

def update_prep(data, identifier, item_key, status_str):
    match = None
    for lid, p in data.items():
        if lid == identifier or str(p.get("crm_id")) == identifier or identifier.lower() in p.get("nom", "").lower():
            match = (lid, p)
            break
            
    if not match:
        print(f"❌ Prospect '{identifier}' introuvable.")
        return

    lid, p = match
    p = ensure_lead_structure(lid, p)
    is_done = status_str.lower() in ["done", "true", "yes", "1", "ok"]
    p["prep_checklist"][item_key] = is_done
    save_data(data)
    print(f"✅ Checklist mise à jour pour {p.get('nom')} : {item_key} = {is_done}")

def main():
    parser = argparse.ArgumentParser(description="Bndar Stateful Prospection Engine")
    parser.add_argument("--list", action="store_true", help="Lister tous les prospects et leurs états")
    parser.add_argument("--show", type=str, metavar="NAME_OR_ID", help="Afficher la fiche détaillée et le script suivant")
    parser.add_argument("--event", nargs="+", help="Enregistrer une réponse/action (ex: --event karima asked_identity 'veut savoir qui on est')")
    parser.add_argument("--prep", nargs=3, metavar=("NAME_OR_ID", "CHECKLIST_ITEM", "STATUS"), help="Valider un élément de préparation (ex: photos_enhanced done)")

    args = parser.parse_args()
    data = load_data()

    if args.list:
        list_prospects(data)
    elif args.show:
        show_prospect(data, args.show)
    elif args.event:
        identifier = args.event[0]
        event = args.event[1]
        note = " ".join(args.event[2:]) if len(args.event) > 2 else ""
        record_event(data, identifier, event, note)
    elif args.prep:
        identifier, item, stat = args.prep
        update_prep(data, identifier, item, stat)
    else:
        list_prospects(data)

if __name__ == "__main__":
    main()
