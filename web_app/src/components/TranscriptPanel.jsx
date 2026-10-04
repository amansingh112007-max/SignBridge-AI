export default function TranscriptPanel({ transcript, onClear, lang, largeText }) {
  return (
    <div className="rounded-2xl bg-panel ring-1 ring-slate-800 p-5 flex flex-col min-h-[320px] max-h-[480px]">
      <div className="flex items-center justify-between mb-3">
        <h2 className={`font-semibold text-slate-200 ${largeText ? 'text-xl' : 'text-base'}`}>
          {lang === 'hi' ? 'हिंदी' : 'English'} Conversation Transcript
        </h2>
        <button onClick={onClear} className="text-xs px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300">
          Clear
        </button>
      </div>

      {transcript.length === 0 ? (
        <p className="text-slate-500 text-sm italic font-display">No signs recognized yet. Start translating!</p>
      ) : (
        <ul className="space-y-2 overflow-y-auto pr-1 flex-1">
          {transcript.map((item, i) => (
            <li key={i} className="flex items-baseline gap-2 bg-slate-800/50 rounded-lg px-3 py-2">
              <span className="text-[10px] text-slate-500 shrink-0">{item.time}</span>
              <span className={`font-medium text-accent ${largeText ? 'text-xl' : 'text-sm'}`}>{item.text}</span>
              <span className="ml-auto text-[10px] text-slate-500">{item.confidence}%</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}