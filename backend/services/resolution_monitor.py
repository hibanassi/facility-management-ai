import time

from backend.services.google_sheets_service import get_google_sheet
from backend.services.email_service import send_resolution_email


def check_resolved_complaints():
    """
    Vérifie les réclamations dans Google Sheets.

    N = Status
    O = Resolution Email Sent

    Si :
        Status = RESOLVED
        ET
        Resolution Email Sent = NO

    alors la réclamation est prête pour l'envoi
    de l'email à l'employé.
    """

    worksheet = get_google_sheet()

    rows = worksheet.get_all_values()

    if not rows:
        return

    # La première ligne contient les en-têtes
    for row_number, row in enumerate(rows[1:], start=2):

        # Éviter les problèmes si une ligne est incomplète
        if len(row) < 15:
            continue

        complaint_id = row[0]       # A
        employee_email = row[2]     # D
        status = row[13].strip().upper()       # Q
        email_sent = row[14].strip().upper()   # R

        print(
            f"[MONITOR] {complaint_id} | "
            f"Status={status} | "
            f"Email Sent={email_sent}"
        )

        if (
            status == "RESOLVED"
            and email_sent == "NO"
            and employee_email
        ):

            print(
                f"Réclamation résolue détectée : "
                f"{complaint_id}"
            )

            print(
                f"Email employé : "
                f"{employee_email}"
            )

            try:

                send_resolution_email(
                    employee_email,
                    complaint_id
                )

                # Colonne R = Resolution Email Sent
                worksheet.update_cell(
                    row_number,
                    15,
                    "YES"
                )

                print(
                    f"Colonne O mise à YES pour "
                    f"{complaint_id}"
                )

            except Exception as e:

                print(
                    f"Erreur lors de l'envoi de l'email "
                    f"pour {complaint_id} :"
                )

                print(e)


def monitor_loop():
    """
    Vérifie Google Sheets toutes les 10 secondes.
    """

    print("Surveillance Google Sheets démarrée...")

    while True:

        try:

            check_resolved_complaints()

        except Exception as e:

            print(
                "Erreur lors de la surveillance :"
            )

            print(e)

        time.sleep(10)