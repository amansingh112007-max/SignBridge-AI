import { useState } from 'react';
import useSignBridge from './hooks/useSignBridge.js';
import VideoFeed from './components/VideoFeed.jsx';
import TranscriptPanel from './components/TranscriptPanel.jsx';
import ControlBar from './components/ControlBar.jsx';
import KeypointPreview from './components/KeypointPreview.jsx';

const STEPS = [
  { n: '01', t: 'Show up as you are', d: 'Open your camera. A gentle framing guide helps you find the right light and space.' },
  { n: '02', t: 'Move naturally', d: 'Our on-device model follows 3D hand, face, and body movement in real time.' },
  { n: '03', t: 'Be understood', d: 'Captions appear instantly. Tap once to let your voice carry further.' },
];

export default function App() {
  const {
    videoRef, canvasRef, connected, running, tracking, currentText, confidence,
    landmarks, transcript, error, lang, setLang, seconds, start, stop, clearTranscript,
  } = useSignBridge();

  const [largeText, setLargeText] = useState(false);
  const [highContrast, setHighContrast] = useState(false);

  return (
    <div className={`min-h-screen ${highContrast ? 'bg-black text-yellow-200' : 'bg-ink text-slate-200'} transition-colors`}>
      {/* Top bar */}
      <header className="max-w-7xl mx-auto px-6 pt-6 flex items-center justify-between">
        <div className="flex items-center gap-2 text-xl font-extrabold">
          🤟 SignBridge <span className="font-display italic text-accent">AI</span>
        </div>
        <div className="text-[10px] uppercase tracking-[0.3em] text-slate-500">Private beta · On-device AI</div>
      </header>

      {/* Hero line */}
      <section className="max-w-7xl mx-auto px-6 pt-10 pb-8">
        <h1 className={`font-display font-semibold leading-tight ${largeText ? 'text-6xl' : 'text-5xl'}`}>
          Every sign <em className="italic text-accent">deserves</em> to be heard.
        </h1>
        <p className="mt-3 text-slate-400 max-w-2xl">
          SignBridge turns sign language into clear, natural speech — instantly.
          A quiet bridge for louder human connection.
        </p>
      </section>

      {error && (
        <div className="max-w-7xl mx-auto px-6 mb-4">
          <div className="rounded-xl bg-red-500/15 ring-1 ring-red-500 text-red-300 px-4 py-3 text-sm">⚠️ {error}</div>
        </div>
      )}

      {/* Live studio grid */}
      <main className="max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <VideoFeed
            videoRef={videoRef} canvasRef={canvasRef}
            running={running} tracking={tracking}
            currentText={currentText} confidence={confidence}
            landmarks={landmarks} seconds={seconds} lang={lang}
            largeText={largeText} highContrast={highContrast}
          />
        </div>
        <div className="space-y-6">
          <KeypointPreview tracking={tracking} confidence={confidence} />
          <TranscriptPanel transcript={transcript} onClear={clearTranscript} lang={lang} largeText={largeText} />
        </div>
      </main>

      {/* Controls */}
      <div className="max-w-7xl mx-auto px-6 py-10">
        <ControlBar
          running={running} onStart={start} onStop={stop}
          lang={lang} setLang={setLang}
          largeText={largeText} setLargeText={setLargeText}
          highContrast={highContrast} setHighContrast={setHighContrast}
        />
      </div>

      {/* How it works */}
      <section className="max-w-7xl mx-auto px-6 pb-10 grid grid-cols-1 md:grid-cols-3 gap-6">
        {STEPS.map((s) => (
          <div key={s.n} className="rounded-2xl bg-panel ring-1 ring-slate-800 p-6">
            <div className="text-[10px] uppercase tracking-[0.3em] text-accent">{s.n}</div>
            <h3 className="mt-2 font-display italic text-xl text-slate-100">{s.t}</h3>
            <p className="mt-2 text-sm text-slate-400">{s.d}</p>
          </div>
        ))}
      </section>

      {/* Privacy strip */}
      <footer className="border-t border-slate-800/70">
        <div className="max-w-7xl mx-auto px-6 py-5 flex flex-wrap items-center justify-center gap-x-8 gap-y-2 text-[11px] uppercase tracking-[0.2em] text-slate-500">
          <span>0 sec raw video retention</span>
          <span>·</span>
          <span>Processing on this device</span>
          <span>·</span>
          <span>No video stored</span>
        </div>
      </footer>
    </div>
  );
}