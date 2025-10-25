export const API_URL = (import.meta.env.VITE_API_BASE_URL as string) || 'http://127.0.0.1:8000';

export type PriceResponse = {
  product_id?: string | null;
  price?: number | null;
  currency: string;
  last_updated: string;
  source?: string | null;
  confidence?: number | null;
  description?: string | null;
  blockchain_tx_id?: string | null;
  price_updated?: boolean;
};

// Enhanced price computation with blockchain integration
export async function computePrice(productId: string, marginPercent = 3.0): Promise<any> {
  const url = new URL(`${API_URL}/api/price`);
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      product_id: productId,
      margin_percent: marginPercent
    })
  });
  if (!res.ok) throw new Error(`Failed to compute price: ${res.status}`);
  return res.json();
}

// Legacy price fetching for backward compatibility
export async function fetchPrice(productId?: string): Promise<PriceResponse> {
  const url = new URL(`${API_URL}/price`);
  if (productId) url.searchParams.set('product_id', productId);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Failed to fetch price: ${res.status}`);
  return res.json();
}

export function createPriceWebSocket(productId?: string): WebSocket {
  const wsBase = API_URL.replace(/^http/i, 'ws');
  const url = `${wsBase}/ws/price${productId ? `?product_id=${encodeURIComponent(productId)}` : ''}`;
  return new WebSocket(url);
}
