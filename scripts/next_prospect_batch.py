#!/usr/bin/env python3
"""
next_prospect_batch.py - Bndar Conciergerie Prospection Batch Generator
Outputs actionable 5-prospect batches with WhatsApp warmup links, tailored Darija scripts,
and CRM tracking integration.
"""

import os
import sys
import json
import argparse
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"
QUALIFIED_FILE = DATA_DIR / "bndar_leads_qualified_85.json"
FULL_FILE = DATA_DIR / "bndar_leads_full_262.json"
STATE_FILE = DATA_DIR / "prospection_state.json"
ALL_ADS_FILE = Path("/home/mhawar/.gemini/antigravity/brain/f4e23eb6-ba8e-42dd-a929-0c7cba2369ee/scratch/all_unique_ads.json")

def load_ads():
    if ALL_ADS_FILE.exists():
        try:
            with open(ALL_ADS_FILE, "r", encoding="utf-8") as f:
                ads = json.load(f)
            return {a.get("href"): a for a in ads if a.get("href")}
        except Exception:
            return {}
    return {}

def load_state():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Initial seed
    default_state = {
        "11599": {"crm_id": "11599", "nom": "Karima", "status": "Pas répondu relance 1", "touchpoint": "whatsapp", "note": "Vocal 11.9s envoyé"},
        "11414": {"crm_id": "11414", "nom": "Jdb Mounir", "status": "Non Qualifié", "touchpoint": "whatsapp", "note": "Pris par une autre conciergerie"}
    }
    save_state(default_state)
    return default_state

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def clean_phone(phone_str):
    if not phone_str:
        return ""
    digits = "".join(c for c in phone_str if c.isdigit())
    if digits.startswith("212"):
        return digits
    if digits.startswith("0"):
        return "212" + digits[1:]
    if len(digits) == 9:
        return "212" + digits
    return digits

def generate_script(lead, ad):
    nom = lead.get("nom_complet", "Moul Dar").strip()
    quartier = lead.get("quartier", "").strip()
    
    # Ground-truth override if specific ad clues found
    desc = ""
    subj = ""
    if ad:
        desc = ad.get("description", "")
        subj = ad.get("subject", "")
    
    # Honor specific micro-locations
    loc_display = quartier
    if "134 square" in desc.lower() or "134 square" in subj.lower():
        loc_display = "Le 134 Square côté Ain Gedid"
    elif "twin center" in desc.lower() or "twin center" in subj.lower():
        loc_display = "Maârif côté Twin Center"
    elif "bourgogne" in quartier.lower() and ("mosquée" in desc.lower() or "corniche" in desc.lower()):
        loc_display = "Bourgogne côté Mosquée Hassan II"
    elif "derb omar" in quartier.lower():
        loc_display = "Derb Omar"
    elif "belvédère" in quartier.lower():
        loc_display = "Belvédère côté Casa-Voyageurs"

    # Clean name of any tags like [P1-1] or suffixes like (Dar Bouazza)
    import re
    cleaned_nom = re.sub(r'\[.*?\]', '', nom)
    cleaned_nom = re.sub(r'\(.*?\)', '', cleaned_nom).strip()
    tokens = [t for t in cleaned_nom.split() if t]
    first_name = tokens[0].title() if tokens else "Moul Dar"
    
    # Check for known female names in any token
    is_female = False
    chosen_name = first_name
    for token in tokens:
        if token.lower() in ["karima", "hajar", "sonia", "fatima", "imane", "ouafaa", "chaimaa", "salma", "nadia", "leila", "meryem", "meryam", "sara", "dounia", "soukaina", "zineb", "asmaa", "khadija"]:
            is_female = True
            chosen_name = token.title()
            break

    salutation = f"Lalla {chosen_name}" if is_female else f"Si {first_name}"

    prop_term = "l'appartement"
    if "studio" in subj.lower() or "studio" in desc.lower():
        prop_term = "le studio"
    elif "villa" in subj.lower() or "villa" in desc.lower():
        prop_term = "la villa"
    elif "loft" in subj.lower() or "loft" in desc.lower():
        prop_term = "le loft"

    adj = "zwina bzaf" if prop_term in ["l'appartement", "la villa"] else "zwin bzaf"
    pronoun = "fiha" if prop_term in ["l'appartement", "la villa"] else "fih"

    # Specific hook
    hook = ""
    if "piscine" in desc.lower() or "vue mer" in desc.lower():
        hook = ", vue mer m3a la piscine saraha"
    elif "neuf" in desc.lower() or "rénové" in desc.lower():
        hook = ", nqi w m-finy mzyan"

    script = (
        f"« Salam {salutation},\\n"
        f"Cheft l'annonce f Avito 3la {prop_term} dialek f {loc_display} — saraha {adj}{hook} {pronoun} potentiel kbir.\\n"
        f"Dakchi 3lach sbe9t w khedmet 3la 9eblek, fabour: 9addit w 7essent lik t-tsawer, w wejjedt lik un audit fih l-khotowat li t9ed dir bach t-tele3 l-madkhoul dialek b 30% tal 40%.\\n"
        f"Wach momkin tkoun disponible l chi appel visio wla chi rencontre / goulsa, bach nwerik hadchi li wejjedt lik ? »"
    )
    return script

