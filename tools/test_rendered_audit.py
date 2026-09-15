"""Negative safety tests and data-only registry update test; never edit frozen data."""
import json, hashlib
from pathlib import Path
from audit_rendered_credits import audit
from build_credits import render
ROOT=Path(__file__).resolve().parents[1]
raw=(ROOT/'data/credits-registry.v1.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='3f139dd6d7734f7b3631033db839b95bfea5017330b3e0fe5be136392eb6657a','Frozen dataset changed'
reg=json.loads(raw);page=(ROOT/'index.html').read_text()
for mutated in [page.replace('<li>Recording</li>','<li>Recording Engineer</li>',1),page.replace('<span class="evidence-label">Publicly documented</span>','<span class="evidence-label">Public metadata</span>',1),page.replace('<h4>First-hand studio history</h4>','<h4><span class="evidence-label">Public metadata</span></h4>',1)]:
 try:audit(reg,mutated)
 except AssertionError:pass
 else:raise AssertionError('Audit accepted an invalid role or badge')
fixture=json.loads(json.dumps(reg));fixture['KREAZOE_MASTER_CREDITS_REGISTRY_VERSION']='test';fixture['records']=fixture['records'][:3]
html=render(fixture);assert 'Version test.' in html and '>3 records</p>' in html
assert audit(fixture,html)['records_audited']==3
print('PASS: frozen checksum; rejects role conversion, Tier B upgrade and first-hand verification; version/count updates need no layout rewrite.')
