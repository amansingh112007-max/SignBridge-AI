// Start/Stop + accessibility toggles (high contrast & large text)
export default function ControlBar({ running, onStart, onStop, largeText, setLargeText, highContrast, setHighContrast }) {
  return (
    <div className="flex flex-wrap items-center justify-center gap-3">
      {/* Main action button */}
      {!running ? (
        <button
          onClick={onStart}
          className="px-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-lg shadow-lg shadow-emerald-500/20 transition"
        >
          ▶ Start Translation
        </button>
      ) : (
        <button
          onClick={onStop}
          className="px-6 py-3 rounded-xl bg-red-500 hover:bg-red-400 text-white font-bold text-lg shadow-lg shadow-red-500/20 transition"
        >
          ■ Stop
        </button>
      )}

      {/* Accessibility toggles */}
      <button
        onClick={() => setLargeText(!largeText)}
        className={`px-4 py-2 rounded-xl text-sm font-medium ring-1 transition ${
          largeText ? 'bg-slate-100 text-slate-900 ring-slate-100' : 'bg-slate-800 text-slate-300 ring-slate-600 hover:bg-slate-700'
        }`}
      >
        🔍 Large Text
      </button>
      <button
        onClick={() => setHighContrast(!highContrast)}
        className={`px-4 py-2 rounded-xl text-sm font-medium ring-1 transition ${
          highContrast ? 'bg-yellow-300 text-black ring-yellow-300' : 'bg-slate-800 text-slate-300 ring-slate-600 hover:bg-slate-700'
        }`}
      >
        🌓 High Contrast
      </button>
    </div>
  );
}