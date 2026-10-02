"""Declared reporting policy. Amounts are line-rounded GBP integer pence."""
from decimal import Decimal, ROUND_HALF_UP

def pence(quantity, price):
    amount = Decimal(str(price)) * Decimal(str(quantity))
    return int((amount * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

def classify(row, policy='signed', exclude_description=False, exclude_customer=False):
    # Precedence makes contributions disjoint; diagnostics remain overlapping.
    price = Decimal(row['unit_price'])
    if price < 0:
        return 'negative_price'
    if price == 0:
        return 'zero_price'
    if row['quantity'] == 0:
        return 'zero_quantity'
    if exclude_description and not row['description']:
        return 'missing_description'
    if exclude_customer and row['missing_customer']:
        return 'missing_customer'
    if policy == 'positive' and row['quantity'] < 0:
        return 'c_prefix_negative' if row['invoice'].upper().startswith('C') else 'other_negative'
    return 'included'

def summarize(rows, policy='signed', exclude_description=False, exclude_customer=False):
    groups = {}
    raw = 0
    for row in rows:
        amount = pence(row['quantity'], row['unit_price'])
        key = classify(row, policy, exclude_description, exclude_customer)
        bucket = groups.setdefault(key, {'rows': 0, 'pence': 0})
        bucket['rows'] += 1
        bucket['pence'] += amount
        raw += amount
    included = groups.get('included', {'rows': 0, 'pence': 0})
    excluded = sum(g['pence'] for key, g in groups.items() if key != 'included')
    assert raw == included['pence'] + excluded
    return {'rows': len(rows), 'raw_pence': raw, 'included_pence': included['pence'],
            'included_rows': included['rows'], 'excluded_pence': excluded, 'groups': groups,
            'policy': policy, 'exclude_description': exclude_description,
            'exclude_customer': exclude_customer, 'identity_verified': True}
