"""Independently audit rendered role text, badge scope and evidence against JSON.
No dependency on the renderer. Exit nonzero for any mismatched or unscoped role.
"""
from html.parser import HTMLParser
from pathlib import Path
import argparse, json, hashlib
ROOT=Path(__file__).resolve().parents[1]
class Node:
 def __init__(self,tag='',attrs=(),parent=None):self.tag=tag;self.attrs=dict(attrs);self.parent=parent;self.children=[]
 def text(self):return ''.join(c if isinstance(c,str) else c.text() for c in self.children)
 def has(self,cls):return cls in self.attrs.get('class','').split()
 def find(self,predicate):
  result=[]
  for c in self.children:
   if isinstance(c,Node):
    if predicate(c):result.append(c)
    result.extend(c.find(predicate))
  return result
class Tree(HTMLParser):
 def __init__(self,source):
  super().__init__(convert_charrefs=True);self.root=Node();self.stack=[self.root];self.feed(source)
 def handle_starttag(self,tag,attrs):
  n=Node(tag,attrs,self.stack[-1]);self.stack[-1].children.append(n)
  if tag not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'):self.stack.append(n)
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==tag:del self.stack[i:];break
 def handle_data(self,data):self.stack[-1].children.append(data)
def audit(reg,source):
 tree=Tree(source).root
 cards=tree.find(lambda n:n.has('registry-credit'))
 expected={f'credit-{i:03}':r for i,r in enumerate(reg['records'],1) if r['portfolio_status']!='EXCLUDED'}
 assert len(cards)==len(expected),'Unexpected or missing credit cards'
 assert {c.attrs['id'] for c in cards}==set(expected),'Credit identity mismatch'
 selections=tree.find(lambda n:n.has('selection-card'))
 featured={key:r for key,r in expected.items() if r['portfolio_status']=='FEATURED_VERIFIED'}
 assert len(selections)==len(featured),'Featured selection count mismatch'
 for item in selections:
  key=item.attrs['data-feature-ref']; assert key in featured and item.attrs['href']=='#'+key
  assert item.find(lambda n:n.tag=='h3')[0].text()==featured[key]['track']
  assert not item.find(lambda n:n.has('evidence-label') or n.has('credit-roles')),'Selection assigns track-wide badge or roles'
 total_roles=0;total_badges=0;rows=[]
 for card in cards:
  rec=expected[card.attrs['id']];tier=rec['evidence_tier']
  assert card.attrs['data-artist']==rec['artist'] and card.attrs['data-tier']==tier
  public=card.find(lambda n:n.has('public-role-block'))
  first=card.find(lambda n:n.has('first-hand-role-block'))
  assert len(public)==bool(rec['public_roles']),'Public block mismatch'
  assert len(first)==bool(rec['first_hand_roles']),'Studio block mismatch'
  assert len(card.find(lambda n:n.has('role-block')))==len(public)+len(first),'Unscoped role block'
  row={'id':card.attrs['id'],'artist':rec['artist'],'track':rec['track'],'tier':tier}
  scoped_badges=0
  for blocks,field in ((public,'public_roles'),(first,'first_hand_roles')):
   if not blocks:row[field]=[];continue
   block=blocks[0];lists=block.find(lambda n:n.has('credit-roles'))
   assert len(lists)==1,'Missing or extra role list'
   roles=[n.text().strip() for n in lists[0].find(lambda n:n.tag=='li')]
   assert roles==rec[field],f'{card.attrs["id"]}: inferred, removed or converted {field}'
   assert json.loads(card.attrs['data-public' if field=='public_roles' else 'data-first-hand'])==roles
   total_roles+=len(roles);row[field]=roles
   badges=block.find(lambda n:n.has('evidence-label'));headings=block.find(lambda n:n.tag=='h4')
   assert len(headings)==1
   if field=='public_roles':
    assert tier in ('A','B')
    label={'A':'Public metadata','B':'Publicly documented'}[tier]
    assert len(badges)==1 and badges[0].text()==label,'Wrong badge for evidence tier'
    assert headings[0].text()==label,'Incorrect public scope label'
    links=block.find(lambda n:n.tag=='a')
    assert [n.attrs['href'] for n in links]==[s['url'] for s in rec['evidence_sources']],'Evidence mismatch'
    scoped_badges+=1
   else:
    assert not badges,'Verification badge incorrectly applied to first-hand role'
    assert headings[0].text()=='First-hand studio history'
    assert not block.find(lambda n:n.tag=='a'),'Public evidence linked to first-hand roles'
  assert len(card.find(lambda n:n.has('evidence-label')))==scoped_badges,'Badge outside public scope'
  assert len(card.find(lambda n:n.has('credit-roles')))==len(public)+len(first),'Roles outside evidence scope'
  total_badges+=scoped_badges;rows.append(row)
 assert len(tree.find(lambda n:n.has('evidence-label')))==total_badges,'Unscoped evidence badge'
 assert len(tree.find(lambda n:n.has('credit-roles')))==sum(bool(r['public_roles'])+bool(r['first_hand_roles']) for r in expected.values()),'Unscoped role list'
 return {'registry_version':reg['KREAZOE_MASTER_CREDITS_REGISTRY_VERSION'],'records_audited':len(cards),'public_metadata_badges':sum(bool(r['public_roles']) and r['evidence_tier']=='A' for r in expected.values()),'publicly_documented_badges':sum(bool(r['public_roles']) and r['evidence_tier']=='B' for r in expected.values()),'first_hand_blocks':sum(bool(r['first_hand_roles']) for r in expected.values()),'featured_record_previews':len(selections),'public_role_values':sum(len(r['public_roles']) for r in expected.values()),'first_hand_role_values':sum(len(r['first_hand_roles']) for r in expected.values()),'role_values_audited':total_roles,'inferred_roles':0,'misapplied_badges':0,'records':rows}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--registry',type=Path,default=ROOT/'data/credits-registry.v1.json');p.add_argument('--html',type=Path,default=ROOT/'index.html');p.add_argument('--report',type=Path);args=p.parse_args()
 reg=args.registry.read_bytes();page=args.html.read_bytes();report=audit(json.loads(reg),page.decode())
 report['registry_sha256']=hashlib.sha256(reg).hexdigest();report['html_sha256']=hashlib.sha256(page).hexdigest()
 if args.report:args.report.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
if __name__=='__main__':main()
