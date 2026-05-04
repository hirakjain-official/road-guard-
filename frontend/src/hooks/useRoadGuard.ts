import { useEffect, useRef, useState, useCallback } from 'react'
import type { AlertEntry, Config, DetectionStatus, WSPayload } from '../types'

const BACKEND = 'http://localhost:8000'
const WS_URL = 'ws://localhost:8000/ws'

const DEFAULT_STATUS: DetectionStatus = {
  speed: null,
  overspeeding: false,
  vehiclesDetected: 0,
  cooldownRemaining: 0,
  alertActive: false,
}

const DEFAULT_CONFIG: Config = {
  speedLimit: 60,
  pixelSpeedMult: 0.5,
  cooldownSeconds: 30,
  line1Pct: 0.35,
  line2Pct: 0.65,
  confidence: 0.4,
  callOnAnyDetection: true,
}

export function useRoadGuard() {
  const [status, setStatus] = useState<DetectionStatus>(DEFAULT_STATUS)
  const [alerts, setAlerts] = useState<AlertEntry[]>([])
  const [config, setConfig] = useState<Config>(DEFAULT_CONFIG)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const seenAlertIds = useRef<Set<string>>(new Set())

  useEffect(() => {
    let reconnectTimer: ReturnType<typeof setTimeout>

    function connect() {
      const ws = new WebSocket(WS_URL)
      wsRef.current = ws

      ws.onopen = () => setConnected(true)

      ws.onmessage = (e) => {
        const payload: WSPayload = JSON.parse(e.data)
        setStatus(payload.status)
        setConfig(payload.config)

        const newAlerts = payload.alerts.filter(
          (a) => !seenAlertIds.current.has(a.id)
        )
        if (newAlerts.length > 0) {
          newAlerts.forEach((a) => seenAlertIds.current.add(a.id))
          setAlerts((prev) => [...newAlerts, ...prev].slice(0, 50))
        }
      }

      ws.onclose = () => {
        setConnected(false)
        reconnectTimer = setTimeout(connect, 2000)
      }

      ws.onerror = () => ws.close()
    }

    connect()
    return () => {
      clearTimeout(reconnectTimer)
      wsRef.current?.close()
    }
  }, [])

  const updateConfig = useCallback(async (patch: Partial<Config>) => {
    const merged = { ...config, ...patch }
    setConfig(merged)
    try {
      await fetch(`${BACKEND}/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          speed_limit: merged.speedLimit,
          pixel_speed_mult: merged.pixelSpeedMult,
          cooldown_seconds: merged.cooldownSeconds,
          line1_pct: merged.line1Pct,
          line2_pct: merged.line2Pct,
          confidence: merged.confidence,
          call_on_any_detection: merged.callOnAnyDetection,
        }),
      })
    } catch {
      // backend not yet running — config stays in local state
    }
  }, [config])

  return { status, alerts, config, connected, updateConfig }
}
