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

  // ============================================================
  // PREMIER MESSAGE
  // ============================================================

  const startConversation = async (text) => {
    const newSessionId = crypto.randomUUID();

    setSessionId(newSessionId);

    // ------------------------------------------------------------
    // 1. AFFICHER IMMEDIATEMENT LE MESSAGE UTILISATEUR
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

    // ------------------------------------------------------------
    // 2. AFFICHER L'INDICATEUR DE FRAPPE
    // ------------------------------------------------------------

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

      // ----------------------------------------------------------
      // 3. AJOUTER LA REPONSE DU CHATBOT
      // ----------------------------------------------------------

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

    } catch (error) {
      console.error(error);

      // ----------------------------------------------------------
      // MESSAGE D'ERREUR
      // ----------------------------------------------------------

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
    // 1. AFFICHER IMMEDIATEMENT LE MESSAGE UTILISATEUR
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

    // ------------------------------------------------------------
    // 2. AFFICHER "..."
    // ------------------------------------------------------------

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

      // ----------------------------------------------------------
      // 3. AJOUTER LA REPONSE DU CHATBOT
      // ----------------------------------------------------------

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
        />

      </div>
    </div>
  );
}

export default Chatbot;