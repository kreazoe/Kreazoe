"""Safety regression checks: registry fidelity, scoped roles, exclusion, static paths."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import json, re, hashlib
from build_credits import render, render_sections
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'data/credits-registry.v1.json').read_text()); records=r['records']; page=(ROOT/'index.html').read_text()
expected_tracks=['Abantu','Lessons','Bring It Back','I Need Love','Isibhamu','Thula','Bet','My People','Icebo','Life','Amen','Njani','Messed Up','Rockstar','Been Through It','Please Understand','Roll','Baddest In The Game','Prayer','Smogolo','Winning','Andisababoni','Lollipop','Sucker Free','Right Back','Movie','Get Money','Umona','Questions','Every Morning','Is It True','Phinde','MULTIPLE_TRACKS','Iskhwele']
assert [x['track'] for x in records]==expected_tracks
assert [x['evidence_tier'] for x in records]==['A']*17+['B']+['C']*16
assert sum(x['portfolio_status']=='FEATURED_VERIFIED' for x in records)==10
for i,x in enumerate(records):
 expected_public=(['Producer','StudioProducer','NonLyricAuthor'] if i in (0,1,2,3,12) else ['Composer','Producer'] if i==10 else ['Producer']) if i<18 else []
 expected_first=['Recording'] if i<5 or i==32 else ['Producer','Recording'] if 18<=i<32 else ['Producer'] if i==33 else []
 assert x['public_roles']==expected_public,(i,'public role mutation')
 assert x['first_hand_roles']==expected_first,(i,'first-hand role mutation')
 assert x['year'] is None if i in (18,19,24,25,26,32,33) else isinstance(x['year'],int)
required={'artist','featured_artists','track','project','year','public_roles','first_hand_roles','credited_as','collaborators','evidence_tier','evidence_sources','portfolio_status','notes'}
assert all(set(x)==required for x in records)
assert records[4]['collaborators']==['Mfanafuthi Ruff Nkosi']
assert records[8]['collaborators']==['Pheto Mbulelo Mabena']
assert records[10]['credited_as']=='Bheki Christopher Thobela / Christopher Thobela'
assert records[32]['project']=='Busisiwe' and records[32]['track']=='MULTIPLE_TRACKS'
assert all(part in page for part in render_sections(r)), 'Generated HTML is stale'
class Audit(HTMLParser):
 def __init__(self):
  super().__init__();self.ids=[];self.urls=[];self.cards=[];self.feed(page)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  self.urls.extend(a[k] for k in ('href','src') if k in a)
  if tag=='details' and 'registry-credit' in a.get('class',''):self.cards.append(a)
a=Audit();assert len(a.ids)==len(set(a.ids));assert len(a.cards)==34
for attrs,rec in zip(a.cards,records):
 assert json.loads(attrs['data-public'])==rec['public_roles']
 assert json.loads(attrs['data-first-hand'])==rec['first_hand_roles']
for url in a.urls:
 if url.startswith('#'):assert url[1:] in a.ids,url
 elif not urlparse(url).scheme:assert (ROOT/url).is_file(),url
 else:assert urlparse(url).scheme in ('https','mailto','tel'),url
for i,rec in enumerate(records,1):
 card=re.search(rf'<details id="credit-{i:03}".*?</details>',page,re.S).group()
 assert ('class="evidence-label"' in card)==bool(rec['public_roles'])
 assert ('first-hand-role-block' in card)==bool(rec['first_hand_roles'])
 if rec['evidence_tier']=='B':assert 'Publicly documented' in card and 'Public metadata' not in card
 if rec['evidence_tier']=='C':assert not re.search('verified|metadata',card,re.I)
 assert len(re.findall('class="role-block public-role-block"',card))==bool(rec['public_roles'])
 for source in rec['evidence_sources']:assert source['url'] in card
assert 'Co-production with Mfanafuthi Ruff Nkosi.' in page
assert 'Co-production with Pheto Mbulelo Mabena.' in page
assert 'not a claim of sole production' in page
assert not re.search(r'work-title">DIY 2[<\s]',page)
assert 'dispute' not in page.lower() and 'conflicting' not in page.lower()
assert 'On My Mama' not in page,'Unregistered V3 credit leaked into V4'
assert 'Recording on most songs on Busisiwe' in page
# Rendering a future excluded entry must never publish it.
copy=json.loads(json.dumps(r));copy['records'][0]['portfolio_status']='EXCLUDED'
assert 'id="credit-001"' not in render(copy)
# Existing structured data remains parseable.
json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',page,re.S).group(1))
print('PASS: 34 frozen records; exact role arrays; 17 A / 1 B / 16 C; mixed-role separation; co-production; exclusion; evidence links; anchors; assets; JSON-LD.')
