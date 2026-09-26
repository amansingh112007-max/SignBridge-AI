import { useState } from 'react';
import useSignBridge from './hooks/useSignBridge.js';
import VideoFeed from './components/VideoFeed.jsx';
import TranscriptPanel from './components/TranscriptPanel.jsx';
import ControlBar from './components/ControlBar.jsx';

export default function App() {
  // All camera + AI logic lives in our custom hook
  const {
    videoRef, canvasRef,
    connected, running, currentGesture, transcript, error,
    start, stop, clearTranscript,
  } = useSignBridge();

  // Accessibility preferences
  const [largeText, setLargeText] = useState(false);
  const [highContrast, setHighContrast] = useState(false);

  return (
    <div className={`min-h-screen ${highContrast ? 'bg-black text-yellow-200' : 'bg-slate-950 text-slate-100'} transition-colors`}>
      {/* Header */}
      <header className="max-w-6xl mx-auto px-6 pt-8 pb-4 flex items-center justify-between">
        <h1 className={`font-extrabold tracking-tight ${largeText ? 'text-3xl' : 'text-2xl'}`}>
          🤟 SignBridge <span className="text-emerald-400">AI</span>
        </h1>
        <p className="text-sm text-slate-400 hidden sm:block">Real-Time Sign Language → Speech</p>
      </header>

      {/* Error banner */}
      {error && (
        <div className="max-w-6xl mx-auto px-6">
          <div className="mb-4 rounded-xl bg-red-500/15 ring-1 ring-red-500 text-red-300 px-4 py-3 text-sm">
            ⚠️ {error}
          </div>
        </div>
      )}

      {/* Main layout: video + transcript */}
      <main className="max-w-6xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <VideoFeed
            videoRef={videoRef}
            canvasRef={canvasRef}
            running={running}
            connected={connected}
            currentGesture={currentGesture}
            largeText={largeText}
          />
        </div>
        <div className="lg:col-span-1">
          <TranscriptPanel transcript={transcript} onClear={clearTranscript} largeText={largeText} />
        </div>
      </main>

      {/* Controls */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        <ControlBar
          running={running}
          onStart={start}
          onStop={stop}
          largeText={largeText}
          setLargeText={setLargeText}
          highContrast={highContrast}
          setHighContrast={setHighContrast}
        />
      </div>

      <footer className="text-center text-xs text-slate-600 pb-6">
        Privacy-first: raw video never leaves this device — only skeletal keypoints are processed.
      </footer>
    </div>
  );
}