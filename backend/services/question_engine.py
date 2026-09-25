
import unicodedata
from typing import Optional


# ============================================================
# OUTILS
# ============================================================

def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower().strip()

    text = unicodedata.normalize("NFD", text)

    text = "".join(
        char
        for char in text
        if unicodedata.category(char) != "Mn"
    )

    return text


def get_value(data: dict, path: str) -> Optional[object]:
    current = data

    for key in path.split("."):
        if not isinstance(current, dict):
            return None

        current = current.get(key)

        if current is None:
            return None

    return current


def is_filled(value) -> bool:

    if value is None:
        return False

    if isinstance(value, str):
        return value.strip() != ""

    return True


# ============================================================
# DESCRIPTION
# ============================================================

GENERIC_DESCRIPTIONS = [
    "j'ai un probleme",
    "jai un probleme",
    "j'ai un souci",
    "jai un souci",
    "un probleme",
    "un souci",
    "il y a un probleme",
    "il y a un souci",
    "probleme dans mon bureau",
    "souci dans mon bureau",
    "il y a quelque chose qui ne va pas",
    "ca ne marche pas",
    "ça ne marche pas",
    "cela ne marche pas"
]


def is_meaningful_description(value) -> bool:

    if not is_filled(value):
        return False

    text = normalize_text(str(value))

    for generic in GENERIC_DESCRIPTIONS:

        if text == normalize_text(generic):
            return False

    # Une description très courte reste potentiellement trop vague
    words = text.split()

    if len(words) <= 2:
        return False

    return True


# ============================================================
# QUESTIONS
# ============================================================

QUESTIONS = {

    "problem.category":
        "Pouvez-vous préciser quel est le problème rencontré ?",

    "employee.employee_id":
        "Pouvez-vous me communiquer votre Employee ID ?",

    "employee.email":
    "Quelle est votre adresse e-mail ?",

    "problem.description":
        "Pouvez-vous décrire précisément le problème rencontré ?",

    "location.building":
        "Dans quel bâtiment se trouve le problème ?",

    "location.floor":
        "À quel étage se trouve le problème ?",

    "location.office":
        "Quel est le numéro du bureau concerné ?",
        
    "location.department":
        "Dans quel département se trouve le problème ?",    

    "location.area":
        "Dans quelle zone se trouve le problème ?",

    "location.specific_location":
        "Pouvez-vous préciser la localisation exacte du problème ?",

    "location.near_department":
        "Près de quel département se trouve le problème ?",

    "location.near_office":
        "Près de quel bureau se trouve le problème ?",

    "location.landmark":
        "Pouvez-vous me donner un repère proche pour localiser le problème ?",

    "location.restroom_type":
        "S'agit-il des toilettes hommes ou femmes ?",

    "equipment.type":
        "Quel équipement est concerné ?",

    "incident.duration":
        "Depuis combien de temps le problème se produit-il ?"
}


# ============================================================
# TYPE DE LOCALISATION
# ============================================================

def determine_location_type(data: dict) -> str:

    location = data.get("location", {})

    area = normalize_text(
        location.get("area")
        if location.get("area")
        else ""
    )

    office = location.get("office")
    restroom_type = location.get("restroom_type")

    # --------------------------------------------------------
    # BUREAU
    # --------------------------------------------------------

    if is_filled(office):
        return "office"

    if area == "bureau":
        return "office"

    # --------------------------------------------------------
    # TOILETTES
    # --------------------------------------------------------

    if area in [
        "toilettes",
        "toilette",
        "wc",
        "restroom",
        "bathroom"
    ]:
        return "restroom"

    if is_filled(restroom_type):
        return "restroom"

    # --------------------------------------------------------
    # PARKING
    # --------------------------------------------------------

    if area == "parking":
        return "parking"

    # --------------------------------------------------------
    # ESPACE VERT
    # --------------------------------------------------------

    if area in [
        "espace vert",
        "jardin",
        "pelouse"
    ]:
        return "landscaping"

    # --------------------------------------------------------
    # ZONES COMMUNES
    # --------------------------------------------------------

    if area in [
        "couloir",
        "hall",
        "salle de reunion",
        "cafeteria"
    ]:
        return "common_area"

    return "unknown"


# ============================================================
# CHAMPS OBLIGATOIRES PAR CATEGORIE
# ============================================================

