/* Progressive enhancement only: frozen credit content is already in the HTML. */
(() => {
  const form = document.getElementById('credit-filters');
  if (!form) return;
  const cards = [...document.querySelectorAll('.registry-credit')].map(el => ({
    el, publicRoles: JSON.parse(el.dataset.public), firstHandRoles: JSON.parse(el.dataset.firstHand)
  }));
  const query = document.getElementById('credit-search');
  const artist = document.getElementById('credit-artist');
  const evidence = document.getElementById('credit-evidence');
  const role = document.getElementById('credit-role');
  const featured = document.getElementById('credit-featured');
  const result = document.getElementById('credit-result');
  const collections = [...document.querySelectorAll('.credit-collection')];
  const filter = () => {
    const terms = query.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let count = 0;
    for (const {el, publicRoles, firstHandRoles} of cards) {
      // Match a role only inside the requested evidence scope. Never infer roles.
      const scopedRoles = evidence.value === 'C' ? firstHandRoles
        : evidence.value ? (el.dataset.tier === evidence.value ? publicRoles : [])
        : [...publicRoles, ...firstHandRoles];
      const match = (!artist.value || el.dataset.artist === artist.value)
        && (!evidence.value || scopedRoles.length > 0)
        && (!role.value || scopedRoles.includes(role.value))
        && (!featured.checked || el.dataset.featured === 'true')
        && terms.every(term => el.dataset.search.toLocaleLowerCase().includes(term));
      el.hidden = !match;
      if (match) count++;
    }
    for (const group of collections) group.hidden = ![...group.querySelectorAll('.registry-credit')].some(el => !el.hidden);
    document.getElementById('credit-empty').hidden = count !== 0;
    result.textContent = `${count} of ${cards.length} records`;
  };
  form.hidden = false;
  form.addEventListener('submit', e => e.preventDefault());
  form.addEventListener('input', filter);
  form.addEventListener('change', filter);
  form.addEventListener('reset', () => requestAnimationFrame(filter));
  function revealHash() {
    const match = cards.find(({el}) => `#${el.id}` === location.hash);
    if (!match) return;
    form.reset(); filter(); match.el.open = true;
    requestAnimationFrame(() => match.el.scrollIntoView({block:'start', behavior:'instant'}));
  }
  document.querySelector('.registry-toolbar a[href="#discography"]').addEventListener('click', () => {
    form.reset(); filter();
  });
  document.querySelectorAll('.credit-permalink').forEach(link => link.addEventListener('click', () => {
    if (link.hash === location.hash) revealHash();
  }));
  addEventListener('hashchange', revealHash);
  revealHash();
})();
