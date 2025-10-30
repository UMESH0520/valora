import React from 'react'
import { useLivePrice } from '@/hooks/useLivePrice'

interface LivePriceTagProps {
  productId: string
  marginPercent?: number
  className?: string
}

export default function LivePriceTag({ productId, marginPercent = 3.0, className }: LivePriceTagProps) {
  const { displayRupees, isUpdating, triggerPriceUpdate } = useLivePrice(productId, marginPercent, true)

  return (
    <div className={className}>
      <div className="inline-flex items-center gap-2">
        <span className="text-sm text-muted-foreground">Price</span>
        <span className="text-base font-semibold">{displayRupees != null ? `₹${displayRupees.toFixed(2)}` : '—'}</span>
        <button
          onClick={triggerPriceUpdate}
          disabled={isUpdating}
          className="text-xs px-2 py-1 border rounded hover:bg-muted disabled:opacity-50"
          title="Refresh price"
        >{isUpdating ? 'Updating…' : 'Refresh'}</button>
      </div>
    </div>
  )
}
