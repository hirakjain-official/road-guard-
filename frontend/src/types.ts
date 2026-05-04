export interface Config {
  speedLimit: number
  pixelSpeedMult: number
  cooldownSeconds: number
  line1Pct: number
  line2Pct: number
  confidence: number
  callOnAnyDetection: boolean
}

export interface AlertEntry {
  id: string
  timestamp: string
  speed: number
  callStatus: 'triggered' | 'cooldown' | 'error' | 'no_key'
}

export interface DetectionStatus {
  speed: number | null
  overspeeding: boolean
  vehiclesDetected: number
  cooldownRemaining: number
  alertActive: boolean
}

export interface WSPayload {
  status: DetectionStatus
  alerts: AlertEntry[]
  config: Config
}
