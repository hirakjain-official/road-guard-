interface StatusBadgeProps {
  connected: boolean
  alertActive: boolean
  overspeeding: boolean
  cooldownRemaining: number
}

export default function StatusBadge({
  connected,
  alertActive,
  overspeeding,
  cooldownRemaining,
}: StatusBadgeProps) {
  if (!connected) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-gray-800 border border-gray-700 text-gray-400 text-sm">
        <span className="w-2 h-2 rounded-full bg-gray-500" />
        OFFLINE
      </div>
    )
  }

  if (alertActive) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-red-950 border border-red-700 text-red-400 text-sm animate-pulse">
        <span className="w-2 h-2 rounded-full bg-red-400" />
        ALERT TRIGGERED
      </div>
    )
  }

  if (cooldownRemaining > 0) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-yellow-950 border border-yellow-700 text-yellow-400 text-sm">
        <span className="w-2 h-2 rounded-full bg-yellow-400" />
        COOLDOWN {cooldownRemaining}s
      </div>
    )
  }

  if (overspeeding) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-orange-950 border border-orange-700 text-orange-400 text-sm animate-pulse">
        <span className="w-2 h-2 rounded-full bg-orange-400" />
        OVERSPEEDING
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-green-950 border border-green-800 text-green-400 text-sm">
      <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
      MONITORING
    </div>
  )
}
