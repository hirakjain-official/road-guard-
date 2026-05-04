import type { AlertEntry } from '../types'

interface AlertLogProps {
  alerts: AlertEntry[]
}

const statusLabel: Record<AlertEntry['callStatus'], string> = {
  triggered: '📞 CALL MADE',
  cooldown: '⏳ COOLDOWN',
  error: '❌ CALL FAILED',
  no_key: '🔑 NO API KEY',
}

const statusColor: Record<AlertEntry['callStatus'], string> = {
  triggered: 'text-green-400',
  cooldown: 'text-yellow-400',
  error: 'text-red-400',
  no_key: 'text-gray-500',
}

export default function AlertLog({ alerts }: AlertLogProps) {
  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 flex flex-col" style={{ maxHeight: '280px' }}>
      <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between">
        <span className="text-xs text-gray-400 tracking-widest font-semibold">ALERT LOG</span>
        <span className="text-xs text-gray-600">{alerts.length} events</span>
      </div>

      <div className="overflow-y-auto scrollbar-thin flex-1">
        {alerts.length === 0 ? (
          <div className="flex items-center justify-center h-20 text-gray-700 text-xs">
            No alerts yet — system monitoring
          </div>
        ) : (
          <ul className="divide-y divide-gray-800/50">
            {alerts.map((alert) => (
              <li key={alert.id} className="px-4 py-3 flex items-center gap-3 text-xs hover:bg-gray-800/30 transition-colors">
                <div className="flex-1 min-w-0">
                  <div className="text-gray-200 font-semibold">
                    {Math.round(alert.speed)} km/h detected
                  </div>
                  <div className="text-gray-600 mt-0.5 truncate">{alert.timestamp}</div>
                </div>
                <div className={`shrink-0 font-semibold ${statusColor[alert.callStatus]}`}>
                  {statusLabel[alert.callStatus]}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
