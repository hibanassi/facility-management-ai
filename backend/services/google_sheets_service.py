import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from uuid import uuid4


GOOGLE_CREDENTIALS_FILE = (
    "credentials/google-service-account.json"
)

SPREADSHEET_NAME = "facility-management-ai"


def get_google_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    credentials = Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE,
        scopes=scopes
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open(SPREADSHEET_NAME)
    worksheet = spreadsheet.sheet1

    return worksheet


def generate_complaint_id():
    """
    Génère un identifiant unique pour la réclamation.
    Exemple : REC-8F3A21C4
    """
    return f"REC-{uuid4().hex[:8].upper()}"


def save_complaint(complaint):
    """
    Enregistre une réclamation complète dans Google Sheets.

    Colonnes :

    A - Complaint ID
    B - Date
    C - Employee Email
    D - Problem Description
    E - Category
    F - Subcategory
    G - Equipment
    H - Department
    I - Restroom Type
    J - Specific Location
    K - Near Department
    L - Near Office
    M - Duration
    N - Status
    O - Resolution Email Sent
    """

    worksheet = get_google_sheet()

    employee = complaint.get("employee", {})
    problem = complaint.get("problem", {})
    equipment = complaint.get("equipment", {})
    location = complaint.get("location", {})
    incident = complaint.get("incident", {})

    complaint_id = complaint.get("complaint_id")

    if not complaint_id:
        complaint_id = generate_complaint_id()

    date = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # =====================================================
    # CONSTRUCTION DE LA LIGNE
    # =====================================================

    row = [

        # A - Complaint ID
        complaint_id,

        # B - Date
        date,

        # C - Employee Email
        employee.get("email") or "",

        # D - Problem Description
        problem.get("description") or "",

        # E - Category
        problem.get("category") or "",

        # F - Subcategory
        problem.get("subcategory") or "",

        # G - Equipment
        equipment.get("type") or "",

        # H - Department
        location.get("department") or "",

        # I - Restroom Type
        location.get("restroom_type") or "",

        # J - Specific Location
        location.get("specific_location") or "",

        # K - Near Department
        location.get("near_department") or "",

        # L - Near Office
        location.get("near_office") or "",

        # M - Duration
        incident.get("duration") or "",

        # N - Status
        complaint.get("status") or "NEW",

        # O - Resolution Email Sent
        "NO"
    ]

    # =====================================================
    # TROUVER LA PROCHAINE LIGNE
    # =====================================================

    column_a = worksheet.col_values(1)

    next_row = len(column_a) + 1

    # =====================================================
    # ECRITURE A:P
    # =====================================================

    range_name = f"A{next_row}:O{next_row}"

    worksheet.update(
        range_name,
        [row],
        value_input_option="USER_ENTERED"
    )

    print(
        f"Réclamation enregistrée : "
        f"{complaint_id} dans {range_name}"
    )

    return complaint_id