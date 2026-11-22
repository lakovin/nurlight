// Анимация коробки: прогресс прокрутки блока #unbox (0…1) → CSS-переменные сцены
(function () {
  var root = document.documentElement;
  var unbox = document.getElementById("unbox");
  var intro = document.querySelector("[data-fade=out]");
  var reveal = document.querySelector("[data-fade=in]");
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function clamp(v) { return Math.min(1, Math.max(0, v)); }
  // Отрезок прогресса [a, b] → 0…1 с плавным началом и концом
  function seg(p, a, b) {
    var t = clamp((p - a) / (b - a));
    return t * t * (3 - 2 * t);
  }
  function mix(a, b, t) { return a + (b - a) * t; }

  function render(p) {
    var open = seg(p, 0.08, 0.5);      // крышка
    var rise = seg(p, 0.38, 0.72);     // пицца поднимается
    var look = seg(p, 0.2, 0.75);      // камера заглядывает внутрь
    var size = unbox.querySelector(".scene").offsetWidth;

    root.style.setProperty("--lid", (open * 112).toFixed(2) + "deg");
    root.style.setProperty("--tilt", mix(60, 40, look).toFixed(2) + "deg");
    root.style.setProperty("--turn", mix(-24, -8, look).toFixed(2) + "deg");
    root.style.setProperty("--rise", (rise * size * 0.16).toFixed(1) + "px");
    root.style.setProperty("--spin", (rise * 40).toFixed(2) + "deg");
    root.style.setProperty("--steam", seg(p, 0.45, 0.65).toFixed(3));

    intro.style.opacity = (1 - seg(p, 0, 0.18)).toFixed(3);
    var shown = seg(p, 0.62, 0.86);
    reveal.style.opacity = shown.toFixed(3);
    reveal.style.transform = "translateY(" + ((1 - shown) * 30).toFixed(1) + "px)";
    reveal.style.pointerEvents = shown > 0.5 ? "auto" : "none";
  }

  function progress() {
    var rect = unbox.getBoundingClientRect();
    var total = unbox.offsetHeight - window.innerHeight;
    return clamp(-rect.top / total);
  }

  if (reduced) {
    render(1);
  } else {
    var queued = false;
    var update = function () {
      if (queued) return;
      queued = true;
      requestAnimationFrame(function () { queued = false; render(progress()); });
    };
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    render(progress());
  }

  // Секции ниже мягко появляются при прокрутке
  var items = document.querySelectorAll(".section .card, .section-title, .cta");
  if (!reduced && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("shown"); io.unobserve(e.target); }
      });
    }, { threshold: 0.15 });
    items.forEach(function (el) { el.classList.add("will-show"); io.observe(el); });
  }
})();
