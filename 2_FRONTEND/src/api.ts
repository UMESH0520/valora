export const API_URL = (import.meta.env.VITE_API_BASE_URL as string) || 'http://127.0.0.1:8000';

export type FetchedItem = {
  adapter?: string | null;
  paise?: number | null;
  rupees?: number | null;
  confidence?: number | null;
  raw?: Record<string, any> | null;
};

export type ProductInfo = {
  product_id: string;
  name?: string | null;
  brand?: string | null;
  model?: string | null;
  category?: string | null;
  last_known_paise?: number | null;
  last_known_price_readable?: string | null;
  is_active?: boolean | null;
};

export type BackendPriceOutput = {
  DISPLAY_PRICE: number; // rupees
  FETCHED_PRICE: FetchedItem[];
  PRODUCTS_LIST: ProductInfo[];
};

export type WsPriceUpdate = {
  type: 'price_update';
  product_id: string;
  display_paise: number;
  display_price_readable: string;
  lowest_paise: number;
  margin_percent: number;
  blockchain?: {
    lowest_tx_id?: string | null;
    display_tx_id?: string | null;
    lowest_confirmed?: boolean;
    display_confirmed?: boolean;
  };
};

export async function computePrice(productId: string, marginPercent = 3.0): Promise<BackendPriceOutput> {
  const url = new URL(`${API_URL}/api/price`);
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId, margin_percent: marginPercent }),
  });
  if (!res.ok) throw new Error(`Failed to compute price: ${res.status}`);
  return res.json();
}

export async function getLatestPrice(productId: string, marginPercent = 3.0): Promise<BackendPriceOutput> {
  const url = new URL(`${API_URL}/api/price/${encodeURIComponent(productId)}`);
  if (marginPercent != null) url.searchParams.set('margin_percent', String(marginPercent));
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Failed to fetch latest price: ${res.status}`);
  return res.json();
}

export function createPriceWebSocket(productId: string): WebSocket {
  const wsBase = API_URL.replace(/^http/i, 'ws');
  const url = `${wsBase}/ws/prices/${encodeURIComponent(productId)}`;
  return new WebSocket(url);
}
