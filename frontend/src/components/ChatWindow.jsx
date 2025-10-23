import { useState, useRef, useEffect } from 'react';
import Message from './Message';

const API_BASE = process.env.REACT_APP_API_BASE_URL || '';

const initialMessages = [
  {
    id: 'welcome',
    role: 'assistant',
    content: 'Hi! Ask me about your documents or upload new ones to get started.',
    sources: [],
  },
];

export default function ChatWindow({ onSelectSources }) {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const controllerRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!input.trim()) return;

    const userMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input.trim(),
      sources: [],
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    try {
      setIsLoading(true);
      controllerRef.current = new AbortController();
      const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage.content }),
        signal: controllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error('Failed to fetch answer');
      }

      const data = await response.json();
      const assistantMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);
      onSelectSources(assistantMessage.sources);
    } catch (error) {
      if (error.name === 'AbortError') {
        const abortMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: 'Generation stopped.',
          sources: [],
        };
        setMessages((prev) => [...prev, abortMessage]);
      } else {
        const errorMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: 'Sorry, something went wrong fetching the answer.',
          sources: [],
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } finally {
      setIsLoading(false);
      controllerRef.current = null;
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit(event);
    }
  };

  const handleStop = () => {
    if (controllerRef.current) {
      controllerRef.current.abort();
      controllerRef.current = null;
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        {isLoading && (
          <div className="flex items-center gap-3 text-sm text-emerald-400/80">
            <div className="flex space-x-1">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" style={{ animationDelay: '0ms' }}></span>
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" style={{ animationDelay: '300ms' }}></span>
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" style={{ animationDelay: '600ms' }}></span>
            </div>
            Generating answer...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form
        onSubmit={handleSubmit}
        className="border-t border-slate-800/50 p-6 bg-slate-900/50 backdrop-blur-sm"
      >
        <div className="flex gap-4 max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <textarea
              className="w-full resize-none rounded-xl border border-slate-700/50 bg-slate-800/50 px-4 py-3 text-sm 
                focus:outline-none focus:ring-2 focus:ring-emerald-500/50 placeholder:text-slate-400
                backdrop-blur-sm transition-all duration-200"
              rows={2}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask something about your documents... (Press Enter to send)"
            />
            <div className="absolute right-2 bottom-2 text-xs text-slate-400">
              Press Shift + Enter for new line
            </div>
          </div>
          <div className="flex flex-col gap-2">
            <button
              type="submit"
              disabled={isLoading}
              className="px-5 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-600 text-white font-medium 
                hover:from-emerald-400 hover:to-emerald-500 transition-all duration-200 shadow-lg shadow-emerald-500/20
                disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none
                active:shadow-sm active:translate-y-0.5"
            >
              Send
            </button>
            {isLoading && (
              <button
                type="button"
                onClick={handleStop}
                className="px-5 py-3 rounded-xl border border-slate-700/50 text-sm hover:bg-slate-800/50 
                  transition-all duration-200"
              >
                Stop
              </button>
            )}
          </div>
        </div>
      </form>
    </div>
  );
}