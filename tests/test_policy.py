import json, random, sys, unittest
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from core import pence, classify, summarize

def row(**overrides):
    result={'source_row':2,'invoice':'123','stock':'TEST','description':'Synthetic unit-test fixture',
            'quantity':1,'unit_price':'2.50','missing_customer':False};result.update(overrides);return result

class PolicyTests(unittest.TestCase):
    def test_round_line_once_half_away_zero(self):
        self.assertEqual(pence(3,'0.005'),2)
        self.assertEqual(pence(-3,'0.005'),-2)
        self.assertEqual(pence(1,'0.001'),0)
        self.assertEqual(pence(6,'2.55'),1530)
    def test_overlap_precedence_preserves_disjoint_contributions(self):
        rows=[row(quantity=-2,unit_price='-3.50',description='',missing_customer=True),
              row(quantity=-3,invoice='C9',description='',missing_customer=True),
              row(quantity=-1,invoice='C8',missing_customer=True),row(quantity=-1,invoice='C7'),row()]
        summary=summarize(rows,'positive',True,True)
        self.assertEqual(set(summary['groups']),{'negative_price','missing_description','missing_customer','c_prefix_negative','included'})
        self.assertEqual(sum(g['rows'] for g in summary['groups'].values()),len(rows))
        self.assertEqual(summary['raw_pence'],summary['included_pence']+summary['excluded_pence'])
    def test_missing_customer_is_optional_not_invalid_sale(self):
        r=row(missing_customer=True)
        self.assertEqual(classify(r,'signed'),'included')
        self.assertEqual(classify(r,'signed',False,True),'missing_customer')
    def test_c_prefix_is_not_negative_quantity(self):
        self.assertEqual(classify(row(invoice='C1',quantity=2),'positive'),'included')
        self.assertEqual(classify(row(invoice='A1',quantity=-2),'positive'),'other_negative')
    def test_random_arithmetic_against_decimal(self):
        rng=random.Random(20261003)
        for _ in range(1000):
            q=rng.randint(-10000,10000);price=str(Decimal(rng.randint(-50000,50000))/1000)
            reference=int((Decimal(q)*Decimal(price)*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
            self.assertEqual(pence(q,price),reference)
    def test_real_sample_matches_committed_results_all_five_policies(self):
        rows=json.loads((ROOT/'data/sample.json').read_text(encoding='utf-8'))['rows']
        report=json.loads((ROOT/'eval/results.json').read_text(encoding='utf-8'))
        self.assertEqual(len(rows),1004)
        self.assertEqual(sum(Decimal(r['unit_price'])<0 for r in rows),2)
        self.assertTrue(all('customer_id' not in r for r in rows))
        for policy in report['sample_policies'].values():
            actual=summarize(rows,policy['policy'],policy['exclude_description'],policy['exclude_customer'])
            self.assertEqual(actual,policy)

if __name__=='__main__':unittest.main()
