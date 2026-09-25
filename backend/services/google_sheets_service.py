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
    C - Employee ID
    D - Employee Email
    E - Problem Description
    F - Category
    G - Subcategory
    H - Equipment
    I - Building
    J - Floor
    K - Department
    L - Restroom Type
    M - Specific Location
    N - Near Department
    O - Near Office
    P - Duration
    Q - Status
    R - Resolution Email Sent
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

        # C - Employee ID
        employee.get("employee_id") or "",

        # D - Employee Email
        employee.get("email") or "",

        # E - Problem Description
        problem.get("description") or "",

        # F - Category
        problem.get("category") or "",

        # G - Subcategory
        problem.get("subcategory") or "",

        # H - Equipment
        equipment.get("type") or "",

        # I - Building
        location.get("building") or "",

        # J - Floor
        location.get("floor")
        if location.get("floor") is not None
        else "",

        # K - Department
        location.get("department") or "",

        # L - Restroom Type
        location.get("restroom_type") or "",

        # M - Specific Location
        location.get("specific_location") or "",

        # N - Near Department
        location.get("near_department") or "",

        # O - Near Office
        location.get("near_office") or "",

        # P - Duration
        incident.get("duration") or "",

        # Q - Status
        complaint.get("status") or "NEW",

        # R - Resolution Email Sent
        "NO"
    ]

    # =====================================================
    # TROUVER LA PROCHAINE LIGNE
    # =====================================================

    column_a = worksheet.col_values(1)

    next_row = len(column_a) + 1

    # =====================================================
    # ECRITURE A:R
    # =====================================================

    range_name = f"A{next_row}:R{next_row}"

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

