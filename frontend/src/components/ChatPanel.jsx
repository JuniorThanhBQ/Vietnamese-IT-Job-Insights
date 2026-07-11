import { useRef, useEffect, useState } from 'react';

import { Send, Bot, User, Trash2, ArrowRight } from 'lucide-react';

const SUGGESTIONS = [
  'Tìm công việc Python Remote lương cao',
  'Yêu cầu kỹ năng đối với Senior React',
  'Có công việc Golang nào tuyển ở Hà Nội không?',
  'Tổng hợp các công việc có lương đô la (USD)',
];

export function ChatPanel({ messages, streaming, error, sendMessage, onClear }) {
  const [input, setInput] = useState('');
  const chatEndRef = useRef(null);

  // Auto scroll to bottom on new message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streaming]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || streaming) return;
    sendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="glass-panel rounded-xl flex flex-col h-[calc(100vh-140px)] max-h-[750px]">
      {/* Header */}
      <div className="p-4 border-b border-gray-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400 border border-blue-500/20">
            <Bot size={18} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-gray-200">Trợ Lý Ảo Tuyển Dụng</h3>
            <p className="text-xs text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Sẵn sàng hỗ trợ bạn
            </p>
          </div>
        </div>
        {messages.length > 0 && (
          <button
            onClick={onClear}
            className="p-1.5 rounded-lg hover:bg-red-500/10 text-gray-500 hover:text-red-400 transition-colors cursor-pointer"
            title="Xóa lịch sử hội thoại"
          >
            <Trash2 size={16} />
          </button>
        )}
      </div>

      {/* Message List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto p-4">
            <Bot size={48} className="text-blue-400 mb-4 animate-bounce" />
            <h4 className="text-base font-bold text-gray-200 mb-2">
              Trò chuyện tuyển dụng thông minh
            </h4>
            <p className="text-sm text-gray-400 mb-6 leading-relaxed">
              Hãy hỏi tôi về các công việc IT tại Việt Nam (ITviec và TopDev). Tôi sẽ tìm kiếm ngữ
              nghĩa và trả lời bạn tức thì!
            </p>
            <div className="w-full space-y-2">
              {SUGGESTIONS.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => sendMessage(s)}
                  className="w-full flex items-center justify-between p-3 rounded-lg bg-gray-900/40 hover:bg-gray-900 border border-gray-800 hover:border-blue-500/40 text-left text-xs font-semibold text-gray-300 transition-all cursor-pointer group"
                >
                  <span>{s}</span>
                  <ArrowRight
                    size={14}
                    className="text-gray-600 group-hover:text-blue-400 transition-colors"
                  />
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, index) => {
            const isUser = msg.role === 'user';
            return (
              <div key={index} className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
                {/* Avatar */}
                {!isUser && (
                  <div className="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20 shrink-0 flex items-center justify-center">
                    <Bot size={16} />
                  </div>
                )}

                {/* Bubble */}
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
                    isUser
                      ? 'bg-blue-600 text-white rounded-tr-none'
                      : 'bg-white/3 border border-white/5 text-gray-200 rounded-tl-none font-sans'
                  }`}
                >
                  {msg.content}
                </div>

                {isUser && (
                  <div className="w-8 h-8 rounded-lg bg-gray-800 text-gray-400 border border-gray-700 shrink-0 flex items-center justify-center">
                    <User size={16} />
                  </div>
                )}
              </div>
            );
          })
        )}

        {/* Streaming text indicator */}
        {streaming && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20 shrink-0 flex items-center justify-center">
              <Bot size={16} />
            </div>
            <div className="bg-white/3 border border-white/5 text-gray-200 rounded-2xl rounded-tl-none px-4 py-3 text-sm flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-blue-400 animate-bounce [animation-delay:-0.3s]"></span>
              <span className="w-2 h-2 rounded-full bg-blue-400 animate-bounce [animation-delay:-0.15s]"></span>
              <span className="w-2 h-2 rounded-full bg-blue-400 animate-bounce"></span>
            </div>
          </div>
        )}

        {error && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
            Lỗi: {error}
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-800 flex gap-2">
        <textarea
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Nhập câu hỏi của bạn (ví dụ: Tuyển dụng Python Senior lương tốt tại Hồ Chí Minh)..."
          className="flex-1 bg-gray-900/50 border border-gray-800 focus:border-blue-500/50 rounded-lg px-3 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none resize-none min-h-[42px] max-h-[120px]"
        />
        <button
          type="submit"
          disabled={!input.trim() || streaming}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 text-white disabled:text-gray-500 rounded-lg transition-colors flex items-center justify-center cursor-pointer shrink-0"
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
