(function () {
  'use strict';
  function parseSchedule(text, mapping, count) {
    const valid = new Set(Object.values(mapping));
    const stages = new Map();
    const errors = [];
    text.split(/\r?\n/).forEach((line, i) => {
      if (!line.trim()) return;
      const tokens = line.trim().toLowerCase().split(/\s+/);
      const start = Number(tokens.shift());
      if (!Number.isSafeInteger(start) || start < 1 || start > count || !tokens.length || tokens.some(t => !valid.has(t))) {
        errors.push(i + 1); return;
      }
      tokens.forEach(t => stages.set(t, Math.min(start, stages.get(t) ?? Infinity)));
    });
    return { stages, errors };
  }
  function convertedParts(text, step, stages, mapping) {
    const parts = [];
    const keys = Object.keys(mapping).sort((a, b) => b.length - a.length);
    for (let i = 0; i < text.length;) {
      const key = keys.find(key => text.slice(i, i + key.length).toLowerCase() === key);
      const source = key ? text.slice(i, i + key.length) : String.fromCodePoint(text.codePointAt(i));
      const target = key ? mapping[key] : null;
      const converted = Boolean(target && (stages.get(target) ?? Infinity) <= step);
      const uppercase = source[0] !== source[0].toLowerCase();
      const value = converted ? (uppercase ? target[0].toUpperCase() + target.slice(1) : target) : source;
      parts.push({text: value, converted: converted || /[А-Яа-яЁё]/u.test(source)});
      i += source.length;
    }
    return parts;
  }
  if (typeof module !== 'undefined') module.exports = { parseSchedule, convertedParts };
  if (typeof document === 'undefined') return;
  const config = JSON.parse(document.querySelector('#reader-config').textContent);
  const order = document.querySelector('#letter-order');
  const original = document.querySelector('#latin-only');
  const error = document.querySelector('#schedule-error');
  const read = key => { try { return localStorage.getItem(key); } catch { return null; } };
  const save = (key, value) => { try { localStorage.setItem(key, value); } catch {} };
  const cyrillicClass = text => /[ХхУуСс]/u.test(text) ? 'cyrillic false-friend' : 'cyrillic';
  const russianSpan = text => {
    const span = document.createElement('span');
    span.className = cyrillicClass(text);
    span.textContent = text;
    return span;
  };
  const texts = [...document.querySelectorAll('.tsonga')].map(element => ({element, text: element.textContent, step: Number(element.dataset.step)}));
  let stages = parseSchedule(config.defaultSchedule, config.mapping, config.paragraphCount).stages;
  const render = () => {
    for (const {element, text, step} of texts) {
      const fragment = document.createDocumentFragment();
      let run = '', active = '';
      const flush = () => {
        if (!run) return;
        const node = active ? document.createElement('span') : document.createTextNode(run);
        if (active) { node.className = active; node.textContent = run; }
        fragment.append(node); run = '';
      };
      for (const part of convertedParts(text, step, original.checked ? new Map() : stages, config.mapping)) {
        const style = part.converted ? cyrillicClass(part.text) : '';
        if (style !== active) { flush(); active = style; }
        run += part.text;
      }
      flush(); element.replaceChildren(fragment);
    }
    for (const pair of document.querySelectorAll('.paragraph-pair')) {
      const number = Number(pair.dataset.paragraph);
      const introduced = [...stages].filter(([,start]) => start === number).flatMap(([target]) => {
        // These lowercase Latin/Cyrillic pairs have the same visible letterform.
        const sources = Object.keys(config.mapping).filter(k => config.mapping[k] === target && !['a', 'e', 'o'].includes(k));
        return sources.map(source => ({source, target}));
      });
      pair.querySelector('.introduced').replaceChildren(...(original.checked ? [] : introduced.map(({source, target}) => {
        const line = document.createElement('span');
        line.className = 'introduced-entry';
        line.append(document.createTextNode(`${source} → `), russianSpan(target));
        return line;
      })));
    }
  };
  const apply = () => {
    const parsed = parseSchedule(order.value, config.mapping, config.paragraphCount);
    order.setAttribute('aria-invalid', parsed.errors.length ? 'true' : 'false');
    error.textContent = parsed.errors.length ? `Строка ${parsed.errors.join(', ')}` : '';
    if (parsed.errors.length) return; // Retain the last valid rendering while editing.
    stages = parsed.stages;
    save('where-are-you-letter-order-v1', order.value);
    render();
  };
  const storedOrder = read('where-are-you-letter-order-v1');
  order.value = config.legacyDefaultSchedules?.includes(storedOrder) ? config.defaultSchedule : storedOrder ?? config.defaultSchedule;
  original.checked = read('where-are-you-latin-only-v1') === 'true';
  apply(); render();
  order.addEventListener('input', apply);
  original.addEventListener('change', () => { save('where-are-you-latin-only-v1', String(original.checked)); render(); });
  document.querySelector('#auto-order').addEventListener('click', () => { order.value = config.defaultSchedule; original.checked = false; save('where-are-you-latin-only-v1', 'false'); apply(); });
  const list = document.querySelector('#mapping-list');
  for (const [latin, russian] of Object.entries(config.mapping)) {
    if (!texts.some(({text}) => text.toLowerCase().includes(latin))) continue;
    const entry = document.createElement('span');
    entry.append(document.createTextNode(`${latin} → `));
    const target = russianSpan(russian);
    entry.append(target); list.append(entry);
  }
  const pageSelect = document.querySelector('#page-select');
  const sections = [...document.querySelectorAll('.story-page')];
  pageSelect.addEventListener('change', () => {
    document.querySelector(`#page-${pageSelect.value}`).scrollIntoView({block:'start'});
    history.replaceState(null, '', `#page-${pageSelect.value}`);
  });
  let queued = false;
  const update = () => {
    const boundary = document.querySelector('.toolbar').getBoundingClientRect().bottom + 40;
    let current = sections[0];
    for (const section of sections) if (section.getBoundingClientRect().top <= boundary) current = section;
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
