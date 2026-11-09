const pages = [...document.querySelectorAll('.lesson-page')];
const stack = document.querySelector('.pages');
const selector = document.querySelector('#page-select');
const counter = document.querySelector('#page-counter');
const scrollArea = document.querySelector('.page-scroll');
let zoom = 1;

const imageObserver = new IntersectionObserver(entries => {
  entries.filter(entry => entry.isIntersecting).forEach(entry => {
    entry.target.querySelectorAll('image[data-src]').forEach(image => {
      image.setAttributeNS('http://www.w3.org/1999/xlink', 'href', image.dataset.src);
      image.removeAttribute('data-src');
    });
    imageObserver.unobserve(entry.target);
  });
}, {rootMargin: '1200px 0px'});
pages.forEach(page => imageObserver.observe(page));

function fitWidth() {
  return Math.min(840, scrollArea.clientWidth - (matchMedia('(max-width:700px)').matches ? 20 : 36));
}
function applyZoom() {
  stack.style.setProperty('--reader-width', `${fitWidth() * zoom}px`);
  stack.classList.toggle('zoomed', zoom > 1);
  document.querySelector('#zoom-out').disabled = zoom <= 1;
  document.querySelector('#zoom-in').disabled = zoom >= 2;
}
function changeZoom(delta) {
  const anchor = document.getElementById(`page-${selector.value}`);
  zoom = Math.max(1,Math.min(2,zoom+delta));
  applyZoom();
  requestAnimationFrame(() => anchor.scrollIntoView({behavior:'instant',block:'start'}));
}
document.querySelector('#zoom-in').addEventListener('click', () => changeZoom(.25));
document.querySelector('#zoom-out').addEventListener('click', () => changeZoom(-.25));
selector.addEventListener('change', () => {
  const id = `page-${selector.value}`;
  document.getElementById(id).scrollIntoView({behavior: 'instant', block: 'start'});
  history.replaceState(null, '', `#${id}`);
});
const visiblePages = new Map();
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) visiblePages.set(entry.target,entry);
    else visiblePages.delete(entry.target);
  });
  const visible = [...visiblePages.values()].sort((a,b) => b.intersectionRatio - a.intersectionRatio);
  if (!visible.length) return;
  const number = visible[0].target.dataset.page;
  selector.value = number;
  counter.textContent = `${number} / ${pages.length}`;
}, {rootMargin: '-70px 0px -35% 0px', threshold: [0,.1,.25,.5,.75]});
pages.forEach(page => observer.observe(page));
window.addEventListener('resize', applyZoom);
applyZoom();
