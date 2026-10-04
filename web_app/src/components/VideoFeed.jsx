import { useEffect, useRef } from 'react';

// Bone connections for drawing hands & torso
const HAND_BONES = [[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[5,9],[9,10],[10,11],[11,12],[9,13],[13,14],[14,15],[15,16],[13,17],[17,18],[18,19],[19,20],[0,17]];
const POSE_BONES = [[11,12],[11,13],[13,15],[12,14],[14,16],[11,23],[12,24],[23,24]];

function mmss(s) {
  const m = String(Math.floor(s / 60)).padStart(2, '0');
  const ss = String(s % 60).padStart(2, '0');
  return `${m}:${ss}`;
}

export default function VideoFeed({ videoRef, canvasRef, running, tracking, currentText, confidence, landmarks, seconds, lang, largeText, highContrast }) {
  const overlayRef = useRef(null);

  // Draw the skeletal preview every time new landmarks arrive
  useEffect(() => {
    const canvas = overlayRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;
    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (!landmarks) return;

    // Mirror X to match the CSS-flipped video
    const px = (p) => [(1 - p[0]) * canvas.width, p[1] * canvas.height];
    const dots = (pts, color, r) => {
      ctx.fillStyle = color;
      pts.forEach((p) => { const [x, y] = px(p); ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill(); });
    };
    const bones = (pts, pairs, color) => {
      ctx.strokeStyle = color; ctx.lineWidth = 2;
      pairs.forEach(([a, b]) => {
        const [x1, y1] = px(pts[a]); const [x2, y2] = px(pts[b]);
        ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
      });
    };

    bones(landmarks.pose, POSE_BONES, 'rgba(52,211,153,0.5)');
    dots(landmarks.pose, 'rgba(52,211,153,0.8)', 2);
    bones(landmarks.leftHand, HAND_BONES, 'rgba(96,165,250,0.85)');
    dots(landmarks.leftHand, '#93c5fd', 3);
    bones(landmarks.rightHand, HAND_BONES, 'rgba(244,114,182,0.85)');
    dots(landmarks.rightHand, '#f9a8d4', 3);
  }, [landmarks, videoRef]);

  const captionColor = highContrast ? 'text-yellow-300' : 'text-white';

  return (
    <div className="rounded-2xl overflow-hidden bg-black ring-1 ring-slate-800 shadow-2xl">
      {/* Studio status bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-panel border-b border-slate-800 text-[10px] uppercase tracking-[0.25em] text-slate-500">
        <span className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${running ? 'bg-red-500 animate-pulse-soft' : 'bg-slate-600'}`} />
          {running ? 'Live' : 'Translation standby'}
        </span>
        <span>Session {mmss(seconds)}</span>
      </div>

      <div className="relative aspect-video bg-black">
        <video ref={videoRef} playsInline muted className="w-full h-full object-cover -scale-x-100" />
        <canvas ref={canvasRef} className="hidden" />
        <canvas ref={overlayRef} className="absolute inset-0 w-full h-full pointer-events-none" />

        {/* Framing guide corners */}
        <div className="absolute inset-6 pointer-events-none">
          <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-slate-500/60 rounded-tl" />
          <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-slate-500/60 rounded-tr" />
          <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-slate-500/60 rounded-bl" />
          <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-slate-500/60 rounded-br" />
        </div>

        {/* Idle / framing guidance */}
        {!running && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-slate-400">
            <span className="text-5xl">🤟</span>
            <p className="font-display italic text-lg">Ready when you are</p>
            <p className="text-sm">Start a session to translate</p>
          </div>
        )}
        {running && !tracking && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-1 text-slate-300 bg-black/30">
            <p className="font-medium">Position yourself inside the frame</p>
            <p className="text-xs text-slate-400">Good lighting · hands visible</p>
          </div>
        )}

        {/* Live caption bar with confidence chip */}
        <div className="absolute bottom-0 inset-x-0 p-4 bg-gradient-to-t from-black/90 to-transparent">
          <div className="flex items-end justify-between gap-3">
            {currentText ? (
              <p className={`font-display font-semibold leading-tight ${largeText ? 'text-6xl' : 'text-4xl'} ${captionColor}`} role="status" aria-live="polite">
                {currentText}
              </p>
            ) : (
              <p className="text-slate-400 italic font-display">{running ? 'Listening with its eyes…' : '—'}</p>
            )}
            {currentText && (
              <span className="shrink-0 text-[10px] uppercase tracking-widest bg-accent/15 text-accent ring-1 ring-accent/40 rounded-full px-3 py-1">
                {confidence}% confidence
              </span>
            )}
          </div>
        </div>

        {/* Language chip */}
        <div className="absolute top-3 right-3 text-[10px] uppercase tracking-widest bg-black/60 rounded-full px-3 py-1 text-slate-300">
          {lang === 'hi' ? 'हिंदी' : 'English'} · {tracking ? 'tracking' : 'idle'}
        </div>
      </div>
    </div>
  );
}