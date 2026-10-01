
import ollama
import time
import json
import re
import unicodedata


MODEL_NAME = "qwen3:1.7b"


# ============================================================
# OUTILS
# ============================================================

def normalize_text(text: str) -> str:
    """
    Met le texte en minuscule et supprime les accents
    uniquement pour faciliter les recherches.
    """
    text = text.lower()

    text = unicodedata.normalize("NFD", text)
    text = "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )

    return text


def empty_data():

    return {

        "employee": {
            "name": None,
            "email": None
        },

        "problem": {
            "description": None,
            "category": None,
            "subcategory": None
        },

        "equipment": {
            "type": None,
            "brand": None,
            "model": None,
            "asset_id": None,
            "serial_number": None
        },

        "location": {
            "department": None,
            "area": None,
            "specific_location": None,
            "near_department": None,
            "near_office": None,
            "landmark": None,
            "restroom_type": None
        },

        "incident": {
            "reported_at": None,
            "occurred_at": None,
            "duration": None
        }
    }


# ============================================================
# CLASSIFICATION
# ============================================================

CATEGORY_RULES = {

    "HVAC": [
        "climatisation",
        "climatiseur",
        "clim",
        "clima",
        "chauffage",
        "ventilation",
        "air conditioning",
        "air conditioner"
    ],

    "PLUMBING": [
        "fuite d'eau",
        "fuite",
        "robinet",
        "canalisation",
        "tuyau",
        "evier",
        "lavabo",
        "chasse d'eau",
        "chasse",
        "leau",
        "l'eau",
        "l'ingette",
        "lingette",
        "savon",
        "wc bouche",
        "toilette bouchee",
        "toilette bouche",
        "toillette bouchee",
        "toillete bouche",
        "toilette bouche",
        "pression d'eau"
    ],

    "ELECTRICAL": [
        "electricite",
        "circuit",
        "cable",
        "prise electrique",
        "prise",
        "courant",
        "disjoncteur",
        "cable electrique",
        "ampoule",
        "lumiere",
        "eclairage",
        "lampe"
    ],

    "IT_EQUIPMENT": [
        "ordinateur",
        "pc",
        "imprimante",
        "printer",
        "ecran",
        "moniteur",
        "clavier",
        "souris",
        "scanner",
        "serveur"
    ],

    "FURNITURE": [
        "chaise",
        "table",
        "armoire",
        "fauteuil",
        "meuble",
        "etagere",
        "canape",
        "desk",
        "cabinet"
    ],

    "CLEANING": [
        "nettoyage",
        "nettoyer",
        "sale",
        "salete",
        "poubelle",
        "dechet",
        "ordure",
        "menage",
        "nettoyage insuffisant"
    ],

    "LANDSCAPING": [
        "pelouse",
        "herbe",
        "plante",
        "plantes",
        "espace vert",
        "arrosage",
        "irrigation"
    ],

    "PARKING": [
        "stationnement",
        "place de parking",
        "barriere de parking"
    ],

    "SECURITY": [
        "badge",
        "acces",
        "pointage",
        "securite",
        "camera",
        "intrusion",
        "alarme de securite",
        "controle d'acces"
    ],

    "CIVIL_WORKS": [
        "mur",
        "plafond",
        "sol",
        "fenetre",
        "fissure",
        "infiltration",
        "porte cassee",
        "porte endommagee",
        "fenetre cassee",
        "ma chaise est casee",
        "chaise casse"
    ],

    "FIRE_SAFETY": [
        "alarme incendie",
        "extincteur",
        "detecteur de fumee",
        "fumee",
        "incendie",
        "systeme incendie"
    ]
}


def classify_category(message: str):
    """
    Classification déterministe pour les cas évidents.
    """

    text = normalize_text(message)

    scores = {}

    for category, keywords in CATEGORY_RULES.items():

        score = 0

        for keyword in keywords:

            keyword_normalized = normalize_text(keyword)

            if keyword_normalized in text:

                # Les expressions de plusieurs mots
                # sont considérées comme plus fortes.
                if len(keyword_normalized.split()) > 1:
                    score += 2
                else:
                    score += 1

        if score > 0:
            scores[category] = score

    if not scores:
        return None

    # catégorie ayant le meilleur score
    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]

    # Vérification d'une éventuelle égalité
    winners = [
        category
        for category, score in scores.items()
        if score == best_score
    ]

    if len(winners) > 1:
        return None

    return best_category

