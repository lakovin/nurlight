// Первый экран: телефон с чатом бота один раз проигрывает заказ, когда появляется на экране.
// Шаги слева подсвечиваются вместе с чатом, клик по шагу перематывает к нему.
(function () {
  var feed = document.getElementById("feed");
  var steps = Array.prototype.slice.call(document.querySelectorAll(".step"));
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var pizza = document.getElementById("pizza").innerHTML;
  var timers = [];

  // Сценарий: [этап, задержка до шага (мс), что показать]
  var script = [
    [0, 300, out("/start")],
    [0, 500, typing()],
    [0, 700, inMsg("Здравствуйте! Я бот службы доставки Nurlight. Здесь можно выбрать блюда и оформить заказ.", ["Каталог", "Корзина", "Мои заказы"], 0)],
    [1, 900, out("Каталог")],
    [1, 500, typing()],
    [1, 700, card()],
    [1, 900, tap()],
    [1, 600, inMsg("Корзина: Пепперони × 1 = 3 400 ₸", ["Оформить заказ"])],
    [1, 900, out("Абая 10, кв. 5")],
    [2, 500, typing()],
    [2, 700, inMsg("Заказ №000123 создан. Ожидает подтверждения оператора.")],
    [2, 900, status(1)],
    [2, 1100, status(2)],
    [2, 1100, status(3)],
    [2, 1100, status(4)]
  ];

  function el(cls, html) { var d = document.createElement("div"); d.className = cls; d.innerHTML = html; return d; }
  function now() { return "12:" + String(10 + feed.children.length).padStart(2, "0"); }
  function out(text) { return function () { add(el("msg out", text + "<time>" + now() + "</time>")); }; }
  function inMsg(text, buttons, tapIndex) {
    return function () {
      var kb = buttons ? '<div class="kb">' + buttons.map(function (b) { return "<span>" + b + "</span>"; }).join("") + "</div>" : "";
      add(el("msg in", text + "<time>" + now() + "</time>" + kb));
    };
  }
  function card() {
    return function () {
      add(el("msg in card-msg", '<div class="ph">' + pizza + '</div><div class="body"><b>Пепперони</b><br>Томатный соус, моцарелла, пепперони<br><b>3 400 ₸</b><time>' + now() + '</time></div><div class="kb"><span data-cart>В корзину</span></div>'));
    };
  }
  function tap() {
    return function () { var b = feed.querySelector("[data-cart]"); if (b) b.classList.add("tap"); };
  }
  var LABELS = ["Новый", "Принят", "Передан курьеру", "В пути", "Доставлен"];
  function status(level) {
    return function () {
      var html = '<b>Заказ №000123</b>' + (level === 4 ? " доставлен. Спасибо!" : " — статус обновлён") +
        '<div class="status">' + LABELS.map(function (l, i) {
          var cls = i < level ? "on" : i === level ? (level === 4 ? "on" : "now") : "";
          return '<i class="' + cls + '">' + l + "</i>";
        }).join("") + "</div><time>" + now() + "</time>";
      // Статус обновляется в одном сообщении, как в боте
      var old = feed.querySelector("[data-status]");
      if (old) { old.innerHTML = html; old.style.animation = "none"; old.offsetHeight; old.style.animation = ""; }
      else { var m = el("msg in", html); m.setAttribute("data-status", ""); add(m); }
    };
  }
  function typing() {
    var fn = function () { add(el("typing", "<b></b><b></b><b></b>")); };
    fn.isTyping = true;
    return fn;
  }
  function add(node) {
    var t = feed.querySelector(".typing");
    if (t) t.remove();
    feed.appendChild(node);
    // В ленте остаются только последние сообщения, как в узком экране телефона
    while (feed.scrollHeight > feed.clientHeight && feed.children.length > 1) feed.removeChild(feed.firstChild);
  }
  function mark(stage) { steps.forEach(function (s, i) { s.classList.toggle("active", i === stage); }); }

  function stop() { timers.forEach(clearTimeout); timers = []; }
  // Проиграть с шага from; instant — без задержек (перемотка и «уменьшение движения»)
  function play(from, instant) {
    stop();
    feed.innerHTML = "";
    var t = 0;
    script.forEach(function (row, i) {
      var stage = row[0], delay = row[1], fn = row[2];
      // Уже прошедшие шаги показываем сразу, без анимации и «печатает…»
      if (i < from || instant) { if (!fn.isTyping) { fn(); mark(stage); } return; }
      t += delay;
      timers.push(setTimeout(function () { mark(stage); fn(); }, t));
    });
    Array.prototype.forEach.call(feed.querySelectorAll(".msg"), function (m) { m.style.animation = "none"; });
    if (instant) mark(script[script.length - 1][0]);
  }
  // Клик по шагу — перемотать к началу этого этапа и проиграть дальше
  steps.forEach(function (s, idx) {
    s.addEventListener("click", function () {
      var from = script.findIndex(function (r) { return r[0] === idx; });
      play(from, false);
      mark(idx);
    });
  });
  document.getElementById("replay").addEventListener("click", function () { play(0, reduced); });

  // Проигрывается один раз, когда телефон появился на экране
  if (reduced || !("IntersectionObserver" in window)) { play(0, true); return; }
  var io = new IntersectionObserver(function (entries) {
    if (entries[0].isIntersecting) { play(0, false); io.disconnect(); }
  }, { threshold: 0.4 });
  io.observe(document.querySelector(".phone"));
})();

// Секции ниже мягко появляются при прокрутке
(function () {
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
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
