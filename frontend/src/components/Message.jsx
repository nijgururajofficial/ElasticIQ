import ReactMarkdown from 'react-markdown';

export default function Message({ message }) {
  const { role, content } = message;

  const isUser = role === 'user';
  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-2xl rounded-lg px-4 py-3 text-sm shadow-md ${
          isUser
            ? 'bg-emerald-500 text-slate-950'
            : 'bg-slate-800 text-slate-100 border border-slate-700'
        }`}
      >
        <div className="whitespace-pre-wrap leading-6 prose prose-invert prose-sm max-w-none">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}