BASE_REQUIRED_FIELDS = {

    "HVAC": [
        "employee.employee_id",
        "employee.email",
        "location.building",
        "location.floor",
        "problem.description"
    ],

    "PLUMBING": [
        "employee.employee_id",
        "employee.email",
        "location.building",
        "location.floor",
        "problem.description"
    ],

    "ELECTRICAL": [
        "employee.employee_id",
        "employee.email",
        "location.building",
        "location.floor",
        "problem.description"
    ],

    "IT_EQUIPMENT": [
        "employee.employee_id",
        "employee.email",
        "equipment.type",
        "location.building",
        "location.floor",
        "problem.description"
    ],

    "FURNITURE": [
        "employee.employee_id",
        "employee.email",
        "equipment.type",
        "location.building",
        "location.floor",
        "problem.description"
    ],

    "CLEANING": [
        "employee.employee_id",
        "employee.email",
        "location.building",
        "location.floor",
        "problem.description"
    ],

    "LANDSCAPING": [
        "employee.employee_id",
        "employee.email",
        "problem.description"
    ],

    "PARKING": [
        "employee.employee_id",
        "employee.email",
        "problem.description"
    ],

    "SECURITY": [
        "employee.employee_id",
        "employee.email",
        "location.building",
        "location.floor",
        "problem.description"
    ],

    "CIVIL_WORKS": [
        "employee.employee_id",
        "employee.email",
        "location.building",
        "location.floor",
        "problem.description"
    ],

    "FIRE_SAFETY": [
        "employee.employee_id",
        "employee.email",
        "location.building",
        "location.floor",
        "problem.description"
    ],

    "OTHER": [
        "employee.employee_id",
        "employee.email",
        "location.building",
        "location.floor",
        "problem.description"
    ]
}


# ============================================================
# CATEGORIES POUR LESQUELLES LA DUREE EST IMPORTANTE
# ============================================================

DURATION_CATEGORIES = [
    "HVAC",
    "PLUMBING",
    "ELECTRICAL",
    "IT_EQUIPMENT",
    "FURNITURE",
    "CLEANING",
    "LANDSCAPING",
    "PARKING"
]


# ============================================================
# LOCALISATION PRECISE
# ============================================================

GENERIC_LOCATION_VALUES = [
    "bureau",
    "parking",
    "espace vert",
    "jardin",
    "pelouse",
    "toilettes",
    "toilette",
    "wc",
    "hall",
    "couloir",
    "salle de reunion",
    "cafeteria"
]


def is_precise_location(value) -> bool:

    if not is_filled(value):
        return False

    text = normalize_text(str(value))

    if text in GENERIC_LOCATION_VALUES:
        return False

    return True


# ============================================================
# VERIFICATION DES CHAMPS
# ============================================================

def field_is_filled(data: dict, field: str) -> bool:

    value = get_value(data, field)

    # Description spéciale
    if field == "problem.description":
        return is_meaningful_description(value)

    return is_filled(value)


# ============================================================
# CHAMPS MANQUANTS
# ============================================================

def get_missing_fields(data: dict) -> list[str]:

    missing = []

    # ========================================================
    # 1. CATEGORIE
    # ========================================================

    category = get_value(
        data,
        "problem.category"
    )

    if not is_filled(category):

        return [
            "problem.category"
        ]

    category = str(category).upper()

    # ========================================================
    # 2. INFORMATIONS EMPLOYE
    # ========================================================

    if not field_is_filled(
        data,
        "employee.employee_id"
    ):
        missing.append(
            "employee.employee_id"
        )

    if not field_is_filled(
        data,
        "employee.email"
    ):
        missing.append(
            "employee.email"
        )

    # ========================================================
    # 3. TYPE D'EQUIPEMENT
    # ========================================================

    if category in [
        "IT_EQUIPMENT",
        "FURNITURE"
    ]:

        if not field_is_filled(
            data,
            "equipment.type"
        ):
            missing.append(
                "equipment.type"
            )

    # ========================================================
    # 4. LOCALISATION
    # ========================================================

    location_type = determine_location_type(
        data
    )

    location = data.get(
        "location",
        {}
    )

    # --------------------------------------------------------
    # BUREAU
    # --------------------------------------------------------

    if location_type == "office":

        # Bâtiment
        if not is_filled(
            location.get("building")
        ):
            missing.append(
                "location.building"
            )

        # Étage
        if not is_filled(
            location.get("floor")
        ):
            missing.append(
                "location.floor"
            )

        # Numéro du bureau
        if not is_filled(
            location.get("office")
        ):
            missing.append(
                "location.office"
            )
            
        # --------------------------------------------
        # Département où se trouve le problème
        # --------------------------------------------

        if not is_filled(
            location.get("department")
        ):
            missing.append(
               "location.department"
            )    

    # --------------------------------------------------------
    # TOILETTES
    # --------------------------------------------------------

    elif location_type == "restroom":

        # Bâtiment
        if not is_filled(
            location.get("building")
        ):
            missing.append(
                "location.building"
            )

        # Étage
        if not is_filled(
            location.get("floor")
        ):
            missing.append(
                "location.floor"
            )

        # Hommes / femmes
        if not is_filled(
            location.get("restroom_type")
        ):
            missing.append(
                "location.restroom_type"
            )

        # Département

        if not is_filled(
            location.get("department")
        ):
            missing.append(
                "location.department"
            )

    # --------------------------------------------------------
    # JARDIN
    # --------------------------------------------------------

    elif location_type == "landscaping":

        if not (
            is_filled(
                location.get("near_department")
            )
            or
            is_filled(
                location.get("near_office")
            )
            or
            is_filled(
                location.get("landmark")
            )
            or
            is_precise_location(
                location.get("specific_location")
            )
        ):
            missing.append(
                "location.near_department"
            )

    # --------------------------------------------------------
    # PARKING
    # --------------------------------------------------------

    elif location_type == "parking":

            if not (
                is_precise_location(
                    location.get("specific_location")
                )
                or
                is_filled(
                    location.get("near_department")
                )
                or
                is_filled(
                    location.get("near_office")
                )
                or
                is_filled(
                    location.get("landmark")
                )
            ):
                missing.append(
                    "location.specific_location"
                )

    # --------------------------------------------------------
    # ZONE COMMUNE
    # --------------------------------------------------------

    elif location_type == "common_area":

        if not is_filled(
            location.get("building")
        ):
            missing.append(
                "location.building"
            )

        if not is_filled(
            location.get("floor")
        ):
            missing.append(
                "location.floor"
            )

        if not (
            is_precise_location(
                location.get("specific_location")
            )
            or
            is_filled(
                location.get("near_department")
            )
            or
            is_filled(
                location.get("near_office")
            )
            or
            is_filled(
                location.get("landmark")
            )
        ):
            missing.append(
                "location.specific_location"
            )

    # --------------------------------------------------------
    # LOCALISATION INCONNUE
    # --------------------------------------------------------

    elif location_type == "unknown":

        if not is_filled(
            location.get("building")
        ):
            missing.append(
                "location.building"
            )

        if not is_filled(
            location.get("floor")
        ):
            missing.append(
                "location.floor"
            )

        if not is_filled(
            location.get("area")
        ):
            missing.append(
                "location.area"
            )

    # ========================================================
    # 5. DESCRIPTION DU PROBLEME
    # ========================================================

    if not field_is_filled(
        data,
        "problem.description"
    ):
        missing.append(
            "problem.description"
        )

    # ========================================================
    # 6. DUREE
    # ========================================================

    if category in DURATION_CATEGORIES:

        if not is_filled(
            get_value(
                data,
                "incident.duration"
            )
        ):
            missing.append(
                "incident.duration"
            )

    # ========================================================
    # 7. SUPPRESSION DES DOUBLONS
    # ========================================================

    result = []

    for field in missing:

        if field not in result:
            result.append(field)

    return result


