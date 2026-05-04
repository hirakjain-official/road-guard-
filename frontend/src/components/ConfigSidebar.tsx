import { useState } from 'react'
import type { Config } from '../types'

interface ConfigSidebarProps {
  config: Config
  onUpdate: (patch: Partial<Config>) => void
}

function Slider({
  label,
  value,
  min,
  max,
  step,
  unit,
  onChange,
}: {
  label: string
  value: number
  min: number
  max: number
  step: number
  unit: string
  onChange: (v: number) => void
}) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-gray-400">{label}</span>
        <span className="text-gray-200 font-semibold tabular-nums">
          {value}
          {unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-green-500 cursor-pointer"
      />
    </div>
  )
}

export default function ConfigSidebar({ config, onUpdate }: ConfigSidebarProps) {
  const [open, setOpen] = useState(true)

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full px-4 py-3 flex items-center justify-between text-xs text-gray-400 tracking-widest font-semibold hover:text-gray-200 transition-colors"
      >
        <span>CONFIG</span>
        <span className="text-gray-600">{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <div className="px-4 pb-4 space-y-5 border-t border-gray-800 pt-4">
          <Slider
            label="Speed Limit"
            value={config.speedLimit}
            min={20}
            max={200}
            step={5}
            unit=" km/h"
            onChange={(v) => onUpdate({ speedLimit: v })}
          />
          <Slider
            label="Speed Multiplier"
            value={config.pixelSpeedMult}
            min={0.01}
            max={2}
            step={0.01}
            unit="×"
            onChange={(v) => onUpdate({ pixelSpeedMult: v })}
          />
          <Slider
            label="Cooldown"
            value={config.cooldownSeconds}
            min={5}
            max={300}
            step={5}
            unit="s"
            onChange={(v) => onUpdate({ cooldownSeconds: v })}
          />
          <Slider
            label="Line 1 Position"
            value={Math.round(config.line1Pct * 100)}
            min={10}
            max={50}
            step={1}
            unit="%"
            onChange={(v) => onUpdate({ line1Pct: v / 100 })}
          />
          <Slider
            label="Line 2 Position"
            value={Math.round(config.line2Pct * 100)}
            min={51}
            max={90}
            step={1}
            unit="%"
            onChange={(v) => onUpdate({ line2Pct: v / 100 })}
          />
          <Slider
            label="YOLO Confidence"
            value={config.confidence}
            min={0.1}
            max={0.9}
            step={0.05}
            unit=""
            onChange={(v) => onUpdate({ confidence: v })}
          />

          {/* Call on any detection toggle */}
          <div className="flex items-center justify-between border-t border-gray-800 pt-4">
            <div>
              <p className="text-xs text-gray-300 font-semibold">Call on any car</p>
              <p className="text-xs text-gray-600 mt-0.5">Demo mode — call whenever car crosses lines</p>
            </div>
            <button
              onClick={() => onUpdate({ callOnAnyDetection: !config.callOnAnyDetection })}
              className={`w-10 h-5 rounded-full transition-colors duration-200 relative ${
                config.callOnAnyDetection ? 'bg-green-500' : 'bg-gray-700'
              }`}
            >
              <span
                className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform duration-200 ${
                  config.callOnAnyDetection ? 'translate-x-5' : 'translate-x-0.5'
                }`}
              />
            </button>
          </div>

          <p className="text-gray-700 text-xs">
            Tune Speed Multiplier until a slow-moving toy car registers ~80 km/h
          </p>
        </div>
      )}
    </div>
  )
}
