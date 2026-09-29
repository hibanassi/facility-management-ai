import { useState } from "react";

import ChatHeader from "../components/ChatHeader";
import MessageList from "../components/MessageList";
import ChatInput from "../components/ChatInput";

const API_URL = "http://localhost:8000";

function Chatbot() {
  const [sessionId, setSessionId] = useState(null);

  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: "bot",
      text:
        "Bonjour 👋 Je suis votre assistant Facility Management. " +
        "Je suis là pour vous aider à signaler un problème dans vos locaux. " +
        "Décrivez-moi simplement votre problème.",
    },
  ]);

  const [isTyping, setIsTyping] = useState(false);
  const [started, setStarted] = useState(false);

  // Nouvelle variable :
  // indique si le chatbot attend obligatoirement une photo
  const [photoRequired, setPhotoRequired] = useState(false);

  // ============================================================
  // PREMIER MESSAGE
  // ============================================================

  const startConversation = async (text) => {
    const newSessionId = crypto.randomUUID();

    setSessionId(newSessionId);

    const userMessage = {
      id: Date.now(),
      sender: "user",
      text: text,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setIsTyping(true);

    try {
      const response = await fetch(`${API_URL}/chat/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: newSessionId,
          message: text,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error("Erreur serveur");
      }

      const botMessage = {
        id: Date.now() + 1,
        sender: "bot",
        text:
          data.message ||
          data.question ||
          "Merci. Votre réclamation a été enregistrée.",
      };

      setMessages((previous) => [
        ...previous,
        botMessage,
      ]);

      setStarted(true);

      // Si le backend demande une photo
      if (
          data.status === "COLLECTING" &&
          data.current_question_field === "photo"
      ) {
          setPhotoRequired(true);
      } else {
          setPhotoRequired(false);
      }

    } catch (error) {
      console.error(error);

      setMessages((previous) => [
        ...previous,
        {
          id: Date.now() + 1,
          sender: "bot",
          text:
            "Désolé, une erreur est survenue lors de la connexion au serveur.",
        },
      ]);

    } finally {
      setIsTyping(false);
    }
  };

  // ============================================================
  // MESSAGES SUIVANTS
  // ============================================================

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    // ------------------------------------------------------------
    // PREMIER MESSAGE
    // ------------------------------------------------------------

    if (!started) {
      await startConversation(text);
      return;
    }

    // ------------------------------------------------------------
    // MESSAGE UTILISATEUR
    // ------------------------------------------------------------

    const userMessage = {
      id: Date.now(),
      sender: "user",
      text: text,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setIsTyping(true);

    try {
      const response = await fetch(`${API_URL}/chat/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: text,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error("Erreur serveur");
      }

      const botMessage = {
        id: Date.now() + 1,
        sender: "bot",
        text:
          data.message ||
          data.question ||
          "Merci. Votre réclamation est maintenant complète.",
      };

      setMessages((previous) => [
        ...previous,
        botMessage,
      ]);

      // ----------------------------------------------------------
      // LE BACKEND DEMANDE UNE PHOTO
      // ----------------------------------------------------------

      if (
          data.status === "COLLECTING" &&
          data.current_question_field === "photo"
      ) {
          setPhotoRequired(true);
      } else {
          setPhotoRequired(false);
      }

    } catch (error) {
      console.error(error);

      setMessages((previous) => [
        ...previous,
        {
          id: Date.now() + 1,
          sender: "bot",
          text:
            "Désolé, je n'arrive pas à contacter le serveur.",
        },
      ]);

    } finally {
      setIsTyping(false);
    }
  };

  // ============================================================
  // ENVOI DE LA PHOTO
  // ============================================================

  const sendPhoto = async (file) => {
    if (!file || !sessionId) return;

    // ------------------------------------------------------------
    // Vérification du type
    // ------------------------------------------------------------

    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/webp",
    ];

    if (!allowedTypes.includes(file.type)) {
      setMessages((previous) => [
        ...previous,
        {
          id: Date.now(),
          sender: "bot",
          text:
            "❌ Format non accepté. Veuillez sélectionner une image JPG, PNG ou WEBP.",
        },
      ]);

      return;
    }

    // ------------------------------------------------------------
    // Vérification de la taille
    // ------------------------------------------------------------

    const maxSize = 5 * 1024 * 1024; // 5 MB

    if (file.size > maxSize) {
      setMessages((previous) => [
        ...previous,
        {
          id: Date.now(),
          sender: "bot",
          text:
            "❌ La photo est trop volumineuse. La taille maximale est de 5 MB.",
        },
      ]);

      return;
    }

    // ------------------------------------------------------------
    // Afficher la photo dans la conversation
    // ------------------------------------------------------------

    const userPhotoMessage = {
      id: Date.now(),
      sender: "user",
      text: `📷 ${file.name}`,
    };

    setMessages((previous) => [
      ...previous,
      userPhotoMessage,
    ]);

    setIsTyping(true);

    try {
      // ----------------------------------------------------------
      // FormData pour envoyer un fichier
      // ----------------------------------------------------------

      const formData = new FormData();

      formData.append("session_id", sessionId);
      formData.append("photo", file);

      const response = await fetch(`${API_URL}/chat/photo`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.message || "Erreur lors de l'envoi de la photo"
        );
      }

      // ----------------------------------------------------------
      // Réponse du chatbot
      // ----------------------------------------------------------

      const botMessage = {
        id: Date.now() + 1,
        sender: "bot",
        text:
          data.message ||
          "📷 Photo reçue avec succès.",
      };

      setMessages((previous) => [
        ...previous,
        botMessage,
      ]);

      // ----------------------------------------------------------
      // La photo n'est plus demandée
      // ----------------------------------------------------------

      setPhotoRequired(false);

      // Si le backend demande encore une photo
      if (data.current_question_field === "photo") {
        setPhotoRequired(true);
      }

    } catch (error) {
      console.error(error);

      setMessages((previous) => [
        ...previous,
        {
          id: Date.now() + 1,
          sender: "bot",
          text:
            "❌ Impossible d'envoyer la photo. Veuillez réessayer.",
        },
      ]);

    } finally {
      setIsTyping(false);
    }
  };

  // ============================================================
  // INTERFACE
  // ============================================================

  return (
    <div className="chat-page">
      <div className="chat-container">

        <ChatHeader />

        <MessageList
          messages={messages}
          isTyping={isTyping}
        />

        <ChatInput
          onSend={sendMessage}
          onPhotoSelect={sendPhoto}
          photoRequired={photoRequired}
        />

      </div>
    </div>
  );
}

export default Chatbot;