def get_next_batch(batch_size=5, channel="whatsapp", source="qualified"):
    state = load_state()
    ads = load_ads()

    candidates = []

    priority_order = {
        "[P1-1]": 1,
        "[P1-2]": 2,
        "[P1-3]": 3,
        "[P1-4]": 4,
        "[P2-5]": 5,
        "[P2-6]": 6,
        "[P2-7]": 7,
        "[P2-8]": 8,
        "[P3-15]": 9,
        "[P4]": 10
    }

    # Load touched phones from state
    touched_phones = set()
    for item in state.values():
        p = clean_phone(item.get("phone", "") or item.get("telephone", ""))
        if p:
            touched_phones.add(p)
    # Also add Karima and Mounir explicitly
    touched_phones.add(clean_phone("06 68 23 76 08"))
    touched_phones.add(clean_phone("06 95 25 00 33"))

    BROKER_BLACKLIST = ["airbnb", "concierge", "conciergerie", "agence", "immobilière", "immobilier", "courtier", "intermédiaire", "suites hotel", "call maroc"]

    if source in ["qualified", "all"]:
        if QUALIFIED_FILE.exists():
            with open(QUALIFIED_FILE, "r", encoding="utf-8") as f:
                leads = json.load(f)

            for lead in leads:
                crm_id = str(lead.get("crm_id"))
                phone = clean_phone(lead.get("telephone", ""))
                if crm_id in state or phone in touched_phones:
                    continue  # Already touched

                url = lead.get("url_annonce", "")
                ad = ads.get(url, {})
                full_text = (ad.get("description", "") + " " + ad.get("subject", "")).lower()

                has_wa_mention = any(w in full_text for w in ["whatsapp", "watssap", "watsap", "wa.me"])
                lead_priority = priority_order.get(lead.get("priorite_code"), 99)

                score = lead_priority
                if has_wa_mention:
                    score -= 10

                candidates.append({
                    "lead": lead,
                    "ad": ad,
                    "score": score,
                    "has_wa": has_wa_mention
                })
                if phone:
                    touched_phones.add(phone)

    if source in ["whatsapp_pool", "all"]:
        # Also include independent owners from all_unique_ads who specifically requested WhatsApp
        if ALL_ADS_FILE.exists():
            with open(ALL_ADS_FILE, "r", encoding="utf-8") as f:
                all_ads_list = json.load(f)

            for a in all_ads_list:
                desc = (a.get("description") or "").lower()
                subj = (a.get("subject") or "").lower()
                full = desc + " " + subj
                raw_phone = (a.get("seller", {}).get("phone", {}) or {}).get("number") or ""
                phone = clean_phone(raw_phone)
                seller_name = (a.get("seller", {}).get("name") or "").lower()
                s_type = a.get("seller", {}).get("type", "")
                href = a.get("href", "")

                if not phone or phone in touched_phones or s_type == "STORE":
                    continue

                if any(b in seller_name or b in subj for b in BROKER_BLACKLIST):
                    continue

                ad_id = str(a.get("listId") or a.get("id"))
                if ad_id in state:
                    continue

                if any(w in full for w in ["whatsapp", "watssap", "watsap"]):
                    loc = a.get("location", "")
                    lead_obj = {
                        "crm_id": ad_id,
                        "nom_complet": a.get("seller", {}).get("name", "Moul Dar"),
                        "telephone": raw_phone,
                        "quartier": loc.replace("Casablanca,", "").strip(),
                        "priorite_code": "[WA-Inbound]",
                        "url_annonce": href
                    }
                    candidates.append({
                        "lead": lead_obj,
                        "ad": a,
                        "score": -20,  # Prioritize direct WhatsApp seekers at the very top
                        "has_wa": True
                    })
                    touched_phones.add(phone)

    candidates.sort(key=lambda x: (x["score"], x["lead"].get("crm_id", "0")))

    batch = candidates[:batch_size]
    return batch

