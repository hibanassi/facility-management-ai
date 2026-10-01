import os
import smtplib
import mimetypes
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# CONFIGURATION SMTP
# ============================================================

FACILITY_MANAGEMENT_EMAIL = os.getenv(
    "FACILITY_MANAGEMENT_EMAIL"
)

SMTP_HOST = os.getenv(
    "SMTP_HOST",
    "smtp.gmail.com"
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587"
    )
)

SMTP_USER = os.getenv(
    "SMTP_USER"
)

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD"
)


# ============================================================
# ENVOI D'UNE RECLAMATION
# ============================================================

def send_complaint_email(complaint):

    if not SMTP_USER:
        raise ValueError(
            "SMTP_USER n'est pas configuré dans le fichier .env"
        )

    if not SMTP_PASSWORD:
        raise ValueError(
            "SMTP_PASSWORD n'est pas configuré dans le fichier .env"
        )

    if not FACILITY_MANAGEMENT_EMAIL:
        raise ValueError(
            "FACILITY_MANAGEMENT_EMAIL n'est pas configuré dans le fichier .env"
        )

    # ========================================================
    # RECUPERATION DES DONNEES
    # ========================================================

    employee = complaint.get("employee", {})
    problem = complaint.get("problem", {})
    equipment = complaint.get("equipment", {})
    location = complaint.get("location", {})
    incident = complaint.get("incident", {})
    photo = complaint.get("photo", {})
    
    photo_path = photo.get("path")
    photo_filename = photo.get("filename")
    photo_content_type = photo.get("content_type")

    if not photo_path:
        raise ValueError(
            "La photo est obligatoire pour envoyer la réclamation."
        )

    if not os.path.exists(photo_path):
        raise FileNotFoundError(
            f"La photo de la réclamation est introuvable : {photo_path}"
        )

    complaint_id = complaint.get(
        "complaint_id",
        "N/A"
    )

    # ========================================================
    # OBJET DE L'EMAIL
    # ========================================================

    subject = (
        f"[Nouvelle réclamation Facility Management] "
        f"{complaint_id}"
    )

    # ========================================================
    # CONSTRUCTION DYNAMIQUE DU CONTENU
    # ========================================================

    sections = []

    # ========================================================
    # EMPLOYE
    # ========================================================

    employee_lines = []

    if employee.get("email"):
        employee_lines.append(
            f"Adresse e-mail : {employee.get('email')}"
        )

    if employee_lines:
        sections.append(
            "EMPLOYE\n\n"
            + "\n".join(employee_lines)
        )

    # ========================================================
    # PROBLEME
    # ========================================================

    problem_lines = []

    if problem.get("description"):
        problem_lines.append(
            f"Description : {problem.get('description')}"
        )

    if problem.get("category"):
        problem_lines.append(
            f"Catégorie : {problem.get('category')}"
        )

    if problem.get("subcategory"):
        problem_lines.append(
            f"Sous-catégorie : {problem.get('subcategory')}"
        )

    if problem_lines:
        sections.append(
            "PROBLEME\n\n"
            + "\n".join(problem_lines)
        )

    # ========================================================
    # EQUIPEMENT
    # ========================================================

    equipment_lines = []

    if equipment.get("type"):
        equipment_lines.append(
            f"Type : {equipment.get('type')}"
        )

    if equipment.get("brand"):
        equipment_lines.append(
            f"Marque : {equipment.get('brand')}"
        )

    if equipment.get("model"):
        equipment_lines.append(
            f"Modèle : {equipment.get('model')}"
        )

    if equipment.get("asset_id"):
        equipment_lines.append(
            f"Asset ID : {equipment.get('asset_id')}"
        )

    if equipment.get("serial_number"):
        equipment_lines.append(
            f"Numéro de série : {equipment.get('serial_number')}"
        )

    if equipment_lines:
        sections.append(
            "EQUIPEMENT\n\n"
            + "\n".join(equipment_lines)
        )

    # ========================================================
    # LOCALISATION
    # ========================================================

    location_lines = []

    if location.get("department"):
        location_lines.append(
            f"Département : {location.get('department')}"
        )


    if location.get("area"):
        location_lines.append(
            f"Zone : {location.get('area')}"
        )

    if location.get("specific_location"):
        location_lines.append(
            f"Localisation précise : "
            f"{location.get('specific_location')}"
        )

    if location.get("near_department"):
        location_lines.append(
            f"Près du département : "
            f"{location.get('near_department')}"
        )

    if location.get("near_office"):
        location_lines.append(
            f"Près du bureau : "
            f"{location.get('near_office')}"
        )

    if location.get("landmark"):
        location_lines.append(
            f"Repère : {location.get('landmark')}"
        )

    if location.get("restroom_type"):
        location_lines.append(
            f"Type de toilettes : "
            f"{location.get('restroom_type')}"
        )

    if location_lines:
        sections.append(
            "LOCALISATION\n\n"
            + "\n".join(location_lines)
        )

    # ========================================================
    # INCIDENT
    # ========================================================

    incident_lines = []

    if incident.get("duration"):
        incident_lines.append(
            f"Durée : {incident.get('duration')}"
        )

    if incident.get("reported_at"):
        incident_lines.append(
            f"Signalé le : {incident.get('reported_at')}"
        )

    if incident.get("occurred_at"):
        incident_lines.append(
            f"Survenu le : {incident.get('occurred_at')}"
        )

    if incident_lines:
        sections.append(
            "INCIDENT\n\n"
            + "\n".join(incident_lines)
        )

    # ========================================================
    # STATUT
    # ========================================================

    status = complaint.get("status")

    if status:
        sections.append(
            "STATUT\n\n"
            f"{status}"
        )

    # ========================================================
    # CORPS FINAL DE L'EMAIL
    # ========================================================

    body = (
        "Bonjour,\n\n"
        "Une nouvelle réclamation vient d'être enregistrée "
        "dans le système Facility Management AI.\n\n"
        "==================================================\n"
        "INFORMATIONS DE LA RECLAMATION\n"
        "==================================================\n\n"
        f"Numéro de réclamation : {complaint_id}\n\n"
        "--------------------------------------------------\n\n"
        + "\n\n"
        + "\n\n--------------------------------------------------\n\n".join(sections)
        + "\n\n"
        "==================================================\n\n"
        "Cet e-mail a été généré automatiquement par "
        "Facility Management AI.\n\n"
        "Cordialement,\n\n"
        "Facility Management AI"
    )

    # ========================================================
    # CREATION DU MESSAGE
    # ========================================================

    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = SMTP_USER
    message["To"] = FACILITY_MANAGEMENT_EMAIL

    message.set_content(body)
    
    # ========================================================
    # PIECE JOINTE : PHOTO DE LA RECLAMATION
    # ========================================================

    with open(photo_path, "rb") as file:
        photo_data = file.read()

    mime_type = photo_content_type

    if not mime_type:
        mime_type, _ = mimetypes.guess_type(photo_path)

    if not mime_type:
        mime_type = "application/octet-stream"

    maintype, subtype = mime_type.split("/", 1)

    message.add_attachment(
        photo_data,
        maintype=maintype,
        subtype=subtype,
        filename=photo_filename or os.path.basename(photo_path)
    )

    # ========================================================
    # CONNEXION GMAIL
    # ========================================================

    print("Connexion à Gmail...")

    with smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT
    ) as server:

        server.starttls()

        print("Authentification Gmail...")

        server.login(
            SMTP_USER,
            SMTP_PASSWORD
        )

        print(
            "Envoi de la réclamation "
            f"{complaint_id}..."
        )

        server.send_message(message)

    print(
        "Réclamation envoyée par email à "
        f"{FACILITY_MANAGEMENT_EMAIL}"
    )
    
def send_resolution_email(employee_email, complaint_id):
    subject = f"Votre réclamation {complaint_id} a été résolue"

    body = f"""
Bonjour,

Nous vous informons que votre réclamation {complaint_id}
a été résolue par le service Facility Management.

Votre demande a été traitée avec succès.

Cordialement,

Facility Management
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = employee_email
    msg.set_content(body)

    print(f"Envoi de l'email de résolution à {employee_email}...")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

    print(
        f"Email de résolution envoyé à {employee_email}"
    )