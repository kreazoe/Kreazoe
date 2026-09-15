(() => {
  const button = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#site-nav');
  if (!button || !nav) return;
  document.documentElement.classList.add('js');
  button.hidden = false;
  const closeMenu = () => {
    button.setAttribute('aria-expanded', 'false');
    nav.classList.remove('is-open');
    button.querySelector('span').textContent = '+';
  };
  button.addEventListener('click', () => {
    const open = button.getAttribute('aria-expanded') !== 'true';
    button.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('is-open', open);
    button.querySelector('span').textContent = open ? '−' : '+';
  });
  nav.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (!link) return;
    closeMenu();
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
      target.addEventListener('blur', () => target.removeAttribute('tabindex'), { once: true });
    }
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
      closeMenu();
      button.focus();
    }
  });
  matchMedia('(min-width: 701px)').addEventListener('change', closeMenu);
})();
