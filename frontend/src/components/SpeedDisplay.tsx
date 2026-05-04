interface SpeedDisplayProps {
  speed: number | null
  speedLimit: number
  overspeeding: boolean
  vehiclesDetected: number
}

export default function SpeedDisplay({
  speed,
  speedLimit,
  overspeeding,
  vehiclesDetected,
}: SpeedDisplayProps) {
  const pct = speed ? Math.min((speed / speedLimit) * 100, 100) : 0
  const color = overspeeding ? '#ef4444' : speed ? '#22c55e' : '#4b5563'

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 space-y-4">
      {/* Speed number */}
      <div className="text-center">
        <div
          className={`text-7xl font-bold tabular-nums transition-colors duration-300 ${overspeeding ? 'speed-pulse' : ''}`}
          style={{ color }}
        >
          {speed !== null ? Math.round(speed) : '--'}
        </div>
        <div className="text-gray-500 text-sm mt-1 tracking-widest">KM/H</div>
      </div>

      {/* Bar */}
      <div>
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>0</span>
          <span>Limit {speedLimit}</span>
        </div>
        <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{ width: `${pct}%`, backgroundColor: color }}
          />
        </div>
        {overspeeding && (
          <p className="text-red-400 text-xs text-center mt-2 font-semibold tracking-widest animate-pulse">
            OVER LIMIT +{speed ? Math.round(speed - speedLimit) : 0} KM/H
          </p>
        )}
      </div>

      {/* Vehicles */}
      <div className="flex justify-between text-xs text-gray-500 border-t border-gray-800 pt-3">
        <span>Vehicles in frame</span>
        <span className="text-gray-300 font-bold">{vehiclesDetected}</span>
      </div>
    </div>
  )
}
