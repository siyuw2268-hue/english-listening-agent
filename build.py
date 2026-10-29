#!/usr/bin/env python3
"""Create a public-news English listening session for static GitHub Pages."""
import argparse, datetime as dt, hashlib, html, json, os, re, subprocess, sys, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parent
SITE=ROOT/'site'; GEN=SITE/'generated'; GEN.mkdir(parents=True,exist_ok=True)
STATE=SITE/'state.json'; LATEST=SITE/'latest.json'
FEEDS=['https://feeds.bbci.co.uk/news/technology/rss.xml','https://feeds.bbci.co.uk/news/science_and_environment/rss.xml']
KEYWORDS=['technology','science','space','artificial intelligence','electric','climate','research','innovation','business']
TZ=ZoneInfo('Asia/Shanghai')
def read_json(p,default):
    try:return json.loads(p.read_text(encoding='utf-8'))
    except (OSError,ValueError):return default
def clean(t):return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]*>',' ',t or ''))).strip()
def rss(url):
    req=urllib.request.Request(url,headers={'User-Agent':'EnglishListeningPersonal/6.0'})
    with urllib.request.urlopen(req,timeout=25) as response: raw=response.read(1_000_001)
    if len(raw)>1_000_000:raise ValueError('RSS too large')
    root=ET.fromstring(raw)
    out=[]
    for x in root.findall('.//item')[:40]:
        title=clean(x.findtext('title'));desc=clean(x.findtext('description'));link=clean(x.findtext('link'))
        if title and link.startswith('https://'):
            out.append({'title':title,'desc':desc,'url':link,'feed':url})
    return out
def main():
    p=argparse.ArgumentParser();p.add_argument('--target',choices=['today','tomorrow'],default='today');args=p.parse_args()
    now=dt.datetime.now(TZ); day=(now.date()+dt.timedelta(days=args.target=='tomorrow')).isoformat()
    previous=read_json(LATEST,{})
    if previous.get('date')==day and (SITE/previous.get('audio','')).is_file():
        print('Already built for',day);return
    state=read_json(STATE,{'seen':[],'history':[]})
    entries=[]
    for url in FEEDS:
        try:
            fetched=rss(url);print('RSS',url,len(fetched));entries+=fetched
        except Exception as e:print('RSS WARNING:',str(e),file=sys.stderr)
    seen=set(state.get('seen',[])); ranked=[]
    for i,x in enumerate(entries):
        key=hashlib.sha256(x['title'].lower().encode()).hexdigest()[:16]
        if key in seen:continue
        text=(x['title']+' '+x['desc']).lower()
        score=sum(k in text for k in KEYWORDS)
        ranked.append((score,-i,key,x))
    ranked.sort(reverse=True)
    chosen=ranked[:3]
    if not chosen:raise RuntimeError('No fresh RSS stories; no new lesson or notification will be published')
    lines=['Welcome to your daily English listening briefing.','Here are today’s stories.']
    sources=[]
    for i,(_,_,key,x) in enumerate(chosen,1):
        lines.extend([f'Story number {i}.',x['title'].rstrip('.!?')+'.'])
        desc=x['desc'][:240]
        if len(x['desc'])>240:desc=desc.rsplit(' ',1)[0]
        if desc and desc.lower() not in x['title'].lower():lines.append(desc.rstrip('.!?')+'.')
        sources.append({'title':x['title'],'url':x['url'],'hash':key})
    lines.append('That concludes today’s English listening briefing. Thank you for listening.')
    lesson='\n\n'.join(lines)
    slug=day; txt=GEN/(slug+'.txt');mp3=GEN/(slug+'.mp3');srt=GEN/(slug+'.srt')
    txt.write_text(lesson,encoding='utf-8')
    subprocess.run([sys.executable,'-m','edge_tts','--file',str(txt),'--voice','en-GB-SoniaNeural','--rate=-15%','--write-media',str(mp3),'--write-subtitles',str(srt)],check=True,timeout=360)
    if mp3.stat().st_size<1000 or not srt.read_text(encoding='utf-8').strip():raise RuntimeError('Empty audio or subtitles')
    data={'date':day,'title':'Daily English Briefing · '+day,'audio':'generated/'+slug+'.mp3','srt':'generated/'+slug+'.srt','text':'generated/'+slug+'.txt','sources':sources}
    LATEST.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (GEN/(slug+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    history=[{'date':day,'title':data['title']}]+[h for h in state.get('history',[]) if h.get('date')!=day]
    state={'seen':(list(seen)+[x[2] for x in chosen])[-500:],'history':history[:14]}
    STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Keep 14 days of generated lessons on the public site
    keep={h['date'] for h in state['history']}
    for f in GEN.iterdir():
        if f.name[:10] not in keep and f.suffix in ('.mp3','.srt','.txt','.json'):f.unlink()
    print('Generated',day,'bytes',mp3.stat().st_size)
if __name__=='__main__':main()
