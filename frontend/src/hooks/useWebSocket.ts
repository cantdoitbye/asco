import { useState, useEffect, useCallback, useRef } from 'react'

interface WebSocketMessage {
  type: string
  payload?: unknown
  timestamp?: string
}

interface UseWebSocketReturn {
  isConnected: boolean
  lastMessage: WebSocketMessage | null
  sendMessage: (message: WebSocketMessage) => void
  reconnect: () => void
}

const getWebSocketUrl = () => {
  const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
  return wsUrl
}

export default function useWebSocket(): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const maxReconnectAttempts = 5

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      const ws = new WebSocket(getWebSocketUrl())

      ws.onopen = () => {
        setIsConnected(true)
        reconnectAttemptsRef.current = 0
      }

      ws.onclose = () => {
        setIsConnected(false)
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++
            connect()
          }, 3000 * (reconnectAttemptsRef.current + 1))
        }
      }

      ws.onerror = () => {
        setIsConnected(false)
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
        } catch {
          console.error('Failed to parse WebSocket message')
        }
      }

      wsRef.current = ws
    } catch {
      setIsConnected(false)
    }
  }, [])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsConnected(false)
  }, [])

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    }
  }, [])

  const reconnect = useCallback(() => {
    disconnect()
    reconnectAttemptsRef.current = 0
    connect()
  }, [connect, disconnect])

  useEffect(() => {
    connect()
    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    isConnected,
    lastMessage,
    sendMessage,
    reconnect,
  }
}