# ============================================================
# QUESTION SUIVANTE
# ============================================================

def get_next_question(
    data: dict
) -> Optional[str]:

    missing_fields = get_missing_fields(
        data
    )

    if not missing_fields:
        return None

    field = missing_fields[0]

    # --------------------------------------------------------
    # Questions contextualisées
    # --------------------------------------------------------

    category = get_value(
        data,
        "problem.category"
    )

    location_type = determine_location_type(
        data
    )

    if field == "problem.category":

        location_type = determine_location_type(data)

        if location_type == "office":
            return (
                "Quel est le problème rencontré dans votre bureau ? "
                "Par exemple : climatisation, électricité, nettoyage, "
                "équipement informatique, mobilier, etc."
            )

        if location_type == "restroom":
            return (
                "Quel est le problème rencontré dans les toilettes ? "
                "Pouvez-vous me le décrire ?"
            )

        if location_type == "landscaping":
            return (
                "Quel est le problème rencontré dans le jardin "
                "ou l'espace vert ?"
            )

        if location_type == "parking":
            return (
                "Quel est le problème rencontré dans le parking ? "
                "Pouvez-vous me le décrire ?"
            )

        if location_type == "common_area":
            return (
                "Quel est le problème rencontré dans cette zone ? "
                "Pouvez-vous me le décrire ?"
            )

        return (
            "Pouvez-vous préciser quel est le problème rencontré ?"
        )
        
    if field == "location.department":
        return (
            "Dans quel département se trouve le problème ?"
        )

    if field == "location.near_department":

        if location_type == "restroom":

            return (
                "Pour permettre à l'équipe Facility Management "
                "de localiser rapidement les toilettes, "
                "près de quel département ou bureau se trouvent-elles ?"
            )

        if location_type == "landscaping":

            return (
                "Pour localiser précisément l'espace vert, "
                "près de quel département, bureau ou repère se trouve-t-il ?"
            )

        return (
            "Pouvez-vous préciser près de quel département "
            "se trouve le problème ?"
        )

    if field == "location.specific_location":

        if location_type == "parking":

            return (
                "Pouvez-vous préciser la zone ou l'emplacement "
                "exact du parking concerné, par exemple près d'un "
                "bâtiment, d'une entrée ou d'un repère ?"
            )

        if location_type == "common_area":

            return (
                "Pouvez-vous préciser l'emplacement exact "
                "dans cette zone ?"
            )

    if field == "location.restroom_type":

        return (
            "S'agit-il des toilettes hommes ou femmes ?"
        )

    if field == "location.office":

        return (
            "Quel est le numéro du bureau concerné ?"
        )

    # --------------------------------------------------------
    # Question standard
    # --------------------------------------------------------

    return QUESTIONS.get(
        field,
        "Pouvez-vous préciser cette information ?"
    )