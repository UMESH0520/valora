import statistics
import logging
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger('valora.ai.aggregator')


def reject_outliers(values: List[float], m: float = 1.5) -> List[float]:
    """Remove outliers using IQR method"""
    if len(values) < 4:
        return values
    
    try:
        q1 = statistics.quantiles(values, n=4)[0]
        q3 = statistics.quantiles(values, n=4)[2]
        iqr = q3 - q1
        
        if iqr == 0:
            return values
        
        lower = q1 - m * iqr
        upper = q3 + m * iqr
        filtered = [v for v in values if v >= lower and v <= upper]
        
        logger.debug(f"Outlier rejection: {len(values)} -> {len(filtered)} values")
        return filtered
    except Exception as e:
        logger.warning(f"Error in outlier rejection: {e}")
        return values


def calculate_weighted_price(normalized: List[Dict]) -> int:
    """
    Calculate weighted average price based on confidence scores
    Higher confidence sources have more weight
    """
    if not normalized:
        raise ValueError('No data for weighted calculation')
    
    total_weight = 0
    weighted_sum = 0
    
    for item in normalized:
        price = item['paise']
        confidence = item.get('confidence', 0.8)
        
        # Adjust confidence based on age if timestamp available
        if 'scraped_at' in item:
            age_hours = (datetime.utcnow() - item['scraped_at']).total_seconds() / 3600
            # Decay confidence by 5% per hour, max 50% decay
            age_factor = max(0.5, 1.0 - (age_hours * 0.05))
            confidence = confidence * age_factor
        
        weight = confidence
        weighted_sum += price * weight
        total_weight += weight
    
    if total_weight == 0:
        return int(min(item['paise'] for item in normalized))
    
    return int(weighted_sum / total_weight)


def aggregate_prices(normalized: List[Dict]) -> Dict:
    """
    Aggregate prices from multiple sources with advanced algorithms
    
    Strategy:
    1. Remove statistical outliers
    2. Calculate weighted average
    3. Find absolute minimum
    4. Choose the lower of weighted avg and minimum
    5. Identify supporting adapters
    """
    if not normalized:
        raise ValueError('No price data to aggregate')
    
    product_id = normalized[0]['product_id']
    
    # Extract values for outlier detection
    values = [n['paise'] for n in normalized]
    
    # Remove outliers
    filtered_values = reject_outliers(values)
    
    # Filter normalized data to only include non-outliers
    if filtered_values:
        filtered_normalized = [
            n for n in normalized 
            if n['paise'] in filtered_values
        ]
    else:
        filtered_normalized = normalized
        logger.warning(f"All values were outliers for {product_id}, using original data")
    
    # Calculate different price metrics
    absolute_min = min(item['paise'] for item in filtered_normalized)
    weighted_avg = calculate_weighted_price(filtered_normalized)
    
    # Choose final price (conservative approach - use lower value)
    final_price = min(absolute_min, weighted_avg)
    
    # Find supporting adapters (within 1% of final price)
    tolerance = max(1, int(final_price * 0.01))
    support = [
        n['adapter'] for n in filtered_normalized 
        if abs(n['paise'] - final_price) <= tolerance
    ]
    
    logger.info(
        f"Price aggregated for {product_id}: "
        f"min={absolute_min}, weighted={weighted_avg}, final={final_price}, "
        f"sources={len(normalized)}, support={len(support)}"
    )
    
    return {
        'product_id': product_id,
        'final_lowest_paise': int(final_price),
        'absolute_min_paise': int(absolute_min),
        'weighted_avg_paise': int(weighted_avg),
        'support': support,
        'all': normalized,
        'sources_count': len(normalized),
        'outliers_removed': len(normalized) - len(filtered_normalized)
    }
