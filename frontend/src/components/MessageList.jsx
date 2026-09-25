import { useEffect, useRef } from "react";
import Message from "./Message";

function MessageList({ messages, isTyping }) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isTyping]);

  return (
    <div className="message-list">
      {messages.map((message) => (
        <Message
          key={message.id}
          message={message}
        />
      ))}

      {isTyping && (
        <div className="message-row message-bot">
          <div className="message-avatar">
            🤖
          </div>

          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      )}

      {/* Point invisible utilisé pour le scroll automatique */}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default MessageList;