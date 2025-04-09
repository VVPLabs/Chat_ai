import { MessageSquare, Send, X, Clock } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

export default function ChatBox() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { id: 1, text: "Hi there! How can I help you today?", sender: "bot", timestamp: new Date() }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const threadId = useRef(crypto.randomUUID());
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Handle window resize for mobile responsiveness
  useEffect(() => {
    const handleResize = () => {
      if (chatContainerRef.current) {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize(); // Initialize on first render
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleChat = () => setIsOpen(!isOpen);

  const handleInputChange = (e) => setInputValue(e.target.value);

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleSendMessage = async () => {
    const trimmed = inputValue.trim();
    if (!trimmed) return;

    const now = new Date();
    const newUserMessage = { 
      id: messages.length + 1, 
      text: trimmed, 
      sender: "user", 
      timestamp: now 
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    setInputValue('');
    setIsLoading(true);

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
      const sanitizedData = data.replace(/^"(.*)"$/, '$1');
      
      setIsLoading(false);
      const botResponse = {
        id: messages.length + 2,
        text: sanitizedData,
        sender: "bot",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botResponse]);

    } catch (err) {
      console.error("Error sending message:", err);
      setIsLoading(false);
      setMessages(prev => [...prev, {
        id: messages.length + 2,
        text: "Oops! Something went wrong. Please try again later.",
        sender: "bot",
        timestamp: new Date()
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
        <div 
          ref={chatContainerRef}
          className="bg-white rounded-xl shadow-2xl w-80 sm:w-96 flex flex-col mb-4 border border-gray-200 overflow-hidden transition-all duration-300 ease-in-out"
          style={{ height: 'calc(var(--vh, 1vh) * 70)', maxHeight: '28rem' }}
        >
          <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-4 flex justify-between items-center">
            <h3 className="font-medium flex items-center">
              <MessageSquare className="h-5 w-5 mr-2" />
              Chat Assistant
            </h3>
            <button 
              onClick={toggleChat} 
              className="text-white hover:bg-indigo-700 rounded-full p-1 transition duration-200"
              title="Close chat"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="flex-1 p-4 overflow-y-auto bg-gray-50 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
            {messages.map((message) => (
              <div key={message.id} className={`mb-4 flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className="flex flex-col max-w-xs">
                  <div 
                    className={`rounded-2xl px-4 py-3 break-words shadow-sm ${
                      message.sender === 'user'
                        ? 'bg-blue-600 text-white rounded-br-none'
                        : 'bg-white text-gray-800 rounded-bl-none border border-gray-200'
                    }`}
                  >
                    {message.text}
                  </div>
                  <div className={`text-xs mt-1 flex items-center ${message.sender === 'user' ? 'justify-end mr-2' : 'justify-start ml-2'} text-gray-500`}>
                    <Clock className="h-3 w-3 mr-1" />
                    {formatTime(message.timestamp)}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-white text-gray-800 rounded-2xl rounded-bl-none px-4 py-3 max-w-xs shadow-sm border border-gray-200">
                  <div className="flex space-x-1 items-center h-6">
                    <div className="h-2 w-2 bg-blue-400 rounded-full animate-pulse"></div>
                    <div className="h-2 w-2 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: '300ms' }}></div>
                    <div className="h-2 w-2 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: '600ms' }}></div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} className="h-1" />
          </div>

          <div className="border-t border-gray-200 p-3 bg-white">
            <div className="flex items-center">
              <input
                ref={inputRef}
                type="text"
                placeholder="Type a message..."
                className="flex-1 border border-gray-300 rounded-full px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50 text-gray-700"
                value={inputValue}
                onChange={handleInputChange}
                onKeyDown={handleKeyPress}
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={inputValue.trim() === '' || isLoading}
                className={`ml-2 p-3 rounded-full transition-all duration-200 ${
                  inputValue.trim() === '' || isLoading
                    ? 'bg-gray-200 text-gray-400'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
                title="Send message"
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      )}

      <button
        onClick={toggleChat}
        className={`rounded-full p-4 shadow-lg ${
          isOpen ? 'bg-indigo-700' : 'bg-blue-600 hover:bg-blue-700'
        } text-white transition-all duration-300 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
        aria-label="Toggle chat"
      >
        <MessageSquare className="h-6 w-6" />
      </button>
    </div>
  );
}