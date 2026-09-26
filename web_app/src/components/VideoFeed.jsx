// The live camera view with the caption overlay on top
export default function VideoFeed({ videoRef, canvasRef, running, connected, currentGesture, largeText }) {
  return (
    <div className="relative rounded-2xl overflow-hidden bg-black aspect-video shadow-2xl ring-1 ring-slate-700">
      {/* Mirror the selfie view so it feels natural (like Part 1's cv2.flip) */}
      <video
        ref={videoRef}
        playsInline
        muted
        className="w-full h-full object-cover -scale-x-100"
      />
      {/* Hidden canvas used to grab frames for the AI */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Idle screen */}
      {!running && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-slate-400">
          <span className="text-5xl">🤟</span>
          <p>Camera is off — press Start Translation</p>
        </div>
      )}

      {/* Connection badge */}
      <div className="absolute top-3 right-3 flex items-center gap-2 bg-black/60 rounded-full px-3 py-1 text-xs font-medium">
        <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
        {connected ? 'AI Connected' : 'Disconnected'}
      </div>

      {/* Live caption overlay (FR-3) */}
      <div className="absolute bottom-0 inset-x-0 p-4 bg-gradient-to-t from-black/85 to-transparent">
        {currentGesture ? (
          <p className={`text-center font-extrabold text-white drop-shadow-lg ${largeText ? 'text-6xl' : 'text-4xl'}`}
             role="status" aria-live="polite">
            {currentGesture}
          </p>
        ) : (
          <p className={`text-center text-slate-300 ${largeText ? 'text-2xl' : 'text-lg'}`}>
            {running ? 'Watching for a sign…' : '—'}
          </p>
        )}
      </div>
    </div>
  );
}