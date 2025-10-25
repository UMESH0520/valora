import { useEffect, useMemo, useRef, useState, useCallback } from 'react'
import { createPriceWebSocket, fetchPrice, computePrice, PriceResponse } from '@/api'

export function useLivePrice(productId?: string, enableBlockchainUpdates = true) {
  const [data, setData] = useState<PriceResponse | null>(null)
  const [isUpdating, setIsUpdating] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const lastUpdateRef = useRef<number>(0)

  // Function to trigger price computation with blockchain update
  const triggerPriceUpdate = useCallback(async (marginPercent = 3.0) => {
    if (!productId || isUpdating) return
    
    setIsUpdating(true)
    try {
      const result = await computePrice(productId, marginPercent)
      if (result.blockchain_successful) {
        // Force refresh the price data
        const refreshedPrice = await fetchPrice(productId)
        setData(refreshedPrice)
        lastUpdateRef.current = Date.now()
      }
    } catch (error) {
      console.error('Failed to trigger price update:', error)
    } finally {
      setIsUpdating(false)
    }
  }, [productId, isUpdating])

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const res = await fetchPrice(productId)
        if (!cancelled) {
          setData(res)
          lastUpdateRef.current = Date.now()
        }
      } catch {}
    }

    load()

    if (enableBlockchainUpdates) {
      wsRef.current?.close()
      const ws = createPriceWebSocket(productId)
      wsRef.current = ws
      ws.onmessage = (ev) => {
        try {
          const payload = JSON.parse(ev.data) as PriceResponse
          if (!cancelled) {
            setData(payload)
            // Check if this is a blockchain update
            if (payload.price_updated && payload.blockchain_tx_id) {
              lastUpdateRef.current = Date.now()
            }
          }
        } catch {}
      }
      ws.onerror = () => ws.close()
    }

    return () => {
      cancelled = true
      wsRef.current?.close()
    }
  }, [productId, enableBlockchainUpdates])

  const price = data?.price ?? null
  const lastUpdated = data?.last_updated ?? null
  const isBlockchainPrice = data?.source === 'onchain' || Boolean(data?.blockchain_tx_id)
  const confidence = data?.confidence ?? null
  
  return { 
    price, 
    lastUpdated, 
    isBlockchainPrice, 
    confidence,
    isUpdating,
    triggerPriceUpdate,
    source: data?.source,
    blockchainTxId: data?.blockchain_tx_id
  }
}

export function useLivePricesMap(ids: string[]) {
  const unique = useMemo(() => Array.from(new Set(ids)).filter(Boolean), [ids])
  const [prices, setPrices] = useState<Record<string, number>>({})
  const socketsRef = useRef<Record<string, WebSocket>>({})

  useEffect(() => {
    let cancelled = false

    async function prime() {
      await Promise.all(unique.map(async (id) => {
        try {
          const res = await fetchPrice(id)
          if (!cancelled && res.price != null) {
            setPrices((prev) => ({ ...prev, [id]: res.price as number }))
          }
        } catch {}
      }))
    }

    prime()

    // close old
    Object.values(socketsRef.current).forEach((ws) => ws.close())
    socketsRef.current = {}

    unique.forEach((id) => {
      const ws = createPriceWebSocket(id)
      socketsRef.current[id] = ws
      ws.onmessage = (ev) => {
        try {
          const payload = JSON.parse(ev.data) as PriceResponse
          if (payload.product_id && payload.price != null) {
            setPrices((prev) => ({ ...prev, [payload.product_id as string]: payload.price as number }))
          }
        } catch {}
      }
      ws.onerror = () => ws.close()
    })

    return () => {
      cancelled = true
      Object.values(socketsRef.current).forEach((ws) => ws.close())
      socketsRef.current = {}
    }
  }, [unique.join('|')])

  return prices
}
