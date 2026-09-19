"""V5 presentation safety checks; immutable credits are audited separately."""
from pathlib import Path
import hashlib, json, re
from audit_rendered_credits import Tree
root=Path(__file__).resolve().parents[1]
s=(root/'index.html').read_text();tree=Tree(s).root
assert 'linkedin' not in s.lower()
assert 'localhost' not in s and '127.0.0.1' not in s
sections=[n.attrs.get('id') for n in tree.find(lambda n:n.tag=='section')]
assert sections==['top','snapshot','story','work','practice','education','explorer','contact'],sections
assert len(tree.find(lambda n:n.tag=='h1'))==1
for text in ['Qualification quality-assured by SAMRO','Rights/Repertoire and Release/Distribution support','first-hand studio history','Soul Candi Institute of Music']:
 assert text in s
for n in tree.find(lambda n:n.tag=='a' and n.text().strip()=='View CV ↗'):
 assert n.attrs['href']=='Bheki_Christopher_Thobela_CV.pdf' and 'download' not in n.attrs
assert len(tree.find(lambda n:n.tag=='a' and n.text().strip()=='View CV ↗'))==2
for ext,expected in [('pdf',''),('docx','')]:
 p=root/f'Bheki_Christopher_Thobela_CV.{ext}'
 assert p.is_file()
ld=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s).group(1))
assert ld['name']=='Bheki Christopher Thobela' and ld['telephone']=='+27765700811'
assert ld['email']=='mailto:kreazoe@gmail.com' and 'sameAs' not in ld
assert 'prefers-reduced-motion:reduce' in (root/'assets/job-ready.css').read_text()
print('PASS: V5 section order; no LinkedIn; CV view semantics; contact identity; structured data; career-interest distinction; reduced motion.')
