import React, { useRef, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../apiConfig';

export const ChatPanel = ({ chatPanelVisible, setChatPanelVisible, chatMessages, setChatMessages, onSendMessage, sessionId, localName }) => {
  const chatMessagesRef = useRef(null);
  const chatInputRef = useRef(null);

  useEffect(() => {
    if (sessionId && setChatMessages) {
      axios.get(`${API_BASE_URL}/interviews/chat/${sessionId}/`)
        .then(response => {
          const formattedMessages = response.data.map((msg, index) => ({
            id: msg.timestamp + index,
            sender: msg.sender,
            text: msg.message,
            time: new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            isMine: msg.sender.toLowerCase() === (localName || '').toLowerCase()
          }));
          setChatMessages(formattedMessages);
        })
        .catch(err => console.error("Error fetching chat messages:", err));
    }
  }, [sessionId, setChatMessages, localName]);

  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  }, [chatMessages, chatPanelVisible]);

  const handleSend = () => {
    const msg = chatInputRef.current?.value.trim();
    if (msg) {
      onSendMessage(msg);
      if (chatInputRef.current) chatInputRef.current.value = '';
    }
  };

  return (
    <div className={`chat-sidebar ${!chatPanelVisible ? 'closed' : ''}`}>
      <div className="chat-header">
        <h3>Meeting Chat</h3>
        <button className="close-chat" onClick={() => setChatPanelVisible(false)}>
          <i className="fas fa-times"></i>
        </button>
      </div>

      <div className="chat-messages" ref={chatMessagesRef}>
        {chatMessages.map((msg) => (
          <div key={msg.id} className={`chat-message ${msg.isMine ? 'mine' : 'theirs'}`}>
            <div className="chat-message-header">
              <strong className="chat-message-sender">{msg.sender}</strong>
              <span className="chat-message-time">{msg.time}</span>
            </div>
            <div className="chat-message-text">{msg.text}</div>
          </div>
        ))}
      </div>

      <div className="chat-input-area">
        <input
          ref={chatInputRef}
          type="text"
          placeholder="Type a message..."
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button className="btn-send" onClick={handleSend}>
          <i className="fas fa-paper-plane"></i>
        </button>
      </div>
    </div>
  );
};

export default ChatPanel;
