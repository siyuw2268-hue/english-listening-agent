#!/usr/bin/env python3
"""Send iPhone ntfy attachment + link after checking daily public lesson."""
import datetime as dt, json, os, sys, urllib.request, urllib.parse
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parent
SITE=ROOT/'site'
def main():
    topic=os.environ.get('NTFY_TOPIC','').strip()
    if len(topic)<16 or not all(c.isalnum() or c in '_-' for c in topic):raise RuntimeError('NTFY_TOPIC secret missing/invalid')
    lesson=json.loads((SITE/'latest.json').read_text(encoding='utf-8'))
    today=dt.datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat()
    if lesson['date']!=today:raise RuntimeError('Latest lesson is '+lesson['date']+', not '+today+'; refusing stale push')
    base=os.environ['PAGES_URL'].rstrip('/')+'/'
    link=base+'?listen='+urllib.parse.quote(today)
    audio=SITE/lesson['audio']
    if not audio.is_file():raise RuntimeError('Audio not found')
    req=urllib.request.Request('https://ntfy.sh/'+urllib.parse.quote(topic,safe=''),data=audio.read_bytes(),method='POST',headers={
        'Title':'Daily English Listening · '+today,'Filename':'Daily_English_'+today+'.mp3',
        'Content-Type':'audio/mpeg','Click':link,'Tags':'headphones'})
    with urllib.request.urlopen(req,timeout=60) as r:print('ntfy:',r.status,'player:',link)
if __name__=='__main__':main()
