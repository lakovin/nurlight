// Визитка на трёх языках (RU / KZ / EN) и чат бота в телефоне.
// Тексты страницы — в словаре I18N: элементы с data-i18n берут текст по ключу, data-i18n-html — разметку.

var I18N = {
  ru: {
    title: "Nurlight — доставка пиццы через Telegram",
    desc: "Пицца и напитки с доставкой по городу. Заказ и статус заказа — в Telegram-боте Nurlight.",
    open_bot: "Открыть бота",
    eyebrow: "Доставка по городу",
    h1: 'Пицца с доставкой — заказ через <span class="nw">Telegram-бот</span>',
    lead: "Меню, корзина и статус заказа — в одном чате. Приложение и регистрация не нужны.",
    s1b: "Откройте бота", s1s: "/start — и меню под рукой",
    s2b: "Соберите корзину", s2s: "Блюда и геолокация для доставки",
    s3b: "Следите за заказом", s3s: "Статус обновляется в чате",
    order: "Заказать в Telegram",
    phone_label: "Пример заказа в Telegram-боте Nurlight",
    tg_sub: "бот", tg_input: "Сообщение",
    why: "Почему через Telegram",
    f1h: "Не нужно приложение", f1p: "Бот открывается прямо в Telegram — без установки и пароля.",
    f2h: "Состав и статус каждого заказа", f2p: "Раздел «Мои заказы» показывает, что заказано и на каком этапе заказ.",
    f3h: "Ответы на вопросы в чате", f3p: "Спросите бота, что взять на компанию или сколько стоит доставка — ответит ИИ-консультант.",
    f4h: "Доставка 500 ₸", f4p: "От 5 000 ₸ — бесплатно. Адрес не нужно печатать: достаточно отправить геолокацию.",
    cta_h: "Меню и цены — в боте", cta_p: "@nurlight_delivery_bot в Telegram",
    foot: "© 2026 · Дипломный проект",
    chat: {
      greet: "Здравствуйте! Я бот службы доставки Nurlight. Здесь можно выбрать блюда и оформить заказ.",
      kb: ["Каталог", "Корзина", "Мои заказы"],
      catalog: "Каталог",
      dish: "Пепперони", dish_desc: "Томатный соус, моцарелла, пепперони", to_cart: "В корзину",
      cart: "Пепперони × 1 — 3 400 ₸<br>Доставка — 500 ₸<br><b>Итого: 3 900 ₸</b>",
      checkout: "Отправить геолокацию",
      location: "Геопозиция", location_note: "кв. 5, подъезд 2",
      created: "Заказ №000123 создан. Ожидает подтверждения оператора.",
      order: "Заказ №000123", updated: " — статус обновлён", done: " доставлен. Спасибо!",
      labels: ["Принят", "Готовится", "Готов", "В пути", "Доставлен"]
    }
  },
  kk: {
    title: "Nurlight — Telegram арқылы пицца жеткізу",
    desc: "Қала бойынша пицца мен сусындар жеткізу. Тапсырыс пен оның мәртебесі — Nurlight Telegram-ботында.",
    open_bot: "Ботты ашу",
    eyebrow: "Қала бойынша жеткізу",
    h1: 'Пицца жеткізу — тапсырыс <span class="nw">Telegram-бот</span> арқылы',
    lead: "Мәзір, себет және тапсырыс мәртебесі — бір чатта. Қосымша орнатудың және тіркелудің қажеті жоқ.",
    s1b: "Ботты ашыңыз", s1s: "/start — мәзір әрдайым қолыңызда",
    s2b: "Себетті толтырыңыз", s2s: "Тағамдар және жеткізуге геолокация",
    s3b: "Тапсырысты бақылаңыз", s3s: "Мәртебе чатта жаңарып отырады",
    order: "Telegram-да тапсырыс беру",
    phone_label: "Nurlight Telegram-ботындағы тапсырыс мысалы",
    tg_sub: "бот", tg_input: "Хабарлама",
    why: "Неге Telegram арқылы",
    f1h: "Қосымша қажет емес", f1p: "Бот тікелей Telegram-да ашылады — орнатусыз және құпиясөзсіз.",
    f2h: "Әр тапсырыстың құрамы мен мәртебесі", f2p: "«Менің тапсырыстарым» бөлімі не тапсырыс берілгенін және тапсырыс қай кезеңде екенін көрсетеді.",
    f3h: "Сұрақтарға чатта жауап", f3p: "Ботқа компанияға не алу керектігін немесе жеткізу қанша тұратынын сұраңыз — AI-кеңесші жауап береді.",
    f4h: "Жеткізу 500 ₸", f4p: "5 000 ₸-ден бастап — тегін. Мекенжайды теру қажет емес: геолокацияны жіберу жеткілікті.",
    cta_h: "Мәзір мен бағалар — ботта", cta_p: "Telegram-дағы @nurlight_delivery_bot",
    foot: "© 2026 · Дипломдық жоба",
    chat: {
      greet: "Сәлеметсіз бе! Мен Nurlight жеткізу қызметінің ботымын. Мұнда тағам таңдап, тапсырыс беруге болады.",
      kb: ["Каталог", "Себет", "Менің тапсырыстарым"],
      catalog: "Каталог",
      dish: "Пепперони", dish_desc: "Томат соусы, моцарелла, пепперони", to_cart: "Себетке",
      cart: "Пепперони × 1 — 3 400 ₸<br>Жеткізу — 500 ₸<br><b>Барлығы: 3 900 ₸</b>",
      checkout: "Геолокация жіберу",
      location: "Геолокация", location_note: "5-пәтер, 2-кіреберіс",
      created: "№000123 тапсырыс құрылды. Оператордың растауын күтуде.",
      order: "№000123 тапсырыс", updated: " — мәртебе жаңартылды", done: " жеткізілді. Рақмет!",
      labels: ["Қабылданды", "Дайындалуда", "Дайын", "Жолда", "Жеткізілді"]
    }
  },
  en: {
    title: "Nurlight — pizza delivery via Telegram",
    desc: "Pizza and drinks delivered across the city. Order and track it in the Nurlight Telegram bot.",
    open_bot: "Open the bot",
    eyebrow: "Delivery across the city",
    h1: 'Pizza delivery — order through a <span class="nw">Telegram bot</span>',
    lead: "Menu, cart and order status in one chat. No app and no sign-up.",
    s1b: "Open the bot", s1s: "/start — and the menu is at hand",
    s2b: "Fill your cart", s2s: "Dishes and your location for delivery",
    s3b: "Track your order", s3s: "Status updates right in the chat",
    order: "Order in Telegram",
    phone_label: "Example of an order in the Nurlight Telegram bot",
    tg_sub: "bot", tg_input: "Message",
    why: "Why Telegram",
    f1h: "No app needed", f1p: "The bot opens right in Telegram — nothing to install, no password.",
    f2h: "Items and status of every order", f2p: "“My orders” shows what you ordered and which stage it is at.",
    f3h: "Answers in the chat", f3p: "Ask the bot what to get for a group or how much delivery costs — the AI assistant replies.",
    f4h: "Delivery 500 ₸", f4p: "Free from 5,000 ₸. No need to type an address — just send your location.",
    cta_h: "Menu and prices are in the bot", cta_p: "@nurlight_delivery_bot on Telegram",
    foot: "© 2026 · Diploma project",
    chat: {
      greet: "Hello! I am the Nurlight delivery bot. Here you can pick dishes and place an order.",
      kb: ["Catalog", "Cart", "My orders"],
      catalog: "Catalog",
      dish: "Pepperoni", dish_desc: "Tomato sauce, mozzarella, pepperoni", to_cart: "Add to cart",
      cart: "Pepperoni × 1 — 3,400 ₸<br>Delivery — 500 ₸<br><b>Total: 3,900 ₸</b>",
      checkout: "Send location",
      location: "Location", location_note: "apt 5, entrance 2",
      created: "Order #000123 created. Waiting for the operator to confirm.",
      order: "Order #000123", updated: " — status updated", done: " delivered. Thank you!",
      labels: ["Accepted", "Cooking", "Ready", "On the way", "Delivered"]
    }
  }
};

