# Capture and voiceover script

Use actual 1920×1080 frames from `python scripts/capture.py --serve` or `--url VERIFIED_PUBLIC_URL`. The application has local cached assets, deterministic reset and no login. Figures below are **the 1,004-row display slice**, unless explicitly labelled full corpus. Do not mix these with the complete workbook's totals.

## 60-second Fiverr cut

Caption every step; narration is optional. MP4/H.264, 16:9, under 50 MB. No generated testimonial, customer logo or avatar.

| Time | Actual frame/action | On-screen caption | Optional voiceover |
|---|---|---|---|
| 0–7s | Title card into `01-baseline.png` | “Your sales total changed. Can you show why?” | “A monthly sales total is only useful when you can explain how it was calculated.” |
| 7–17s | Baseline card + policy selector | “Real retail source data. Explicit report rules.” | “This demo uses real public retail data. The positive-quantity view shows fifteen thousand, five hundred and fifty-five pounds in this display sample.” |
| 17–29s | `02-signed-bridge.png`; highlight selected/difference cards | “Include signed quantities → trace the £855.59 difference” | “Switching to signed quantities changes the sample total by eight hundred and fifty-five pounds and fifty-nine pence. The source contributions explain the change.” |
| 29–42s | `03-real-hard-case.png`; zoom warning/selected detail | “Unusual adjustment? Keep it visible for a person.” | “These real negative-price adjustments need interpretation. They stay visible, with their original row and amount, instead of being silently dropped.” |
| 42–53s | `04-source-drilldown.png` then `05-source-linked-export.png` | “Source row IDs. Policy reasons. Downloadable exceptions.” | “Follow each amount to the original source line and export a report with the selected rules and exception reasons.” |
| 53–60s | End card, real value line | “A report you can trace back to its source.” | “I build reporting checks that make differences explainable. Share one source export to define a focused audit.” |

## 90-second portfolio cut

| Time | Frame/action | Caption / timed voiceover |
|---|---|---|
| 0–10s | Hero + baseline | “Source Bridge: policy-aware source traceability on real UCI Online Retail data.” |
| 10–23s | Toggle actual policy; show difference | “The interactive slice contains 1,004 real source rows. Browser arithmetic recomputes the selection; it does not use stored answer totals.” |
| 23–38s | Contribution bridge | “Every line enters one bucket. Disjoint contributions enforce included plus excluded equals the raw signed source amount.” |
| 38–53s | Natural negative-price hard case | “The corpus contains negative-price bad-debt adjustments. Their accounting treatment is unsupported; source amounts stay visible in the excluded contribution.” |
| 53–65s | Source detail and exception CSV | “Original workbook row IDs and policy flags make the CSV auditable. Customer identifier values are omitted.” |
| 65–78s | `06-full-corpus-evidence.png` | “All 541,909 workbook lines were evaluated. Five policies match an independent Decimal-to-SQLite arithmetic reference. Policy differences are descriptive, not accounting accuracy.” |
| 78–90s | Final bridge + repo evidence | “Python/browser parity, safe integer-pence totals, automated headless exports and CI. No paid API, customer uploads or financial-advice claim.” |

No talking head or microphone is necessary to explain this workflow. A genuine short seller introduction/voiceover can be recorded later; the generated product cut must not pretend to contain the seller's voice. No quantified trust-lift claim is made.
