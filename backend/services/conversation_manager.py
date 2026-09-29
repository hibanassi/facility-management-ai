
import json

from backend.services.llm_service import (
    analyze_complaint,
    extract_answer
)

from backend.services.question_engine import (
    get_missing_fields,
    get_next_question
)

from backend.services.google_sheets_service import save_complaint
from backend.services.email_service import send_complaint_email

class ConversationManager:

    def __init__(self):

        self.complaint = {

            "employee": {
                "employee_id": None,
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
                "building": None,
                "floor": None,
                "office": None,
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
            },
            
            "photo": {
                "path": None,
                "filename": None,
                "content_type": None
            }
        }

        self.status = "NEW"

        self.current_question = None

        self.current_question_field = None
        
        self.saved_to_google_sheets = False
        
        self.facility_email_sent = False
        
        self.photo_path = None
        
        self.photo_filename = None

        self.photo_content_type = None

    # MERGE

    def merge_data(self, target, source):

        for key, value in source.items():

            if isinstance(value, dict):

                if key not in target:

                    target[key] = {}

                self.merge_data(
                    target[key],
                    value
                )

            else:

                if value is not None and value != "":

                    target[key] = value


    # PARSE JSON

    def parse_llm_response(self, response):

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

            return json.loads(cleaned)

    # AFFICHER LE TICKET COMPLET


    def print_current_complaint(self):

        print("\n--- Current complaint ---")

        print(
            json.dumps(
                self.complaint,
                indent=4,
                ensure_ascii=False
            )
        )


    # DEMARRER

    def start(self, message):

        print("\n--- Initial message ---")

        print(message)

        response = analyze_complaint(
            message
        )

        extracted_data = self.parse_llm_response(
            response
        )

        print("\n--- Extracted data ---")

        print(
            json.dumps(
                extracted_data,
                indent=4,
                ensure_ascii=False
            )
        )

        self.merge_data(
            self.complaint,
            extracted_data
        )

        self.print_current_complaint()

        return self._continue_conversation()


    # REPONSE UTILISATEUR

    def process_message(self, message):

        if self.status == "COMPLETE":

            return {
                "status": "COMPLETE",
                "question": None,
                "message": (
                    "Cette réclamation est déjà complète."
                ),
                "missing_fields": [],
                "complaint": self.complaint
            }

        print("\n--- Employee response ---")

        print(message)

        response = extract_answer(
            message,
            self.current_question_field,
            self.complaint
        )

        extracted_data = self.parse_llm_response(
            response
        )

        print("\n--- Extracted answer ---")

        print(
            json.dumps(
                extracted_data,
                indent=4,
                ensure_ascii=False
            )
        )

        self.merge_data(
            self.complaint,
            extracted_data
        )

        self.print_current_complaint()

        return self._continue_conversation()


    # CONTINUER

    def _continue_conversation(self):

        missing_fields = get_missing_fields(
            self.complaint
        )

        # COMPLETE

        if not missing_fields:

            self.status = "COMPLETE"

            self.current_question = None

            self.current_question_field = None


            # ENREGISTREMENT GOOGLE SHEETS

            if not self.saved_to_google_sheets:

                self.complaint["status"] = "NEW"

                complaint_id = save_complaint(
                    self.complaint
                )

                self.complaint["complaint_id"] = complaint_id

                self.saved_to_google_sheets = True
                

            # ENVOI EMAIL FACILITY MANAGEMENT

            email_sent = False
            if not self.facility_email_sent:

                try:

                    send_complaint_email(
                        self.complaint
                    )

                    self.facility_email_sent = True
                    email_sent = True

                    print(
                        f" Email Facility Management envoyé "
                        f"pour {self.complaint['complaint_id']}"
                    )

                except Exception as e:

                    print(
                        " Erreur lors de l'envoi de l'email :"
                    )

                    print(e)    


            if email_sent:
                final_message = (
                    "Merci pour toutes ces informations. "
                    "Votre réclamation a bien été enregistrée. "
                    f"Votre numéro de réclamation est "
                    f"{self.complaint['complaint_id']}. "
                    "Elle a également été transmise par e-mail "
                    "au service Facility Management."
                )
            else:
                final_message = (
                    "Merci pour toutes ces informations. "
                    "Votre réclamation a bien été enregistrée. "
                    f"Votre numéro de réclamation est "
                    f"{self.complaint['complaint_id']}. "
                    "Cependant, l'envoi de l'e-mail au service "
                    "Facility Management a rencontré un problème."
                )

            return {
                "status": "COMPLETE",
                "question": None,
                "current_question_field": None,
                "message": final_message,
                "missing_fields": [],
                "complaint": self.complaint
            }


        # COLLECTING

        self.status = "COLLECTING"

        self.current_question_field = (
            missing_fields[0]
        )

        self.current_question = get_next_question(
            self.complaint
        )

        print(
            f"\n[NEXT QUESTION] "
            f"{self.current_question_field}"
        )

        print(
            f"[QUESTION] "
            f"{self.current_question}"
        )

        return {
            "status": "COLLECTING",

            "question": self.current_question,
            
            "current_question_field": self.current_question_field,

            "missing_fields": missing_fields,

            "complaint": self.complaint
        }
    def process_photo(self, file_path, filename, content_type):
        """
        Enregistre la photo associée à la réclamation
        puis reprend le traitement de la conversation.
        """

        self.photo_path = file_path
        self.photo_filename = filename
        self.photo_content_type = content_type

        self.complaint["photo"] = {
            "path": file_path,
            "filename": filename,
            "content_type": content_type
        }

        print("\n--- Photo reçue ---")
        print(f"Nom : {filename}")
        print(f"Type : {content_type}")
        print(f"Chemin : {file_path}")

        self.print_current_complaint()

        return self._continue_conversation()