var LANGS = ["ru", "kk", "en"];

// Язык: выбранный раньше → язык браузера → русский. Хранилище может быть недоступно — тогда без запоминания
function initialLang() {
  try {
    var saved = localStorage.getItem("lang");
    if (LANGS.indexOf(saved) !== -1) return saved;
  } catch (e) {}
  var nav = (navigator.language || "").slice(0, 2);
  if (nav === "kk") return "kk";
  if (nav === "en") return "en";
  return "ru";
}

// ---------- Чат бота в телефоне ----------
var Chat = (function () {
  var feed = document.getElementById("feed");
  var steps = Array.prototype.slice.call(document.querySelectorAll(".step"));
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var pizza = document.getElementById("pizza").innerHTML;
  var timers = [];
  var visible = false;
  var t = I18N.ru.chat;
  var LOOP_PAUSE = 3000;

  // Сценарий: [этап, задержка до шага (мс), что показать]
  function scenario() {
    return [
      [0, 300, out("/start")],
      [0, 500, typing()],
      [0, 700, inMsg(t.greet, t.kb)],
      [1, 900, out(t.catalog)],
      [1, 500, typing()],
      [1, 700, card()],
      [1, 900, tap()],
      [1, 600, inMsg(t.cart, [t.checkout])],
      [1, 900, location()],
      [2, 500, typing()],
      [2, 700, inMsg(t.created)],
      [2, 900, status(0)],
      [2, 1100, status(1)],
      [2, 1100, status(2)],
      [2, 1100, status(3)],
      [2, 1100, status(4)]
    ];
  }
  var script = [];

  function el(cls, html) { var d = document.createElement("div"); d.className = cls; d.innerHTML = html; return d; }
  function now() { return "12:" + String(10 + feed.children.length).padStart(2, "0"); }
  function out(text) { return function () { add(el("msg out", text + "<time>" + now() + "</time>")); }; }
  function inMsg(text, buttons) {
    return function () {
      var kb = buttons ? '<div class="kb">' + buttons.map(function (b) { return "<span>" + b + "</span>"; }).join("") + "</div>" : "";
      add(el("msg in", text + "<time>" + now() + "</time>" + kb));
    };
  }
  function card() {
    return function () {
      add(el("msg in card-msg", '<div class="ph">' + pizza + '</div><div class="body"><b>' + t.dish + "</b><br>" + t.dish_desc +
        "<br><b>3 400 ₸</b><time>" + now() + '</time></div><div class="kb"><span data-cart>' + t.to_cart + "</span></div>"));
    };
  }
  function tap() {
    return function () { var b = feed.querySelector("[data-cart]"); if (b) b.classList.add("tap"); };
  }
  // Клиент отправляет геолокацию вместо адреса
  function location() {
    return function () {
      add(el("msg out loc", '<div class="map"><span class="pin"></span></div><b>' + t.location + "</b><br>" + t.location_note + "<time>" + now() + "</time>"));
    };
  }
  function status(level) {
    var last = t.labels.length - 1;
    return function () {
      var html = "<b>" + t.order + "</b>" + (level === last ? t.done : t.updated) +
        '<div class="status">' + t.labels.map(function (l, i) {
          var cls = i < level ? "on" : i === level ? (level === last ? "on" : "now") : "";
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
    var ty = feed.querySelector(".typing");
    if (ty) ty.remove();
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
    var time = 0;
    script.forEach(function (row, i) {
      var stage = row[0], delay = row[1], fn = row[2];
      // Уже прошедшие шаги показываем сразу, без анимации и «печатает…»
      if (i < from || instant) { if (!fn.isTyping) { fn(); mark(stage); } return; }
      time += delay;
      timers.push(setTimeout(function () { mark(stage); fn(); }, time));
    });
    // Как гифка: после «Доставлен» пауза — и заказ проигрывается заново
    if (!instant) timers.push(setTimeout(function () { play(0, false); }, time + LOOP_PAUSE));
    Array.prototype.forEach.call(feed.querySelectorAll(".msg"), function (m) { m.style.animation = "none"; });
    if (instant) mark(script[script.length - 1][0]);
  }

  // Клик по шагу — перемотать к началу этого этапа и проиграть дальше
  steps.forEach(function (s, idx) {
    s.addEventListener("click", function () {
      var from = script.findIndex(function (r) { return r[0] === idx; });
      play(from, reduced);
      mark(idx);
    });
  });

  // Крутится по кругу, пока телефон на экране; ушёл с экрана — пауза, чтобы не тратить ресурсы.
  // При «уменьшении движения» чат сразу показан целиком и не крутится.
  if (!reduced && "IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      if (visible) { if (!timers.length) play(0, false); }
      else stop();
    }, { threshold: 0.4 }).observe(document.querySelector(".phone"));
  }

  return {
    // Новый язык — пересобрать сценарий и начать чат заново
    setLang: function (lang) {
      t = I18N[lang].chat;
      script = scenario();
      if (reduced || !("IntersectionObserver" in window)) play(0, true);
      else if (visible) play(0, false);
    }
  };
})();

// ---------- Переключатель языка ----------
(function () {
  var buttons = Array.prototype.slice.call(document.querySelectorAll("[data-lang]"));

  function apply(lang) {
    var dict = I18N[lang];
    document.documentElement.lang = lang;
    document.title = dict.title;
    document.querySelector('meta[name="description"]').setAttribute("content", dict.desc);
    Array.prototype.forEach.call(document.querySelectorAll("[data-i18n]"), function (node) {
      node.textContent = dict[node.getAttribute("data-i18n")];
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-i18n-html]"), function (node) {
      node.innerHTML = dict[node.getAttribute("data-i18n-html")];
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-i18n-label]"), function (node) {
      node.setAttribute("aria-label", dict[node.getAttribute("data-i18n-label")]);
    });
    buttons.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-lang") === lang)); });
    Chat.setLang(lang);
  }

  buttons.forEach(function (b) {
    b.addEventListener("click", function () {
      var lang = b.getAttribute("data-lang");
      try { localStorage.setItem("lang", lang); } catch (e) {}
      apply(lang);
    });
  });
  apply(initialLang());
})();

// ---------- Секции ниже мягко появляются при прокрутке ----------
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