def is_generic_complaint(message: str) -> bool:
    """
    Détecte une réclamation générale qui indique seulement
    qu'il existe un problème, sans décrire le problème réel.
    """

    text = normalize_text(message).strip()

    # Correction de quelques fautes fréquentes
    text = text.replace("probelem", "probleme")
    text = text.replace("problme", "probleme")

    generic_phrases = [
        "j'ai un probleme",
        "jai un probleme",
        "j'ai un souci",
        "jai un souci",
        "un probleme",
        "un souci",
        "il y a un probleme",
        "il ya un probleme",
        "il y a un problem",
        "il ya un problem",
    ]

    locations = [
        "dans mon bureau",
        "dans le bureau",
        "dans un bureau",
        "au bureau",
        "dans les toilettes",
        "dans la toilette",
        "aux toilettes",
        "aux wc",
        "dans les wc",
        "dans le parking",
        "au parking",
        "dans le jardin",
        "dans l'espace vert",
        "dans le couloir",
        "dans le hall",
        "dans la cafeteria",
        "dans la cafétéria"
    ]

    for phrase in generic_phrases:

        if text == phrase:
            return True

        for location in locations:

            if text == f"{phrase} {location}":
                return True

    return False

# ============================================================
# SOUS-CATEGORIE
# ============================================================

def detect_subcategory(message: str, category: str):

    text = normalize_text(message)

    if category == "HVAC":

        if any(word in text for word in [
            "climatisation",
            "climatiseur",
            "clim",
            "air conditioning",
            "air conditioner"
        ]):
            return "AC_FAILURE"

        if "chauffage" in text:
            return "HEATING_FAILURE"

        if "ventilation" in text:
            return "VENTILATION_FAILURE"


    elif category == "PLUMBING":

        if any(word in text for word in [
            "fuite",
            "fuite d'eau",
            "infiltration d'eau"
        ]):
            return "WATER_LEAK"

        if any(word in text for word in [
            "toilette",
            "toilettes",
            "wc",
            "chasse d'eau"
        ]):
            return "TOILET"

        if "robinet" in text:
            return "FAUCET"


    elif category == "ELECTRICAL":

        if any(word in text for word in [
            "lumiere",
            "eclairage",
            "ampoule",
            "lampe"
        ]):
            return "LIGHTING_FAILURE"

        if "prise" in text:
            return "OUTLET_FAILURE"

        if "disjoncteur" in text:
            return "CIRCUIT_BREAKER"


    elif category == "IT_EQUIPMENT":

        if any(word in text for word in [
            "imprimante",
            "printer"
        ]):
            return "PRINTER_FAILURE"

        if any(word in text for word in [
            "ordinateur",
            "pc"
        ]):
            return "COMPUTER_FAILURE"

        if any(word in text for word in [
            "ecran",
            "moniteur"
        ]):
            return "MONITOR_FAILURE"


    elif category == "FURNITURE":

        if "chaise" in text:
            return "BROKEN_CHAIR"

        if any(word in text for word in [
            "table",
            "bureau casse",
            "bureau endommage"
        ]):
            return "BROKEN_DESK"


    return None



# ============================================================
# EMAIL EMPLOYE
# ============================================================

def extract_employee_email(message: str):

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    match = re.search(
        pattern,
        message
    )

    if match:
        return match.group(0).strip()

    return None


def extract_area_answer(message: str):
    text = normalize_text(message).strip()

    if any(word in text for word in [
        "toilette",
        "toilettes",
        "wc",
        "restroom",
        "bathroom"
    ]):
        return "toilettes"

    if any(word in text for word in [
        "jardin",
        "pelouse",
        "espace vert",
        "espace verts"
    ]):
        return "espace vert"

    if "parking" in text:
        return "parking"

    if any(word in text for word in [
        "couloir",
        "corridor"
    ]):
        return "couloir"

    if "hall" in text or "reception" in text:
        return "hall"

    if any(word in text for word in [
        "cafeteria",
        "cantine"
    ]):
        return "cafétéria"

    if any(word in text for word in [
        "salle de reunion",
        "salle reunion",
        "meeting room"
    ]):
        return "salle de réunion"

    if text in [
        "bureau",
        "mon bureau"
    ]:
        return "bureau"

    return None

