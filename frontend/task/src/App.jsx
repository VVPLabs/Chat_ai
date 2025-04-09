import { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';

export default function ChatBox() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { id: 1, text: "Hi there! How can I help you today?", sender: "bot" }
  ]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const threadId = useRef(uuidv4());

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const toggleChat = () => setIsOpen(!isOpen);

  const handleInputChange = (e) => setInputValue(e.target.value);

  const handleSendMessage = async () => {
    const trimmed = inputValue.trim();
    if (!trimmed) return;

    const newUserMessage = { id: messages.length + 1, text: trimmed, sender: "user" };
    setMessages(prev => [...prev, newUserMessage]);
    setInputValue('');

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [...messages, newUserMessage].map(m => m.text),
          thread_id: threadId.current,
        }),
      });

      const data = await response.text();

      const botResponse = {
        id: messages.length + 2,
        text: data,
        sender: "bot",
      };
      setMessages(prev => [...prev, botResponse]);

    } catch (err) {
      console.error("Error sending message:", err);
      setMessages(prev => [...prev, {
        id: messages.length + 2,
        text: "Oops! Something went wrong. Please try again later.",
        sender: "bot",
      }]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {isOpen && (
        <div className="bg-white rounded-lg shadow-xl w-80 sm:w-96 flex flex-col mb-4 border border-gray-200 overflow-hidden h-96">
          <div className="bg-indigo-600 text-white p-4 flex justify-between items-center">
            <h3 className="font-medium">Chat Assistant</h3>
            <button onClick={toggleChat} className="text-white hover:bg-indigo-700 rounded-full p-1">
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="flex-1 p-4 overflow-y-auto">
            {messages.map((message) => (
              <div key={message.id} className={`mb-4 flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`rounded-lg px-4 py-2 max-w-xs break-words ${message.sender === 'user'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-800'}`}>
                  {message.text}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div className="border-t border-gray-200 p-3 bg-gray-50">
            <div className="flex items-center">
              <input
                ref={inputRef}
                type="text"
                placeholder="Type a message..."
                className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={inputValue}
                onChange={handleInputChange}
                onKeyDown={handleKeyPress}
              />
              <button
                onClick={handleSendMessage}
                disabled={inputValue.trim() === ''}
                className={`ml-2 p-2 rounded-full ${inputValue.trim() === ''
                  ? 'bg-gray-200 text-gray-400'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
                  }`}>
                <Send className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      )}

      <button
        onClick={toggleChat}
        className={`rounded-full p-3 shadow-lg ${isOpen ? 'bg-indigo-700' : 'bg-indigo-600 hover:bg-indigo-700'} text-white transition-all duration-200`}>
        <MessageSquare className="h-6 w-6" />
      </button>
    </div>
  );
}
