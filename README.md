# Source Bridge — sales report checker

A retail reporting analyst needs a monthly total that ties back to the export. Positive-quantity filters, negative adjustments and missing references can produce different numbers. Source Bridge shows the contribution of every included or excluded line, so the analyst can explain a total before publishing it.

This is a working, read-only engineering demo on **real UCI Online Retail data**, with a visible unsupported case. It makes no accounting, tax, fraud or recovered-revenue claim.

## What you can do

- Compare a positive-quantity baseline with a declared signed-quantity policy.
- Choose a calendar month and explicit missing-description/customer-reference rules.
- See a disjoint contribution bridge: **included + excluded = raw source total**.
- Follow any bucket to original workbook row numbers and source fields.
- Inspect actual negative-price “Adjust bad debt” records; their interpretation is left to a person.
- Download report and exception CSVs containing row IDs, original values, integer-pence amounts and the selected policy.

The browser calculates selected inputs using decimal-string/BigInt line arithmetic. The interface does not play an answer animation or send data to an API. Public exploration uses an attributed, fixed **1,004-row** sample. Customer identifiers are omitted; only their original presence/missingness is retained.

## Demo

**[Open the live demo](https://azamali992.github.io/sales-report-checker/).** Published on free GitHub Pages and checked from a fresh headless browser on 3 October 2026: 16 browser/Python policy comparisons, a real negative-price case, a 257-row exception export and reset all passed, with zero browser errors. This is a fixed public-data engineering demonstration.

## 60-second local run

With Python 3.12+, no install is needed to explore the committed sample:

```sh
python scripts/run.py --reset
```

Open **http://127.0.0.1:8762/**. There is no login. Choose “Signed quantities”, inspect a negative-price record and download the exception CSV. Click **Reset demo** to restore the exact clean view. The server and browser do not persist changes; refresh also resets. Stop the server with Ctrl+C.

All runtime JS/CSS/data is local. No CDN, remote font or model download is required for the default demo.

## Measured results on the real dataset

Evaluated **3 October 2026, Asia/Karachi**. The complete original workbook contains **541,909 source lines**. Five named policies agreed with an independent Decimal-from-original-cells → SQLite integer-SUM reference. Every disjoint included/excluded identity passed. The elapsed **100.612 seconds** is one full read/evaluation run on the build machine, including workbook loading; it is not a benchmark against a human or a production SLA.

| Declared full-corpus policy | Included lines | Included amount | Excluded contribution | Raw signed source amount |
|---|---:|---:|---:|---:|
| Positive quantity, positive price baseline | 530,104 | £10,666,684.54 | −£918,936.61 | £9,747,747.93 |
| Signed quantities, positive price | 539,392 | £9,769,872.05 | −£22,124.12 | £9,747,747.93 |
| Signed, positive price, require description | 539,392 | £9,769,872.05 | −£22,124.12 | £9,747,747.93 |
| Signed, positive price, require customer reference | 406,789 | £8,300,065.81 | £1,447,682.12 | £9,747,747.93 |
| Positive quantities, positive price, require both fields | 397,884 | £8,911,407.90 | £836,340.03 | £9,747,747.93 |

The signed positive-price policy changes the baseline by **−£896,812.49**. This is a difference between explicit aggregation policies on historical public data. There is no independent accounting ground truth establishing either policy as a company's correct revenue.

The functional before/after is a total from a named simple filter → that total plus a traceable source contribution and explicit exclusion reason for **all 541,909 lines**. The baseline is illustrative, not evidence that a real buyer previously made that mistake.

Diagnostic counts **overlap**: 10,624 negative quantities, 9,288 C-prefix rows, 2,517 nonpositive prices, 1,454 missing descriptions and 135,080 missing customer references. Only **2** prices are negative. Four unit prices have subpenny precision; the declared amount rule rounds each complete quantity × price line once, HALF_UP to a penny. Do not confuse negative quantities with C-prefixes, or diagnostic counts with disjoint bridge buckets.

The browser's **1,004-row** slice has different totals: baseline **£15,555.28**, signed positive-price policy **£14,699.69**, difference **−£855.59**, raw signed amount **−£7,424.43**. It intentionally contains both rare negative-price records (combined **−£22,124.12**) for review. It is not a random/prevalence sample; its totals and exception rates must not be extrapolated.

[Raw results](eval/results.json) · [Full policy CSV](eval/full-policy-results.csv) · [Data provenance](DATA.md).

## Reproduce the evaluation and checks

```sh
python -m pip install -r requirements.txt
python scripts/acquire.py
python scripts/evaluate.py
python -m unittest discover -s tests -v
node tests/test_engine.cjs
python -m playwright install chromium
python scripts/capture.py --serve
```

Acquisition fetches the official ZIP and requires the recorded SHA-256. The complete ZIP is **not committed**. Evaluation regenerates the sample, policy CSV and detailed results. It may take a few minutes and extra memory to read Excel. The default application never needs this full transfer.

`capture.py --serve` opens the real UI headlessly at 1920×1080, resets it, compares Python/browser totals for 16 policy/month combinations, inspects the real hard case, clicks a source row, downloads and checks the actual CSV, and saves screenshots, WebM and `capture/verification.json`. For an already running or published demo:

```sh
python scripts/capture.py --url https://YOUR-VERIFIED-DEMO/ --output capture-public
```

Six Python tests include overlapping-exception precedence, random independent decimal arithmetic, real-sample results, optional missing-reference treatment and C-prefix/negative-quantity distinctions. JS tests exercise rounding and safe-number bounds. CI runs these checks plus the headless flow. Workflow execution on a remote host is unverified until it actually runs.

## Honest limitations

- The dataset dates to December 2010–December 2011. It is one UK retail export, not current company activity or a bank ledger.
- This is single-export source traceability, **not paired reconciliation**, return matching, financial advice, a trained AI model or an ERP integration.
- Negative-price adjustments remain unsupported for automatic interpretation. They are kept visible, excluded from the selected positive-price report and exported with their reason.
- “Missing customer reference” is an optional report policy, not proof that a sale is invalid. Missing description has no effect under the tested positive-price corpus policy because those rows are already excluded by price precedence.
- Line rounding is a declared demonstration contract. A buyer may require invoice-level rounding, tax rules or source-decimal precision; those must be specified and tested separately.
- The static public demo accepts no customer uploads and performs no external writes. Downloading a CSV is not server-side approval/authorization.
- No measured analyst-time, error-rate, money-savings, accuracy-against-accounting-truth or production throughput claim is made.
- A production connector, scheduled refresh, access controls or new source schema is a separately scoped build. Hosting the demo does not promise zero operating cost for those services.

## Data and licences

Contains **UCI Online Retail**, Daqing Chen (2015), DOI [10.24432/C5BW33](https://doi.org/10.24432/C5BW33), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This demo changes representation, derives line-rounded policy contributions, takes a declared sample and removes customer identifier values. No endorsement is implied. Original retrieval: **2 October 2026**; cached artifact hash verified during this build. [DATA.md](DATA.md) records source, hashes, preprocessing and sampling.

Software is MIT licensed; dataset contents retain CC BY 4.0 obligations. No client data, logos, documents or operational figures are included.

## API keys and environment variables

**No API key or environment variable is required for the default demo.** There is no optional paid API path. The acquisition script uses the public UCI HTTPS download without credentials.

## Demo capture

See [VIDEO-SCRIPT.md](VIDEO-SCRIPT.md) for a 60-second buyer cut and 90-second technical cut. Screens and the recorded flow come from the actual application; metrics must stay matched to the selected sample/corpus.
