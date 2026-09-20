(() => {
  const root = document.documentElement;
  const button = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#site-nav');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  if (!button || !nav) return;
  root.classList.add('js');
  button.hidden = false;
  const closeMenu = () => {
    button.setAttribute('aria-expanded', 'false');
    button.querySelector('span').textContent = '+';
    nav.classList.remove('is-open');
  };
  button.addEventListener('click', () => {
    const open = button.getAttribute('aria-expanded') !== 'true';
    button.setAttribute('aria-expanded', String(open));
    button.querySelector('span').textContent = open ? '−' : '+';
    nav.classList.toggle('is-open', open);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
      closeMenu(); button.focus();
    }
  });
  nav.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (!link) return;
    closeMenu();
    const target = document.getElementById(link.hash.slice(1));
    if (target) {
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
      target.addEventListener('blur', () => target.removeAttribute('tabindex'), { once: true });
    }
  });
  matchMedia('(min-width: 1001px)').addEventListener('change', closeMenu);
  const links = Array.from(nav.querySelectorAll('a'));
  const sections = links.map(a => document.getElementById(a.hash.slice(1))).filter(Boolean);
  let pending = false;
  const update = () => {
    pending = false;
    const scrollable = root.scrollHeight - innerHeight;
    root.style.setProperty('--read-progress', scrollable > 0 ? Math.min(1, scrollY / scrollable) : 0);
    root.style.setProperty('--hero-drift', reduced.matches ? '0px' : `${Math.min(scrollY * .035, 14)}px`);
    let active = '';
    for (const section of sections) if (section.getBoundingClientRect().top <= 180) active = section.id;
    for (const link of links) {
      if (link.hash === `#${active}`) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  };
  const schedule = () => { if (!pending) { pending = true; requestAnimationFrame(update); } };
  addEventListener('scroll', schedule, { passive: true });
  addEventListener('resize', schedule);
  reduced.addEventListener('change', schedule);
  update();
  if ('IntersectionObserver' in window && !reduced.matches) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) if (entry.isIntersecting) {
        entry.target.classList.add('is-visible'); observer.unobserve(entry.target);
      }
    }, { threshold: .05 });
    for (const el of document.querySelectorAll('.section-heading,.story-intro,.tools')) {
      el.classList.add('reveal-ready'); observer.observe(el);
    }
  }
  // Native disclosures remain fully functional without JavaScript.
  for (const detail of document.querySelectorAll('.production')) {
    detail.addEventListener('toggle', schedule);
  }
})();
