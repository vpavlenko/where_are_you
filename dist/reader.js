(() => {
  const root = document.documentElement;
  const language = document.querySelector('#language');
  const pageSelect = document.querySelector('#page-select');
  const smaller = document.querySelector('#smaller');
  const larger = document.querySelector('#larger');
  const sections = [...document.querySelectorAll('.story-page')];
  let size = window.innerWidth <= 760 ? 20 : 22;
  const read = key => { try { return localStorage.getItem(key); } catch { return null; } };
  const save = (key, value) => { try { localStorage.setItem(key, value); } catch {} };
  const setSize = () => {
    root.style.setProperty('--reader-size', `${size}px`);
    smaller.disabled = size <= 16;
    larger.disabled = size >= 32;
  };
  const storedSize = Number(read('where-are-you-size'));
  if (storedSize >= 16 && storedSize <= 32) size = storedSize;
  setSize();
  const setLanguage = value => {
    root.dataset.language = value;
    root.lang = value === 'ts' ? 'ts' : 'en';
    language.value = value;
  };
  const storedLanguage = read('where-are-you-language');
  if (['both', 'en', 'ts'].includes(storedLanguage)) setLanguage(storedLanguage);
  language.addEventListener('change', () => {
    const current = sections.find(section => section.dataset.page === pageSelect.value);
    setLanguage(language.value);
    save('where-are-you-language', language.value);
    if (current) current.scrollIntoView({block:'start'});
  });
  smaller.addEventListener('click', () => { size = Math.max(16, size - 2); setSize(); save('where-are-you-size', size); });
  larger.addEventListener('click', () => { size = Math.min(32, size + 2); setSize(); save('where-are-you-size', size); });
  pageSelect.addEventListener('change', () => {
    const section = document.querySelector(`#page-${pageSelect.value}`);
    section.scrollIntoView({block:'start'});
    history.replaceState(null, '', `#page-${pageSelect.value}`);
  });
  let queued = false;
  const update = () => {
    const boundary = document.querySelector('.toolbar').getBoundingClientRect().bottom + 60;
    let current = sections[0];
    for (const section of sections) {
      if (section.getBoundingClientRect().top <= boundary) current = section;
    }
    pageSelect.value = current.dataset.page;
    const range = document.documentElement.scrollHeight - window.innerHeight;
    document.querySelector('#progress-bar').style.width = `${range > 0 ? Math.min(100, window.scrollY / range * 100) : 100}%`;
    queued = false;
  };
  window.addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(update); } }, {passive:true});
  window.addEventListener('resize', update);
  window.addEventListener('load', update);
  update();
})();