def extract_near_office(message: str):
    text = normalize_text(message)

    patterns = [
        r"pres du bureau\s+(.+?)(?:[.,!?]|$)",
        r"pres de bureau\s+(.+?)(?:[.,!?]|$)",
        r"a cote du bureau\s+(.+?)(?:[.,!?]|$)",
        r"a cote de bureau\s+(.+?)(?:[.,!?]|$)",
        r"proche du bureau\s+(.+?)(?:[.,!?]|$)",
        r"proche de bureau\s+(.+?)(?:[.,!?]|$)",
        r"near the office\s+(.+?)(?:[.,!?]|$)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            value = match.group(1).strip()

            return value.strip(" .,;:")

    return None

def extract_landmark(message: str):
    text = normalize_text(message).strip()

    patterns = [
        r"pres de (.+)",
        r"pres du (.+)",
        r"pres de la (.+)",
        r"a cote de (.+)",
        r"a cote du (.+)",
        r"a cote de la (.+)",
        r"proche de (.+)",
        r"proche du (.+)",
        r"proche de la (.+)",
        r"en face de (.+)",
        r"en face du (.+)",
        r"en face de la (.+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            value = match.group(1).strip()

            return value.strip(" .,;:")

    return None

# ============================================================
# DEPARTEMENT
# ============================================================

def extract_department(message: str):

    text = normalize_text(message)

    patterns = [

        r"\bdepartement\s*[:\-]?\s*([a-zA-ZÀ-ÿ0-9][a-zA-ZÀ-ÿ0-9 &'\-]*)",

        r"\bdepartment\s*[:\-]?\s*([a-zA-ZÀ-ÿ0-9][a-zA-ZÀ-ÿ0-9 &'\-]*)",

        r"\bservice\s*[:\-]?\s*([a-zA-ZÀ-ÿ0-9][a-zA-ZÀ-ÿ0-9 &'\-]*)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            message,
            re.IGNORECASE
        )

        if match:

            value = match.group(1).strip()

            # Nettoyage de certaines fins de phrase
            value = re.split(
                r"\s+(?:est|se trouve|est situe|est situé|dans|au|a|à)\b",
                value,
                flags=re.IGNORECASE
            )[0]

            return value.strip(" .,;:")

    return None

# ============================================================
# TYPE DE TOILETTES
# ============================================================

def extract_restroom_type(message: str):

    text = normalize_text(message)

    # FEMMES
    if any(pattern in text for pattern in [
        "toilettes des femmes",
        "toilettes femme",
        "wc femmes",
        "wc femme",
        "toilette femme",
        "toilettes feminine",
        "women restroom",
        "womens restroom",
        "women's restroom"
    ]):

        return "FEMMES"

    # HOMMES
    if any(pattern in text for pattern in [
        "toilettes des hommes",
        "toilettes homme",
        "wc hommes",
        "wc homme",
        "toilette homme",
        "toilettes masculin",
        "men restroom",
        "mens restroom",
        "men's restroom"
    ]):

        return "HOMMES"

    return None

# ============================================================
# PRES D'UN DEPARTEMENT
# ============================================================

def extract_near_department(message: str):

    patterns = [

        r"pres du departement\s+(.+?)(?:[.,!?]|$)",

        r"pres de departement\s+(.+?)(?:[.,!?]|$)",

        r"a cote du departement\s+(.+?)(?:[.,!?]|$)",

        r"a cote de departement\s+(.+?)(?:[.,!?]|$)",

        r"proche du departement\s+(.+?)(?:[.,!?]|$)",

        r"proche de departement\s+(.+?)(?:[.,!?]|$)",

        r"near the department\s+(.+?)(?:[.,!?]|$)"
    ]

    normalized_message = normalize_text(message)

    for pattern in patterns:

        match = re.search(
            pattern,
            normalized_message,
            re.IGNORECASE
        )

        if match:

            value = match.group(1).strip()

            return value.strip(" .,;:")

    return None

# ============================================================
# LOCALISATION
# ============================================================

def extract_location(message: str):

    text = normalize_text(message)

    result = {
        "department": extract_department(message),
        "area": None,
        "specific_location": None,
        "near_department": extract_near_department(message),
        "near_office": None,
        "landmark": None,
        "restroom_type": extract_restroom_type(message)
    }

    # --------------------------------------------------------
    # TOILETTES FEMMES
    # --------------------------------------------------------

    if result["restroom_type"] == "FEMMES":

        result["area"] = "toilettes"

        result["specific_location"] = (
            "toilettes des femmes"
        )

        return result

    # --------------------------------------------------------
    # TOILETTES HOMMES
    # --------------------------------------------------------

    if result["restroom_type"] == "HOMMES":

        result["area"] = "toilettes"

        result["specific_location"] = (
            "toilettes des hommes"
        )

        return result

    # --------------------------------------------------------
    # TOILETTES GENERIQUES
    # --------------------------------------------------------

    if any(pattern in text for pattern in [
        "toilettes",
        "toilette",
        "wc",
        "restroom",
        "bathroom"
    ]):

        result["area"] = "toilettes"

        result["specific_location"] = "toilettes"

        return result

    # --------------------------------------------------------
    # SALLE DE REUNION
    # --------------------------------------------------------

    if any(pattern in text for pattern in [
        "salle de reunion",
        "salle reunion",
        "meeting room"
    ]):

        result["area"] = "salle de réunion"

        result["specific_location"] = (
            "salle de réunion"
        )

        return result

    # --------------------------------------------------------
    # CAFETERIA
    # --------------------------------------------------------

    if any(pattern in text for pattern in [
        "cafeteria",
        "cantine"
    ]):

        result["area"] = "cafétéria"

        result["specific_location"] = "cafétéria"

        return result

    # --------------------------------------------------------
    # PARKING
    # --------------------------------------------------------

    if "parking" in text:

        result["area"] = "parking"

        result["specific_location"] = "parking"

        return result

    # --------------------------------------------------------
    # ESPACE VERT
    # --------------------------------------------------------

    if any(pattern in text for pattern in [
        "espace vert",
        "espace verts",
        "green space",
        "jardin",
        "pelouse"
    ]):

        result["area"] = "espace vert"

        result["specific_location"] = "espace vert"

        return result

    # --------------------------------------------------------
    # COULOIR
    # --------------------------------------------------------

    if any(pattern in text for pattern in [
        "couloir",
        "corridor"
    ]):

        result["area"] = "couloir"

        result["specific_location"] = "couloir"

        return result

    # --------------------------------------------------------
    # HALL
    # --------------------------------------------------------

    if any(pattern in text for pattern in [
        "hall",
        "reception",
        "réception"
    ]):

        result["area"] = "hall"

        result["specific_location"] = "hall"

        return result

    # --------------------------------------------------------
    # BUREAU GENERIQUE
    # --------------------------------------------------------

    if re.search(
        r"\b(?:mon|le|un)\s+bureau\b",
        text
    ):

            result["area"] = "bureau"

            result["specific_location"] = "bureau"
            
    return result        

# ============================================================
# EQUIPEMENT
# ============================================================

def extract_equipment(message: str):

    text = normalize_text(message)

    equipment_type = None

    if any(word in text for word in [
        "ordinateur",
        "pc"
    ]):
        equipment_type = "computer"

    elif any(word in text for word in [
        "imprimante",
        "printer"
    ]):
        equipment_type = "printer"

    elif any(word in text for word in [
        "ecran",
        "moniteur"
    ]):
        equipment_type = "monitor"

    elif "clavier" in text:
        equipment_type = "keyboard"

    elif "souris" in text:
        equipment_type = "mouse"

    elif "scanner" in text:
        equipment_type = "scanner"

    elif "chaise" in text:
        equipment_type = "chair"

    elif "table" in text:
        equipment_type = "table"

    elif "armoire" in text:
        equipment_type = "cabinet"

    elif "fauteuil" in text:
        equipment_type = "chair"

    elif "meuble" in text:
        equipment_type = "furniture"

    return {
        "type": equipment_type,
        "brand": None,
        "model": None,
        "asset_id": None,
        "serial_number": None
    }


# ============================================================
# EXTRACTION DETERMINISTE
# ============================================================

def extract_rules(message: str, include_description=False):

    data = empty_data()

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    if include_description and not is_generic_complaint(message):
        data["problem"]["description"] = message.strip()

    # --------------------------------------------------------
    # EMPLOYEE EMAIL
    # --------------------------------------------------------

    employee_email = extract_employee_email(message)

    if employee_email:
        data["employee"]["email"] = employee_email
        
    # --------------------------------------------------------
    # CATEGORIE
    # --------------------------------------------------------

    category = classify_category(message)

    if category:
        data["problem"]["category"] = category

        subcategory = detect_subcategory(
            message,
            category
        )

        if subcategory:
            data["problem"]["subcategory"] = subcategory

    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    location = extract_location(message)

    if isinstance(location, dict):
        for key, value in location.items():

            if value is not None:
                data["location"][key] = value

    # --------------------------------------------------------
    # EQUIPEMENT
    # --------------------------------------------------------

    equipment = extract_equipment(message)

    if equipment["type"] is not None:
        data["equipment"]["type"] = equipment["type"]

    return data


# ============================================================
# VERIFICATION D'UN CHAMP
# ============================================================

def get_value(data: dict, path: str):

    current = data

    for key in path.split("."):

        if not isinstance(current, dict):
            return None

        current = current.get(key)

        if current is None:
            return None

    return current


def has_expected_field(data: dict, expected_field: str):

    value = get_value(
        data,
        expected_field
    )

    return value is not None and value != ""


# ============================================================
# PARSING REPONSE LLM
# ============================================================

def parse_llm_json(response: str):

    try:
        return json.loads(response)

    except json.JSONDecodeError:

        cleaned = response.replace(
            "```json",
            ""
        )

        cleaned = cleaned.replace(
            "```",
            ""
        )

        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)

        except json.JSONDecodeError:

            print("[LLM] Réponse JSON invalide.")

            return empty_data()


# ============================================================
# MERGE SECURISE
# ============================================================

def merge_protected(rule_data: dict, llm_data: dict):

    """
    Les informations extraites par les règles Python
    sont prioritaires.

    Le LLM ne peut donc pas les remplacer.
    """

    result = empty_data()

    # --------------------------------------------------------
    # 1. données LLM
    # --------------------------------------------------------

    def merge(target, source):

        for key, value in source.items():

            if key not in target:
                continue

            if isinstance(value, dict):

                if isinstance(target.get(key), dict):
                    merge(
                        target[key],
                        value
                    )

            else:

                if value is not None and value != "":
                    target[key] = value

    merge(
        result,
        llm_data
    )

    # --------------------------------------------------------
    # 2. données déterministes prioritaires
    # --------------------------------------------------------

    def overwrite(target, source):

        for key, value in source.items():

            if isinstance(value, dict):

                if key not in target:
                    target[key] = {}

                overwrite(
                    target[key],
                    value
                )

            else:

                if value is not None and value != "":
                    target[key] = value

    overwrite(
        result,
        rule_data
    )

    return result


# ============================================================
# ANALYSE DE LA RECLAMATION
# ============================================================

def analyze_complaint(message: str):

    # --------------------------------------------------------
    # 1. Extraction déterministe
    # --------------------------------------------------------

    rule_data = extract_rules(
        message,
        include_description=True
    )

    print("\n[EXTRACTOR] Données détectées :")
    print(
        json.dumps(
            rule_data,
            indent=4,
            ensure_ascii=False
        )
    )

    # --------------------------------------------------------
    # 2. SI LA CATEGORIE EST CLAIRE
    #
    # On ne demande PAS au LLM de refaire le travail.
    # --------------------------------------------------------

    # --------------------------------------------------------
    # 2. CATEGORIE DETECTEE
    # --------------------------------------------------------

    if rule_data["problem"]["category"] is not None:

        print(
            "[EXTRACTOR] Catégorie détectée automatiquement."
        )

        return json.dumps(
            rule_data,
            ensure_ascii=False
        )


    # --------------------------------------------------------
    # 3. RECLAMATION GENERIQUE
    # --------------------------------------------------------

    if is_generic_complaint(message):

        print(
            "[EXTRACTOR] Réclamation générique : "
            "aucune catégorie inventée."
        )

        return json.dumps(
            rule_data,
            ensure_ascii=False
        )


    # --------------------------------------------------------
    # 4. CATEGORIE AMBIGUE MAIS DESCRIPTION PLUS PRECISE
    # --------------------------------------------------------

    print(
        "[EXTRACTOR] Catégorie ambiguë -> appel LLM"
    )

    start_time = time.perf_counter()

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": """
You are an AI assistant specialized in Facility Management.

Extract structured information from the employee complaint.

Return ONLY valid JSON.

Allowed categories:

HVAC
PLUMBING
ELECTRICAL
IT_EQUIPMENT
FURNITURE
CLEANING
LANDSCAPING
PARKING
SECURITY
CIVIL_WORKS
FIRE_SAFETY
OTHER

Rules:

- Never invent information.
- Use null when information is missing.
- "my office" / "mon bureau" means specific_location = "bureau".
- "women's restroom" means area = "restroom" and specific_location = "women's restroom".
- "men's restroom" means area = "restroom" and specific_location = "men's restroom".
- Do not determine priority.
- Return JSON only.
- "près du département RH" -> near_department = "RH"
- "près du bureau 204" -> near_office = "204"
- "près de la cafétéria" -> landmark = "cafétéria"
- "toilettes femmes" -> restroom_type = "FEMMES"
- "toilettes hommes" -> restroom_type = "HOMMES"
- Department names are dynamic and must never be restricted to a predefined list.
- If the employee explicitly mentions a department or service where the problem is located, extract it into location.department.
- "département Finance" -> department = "Finance"
- "service RH" -> department = "RH"
- "département IT" -> department = "IT"
- Do not confuse a nearby department with the department where the problem is located.
- "près du département RH" -> near_department = "RH", not department = "RH".
Structure:

{
    "employee": {
        "name": null,
        "email": null
    },
    "problem": {
        "description": null,
        "category": null,
        "subcategory": null
    },
    "equipment": {
        "type": null,
        "brand": null,
        "model": null,
        "asset_id": null,
        "serial_number": null
    },
    "location": {
        "department": null,
        "area": null,
        "specific_location": null,
        "near_department": null,
        "near_office": null,
        "landmark": null,
        "restroom_type": null
    },
    "incident": {
        "reported_at": null,
        "occurred_at": null,
        "duration": null
    }
}
"""
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )

    elapsed_time = time.perf_counter() - start_time

    print(
        f"[LLM] analyze_complaint() : "
        f"{elapsed_time:.2f} secondes"
    )

    llm_data = parse_llm_json(
        response.message.content
    )

    # --------------------------------------------------------
    # 4. Les données Python restent prioritaires
    # --------------------------------------------------------

    final_data = merge_protected(
        rule_data,
        llm_data
    )

    return json.dumps(
        final_data,
        ensure_ascii=False
    )


# ============================================================
# EXTRACTION DE LA REPONSE UTILISATEUR
# ============================================================

def extract_answer(
    message: str,
    expected_field: str,
    current_complaint: dict
):

    # --------------------------------------------------------
    # 1. Extraction déterministe
    # --------------------------------------------------------

    rule_data = empty_data()

    # ========================================================
    # EXTRACTION DIRECTE SELON LE CHAMP ATTENDU
    # ========================================================

    if expected_field == "employee.email":

        value = extract_employee_email(message)

        if value:
            rule_data["employee"]["email"] = value

    elif expected_field == "location.area":

        value = extract_area_answer(message)

        if value:
            rule_data["location"]["area"] = value

    elif expected_field == "location.near_department":

        value = extract_near_department(message)

        if value:
            rule_data["location"]["near_department"] = value

        else:
            value = message.strip()

            if value:
                rule_data["location"]["near_department"] = (
                    value.strip(" .,;:")
                )

    elif expected_field == "location.near_office":

        value = extract_near_office(message)

        if value:
            rule_data["location"]["near_office"] = value

        else:
            value = message.strip()

            if value:
                rule_data["location"]["near_office"] = (
                    value.strip(" .,;:")
                )

    elif expected_field == "location.landmark":

        value = extract_landmark(message)

        if value:
            rule_data["location"]["landmark"] = value

        else:
            value = message.strip()

            if value:
                rule_data["location"]["landmark"] = (
                    value.strip(" .,;:")
                )

    elif expected_field == "location.specific_location":

        value = message.strip()

        if value:
            rule_data["location"]["specific_location"] = value

    elif expected_field == "location.department":

        value = message.strip()

        if value:
            rule_data["location"]["department"] = (
                value.strip(" .,;:")
            )

    elif expected_field == "location.restroom_type":

        text = normalize_text(message)

        if any(word in text for word in [
            "femme",
            "femmes",
            "female",
            "women"
        ]):

            rule_data["location"]["restroom_type"] = "FEMMES"

        elif any(word in text for word in [
            "homme",
            "hommes",
            "male",
            "men"
        ]):

            rule_data["location"]["restroom_type"] = "HOMMES"

    elif expected_field == "equipment.type":

        value = extract_equipment(message)["type"]

        if value:
            rule_data["equipment"]["type"] = value

    elif expected_field == "incident.duration":

        value = message.strip()

        if value:
            rule_data["incident"]["duration"] = value

    elif expected_field == "problem.description":

        value = message.strip()

        if value and not is_generic_complaint(value):
            rule_data["problem"]["description"] = value

    elif expected_field == "problem.category":

        category = classify_category(message)

        if category:

            rule_data["problem"]["category"] = category

            subcategory = detect_subcategory(
                message,
                category
            )

            if subcategory:
                rule_data["problem"]["subcategory"] = subcategory

            # La réponse peut également contenir la description
            if not is_generic_complaint(message):

                rule_data["problem"]["description"] = (
                    message.strip()
                )

    # --------------------------------------------------------
    # Si le champ attendu a été trouvé automatiquement
    # --------------------------------------------------------

    if has_expected_field(
        rule_data,
        expected_field
    ):

        print(
            f"[EXTRACTOR] Champ détecté automatiquement : "
            f"{expected_field}"
        )

        return json.dumps(
            rule_data,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # 2. Sinon, on utilise Qwen comme fallback
    # --------------------------------------------------------

    print(
        f"[EXTRACTOR] Champ '{expected_field}' "
        f"non détecté automatiquement -> appel LLM"
    )

    start_time = time.perf_counter()

    current_json = json.dumps(
        current_complaint,
        ensure_ascii=False
    )

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": f"""
You are an information extraction assistant.

The employee is answering a Facility Management chatbot.

Expected field:

{expected_field}

Current complaint:

{current_json}

Employee answer:

{message}

Your task:

1. Extract the value for the expected field.
2. Never invent information.
3. Never replace an existing value with null.
4. Do not modify unrelated existing information.
5. Return valid JSON only.

Important location rules:

- Never extract employee ID or matricule.
- Never extract building.
- Never extract floor.
- Never extract office number.
- These fields must not be returned.
- "toilettes des femmes" -> area = "toilettes", specific_location = "toilettes des femmes"
- "toilettes des hommes" -> area = "toilettes", specific_location = "toilettes des hommes"
- "près du département RH" -> near_department = "RH"
- "près du bureau 204" -> near_office = "204"
- "près de la cafétéria" -> landmark = "cafétéria"
- "toilettes femmes" -> restroom_type = "FEMMES"
- "toilettes hommes" -> restroom_type = "HOMMES"
- Department names are dynamic. Never use a predefined department list.
- "département Finance" -> department = "Finance"
- "service RH" -> department = "RH"
- "département IT" -> department = "IT"
- "près du département RH" -> near_department = "RH", not department = "RH".

Return this structure:

{{
    "employee": {{
        "name": null,
        "email": null
    }},
    "problem": {{
        "description": null,
        "category": null,
        "subcategory": null
    }},
    "equipment": {{
        "type": null,
        "brand": null,
        "model": null,
        "asset_id": null,
        "serial_number": null
    }},
    "location": {{
        "department": null,
        "area": null,
        "specific_location": null,
        "near_department": null,
        "near_office": null,
        "landmark": null,
        "restroom_type": null
    }},
    "incident": {{
        "reported_at": null,
        "occurred_at": null,
        "duration": null
    }}
}}
"""
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )

    elapsed_time = time.perf_counter() - start_time

    print(
        f"[LLM] extract_answer() : "
        f"{elapsed_time:.2f} secondes"
    )

    llm_data = parse_llm_json(
        response.message.content
    )

    # --------------------------------------------------------
    # 3. Les règles Python restent prioritaires
    # --------------------------------------------------------

    final_data = merge_protected(
        rule_data,
        llm_data
    )

    return json.dumps(
        final_data,
        ensure_ascii=False
    )