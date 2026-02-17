const menuToggle = document.getElementById('menuToggle');
const closeMenu = document.getElementById('closeMenu');
const navMenu = document.getElementById('navMenu');
const menuOverlay = document.getElementById('menuOverlay');

// Function to Open
menuToggle.addEventListener('click', () => {
    navMenu.classList.add('active');
    menuOverlay.classList.add('active');
});

// Function to Close
const hideMenu = () => {
    navMenu.classList.remove('active');
    menuOverlay.classList.remove('active');
};

closeMenu.addEventListener('click', hideMenu);
menuOverlay.addEventListener('click', hideMenu);

// Animated Counter for Timeline Years - about section Page

let lastScrollY = window.scrollY;

// Scroll reveal animation
window.addEventListener("scroll", () => {
  const reveals = document.querySelectorAll(".reveal");
  const currentScroll = window.scrollY;

  reveals.forEach(el => {
    const elementTop = el.getBoundingClientRect().top;

    if (elementTop < window.innerHeight - 120) {
      el.classList.add("active");

      if (currentScroll > lastScrollY) {
        el.style.transform += " translateY(8px)";
      } else {
        el.style.transform += " translateY(-8px)";
      }
    }
  });

  lastScrollY = currentScroll;
});

// Year counter animation
const years = document.querySelectorAll(".year");

years.forEach(year => {
  const target = parseInt(year.innerText, 10);
  let count = 0;

  const animate = () => {
    if (count < target) {
      count += Math.ceil(target / 80);
      year.innerText = count;
      requestAnimationFrame(animate);
    } else {
      year.innerText = target;
    }
  };

  animate();
});

