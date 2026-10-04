export default function ControlBar({ running, onStart, onStop, lang, setLang, largeText, setLargeText, highContrast, setHighContrast }) {
  return (
    <div className="flex flex-wrap items-center justify-center gap-4">
      <button
        onClick={running ? onStop : onStart}
        className={
          running
            ? 'px-8 py-4 rounded-full bg-red-500 hover:bg-red-400 text-white font-bold text-lg transition shadow-[0_0_40px_rgba(239,68,68,0.35)]'
            : 'px-8 py-4 rounded-full bg-accent hover:brightness-110 text-ink font-bold text-lg transition shadow-[0_0_40px_rgba(52,211,153,0.35)]'
        }
      >
        {running ? '■ End session' : '▶ Start a session'}
      </button>

      {/* Language segmented control */}
      <div className="flex rounded-full ring-1 ring-slate-700 overflow-hidden text-sm">
        <button onClick={() => setLang('en')}
          className={`px-4 py-2 ${lang === 'en' ? 'bg-slate-100 text-ink font-semibold' : 'text-slate-300 hover:bg-slate-800'}`}>
          English
        </button>
        <button onClick={() => setLang('hi')}
          className={`px-4 py-2 ${lang === 'hi' ? 'bg-slate-100 text-ink font-semibold' : 'text-slate-300 hover:bg-slate-800'}`}>
          हिंदी
        </button>
      </div>

      <button onClick={() => setLargeText(!largeText)}
        className={`px-4 py-2 rounded-full text-sm ring-1 transition ${largeText ? 'bg-slate-100 text-ink ring-slate-100' : 'bg-slate-800/60 text-slate-300 ring-slate-700 hover:bg-slate-700'}`}>
        🔍 Large Text
      </button>
      <button onClick={() => setHighContrast(!highContrast)}
        className={`px-4 py-2 rounded-full text-sm ring-1 transition ${highContrast ? 'bg-yellow-300 text-black ring-yellow-300' : 'bg-slate-800/60 text-slate-300 ring-slate-700 hover:bg-slate-700'}`}>
        🌓 High Contrast
      </button>
    </div>
  );
}