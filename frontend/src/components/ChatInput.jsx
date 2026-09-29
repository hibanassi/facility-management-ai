import { useRef, useState } from "react";

function ChatInput({ onSend, onPhotoSelect, photoRequired }) {
  const [message, setMessage] = useState("");
  const fileInputRef = useRef(null);

  const handleSubmit = (event) => {
    event.preventDefault();

    if (!message.trim()) return;

    onSend(message);
    setMessage("");
  };

  const handlePhotoClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    onPhotoSelect(file);

    // Permet de sélectionner à nouveau la même image
    event.target.value = "";
  };

  return (
    <form
      className="chat-input-container"
      onSubmit={handleSubmit}
    >

      {/* Bouton photo */}
      {photoRequired && (
        <>
          <button
            type="button"
            className="photo-button"
            onClick={handlePhotoClick}
            title="Ajouter une photo"
          >
            +
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileChange}
            style={{ display: "none" }}
          />
        </>
      )}

      <input
        type="text"
        placeholder={
          photoRequired
            ? "Ajoutez une photo du problème..."
            : "Décrivez votre problème..."
        }
        value={message}
        onChange={(event) =>
          setMessage(event.target.value)
        }
        disabled={photoRequired}
      />

      <button
        type="submit"
        disabled={photoRequired}
      >
        ➤
      </button>

    </form>
  );
}

export default ChatInput;