import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader } from 'lucide-react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [userId] = useState(`user_${Date.now()}`);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/process-request`, {
        request: input,
        user_id: userId
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.coordinator_response || 'Respuesta recibida',
        agents: response.data.agents_used || [],
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'error',
        content: error.response?.data?.error || 'Error de conexión con el servidor',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-xl font-semibold text-gray-800">Sistema Multi-Agente</h1>
        <p className="text-sm text-gray-500">Notion AI Assistant</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-400 mt-20">
              <p className="text-lg mb-4">¿En qué puedo ayudarte hoy?</p>
              <div className="space-y-2 text-sm">
                <p>• Analiza mi contenido de Notion</p>
                <p>• Crea tareas para mi proyecto</p>
                <p>• Organiza la estructura de mi documento</p>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-2xl rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : message.role === 'error'
                    ? 'bg-red-50 text-red-800 border border-red-200'
                    : 'bg-white text-gray-800 border border-gray-200'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                {message.agents && message.agents.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-200">
                    <p className="text-xs text-gray-500">
                      Agentes: {message.agents.join(', ')}
                    </p>
                  </div>
                )}
                <p className="text-xs mt-1 opacity-70">{message.timestamp}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
                <Loader className="w-5 h-5 animate-spin text-gray-400" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-4 py-4">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Escribe tu mensaje..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-blue-600 text-white p-3 rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;