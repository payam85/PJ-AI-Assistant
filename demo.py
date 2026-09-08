"""Offline demonstration: Python standard library only, no API or personal data."""
import argparse
import html
import json
from pathlib import Path

SAMPLES = {
    'Candidate': 'Alex Example — fictional graduate with Python coursework and volunteer digital support experience. Work authorisation: not supplied.',
    'Job analysis': 'Fictional Service Desk Trainee role. Evidence: patient communication and basic troubleshooting. Gaps: no verified commercial ticketing experience. Job Fit score unavailable until role requirements and eligibility are confirmed.',
    'LinkedIn draft': 'A useful support handover answers three questions: what happened, what has already been tried, and what should happen next. Clear notes help the next person continue with confidence. What makes a handover useful in your team? #ITSupport #DigitalSupport #Teamwork',
    'Cover letter excerpt': 'Dear Hiring Team, I am interested in your trainee support role. My coursework and volunteer experience have helped me practise explaining technical steps clearly. I would welcome the opportunity to develop these skills in a service desk team.',
    'Application tracker': 'Example Company — Service Desk Trainee — Saved, not applied. No message or application has been sent.',
    'Usage': 'Zero API calls. These are fixed illustrative examples, not AI-generated results. Repeated real requests reuse stored results when their inputs match.',
}

def render():
    cards = ''.join('<details open><summary>'+html.escape(k)+'</summary><p>'+html.escape(v)+'</p></details>' for k,v in SAMPLES.items())
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>PJ Career Assistant · Demo</title>
    <style>body{font:17px/1.65 system-ui;background:#f2f5ef;color:#173e32;max-width:950px;margin:50px auto;padding:24px}h1{font-size:42px;line-height:1.2}details{background:white;padding:22px;border:1px solid #d8e2d5;border-radius:12px;margin:16px 0}summary{font-weight:700;cursor:pointer}.badge{color:#675323;background:#fff0c9;padding:12px;border-radius:8px}footer{font-size:14px}</style>
    <h1>PJ Career Assistant</h1><p class="badge">OFFLINE DEMO · Fictional sample data · No API calls</p><p>Explore the workflow: candidate evidence, job analysis, draft content and application tracking. Click a section to expand or collapse it.</p>'''+cards+'<footer>To generate real drafts, follow the README installation instructions and use your own API key. This preview does not send, search or publish anything.</footer></html>'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent/'private'/'demo.html')
    parser.add_argument('--json',action='store_true')
    args=parser.parse_args()
    if args.json:
        print(json.dumps(SAMPLES,indent=2)); return
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(render(),encoding='utf-8')
    print('Offline demo saved to:',args.output.resolve())
    print('Open this HTML file in a browser. No server, API key or dependencies are required.')

if __name__=='__main__': main()
