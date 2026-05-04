interface VideoFeedProps {
  line1Pct: number
  line2Pct: number
  connected: boolean
}

export default function VideoFeed({ line1Pct, line2Pct, connected }: VideoFeedProps) {
  return (
    <div
      className="relative bg-black rounded-xl overflow-hidden border border-gray-800 shadow-2xl"
      style={{ minHeight: '360px' }}
    >
      {/* MJPEG stream — browser renders this natively, no JS needed */}
      <img
        src="http://localhost:8000/stream"
        alt="Road Guard Live Feed"
        className="w-full block"
        style={{ minHeight: '360px', objectFit: 'contain' }}
      />

      {/* Trigger line overlays */}
      <div
        className="absolute left-0 right-0 h-0.5 pointer-events-none"
        style={{ top: `${line1Pct * 100}%`, background: 'rgba(34,197,94,0.7)' }}
      />
      <div
        className="absolute left-0 right-0 h-0.5 pointer-events-none"
        style={{ top: `${line2Pct * 100}%`, background: 'rgba(239,68,68,0.7)' }}
      />

      {/* LIVE badge */}
      <div className="absolute top-3 left-3 bg-black/70 text-xs px-2 py-1 rounded font-mono flex items-center gap-1.5">
        <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-red-500 animate-pulse' : 'bg-gray-500'}`} />
        <span className={connected ? 'text-green-400' : 'text-gray-500'}>
          {connected ? 'LIVE' : 'OFFLINE'}
        </span>
      </div>
    </div>
  )
}
