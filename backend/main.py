from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
import uuid

from backend.services.resolution_monitor import monitor_loop
from backend.services.conversation_manager import ConversationManager

from dotenv import load_dotenv

load_dotenv()


app = FastAPI(
    title="Facility Management AI",
    description="API de gestion des réclamations Facility Management",
    version="1.0.0"
)


# ============================================================
# RESOLUTION MONITOR
# ============================================================

import threading


def start_resolution_monitor():
    monitor_thread = threading.Thread(
        target=monitor_loop,
        daemon=True
    )

    monitor_thread.start()

    print("Resolution Monitor démarré")


start_resolution_monitor()


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SESSIONS
# ============================================================

conversations = {}


# ============================================================
# DOSSIER DES PHOTOS
# ============================================================

UPLOAD_DIR = "uploads/complaints"

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# TYPES DE FICHIERS AUTORISÉS
# ============================================================

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


# ============================================================
# TAILLE MAXIMALE
# ============================================================

MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5 MB


# ============================================================
# CHAT REQUEST
# ============================================================

class ChatRequest(BaseModel):
    session_id: str
    message: str


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Facility Management AI API",
        "status": "running"
    }


# ============================================================
# START CHAT
# ============================================================

@app.post("/chat/start")
def start_chat(request: ChatRequest):

    manager = ConversationManager()

    conversations[request.session_id] = manager

    result = manager.start(request.message)

    return result


# ============================================================
# CHAT MESSAGE
# ============================================================

@app.post("/chat/message")
def send_message(request: ChatRequest):

    manager = conversations.get(request.session_id)

    if manager is None:

        return {
            "status": "ERROR",
            "message": "Session inconnue. Veuillez commencer une nouvelle conversation."
        }

    result = manager.process_message(request.message)

    return result


# ============================================================
# UPLOAD PHOTO
# ============================================================

@app.post("/chat/photo")
async def upload_photo(
    session_id: str = Form(...),
    photo: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Vérifier que la session existe
    # --------------------------------------------------------

    manager = conversations.get(session_id)

    if manager is None:

        return {
            "status": "ERROR",
            "message": "Session inconnue. Veuillez commencer une nouvelle conversation."
        }


    # --------------------------------------------------------
    # Vérifier le type du fichier
    # --------------------------------------------------------

    if photo.content_type not in ALLOWED_IMAGE_TYPES:

        return {
            "status": "ERROR",
            "message": (
                "Format de photo non accepté. "
                "Veuillez utiliser une image JPG, PNG ou WEBP."
            )
        }


    # --------------------------------------------------------
    # Lire le contenu de la photo
    # --------------------------------------------------------

    photo_data = await photo.read()


    # --------------------------------------------------------
    # Vérifier la taille
    # --------------------------------------------------------

    if len(photo_data) > MAX_PHOTO_SIZE:

        return {
            "status": "ERROR",
            "message": (
                "La photo est trop volumineuse. "
                "La taille maximale est de 5 MB."
            )
        }


    # --------------------------------------------------------
    # Vérifier que le fichier n'est pas vide
    # --------------------------------------------------------

    if len(photo_data) == 0:

        return {
            "status": "ERROR",
            "message": "La photo sélectionnée est vide."
        }


    # --------------------------------------------------------
    # Créer un nom unique
    # --------------------------------------------------------

    extension = ALLOWED_IMAGE_TYPES[photo.content_type]

    unique_filename = (
        f"{uuid.uuid4().hex}{extension}"
    )


    # --------------------------------------------------------
    # Chemin final
    # --------------------------------------------------------

    file_path = os.path.join(
        UPLOAD_DIR,
        unique_filename
    )


    # --------------------------------------------------------
    # Enregistrer la photo
    # --------------------------------------------------------

    with open(file_path, "wb") as file:

        file.write(photo_data)


    # --------------------------------------------------------
    # Pour l'instant :
    # on associe la photo au ConversationManager
    # --------------------------------------------------------

    result = manager.process_photo(
        file_path=file_path,
        filename=photo.filename,
        content_type=photo.content_type
    )

    return result