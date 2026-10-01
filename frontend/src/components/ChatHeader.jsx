import { Bot } from "lucide-react";

function ChatHeader() {
  return (
    <div className="chat-header">
      <div className="header-left">
        <div className="bot-avatar">
          <Bot size={24} />
        </div>

        <div>
          <h2>Facility Assistant</h2>

          <div className="status">
            <span className="status-dot"></span>
            Online
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatHeader;