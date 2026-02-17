/* ============ SLIDE ANIMATION ON SCROLL ============ */
const animatedRows = document.querySelectorAll('.slide-left, .slide-right');

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('slide-active');
    }
  });
}, { threshold: 0.2 });

animatedRows.forEach(row => observer.observe(row));

/* ============ MAGNETIC HOVER EFFECT ============ */
document.querySelectorAll('.image-border').forEach(card => {
  card.addEventListener('mousemove', e => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    card.style.transform = `translate(${x * 0.05}px, ${y * 0.05}px)`;
  });

  card.addEventListener('mouseleave', () => {
    card.style.transform = 'translate(0,0)';
  });
});
