import statistics
def reject_outliers(values, m=1.5):
    if len(values) < 4:
        return values
    q1 = statistics.quantiles(values, n=4)[0]
    q3 = statistics.quantiles(values, n=4)[2]
    iqr = q3 - q1
    if iqr == 0:
        return values
    lower = q1 - m * iqr
    upper = q3 + m * iqr
    return [v for v in values if v>=lower and v<=upper]
def aggregate_prices(normalized: list):
    if not normalized:
        raise ValueError('no data')
    values = [n['paise'] for n in normalized]
    filtered = reject_outliers(values)
    if not filtered:
        filtered = values
    final = min(filtered)
    support = [n['adapter'] for n in normalized if abs(n['paise'] - final) <= max(1, int(final*0.01))]
    return {'product_id': normalized[0]['product_id'],'final_lowest_paise': int(final),'support': support,'all': normalized}
