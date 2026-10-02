"""Fetch official UCI ZIP; never accepts a silent source change."""
import argparse, hashlib, json, shutil, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://archive.ics.uci.edu/static/public/352/online+retail.zip'
EXPECTED = 'f5385cbb54bbebf7196389109c6b0621faab0c304e3702548165e71c84aede8b'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cached-zip', type=Path, help='Copy a previously retrieved official ZIP after hash verification')
    parser.add_argument('--retrieved-date', help='Original retrieval date for an explicitly supplied cached artifact')
    args = parser.parse_args()
    raw = ROOT / 'data' / 'raw'; raw.mkdir(exist_ok=True)
    target = raw / 'online-retail.zip'
    if args.cached_zip:
        if not args.retrieved_date:
            parser.error('--cached-zip requires the original --retrieved-date')
        shutil.copyfile(args.cached_zip, target)
        retrieved = args.retrieved_date
        mode = 'verified copy of previously fetched official artifact'
    else:
        request = urllib.request.Request(URL, headers={'User-Agent': 'SalesReportSourceBridge/1.0 public research demo'})
        with urllib.request.urlopen(request, timeout=90) as response, target.open('wb') as out:
            shutil.copyfileobj(response, out)
        retrieved = datetime.now(timezone.utc).date().isoformat()
        mode = 'official HTTPS retrieval'
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    if digest != EXPECTED:
        target.unlink()
        raise SystemExit('Source checksum changed: stop and review the new dataset, do not silently accept it.')
    record = {'dataset': 'UCI Online Retail', 'doi': '10.24432/C5BW33', 'source_url': URL,
              'dataset_page': 'https://archive.ics.uci.edu/dataset/352/online+retail',
              'licence': 'CC BY 4.0', 'licence_url': 'https://creativecommons.org/licenses/by/4.0/',
              'retrieved_date': retrieved, 'verified_utc': datetime.now(timezone.utc).isoformat(),
              'acquisition_mode': mode, 'sha256': digest, 'bytes': target.stat().st_size}
    (ROOT / 'data' / 'provenance.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, indent=2))

if __name__ == '__main__': main()