def main():
    parser = argparse.ArgumentParser(description="Bndar Prospection Batch Generator")
    parser.add_argument("--size", type=int, default=5, help="Batch size (default: 5)")
    parser.add_argument("--channel", choices=["whatsapp", "call", "all"], default="whatsapp", help="Prospection channel")
    parser.add_argument("--source", choices=["qualified", "whatsapp_pool", "all"], default="all", help="Lead source pool (default: all)")
    parser.add_argument("--status", action="store_true", help="Display prospection stats")
    parser.add_argument("--mark", nargs=3, metavar=("CRM_ID", "STATUS", "NOTE"), help="Mark lead status (e.g. --mark 12345 'En Discussion' 'Interested in call')")

    args = parser.parse_args()

    state = load_state()

    if args.mark:
        cid, stat, note = args.mark
        state[str(cid)] = {
            "crm_id": str(cid),
            "status": stat,
            "note": note
        }
        save_state(state)
        print(f"✅ Lead #{cid} marked as '{stat}' with note: '{note}'")
        return

    if args.status:
        print("=== BNDAR PROSPECTION PIPELINE STATUS ===")
        print(f"Total leads tracked: {len(state)}")
        for cid, info in state.items():
            print(f"- Lead #{cid} ({info.get('nom', 'Unknown')}): [{info.get('status')}] - {info.get('note', '')}")
        return

    batch = get_next_batch(batch_size=args.size, channel=args.channel, source=args.source)
    if not batch:
        print("🎉 No remaining uncontacted leads in the qualified queue!")
        return

    print(f"\n========================================================")
    print(f"🔥 BNDAR PROSPECTION BATCH : {len(batch)} PROSPECTS (WARMUP WHATSAPP)")
    print(f"========================================================\n")

    for i, item in enumerate(batch, 1):
        lead = item["lead"]
        ad = item["ad"]
        phone_raw = lead.get("telephone", "")
        phone_intl = clean_phone(phone_raw)
        wa_link = f"https://wa.me/{phone_intl}" if phone_intl else "N/A"
        url = lead.get("url_annonce", "N/A")
        quartier = lead.get("quartier", "Casablanca")
        priority = lead.get("priorite_code", "P?")
        crm_id = lead.get("crm_id", "N/A")
        nom = lead.get("nom_complet", "Inconnu")
        wa_tag = "💬 [WhatsApp Demandé]" if item["has_wa"] else "📞 [Direct Owner]"

        script = generate_script(lead, ad)

        print(f"### {i}. {nom} — {quartier} {priority} {wa_tag}")
        print(f"- **CRM ID** : #{crm_id}")
        print(f"- **Téléphone** : `{phone_raw}`")
        print(f"- **WhatsApp Direct** : {wa_link}")
        print(f"- **Lien Annonce** : {url}")
        print(f"- **Script Vocal (Étape ①)** :")
        print(script.replace('\\n', '\n'))
        print("\n" + "-"*56 + "\n")

if __name__ == "__main__":
    main()
