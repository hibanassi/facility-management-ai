
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import threading
from backend.services.resolution_monitor import monitor_loop
from backend.services.conversation_manager import ConversationManager
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Facility Management AI",
    description="API de gestion des réclamations Facility Management",
    version="1.0.0"
)

def start_resolution_monitor():
    monitor_thread = threading.Thread(
        target=monitor_loop,
        daemon=True
    )

    monitor_thread.start()

    print("Resolution Monitor démarré")

start_resolution_monitor()
# --------------------------------------------------
# CORS
# --------------------------------------------------

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

# --------------------------------------------------
# Gestion des conversations
# --------------------------------------------------

conversations = {}


# --------------------------------------------------
# Modèle pour recevoir un message
# --------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str
    message: str


# --------------------------------------------------
# Route principale
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Facility Management AI API",
        "status": "running"
    }


# --------------------------------------------------
# Démarrer une conversation
# --------------------------------------------------

@app.post("/chat/start")
def start_chat(request: ChatRequest):

    manager = ConversationManager()

    conversations[request.session_id] = manager

    result = manager.start(request.message)

    return result


# --------------------------------------------------
# Continuer une conversation
# --------------------------------------------------

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