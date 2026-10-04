function Row({ k, v }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-slate-500">{k}</span>
      <span className="text-slate-300">{v}</span>
    </div>
  );
}

export default function KeypointPreview({ tracking, confidence }) {
  return (
    <div className="rounded-2xl bg-panel ring-1 ring-slate-800 p-5">
      <div className="flex items-center justify-between text-[10px] uppercase tracking-[0.25em] text-slate-500">
        <span>Preview · 500+ keypoints</span>
        <span className={tracking ? 'text-accent animate-pulse-soft' : 'text-red-400'}>
          {tracking ? 'Locked' : 'Searching'}
        </span>
      </div>
      <div className="mt-3 font-display text-5xl font-semibold text-slate-100">
        {tracking ? '543' : '0'}
      </div>
      <p className="text-xs text-slate-500 mt-1">3D landmarks tracked per frame — hands · face · pose</p>
      <div className="mt-4 space-y-2 text-xs">
        <Row k="Model" v="LSTM · 2 layers" />
        <Row k="Confidence" v={`${confidence}%`} />
        <Row k="Retention" v="0 sec raw video" />
      </div>
    </div>
  );
}