"""Drive actual local or public UI, verify export/parity, and capture 1080p frames."""
import argparse, csv, json, subprocess, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
from core import summarize

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8762/')
    parser.add_argument('--output',type=Path,default=ROOT/'capture');parser.add_argument('--serve',action='store_true')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    server=None
    if args.serve:
        server=subprocess.Popen([sys.executable,str(ROOT/'scripts/run.py'),'--reset'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        time.sleep(.7)
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            context=browser.new_context(viewport={'width':1920,'height':1080},device_scale_factor=1,
                accept_downloads=True,record_video_dir=str(args.output/'recording'),record_video_size={'width':1920,'height':1080})
            page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(args.url,wait_until='networkidle');page.wait_for_function('window.demoReady === true')
            page.locator('#reset').click();page.screenshot(path=str(args.output/'01-baseline.png'))
            data=json.loads((ROOT/'data/sample.json').read_text(encoding='utf-8'))['rows']
            state=page.evaluate('window.demoState')
            expected=summarize(data,'positive')
            assert state['summary']['includedPence']==expected['included_pence']
            assert state['summary']['rawPence']==expected['raw_pence']
            page.locator('#policy').select_option('signed');page.screenshot(path=str(args.output/'02-signed-bridge.png'))
            state=page.evaluate('window.demoState');expected=summarize(data,'signed')
            assert state['summary']['includedPence']==expected['included_pence']
            page.locator('#show-negative').click();page.screenshot(path=str(args.output/'03-real-hard-case.png'))
            assert 'Adjust bad debt' in page.locator('#selected-detail').inner_text()
            page.locator('#source-rows tr').first.click()
            page.locator('#source-rows').scroll_into_view_if_needed();page.screenshot(path=str(args.output/'04-source-drilldown.png'))
            page.locator('#exclude-description').check();page.locator('#exclude-customer').check()
            state=page.evaluate('window.demoState');expected=summarize(data,'signed',True,True)
            assert state['summary']['includedPence']==expected['included_pence']
            with page.expect_download() as event:page.locator('#export-exceptions').click()
            download=event.value;download.save_as(args.output/'exceptions.csv')
            with (args.output/'exceptions.csv').open(encoding='utf-8',newline='') as f: exported=list(csv.DictReader(f))
            assert len(exported)==expected['rows']-expected['included_rows']
            assert sum(int(r['amount_pence']) for r in exported)==expected['excluded_pence']
            page.screenshot(path=str(args.output/'05-source-linked-export.png'))
            page.locator('.evidence').scroll_into_view_if_needed()
            page.screenshot(path=str(args.output/'06-full-corpus-evidence.png'))
            # Month filters and policy combinations exercise real browser arithmetic, not cached totals.
            parity=[]
            for month in ['all','2010-12','2011-08','2011-12']:
                page.locator('#month').select_option(month)
                for mode,missing_d,missing_c in [('positive',False,False),('signed',False,False),('signed',True,True),('positive',True,False)]:
                    page.locator('#policy').select_option(mode);page.locator('#exclude-description').set_checked(missing_d);page.locator('#exclude-customer').set_checked(missing_c)
                    actual=page.evaluate('window.demoState.summary');rows=data if month=='all' else [r for r in data if r['date'].startswith(month)]
                    exp=summarize(rows,mode,missing_d,missing_c)
                    assert actual['rawPence']==exp['raw_pence'] and actual['includedPence']==exp['included_pence'] and actual['excludedPence']==exp['excluded_pence']
                    assert actual['identityVerified'];parity.append({'month':month,'mode':mode,'exclude_description':missing_d,'exclude_customer':missing_c,'rows':len(rows),'passed':True})
            page.locator('#reset').click();assert page.locator('#policy').input_value()=='positive';assert page.evaluate('window.demoState.summary.rows')==len(data)
            assert not errors,errors
            context.close();browser.close()
            (args.output/'verification.json').write_text(json.dumps({'url':args.url,'viewport':'1920x1080','browser_python_policy_checks':parity,'export_rows':len(exported),'export_pence':expected['excluded_pence'],'console_errors':errors,'reset_verified':True},indent=2)+'\n',encoding='utf-8')
            print(f'Passed 16 browser/Python policy cases, actual CSV export ({len(exported)} rows), natural hard case and reset. Frames: {args.output}')
    finally:
        if server:server.terminate();server.wait(timeout=5)

if __name__=='__main__':main()
