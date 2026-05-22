// --- Mobile nav toggle ---
const toggleBtn = document.querySelector('.nav-toggle');
const navLinks  = document.querySelector('.nav-links');

toggleBtn.addEventListener('click', () => {
  const isOpen = navLinks.classList.toggle('open');
  toggleBtn.querySelector('.hamburger').textContent = isOpen ? '✕' : '☰';
});

toggleBtn.querySelector('.hamburger').textContent = '☰';

// --- Smart sticky nav: hide on scroll down, show on scroll up ---
const nav = document.querySelector('nav');
let lastY = window.scrollY;

window.addEventListener('scroll', () => {
  const currentY = window.scrollY;

  if (currentY > lastY && currentY > 60) {
    // Scrolling down — hide nav
    nav.classList.add('nav-hidden');
  } else {
    // Scrolling up — show nav
    nav.classList.remove('nav-hidden');
  }

  lastY = currentY;
}, { passive: true });