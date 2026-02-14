const nav = document.getElementById("main-nav");
const menuBtn = document.querySelector(".menu-toggle");

if (menuBtn && nav) {
  menuBtn.addEventListener("click", () => {
    const isOpen = nav.classList.toggle("open");
    menuBtn.setAttribute("aria-expanded", String(isOpen));
  });

  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      nav.classList.remove("open");
      menuBtn.setAttribute("aria-expanded", "false");
    });
  });
}

const revealEls = document.querySelectorAll(".reveal");

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.18 },
);

revealEls.forEach((el) => revealObserver.observe(el));

const counters = document.querySelectorAll("[data-count]");

const counterObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const target = Number(el.getAttribute("data-count") || 0);
      let value = 0;
      const step = Math.max(1, Math.floor(target / 24));

      const timer = setInterval(() => {
        value += step;
        if (value >= target) {
          value = target;
          clearInterval(timer);
        }
        el.textContent = `${value}+`;
      }, 26);

      counterObserver.unobserve(el);
    });
  },
  { threshold: 0.42 },
);

counters.forEach((el) => counterObserver.observe(el));
