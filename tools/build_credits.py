"""Render frozen credits into static HTML. Run from any directory; no dependencies.
This never edits the registry. Public and first-hand roles are separate inputs.
"""
from pathlib import Path
import json, re, html, argparse
ROOT=Path(__file__).resolve().parents[1]
def esc(s): return html.escape(str(s),quote=True)
def render(reg):
 assert reg['STATUS']=='FROZEN'
 version=reg['KREAZOE_MASTER_CREDITS_REGISTRY_VERSION']
 assert isinstance(version,str) and version
 records=reg['records']
 visible=[r for r in records if r['portfolio_status']!='EXCLUDED']
 def card(r,i):
  assert r['evidence_tier'] in ('A','B','C')
  if r['portfolio_status']=='EXCLUDED': return ''
  public=r['public_roles']; first=r['first_hand_roles']
  assert r['evidence_tier']!='C' or not public
  assert all(isinstance(role,str) and role for role in public+first)
  assert not public or r['evidence_sources'], 'Public roles require frozen evidence sources'
  title='Multiple tracks' if r['track']=='MULTIPLE_TRACKS' else r['track']
  meta=' · '.join(str(x) for x in [r['project'],r['year']] if x is not None)
  features=('feat. '+', '.join(r['featured_artists'])) if r['featured_artists'] else ''
  attributes={'data-artist':r['artist'],'data-year':str(r['year']) if r['year'] is not None else '', 'data-project':r['project'] or '','data-tier':r['evidence_tier'],'data-public':json.dumps(public),'data-first-hand':json.dumps(first),'data-featured':str(r['portfolio_status']=='FEATURED_VERIFIED').lower(),'data-search':' '.join([r['artist'],title,features,meta,r['credited_as'],*r['collaborators']])}
  attrs=' '.join(f'{k}="{esc(v)}"' for k,v in attributes.items())
  blocks=''
  if public:
   label='Public metadata' if r['evidence_tier']=='A' else 'Publicly documented'
   blocks+=f'<div class="role-block public-role-block"><h4><span class="evidence-label">{label}</span></h4><ul class="credit-roles">'+''.join(f'<li>{esc(x)}</li>' for x in public)+'</ul>'
   # Explicit frozen co-production requirements; never derive a role from collaborators.
   if (r['artist'],r['track']) in [('Sjava','Isibhamu'),('Kid Tini','Icebo')]:
    blocks+='<p class="source-context">Co-production with '+esc(' · '.join(r['collaborators']))+'.</p>'
   if (r['artist'],r['track'])==('Kid Tini','Amen'):
    blocks+='<p class="source-context">Shazam identifies Bheki Christopher Thobela as Composer and Christopher Thobela in production metadata. This is not a claim of sole production. See the source for the full credit context.</p>'
   blocks+='<div class="evidence-links">'
   for source in r['evidence_sources']:
    context=' — project context' if r['track']=='Bet' and source['name']=='Audiomack' else ''
    blocks+=f'<a class="verify" href="{esc(source["url"])}" target="_blank" rel="noopener">{esc(source["name"]+context)} <span aria-hidden="true">↗</span><span class="sr-only"> — evidence for {esc(r["artist"])}: {esc(title)} (opens in new tab)</span></a>'
   blocks+='</div></div>'
  if first:
   blocks+='<div class="role-block first-hand-role-block"><h4>First-hand studio history</h4><ul class="credit-roles">'+''.join(f'<li>{esc(x)}</li>' for x in first)+'</ul><p class="source-context">Supplied by Bheki Christopher Thobela.</p>'
   if r['track']=='MULTIPLE_TRACKS':
    blocks+='<p class="source-context">Recording on most songs on Busisiwe. Project-level studio history; individual track credits are not specified. Production is not claimed.</p>'
   blocks+='</div>'
  return f'''<details id="credit-{i:03}" class="production registry-credit" {attrs} {'open' if i==1 else ''}>
<summary><span class="work-no">{i:02}</span><span class="work-artist">{esc(r['artist'])}</span><span class="work-title">{esc(title)}<small>{esc(features or meta)}</small></span><span class="expand" aria-hidden="true">+</span></summary>
<div class="production-body"><div class="release-identity"><p class="eyebrow">{'Project-level studio history' if r['track']=='MULTIPLE_TRACKS' else 'Track detail'}</p><h3>{esc(title)}</h3>{('<p>'+esc(features)+'</p>') if features else ''}<p>{esc(meta)}</p><p class="credited-as">Credited as<br><span>{esc(r['credited_as'])}</span></p><a class="text-link credit-permalink" href="#credit-{i:03}">Link to this credit <span aria-hidden="true">↗</span></a></div><div class="credit-role-groups">{blocks}</div></div></details>'''
 public=''.join(card(r,i) for i,r in enumerate(records,1) if r['public_roles'])
 studio=''.join(card(r,i) for i,r in enumerate(records,1) if not r['public_roles'])
 artists=''.join(f'<option>{esc(x)}</option>' for x in sorted({r['artist'] for r in visible}))
 role_options=''.join(f'<option>{esc(x)}</option>' for x in sorted({role for r in visible for role in r['public_roles']+r['first_hand_roles']}))
 years=''.join(f'<option>{year}</option>' for year in sorted({r['year'] for r in visible if r['year'] is not None},reverse=True))
 projects=''.join(f'<option>{esc(project)}</option>' for project in sorted({r['project'] for r in visible if r['project']}))
 selections=''.join(f"<a class=\"selection-card\" data-feature-ref=\"credit-{i:03}\" href=\"#credit-{i:03}\"><span class=\"selection-meta\">{esc(r['artist'])} <span>{r['year'] if r['year'] is not None else ''}</span></span><h3>{esc(r['track'])}</h3><p>{esc(r['project'] or '')}</p><span class=\"selection-link\">Explore credit <span aria-hidden=\"true\">↗</span></span></a>" for i,r in enumerate(records,1) if r['portfolio_status']=='FEATURED_VERIFIED')
 return f'''<section id="work" class="section work-section"><div class="wrap"><div class="section-heading"><p class="eyebrow">01 / Selected productions</p><h2>Let the<br><em>work speak.</em></h2><p class="section-note">Explore the records, the roles and the sources. Public credits and first-hand studio work are shown separately, down to each role.</p></div>
<div class="selected-productions" aria-label="Selected productions">{selections}</div><div id="explorer" class="explorer-heading"><div><p class="eyebrow">The catalogue / Roles &amp; evidence</p><h2>Credits <em>Explorer.</em></h2></div><p>Search the body of work. Open a record to see the exact roles, credited name and supporting sources.</p></div><div class="evidence-guide"><div><span class="eyebrow">Public metadata</span><p>Track-level public sources support the public roles shown.</p></div><div><span class="eyebrow">Publicly documented</span><p>Public documentation supports these roles; it is distinct from track-level platform metadata.</p></div><div><span class="eyebrow">First-hand studio history</span><p>Studio work supplied by Bheki. These roles carry no public verification badge.</p></div></div>
<form id="credit-filters" class="credit-filters" role="search" aria-label="Explore music credits" hidden>
<div class="search-field"><label for="credit-search">Find a record</label><input id="credit-search" type="search" placeholder="Track, artist, project or collaborator" autocomplete="off"></div>
<div><label for="credit-artist">Artist</label><select id="credit-artist"><option value="">All artists</option>{artists}</select></div>
<div><label for="credit-year">Year</label><select id="credit-year"><option value="">All years</option>{years}<option value="__unspecified">Not specified</option></select></div>
<div><label for="credit-project">Project</label><select id="credit-project"><option value="">All projects</option>{projects}<option value="__unspecified">Not specified</option></select></div>
<div><label for="credit-evidence">Role evidence</label><select id="credit-evidence"><option value="">All evidence</option><option value="A">Public metadata</option><option value="B">Publicly documented</option><option value="C">First-hand studio history</option></select></div>
<div><label for="credit-role">Exact role</label><select id="credit-role"><option value="">All roles</option>{role_options}</select></div>
<div class="filter-footer"><label class="featured-filter"><input id="credit-featured" type="checkbox"> Featured selections only</label><button type="reset" class="button">Clear filters</button></div></form>
<div class="registry-toolbar"><p id="credit-result" role="status" aria-live="polite" aria-atomic="true">{len(visible)} records</p><a class="text-link" href="#discography">Explore studio history ↓</a></div>
<div class="credit-collection" id="public-collection"><h3 class="collection-title">Public credits <span>Metadata &amp; documentation</span></h3><div class="productions">{public}</div></div>
<div class="credit-collection" id="discography"><h3 class="collection-title">Studio history <span>First-hand studio work</span></h3><p class="collection-intro">Additional studio records. Where a public credit also has first-hand roles, both are separated in that record above.</p><div class="productions">{studio}</div></div>
<p id="credit-empty" class="empty-state" hidden>No records match these filters. Try another role or evidence type, or clear the filters.</p><p class="small-note registry-edition">KREAZOE™ Master Credits Registry · Version {esc(version)}. Evidence labels apply only to the roles beside them.</p></div></section>'''
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--registry',type=Path,default=ROOT/'data/credits-registry.v1.json',help='Path to an authorized frozen registry version')
 args=parser.parse_args()
 reg=json.loads(args.registry.read_text())
 path=ROOT/'index.html'; s=path.read_text()
 section=render(reg)
 if '<!-- CREDITS:START -->' in s:
  s=re.sub(r'<!-- CREDITS:START -->.*?<!-- CREDITS:END -->',lambda _: '<!-- CREDITS:START -->'+section+'<!-- CREDITS:END -->',s,flags=re.S)
 else:
  s=re.sub(r'<section id="work".*?(?=<section id="story")',lambda _: '<!-- CREDITS:START -->'+section+'<!-- CREDITS:END -->\n',s,flags=re.S)
  s=re.sub(r'<section id="discography".*?(?=<section id="practice")','',s,flags=re.S)
 path.write_text(s)
if __name__=='__main__':main()
