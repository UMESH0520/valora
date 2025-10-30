import { useEffect, useMemo, useRef, useState, useCallback } from 'react'
import { createPriceWebSocket, getLatestPrice, computePrice, BackendPriceOutput, WsPriceUpdate } from '@/api'

export function useLivePrice(productId?: string, marginPercent = 3.0, enableLive = true) {
  const [data, setData] = useState<BackendPriceOutput | null>(null)
  const [isUpdating, setIsUpdating] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  const triggerPriceUpdate = useCallback(async () => {
    if (!productId || isUpdating) return
    setIsUpdating(true)
    try {
      const result = await computePrice(productId, marginPercent)
      setData(result)
    } catch (e) {
      console.error(e)
    } finally {
      setIsUpdating(false)
    }
  }, [productId, marginPercent, isUpdating])

  useEffect(() => {
    if (!productId) return
    let cancelled = false

    async function load() {
      try {
        const res = await getLatestPrice(productId, marginPercent)
        if (!cancelled) setData(res)
      } catch (e) {
        console.warn('initial price load failed', e)
      }
    }

    load()

    if (enableLive) {
      wsRef.current?.close()
      const ws = createPriceWebSocket(productId)
      wsRef.current = ws
      ws.onmessage = (ev) => {
        try {
          const payload = JSON.parse(ev.data) as WsPriceUpdate
          if (payload?.type === 'price_update' && payload.product_id === productId) {
            setData((prev) => {
              const rupees = Number((payload.display_paise ?? 0) / 100)
              return {
                DISPLAY_PRICE: rupees,
                FETCHED_PRICE: prev?.FETCHED_PRICE ?? [],
                PRODUCTS_LIST: prev?.PRODUCTS_LIST ?? [],
              }
            })
          }
        } catch {}
      }
      ws.onerror = () => ws.close()
    }

    return () => {
      cancelled = true
      wsRef.current?.close()
    }
  }, [productId, marginPercent, enableLive])

  const displayRupees = data?.DISPLAY_PRICE ?? null

  return {
    displayRupees,
    data,
    isUpdating,
    triggerPriceUpdate,
  }
}

export function useLivePricesMap(ids: string[], marginPercent = 3.0) {
  const unique = useMemo(() => Array.from(new Set(ids)).filter(Boolean) as string[], [ids])
  const [prices, setPrices] = useState<Record<string, number>>({})
  const socketsRef = useRef<Record<string, WebSocket>>({})

  useEffect(() => {
    let cancelled = false

    async function prime() {
      await Promise.all(unique.map(async (id) => {
        try {
          const res = await getLatestPrice(id, marginPercent)
          if (!cancelled && res.DISPLAY_PRICE != null) {
            setPrices((prev) => ({ ...prev, [id]: res.DISPLAY_PRICE as number }))
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
          const payload = JSON.parse(ev.data) as WsPriceUpdate
          if (payload?.type === 'price_update' && payload.product_id) {
            setPrices((prev) => ({ ...prev, [payload.product_id]: (payload.display_paise || 0) / 100 }))
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
  }, [unique.join('|'), marginPercent])

  return prices
}
