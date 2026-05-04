import { useRoadGuard } from './hooks/useRoadGuard'
import VideoFeed from './components/VideoFeed'
import SpeedDisplay from './components/SpeedDisplay'
import StatusBadge from './components/StatusBadge'
import AlertLog from './components/AlertLog'
import ConfigSidebar from './components/ConfigSidebar'

export default function App() {
  const { status, alerts, config, connected, updateConfig } = useRoadGuard()

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-4 md:p-6">
      {/* Header */}
      <header className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🚦</span>
          <div>
            <h1 className="text-lg font-bold tracking-wider text-gray-100">ROAD GUARD</h1>
            <p className="text-xs text-gray-600 tracking-widest">AI SPEED ENFORCEMENT SYSTEM</p>
          </div>
        </div>
        <StatusBadge
          connected={connected}
          alertActive={status.alertActive}
          overspeeding={status.overspeeding}
          cooldownRemaining={status.cooldownRemaining}
        />
      </header>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr_280px] gap-4">
        {/* Left — Config */}
        <aside className="space-y-4">
          <ConfigSidebar config={config} onUpdate={updateConfig} />

          {/* Connection status */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 px-4 py-3">
            <p className="text-xs text-gray-400 tracking-widest font-semibold mb-2">BACKEND</p>
            <div className="flex items-center gap-2 text-xs">
              <span
                className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-red-500'}`}
              />
              <span className={connected ? 'text-green-400' : 'text-red-400'}>
                {connected ? 'Connected — ws://localhost:8000' : 'Offline — start backend'}
              </span>
            </div>
          </div>
        </aside>

        {/* Center — Video + Alert log */}
        <main className="space-y-4">
          <VideoFeed line1Pct={config.line1Pct} line2Pct={config.line2Pct} connected={connected} />
          <AlertLog alerts={alerts} />
        </main>

        {/* Right — Speed + info */}
        <aside className="space-y-4">
          <SpeedDisplay
            speed={status.speed}
            speedLimit={config.speedLimit}
            overspeeding={status.overspeeding}
            vehiclesDetected={status.vehiclesDetected}
          />

          {/* Cooldown bar */}
          {status.cooldownRemaining > 0 && (
            <div className="bg-gray-900 rounded-xl border border-yellow-900 px-4 py-3">
              <div className="flex justify-between text-xs mb-2">
                <span className="text-yellow-400 font-semibold">COOLDOWN</span>
                <span className="text-yellow-600">{status.cooldownRemaining}s</span>
              </div>
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-yellow-500 rounded-full transition-all duration-1000"
                  style={{
                    width: `${(status.cooldownRemaining / config.cooldownSeconds) * 100}%`,
                  }}
                />
              </div>
            </div>
          )}

          {/* Info panel */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 px-4 py-3 space-y-2 text-xs text-gray-500">
            <p className="text-gray-400 font-semibold tracking-widest">SYSTEM INFO</p>
            <div className="flex justify-between">
              <span>Speed limit</span>
              <span className="text-gray-300">{config.speedLimit} km/h</span>
            </div>
            <div className="flex justify-between">
              <span>Multiplier</span>
              <span className="text-gray-300">{config.pixelSpeedMult}×</span>
            </div>
            <div className="flex justify-between">
              <span>YOLO conf.</span>
              <span className="text-gray-300">{config.confidence}</span>
            </div>
            <div className="flex justify-between">
              <span>Alerts total</span>
              <span className="text-gray-300">{alerts.length}</span>
            </div>
            <div className="flex justify-between">
              <span>Calls made</span>
              <span className="text-green-400">
                {alerts.filter((a) => a.callStatus === 'triggered').length}
              </span>
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}
