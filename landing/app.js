// Анимация коробки: прогресс прокрутки блока #unbox (0…1) → CSS-переменные сцены
(function () {
  var unbox = document.getElementById("unbox");
  // Переменные ставим на сцену, а не на всю страницу: иначе каждый кадр пересчитываются стили всех элементов
  var stage = unbox.querySelector(".stage");
  var scene = unbox.querySelector(".scene");
  var size = 0, total = 1, top = 0;
  var last = {};

  // Размеры меряем только при загрузке и изменении окна, не в каждом кадре
  function measure() {
    size = scene.offsetWidth;
    total = Math.max(1, unbox.offsetHeight - window.innerHeight);
    top = unbox.getBoundingClientRect().top + window.scrollY;
  }
  function set(name, value) {
    if (last[name] !== value) { last[name] = value; stage.style.setProperty(name, value); }
  }
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
    set("--lid", (open * 112).toFixed(1) + "deg");
    set("--tilt", mix(60, 40, look).toFixed(2) + "deg");
    set("--turn", mix(-24, -8, look).toFixed(2) + "deg");
    set("--rise", (rise * size * 0.16).toFixed(1) + "px");
    set("--spin", (rise * 40).toFixed(1) + "deg");
    set("--steam", seg(p, 0.45, 0.65).toFixed(2));

    var shown = seg(p, 0.62, 0.86);
    set("--intro", (1 - seg(p, 0, 0.18)).toFixed(3));
    set("--shown", shown.toFixed(3));
    var interactive = shown > 0.5 ? "auto" : "none";
    if (last.pe !== interactive) { last.pe = interactive; reveal.style.pointerEvents = interactive; }
  }

  function progress() {
    return clamp((window.scrollY - top) / total);
  }

  if (reduced) {
    measure();
    render(1);
  } else {
    var queued = false;
    var update = function () {
      if (queued) return;
      queued = true;
      requestAnimationFrame(function () { queued = false; render(progress()); });
    };
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", function () { measure(); update(); });
    measure();
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
