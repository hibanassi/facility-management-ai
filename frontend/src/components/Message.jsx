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
          🤖
        </div>
      )}

      <div className="message-content">
        <div className="message-bubble">
          {message.text}
        </div>
      </div>

      {isUser && (
        <div className="message-avatar user-avatar">
          👤
        </div>
      )}
    </div>
  );
}

export default Message;