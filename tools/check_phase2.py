"""Phase 2 catalogue integrity and unpopulated component checks."""
from pathlib import Path
import json,re
from audit_rendered_credits import Tree,audit
ROOT=Path(__file__).resolve().parents[1];s=(ROOT/'index.html').read_text();tree=Tree(s).root;r=json.loads((ROOT/'data/credits-registry.v1.json').read_text())
audit(r,s)
for kind in ('releases','recognition'):
 nodes=tree.find(lambda n:n.attrs.get('data-future-component')==kind);assert len(nodes)==1
 assert not nodes[0].find(lambda n:n.has('registry-credit') or n.has('selection-card') or n.has('evidence-label') or n.tag in ('blockquote','cite','audio','iframe'))
for id,field in [('credit-year','year'),('credit-project','project')]:
 select=tree.find(lambda n:n.attrs.get('id')==id)[0]
 options=select.find(lambda n:n.tag=='option')
 values={n.text() for n in options if n.attrs.get('value') not in ('','__unspecified')}
 assert values=={str(rec[field]) for rec in r['records'] if rec[field] is not None}
for card in tree.find(lambda n:n.has('registry-credit')):
 rec=r['records'][int(card.attrs['id'].split('-')[1])-1]
 assert card.attrs['data-year']==(str(rec['year']) if rec['year'] is not None else '')
 assert card.attrs['data-project']==(rec['project'] or '')
journeys=tree.find(lambda n:n.has('contact-journeys'))[0]
links=journeys.find(lambda n:n.tag=='a');assert len(links)==2
assert all(n.attrs['href'].startswith('mailto:kreazoe@gmail.com?subject=') for n in links)
assert not journeys.find(lambda n:n.tag=='form')
assert 'Co-production with Mfanafuthi Ruff Nkosi.' in s and 'Co-production with Pheto Mbulelo Mabena.' in s
print('PASS: all featured selections originate in frozen FEATURED_VERIFIED records; year/project filters match data; releases and recognition unpopulated; legitimate contact paths.')
