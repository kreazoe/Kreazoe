const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=require('path').resolve(__dirname,'..')+'/';
const records=JSON.parse(fs.readFileSync(root+'data/credits-registry.v1.json')).records;
const events={},els={};
for(const id of ['credit-search','credit-artist','credit-evidence','credit-year','credit-project','credit-role','credit-featured','credit-result','credit-empty']){
 els[id]={value:'',checked:false,hidden:false,textContent:''};
}
const cardEls=records.map((r,i)=>({id:'credit-'+String(i+1).padStart(3,'0'),hidden:false,open:false,scrollIntoView(){},dataset:{artist:r.artist,year:r.year?String(r.year):'',project:r.project||'',tier:r.evidence_tier,public:JSON.stringify(r.public_roles),firstHand:JSON.stringify(r.first_hand_roles),featured:String(r.portfolio_status==='FEATURED_VERIFIED'),search:[r.artist,r.track,...r.featured_artists,r.project||'',r.credited_as,...r.collaborators].join(' ')}}));
els['credit-filters']={hidden:true,addEventListener:(k,f)=>events[k]=f,reset(){Object.values(els).forEach(e=>{if('value'in e)e.value='';if('checked'in e)e.checked=false});events.reset()}};
const doc={getElementById:id=>els[id],querySelectorAll:q=>q==='.registry-credit'?cardEls:q==='.credit-collection'?[]:[],querySelector:()=>({addEventListener(){}})};
vm.runInNewContext(fs.readFileSync(root+'assets/credits.js','utf8'),{document:doc,requestAnimationFrame:f=>f(),addEventListener(){},location:{hash:''}});
let checks=0;
function test(filters){
 els['credit-filters'].reset();
 for(const [k,v]of Object.entries(filters))els['credit-'+k].value=v;
 const before=JSON.stringify(cardEls.map(c=>c.dataset));
 events.input();
 const expected=records.filter(r=>{
 const e=filters.evidence||'',roles=e==='C'?r.first_hand_roles:e?(r.evidence_tier===e?r.public_roles:[]):[...r.public_roles,...r.first_hand_roles];
 return (!filters.artist||r.artist===filters.artist)&&(!filters.year||(filters.year==='__unspecified'?r.year===null:String(r.year)===filters.year))&&(!filters.project||(filters.project==='__unspecified'?r.project===null:r.project===filters.project))&&(!e||roles.length)&&(!filters.role||roles.includes(filters.role))&&(!filters.search||filters.search.toLowerCase().split(/\s+/).every(t=>[r.artist,r.track,...r.featured_artists,r.project||'',r.credited_as,...r.collaborators].join(' ').toLowerCase().includes(t)));
 });
 assert.equal(cardEls.filter(c=>!c.hidden).length,expected.length,JSON.stringify(filters));
 assert.equal(JSON.stringify(cardEls.map(c=>c.dataset)),before);
 checks++;
}
for(const [field,vals]of Object.entries({artist:[...new Set(records.map(r=>r.artist))],year:['2017','2018','2019','2020','__unspecified'],project:[...new Set(records.map(r=>r.project||'__unspecified'))],role:[...new Set(records.flatMap(r=>[...r.public_roles,...r.first_hand_roles]))],evidence:['A','B','C']}))for(const v of vals)test({[field]:v});
for(const e of ['A','B','C'])for(const role of [...new Set(records.flatMap(r=>[...r.public_roles,...r.first_hand_roles]))])for(const artist of [...new Set(records.map(r=>r.artist))])test({evidence:e,role,artist});
for(const search of ['ISIB','my PeO','second coming','no-match-xyz','Emtee Abantu'])test({search});
test({evidence:'A',role:'Recording'});test({evidence:'C',role:'Recording',artist:'Sjava'});
els['credit-filters'].reset();assert.equal(cardEls.filter(c=>!c.hidden).length,34);
els['credit-featured'].checked=true;events.change();assert.equal(cardEls.filter(c=>!c.hidden).length,10);
console.log('PASS: '+checks+' filter/search cases; mixed evidence and role scope; no-result, reset, 10 featured; all record datasets unchanged. Unit simulation, not browser rendering.');
