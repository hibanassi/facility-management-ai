import { Bot, UserRound } from "lucide-react";

function Message({ message }) {
  const isUser = message.sender === "user";

  return (
    <div
      className={`message-row ${
        isUser ? "message-user" : "message-bot"
      }`}
    >
      {!isUser && (
        <div className="message-avatar">
          <Bot size={24} />
        </div>
      )}

      <div className="message-content">
        <div className="message-bubble">
          {message.text}
        </div>
      </div>

      {isUser && (
        <div className="message-avatar user-avatar">
          <UserRound size={24} />
        </div>
      )}
    </div>
  );
}

export default Message;