# Data provenance and amount contract

## Public source and rights

**Dataset:** UCI Online Retail, Daqing Chen (2015), DOI [10.24432/C5BW33](https://doi.org/10.24432/C5BW33). [Primary publisher page](https://archive.ics.uci.edu/dataset/352/online+retail) declares **Creative Commons Attribution 4.0 International**. [Licence](https://creativecommons.org/licenses/by/4.0/) permits commercial reuse with attribution and modification notices. The original publisher release is the licence evidence; a mirror's label is not used.

**Official download:** https://archive.ics.uci.edu/static/public/352/online+retail.zip

**Original retrieval date:** 2 October 2026. The source was retrieved for the independent pre-build review and copied after SHA verification during this build on 3 October 2026, Asia/Karachi (UTC timestamp in `data/provenance.json`). Reuse of that actual downloaded artifact is explicitly recorded rather than falsely called a new network retrieval. Running `scripts/acquire.py` without cache arguments performs a fresh public-source transfer and records its actual UTC retrieval date.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Official ZIP | 23,715,478 | `f5385cbb54bbebf7196389109c6b0621faab0c304e3702548165e71c84aede8b` |
| Committed `data/sample.json` | See actual file | `d4ae2581560ded92d7312b486a65a4c782196b5eaff9bcd26fd57b03b4fd7173` |

The ZIP and original workbook are ignored. The attributed small sample is committed so the demo runs offline. Dataset attribution: **Contains Online Retail data © Daqing Chen, made available by UCI under CC BY 4.0; modified representation/sample and derived amounts.** The MIT software licence does not relicense data. No publisher endorsement is implied.

## Grain, source IDs and transformations

One row is one original workbook line, not necessarily a unique sale, invoice or matched return. `source_row` is the actual Excel row number, starting at 2 after the header. Preserve invoice, stock code, original description, integer quantity, original unit-price decimal string, ISO source timestamp and country. Customer identifier values are removed from the public sample; `missing_customer` only records whether the original cell was missing. Invoice/item identifiers relate to this historical open corpus, never to a supplied client.

The primary corpus contains **541,909 lines** and **13 calendar months**, December 2010–December 2011. Actual workbook missing cells contradict the publisher's “no missing values” metadata: 1,454 descriptions and 135,080 customer references are missing. Record observations rather than correcting them by guess.

No invented records are used in the primary demo/evaluation. Generated rows in `tests/test_policy.py` are clearly named synthetic unit-test fixtures and are used only to test rounding/precedence, never to make data-quality or business-result claims.

## Frozen deterministic display selection

For each of the 13 calendar months, take **75 evenly spaced original positions**, using index `k * (month_row_count - 1) // 74`, `k=0..74`. Add the first eight original rows of each diagnostic cohort: negative quantity, negative price, zero price, missing description, missing customer reference, C-prefix invoice and subpenny unit price. Deduplicate by original source row and sort by original order. This produces **1,004 rows**.

Top-up selection ensures real messy cases can be inspected; it is **not representative sampling for prevalence or totals**. The rare negative-price records dominate raw sample value. The entire 541,909-row evaluation is separate and none of the UI slice's rates/totals is extrapolated. No filter selects rows because a proposed policy produces a favorable result.

## Amount policy and disjoint exclusions

For each line, calculate `Decimal(original_quantity) × Decimal(original_unit_price)`. Round the **complete line once** to GBP pennies with ROUND_HALF_UP (half away from zero); sum integer pence. Four real prices are `0.001`, and those line amounts round to zero under this contract. Floating-point epsilon heuristics are not used. Browser decimal-string → BigInt arithmetic reproduces Python Decimal.

Assign each line to exactly one bucket in this precedence:

1. Negative price: retained in raw total, excluded as an unsupported adjustment.
2. Zero price: retained as zero contribution, excluded from priced report.
3. Zero quantity: exclude (none found in this corpus).
4. Missing description, **only if** that policy is selected.
5. Missing customer reference, **only if** that policy is selected.
6. Negative quantity, **only under** positive-quantity policy; distinguish C-prefix from other negative quantities.
7. Included: all remaining lines.

Diagnostic flags may overlap; these bridge contributions do not. C-prefix is not synonymous with negative quantity; no return matching is attempted. A negative unit price is not a negative quantity. Missing customer references are not automatically invalid revenue.

`raw signed amount = sum(included contributions) + sum(excluded contributions)` is checked for every policy. A separate reference derives Decimal amounts from the original cells and uses independent SQLite WHERE predicates and integer SUM; it does not call the product's aggregator or classification function. Five policy checks and full/source-sample results are committed in `eval/results.json`.

The illustrative before/after is an unexplained filter total → an explicit, source-linked policy bridge. Policy differences are **descriptive**, not error rates, recovered money, financial advice or evidence of the correct accounting treatment.

## Reproduce

```sh
python -m pip install -r requirements.txt
python scripts/acquire.py
python scripts/evaluate.py
```

No API key or environment variable is required. `acquire.py` stops on an unexpected hash so a changed source cannot silently invalidate measured claims. A previously fetched original ZIP may be explicitly copied with `--cached-zip PATH --retrieved-date YYYY-MM-DD`; that operation is separately labelled in provenance.
