import random
import re
from typing import Optional, Tuple, List, Dict
from aiohttp import ClientTimeout

# A small pool of realistic desktop user agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
]


def build_headers(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-IN,en-US;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    }
    if extra:
        headers.update(extra)
    return headers


async def http_get_text(session, url: str, params: Optional[Dict[str, str]] = None, headers: Optional[Dict[str, str]] = None, total_timeout: float = 12.0) -> Optional[str]:
    # Try up to 2 attempts with varied UA
    for attempt in range(2):
        try:
            hdrs = build_headers(headers)
            timeout = ClientTimeout(total=total_timeout)
            async with session.get(url, params=params, headers=hdrs, timeout=timeout) as resp:
                if resp.status >= 400:
                    continue
                return await resp.text()
        except Exception:
            if attempt == 1:
                return None
    return None


def extract_rupee_candidates(text: str) -> List[float]:
    if not text:
        return []
    # Common patterns: ₹ 1,999 ; Rs. 1,999 ; 1999
    patterns = [
        r"[₹Rs\.]\s*([0-9]{1,3}(?:[, ]?[0-9]{2,3})+(?:\.[0-9]{1,2})?)",
        r"₹\s*([0-9][0-9,]*\.?[0-9]*)",
        r"Rs\.?\s*([0-9][0-9,]*\.?[0-9]*)",
    ]
    vals: List[float] = []
    for pat in patterns:
        for m in re.finditer(pat, text):
            try:
                vals.append(float(m.group(1).replace(',', '').replace(' ', '')))
            except Exception:
                continue
    # Deduplicate
    uniq = []
    seen = set()
    for v in vals:
        if v not in seen:
            seen.add(v)
            uniq.append(v)
    # Filter to plausible INR ranges
    uniq = [v for v in uniq if 50 <= v <= 2000000]
    return uniq


def pick_price_from_candidates(cands: List[float]) -> Optional[float]:
    if not cands:
        return None
    # Heuristic: choose median of lower half to avoid outliers
    c = sorted(cands)
    half = c[: max(1, len(c)//2)]
    return half[len(half)//2]
