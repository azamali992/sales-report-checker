"""Full workbook evaluation with an independent Decimal + SQLite reference."""
import csv, hashlib, json, sqlite3, time, zipfile
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import pandas as pd
from core import summarize, pence

ROOT = Path(__file__).resolve().parents[1]

def main():
    started = time.perf_counter()
    archive = ROOT / 'data/raw/online-retail.zip'
    if not archive.exists():
        raise SystemExit('First run python scripts/acquire.py. Full source ZIP is not committed.')
    with zipfile.ZipFile(archive) as z:
        names = [n for n in z.namelist() if n.endswith('.xlsx')]
        if len(names) != 1: raise ValueError('Unexpected archive structure')
        frame = pd.read_excel(z.open(names[0]))
    rows, diagnostics = [], Counter()
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE source (id INTEGER PRIMARY KEY, amount INTEGER, q INTEGER, positive INTEGER, missing_d INTEGER, missing_c INTEGER, cancel INTEGER)')
    ref_records = []
    rounded_lines = 0
    for index, record in enumerate(frame.itertuples(index=False, name=None), start=2):
        invoice, stock, description, quantity, date, price, customer, country = record
        if int(quantity) != quantity: raise ValueError('Noninteger quantity unsupported')
        price_string = str(price)
        d_missing = pd.isna(description); c_missing = pd.isna(customer)
        r = {'source_row': index, 'invoice': str(invoice), 'stock': str(stock),
             'description': '' if d_missing else str(description), 'quantity': int(quantity),
             'unit_price': price_string, 'date': date.isoformat(), 'country': str(country),
             'missing_customer': bool(c_missing)}
        rows.append(r)
        diagnostics['negative_quantity'] += quantity < 0
        diagnostics['nonpositive_price'] += price <= 0
        diagnostics['negative_price'] += price < 0
        diagnostics['missing_description'] += d_missing
        diagnostics['missing_customer'] += c_missing
        diagnostics['c_prefix'] += str(invoice).upper().startswith('C')
        diagnostics['subpenny_unit_price'] += Decimal(price_string) * 100 != (Decimal(price_string) * 100).to_integral_value()
        # Independent reference from original cells, never the product's amount or bucket.
        raw_amount = Decimal(str(quantity)) * Decimal(str(price)) * Decimal('100')
        reference = int(raw_amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
        rounded_lines += raw_amount != Decimal(reference)
        if reference != pence(quantity, price_string): raise AssertionError(f'Amount mismatch row {index}')
        ref_records.append((index, reference, int(quantity), int(price > 0), int(d_missing), int(c_missing), int(str(invoice).upper().startswith('C'))))
    conn.executemany('INSERT INTO source VALUES (?,?,?,?,?,?,?)', ref_records)
    reference_total = conn.execute('SELECT sum(amount) FROM source').fetchone()[0]
    policies = {}
    for name, mode, missing_d, missing_c, predicate in [
        ('positive_quantity_baseline', 'positive', False, False, 'positive=1 AND q>0'),
        ('signed_positive_price', 'signed', False, False, 'positive=1 AND q!=0'),
        ('signed_require_descriptions', 'signed', True, False, 'positive=1 AND q!=0 AND missing_d=0'),
        ('signed_known_customers', 'signed', False, True, 'positive=1 AND q!=0 AND missing_c=0'),
        ('positive_require_both', 'positive', True, True, 'positive=1 AND q>0 AND missing_d=0 AND missing_c=0')]:
        summary = summarize(rows, mode, missing_d, missing_c)
        ref_sum, ref_count = conn.execute('SELECT coalesce(sum(amount),0),count(*) FROM source WHERE ' + predicate).fetchone()
        assert summary['raw_pence'] == reference_total
        assert summary['included_pence'] == ref_sum and summary['included_rows'] == ref_count
        summary['sqlite_reference_pence'] = ref_sum
        policies[name] = summary
    # 75 evenly spaced rows in each calendar month + first 8 each natural diagnostic cohort.
    month_groups = {}
    for i, r in enumerate(rows): month_groups.setdefault(r['date'][:7], []).append(i)
    selected = set()
    for indices in month_groups.values():
        for k in range(75): selected.add(indices[k * (len(indices)-1) // 74])
    for predicate in [lambda r:r['quantity']<0, lambda r:Decimal(r['unit_price'])<0,
                      lambda r:Decimal(r['unit_price'])==0, lambda r:not r['description'],
                      lambda r:r['missing_customer'], lambda r:r['invoice'].upper().startswith('C'),
                      lambda r:Decimal(r['unit_price'])*100 != (Decimal(r['unit_price'])*100).to_integral_value()]:
        selected.update([i for i, r in enumerate(rows) if predicate(r)][:8])
    sample = [rows[i] for i in sorted(selected)]
    data = {'dataset': 'UCI Online Retail', 'full_rows': len(rows), 'selection': '75 evenly spaced original row positions per calendar month, plus first 8 rows of each declared diagnostic; deduplicated by source row', 'rows': sample}
    sample_file = ROOT / 'data/sample.json'
    sample_file.write_text(json.dumps(data, separators=(',',':'), ensure_ascii=False) + '\n', encoding='utf-8')
    sample_metrics = {key:summarize(sample, v['policy'], v['exclude_description'], v['exclude_customer']) for key,v in policies.items()}
    report = {'evaluation_date': '2026-10-03', 'source_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'rows': len(rows), 'currency': 'GBP', 'amount_contract': 'quantity × original unit price, each line rounded HALF_UP to nearest penny; sum integer pence',
              'diagnostics_overlap': dict(diagnostics), 'lines_requiring_penny_rounding': rounded_lines,
              'policies': policies, 'sample_rows': len(sample), 'sample_sha256': hashlib.sha256(sample_file.read_bytes()).hexdigest(),
              'sample_policies': sample_metrics, 'independent_reference': 'Decimal from original workbook cells -> SQLite integer SUM with independent SQL predicates',
              'elapsed_seconds': round(time.perf_counter()-started,3),
              'claims': 'Descriptive policy contributions and traceability, not accounting accuracy, matched returns, recovered revenue or measured time savings.'}
    (ROOT / 'eval/results.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    with (ROOT / 'eval/full-policy-results.csv').open('w',newline='',encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['policy','source_rows','included_rows','included_pence','excluded_pence','raw_pence','reference_pence'])
        for name,p in policies.items(): w.writerow([name,p['rows'],p['included_rows'],p['included_pence'],p['excluded_pence'],p['raw_pence'],p['sqlite_reference_pence']])
    print(json.dumps({k:report[k] for k in ('rows','diagnostics_overlap','lines_requiring_penny_rounding','sample_rows','elapsed_seconds')},indent=2))
    print('All 5 declared policies agree with independent SQLite reference; disjoint contribution identities pass.')

if __name__ == '__main__': main()
