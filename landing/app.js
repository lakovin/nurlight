// Визитка Nurlight для ресторанов на трёх языках (RU / KZ / EN) и демо-чат бота в телефоне.
// Тексты страницы — в словаре I18N: элементы с data-i18n берут текст по ключу, data-i18n-html — разметку.

var I18N = {
  ru: {
    title: "Nurlight — Telegram-бот для заказов в вашем ресторане",
    desc: "Свой Telegram-бот для заказов и панель для оператора и кухни — под брендом ресторана. Подписка без комиссии с заказов.",
    nav_product: "Что получает ресторан", nav_flow: "Как идёт заказ", nav_start: "Подключение",
    contact: "Написать нам", try_demo: "Попробовать демо-бота",
    eyebrow: "Для ресторанов и кафе",
    h1: 'Свой <span class="nw">Telegram-бот</span> для заказов — под брендом вашего ресторана',
    lead: "Клиенты заказывают и платят в боте, оператор и кухня ведут заказ в панели. Подписка без комиссии с заказов.",
    steps_title: "Так заказывает ваш клиент:",
    s1b: "Открывает бота", s1s: "Меню ресторана — в Telegram",
    s2b: "Собирает корзину и платит", s2s: "Геолокация вместо адреса, оплата картой в чате",
    s3b: "Следит за заказом", s3s: "Статус приходит сообщением от бота",
    phone_label: "Пример заказа в Telegram-боте ресторана", phone_note: "Демо: так будет выглядеть бот вашего ресторана",
    tg_sub: "бот", tg_input: "Сообщение",
    product_title: "Что получает ресторан",
    p1h: "Бот для клиентов", p1p: "Меню, корзина, оплата картой прямо в Telegram, статусы заказа. Русский, казахский и английский. ИИ-консультант отвечает на вопросы о меню и доставке.",
    p2h: "Панель оператора", p2p: "Все заказы в одном списке: принять, назначить курьера, отменить. Геолокация клиента открывается на карте.",
    p3h: "Экран кухни", p3p: "Повар видит только свои заказы и двигает их кнопками: «Готовится», «Упаковывается», «Готов».",
    p4h: "Статистика руководителя", p4p: "Выручка, средний чек, популярные блюда и загрузка курьеров — за неделю, месяц или всё время.",
    flow_title: "Как идёт заказ",
    w_client: "Клиент", w_operator: "Оператор", w_kitchen: "Кухня", w_courier: "Курьер",
    f1: "Заказывает и платит в боте", f2: "Принимает заказ", f3: "Готовит и упаковывает", f4: "Забирает и везёт", f5: "Получает заказ",
    flow_note: "На каждом шаге клиент получает сообщение от бота — звонить и уточнять не нужно.",
    mock_title: "Панель · Кухня", m_no: "Номер", m_dishes: "Блюда", m_status: "Статус",
    m_row1: "Пепперони × 1, Морс × 2", m_row2: "Маргарита × 2", m_row3: "Четыре сыра × 1, Айран × 1",
    st_cooking: "Готовится", st_packing: "Упаковывается", st_accepted: "Принят",
    a_cook: "Начать готовить", a_pack: "Упаковать", a_ready: "Готово",
    mock_caption: "Экран кухни в панели. Данные демонстрационные.",
    model_title: "Как мы работаем",
    m1h: "Внедрение", m1p: "Разово: бот и панель под ваш бренд, загрузка меню, обучение команды.",
    m2h: "Подписка", m2p: "Каждый месяц: работа бота и панели, обновления и поддержка.",
    on_request: "по запросу",
    t1: "Без комиссии с заказов", t2: "Курьеры, меню и клиентская база остаются у ресторана", t3: "Оплата картой — через платёжный сервис ресторана",
    start_title: "Как подключиться",
    c1h: "Знакомство", c1p: "Показываем демо-бота и панель на ваших задачах.",
    c2h: "Меню и бренд", c2p: "Собираем меню с ценами и фото, цены доставки, название и логотип.",
    c3h: "Настройка", c3p: "Запускаем бота ресторана и панель, заводим оператора, кухню и курьеров.",
    c4h: "Запуск", c4p: "Обучаем команду и проводим первые заказы вместе.",
    cta_h: "Посмотрите, как это работает", cta_p: "Откройте демо-бота и закажите что-нибудь — оплата тестовая, деньги не списываются.",
    foot: "© 2026 · Дипломный проект",
    r_label: "Чек", r_total: "Итого", r_included: "входит в подписку",
    chat: {
      greet: "Здравствуйте! Я бот службы доставки Nurlight. Здесь можно выбрать блюда и оформить заказ.",
      kb: ["Меню", "Корзина", "Мои заказы"],
      catalog: "Меню",
      dish: "Пепперони", dish_desc: "Томатный соус, моцарелла, пепперони", to_cart: "В корзину",
      cart: "Пепперони × 1 — 3 400 ₸<br>Доставка — 500 ₸<br><b>Итого: 3 900 ₸</b>",
      checkout: "Отправить геолокацию",
      location: "Геопозиция", location_note: "кв. 5, подъезд 2",
      invoice: "<b>Счёт за заказ</b><br>3 900 ₸ · оплата картой", pay: "Оплатить 3 900 ₸",
      created: "Оплата прошла. Заказ №1 передан ресторану.",
      order: "Заказ №1", updated: " — статус обновлён", done: " доставлен. Спасибо!",
      labels: ["Принят", "Готовится", "Готов", "В пути", "Доставлен"]
    }
  },
  kk: {
    title: "Nurlight — мейрамханаңызға арналған тапсырыс Telegram-боты",
    desc: "Мейрамхана брендімен тапсырыс қабылдайтын жеке Telegram-бот және оператор мен асханаға арналған панель. Тапсырыстан комиссиясыз жазылым.",
    nav_product: "Мейрамхана не алады", nav_flow: "Тапсырыс қалай өтеді", nav_start: "Қосылу",
    contact: "Бізге жазу", try_demo: "Демо-ботты сынап көру",
    eyebrow: "Мейрамханалар мен кафелер үшін",
    h1: 'Мейрамханаңыздың брендімен тапсырыс қабылдайтын жеке <span class="nw">Telegram-бот</span>',
    lead: "Клиенттер ботта тапсырыс беріп, төлейді, ал оператор мен асхана тапсырысты панельде жүргізеді. Тапсырыстан комиссиясыз жазылым.",
    steps_title: "Клиентіңіз осылай тапсырыс береді:",
    s1b: "Ботты ашады", s1s: "Мейрамхана мәзірі — Telegram-да",
    s2b: "Себетті толтырып, төлейді", s2s: "Мекенжай орнына геолокация, чатта картамен төлем",
    s3b: "Тапсырысты бақылайды", s3s: "Мәртебе боттан хабарлама болып келеді",
    phone_label: "Мейрамхана Telegram-ботындағы тапсырыс мысалы", phone_note: "Демо: мейрамханаңыздың боты осындай болады",
    tg_sub: "бот", tg_input: "Хабарлама",
    product_title: "Мейрамхана не алады",
    p1h: "Клиенттерге арналған бот", p1p: "Мәзір, себет, тікелей Telegram-да картамен төлем, тапсырыс мәртебелері. Орыс, қазақ және ағылшын тілдері. AI-кеңесші мәзір мен жеткізу туралы сұрақтарға жауап береді.",
    p2h: "Оператор панелі", p2p: "Барлық тапсырыс бір тізімде: қабылдау, курьер тағайындау, бас тарту. Клиенттің геолокациясы картада ашылады.",
    p3h: "Асхана экраны", p3p: "Аспаз тек өз тапсырыстарын көреді және оларды батырмалармен жылжытады: «Дайындалуда», «Оралуда», «Дайын».",
    p4h: "Басшыға арналған статистика", p4p: "Түсім, орташа чек, танымал тағамдар және курьерлердің жүктемесі — апта, ай немесе барлық уақыт бойынша.",
    flow_title: "Тапсырыс қалай өтеді",
    w_client: "Клиент", w_operator: "Оператор", w_kitchen: "Асхана", w_courier: "Курьер",
    f1: "Ботта тапсырыс беріп, төлейді", f2: "Тапсырысты қабылдайды", f3: "Дайындап, орайды", f4: "Алып, жеткізеді", f5: "Тапсырысты алады",
    flow_note: "Әр қадамда клиент боттан хабарлама алады — қоңырау шалып, нақтылаудың қажеті жоқ.",
    mock_title: "Панель · Асхана", m_no: "Нөмір", m_dishes: "Тағамдар", m_status: "Мәртебе",
    m_row1: "Пепперони × 1, Морс × 2", m_row2: "Маргарита × 2", m_row3: "Төрт ірімшік × 1, Айран × 1",
    st_cooking: "Дайындалуда", st_packing: "Оралуда", st_accepted: "Қабылданды",
    a_cook: "Дайындауды бастау", a_pack: "Орау", a_ready: "Дайын",
    mock_caption: "Панельдегі асхана экраны. Деректер демонстрациялық.",
    model_title: "Қалай жұмыс істейміз",
    m1h: "Енгізу", m1p: "Бір рет: брендіңізге бот пен панель, мәзірді жүктеу, команданы оқыту.",
    m2h: "Жазылым", m2p: "Ай сайын: бот пен панельдің жұмысы, жаңартулар және қолдау.",
    on_request: "сұраныс бойынша",
    t1: "Тапсырыстан комиссия жоқ", t2: "Курьерлер, мәзір және клиенттер базасы мейрамханада қалады", t3: "Картамен төлем — мейрамхананың төлем қызметі арқылы",
    start_title: "Қалай қосылуға болады",
    c1h: "Танысу", c1p: "Демо-бот пен панельді сіздің міндеттеріңізге көрсетеміз.",
    c2h: "Мәзір және бренд", c2p: "Баға мен суреті бар мәзірді, жеткізу бағасын, атауы мен логотипті жинаймыз.",
    c3h: "Баптау", c3p: "Мейрамхана боты мен панельді іске қосамыз, оператор, асхана және курьерлерді қосамыз.",
    c4h: "Іске қосу", c4p: "Команданы оқытып, алғашқы тапсырыстарды бірге өткіземіз.",
    cta_h: "Қалай жұмыс істейтінін көріңіз", cta_p: "Демо-ботты ашып, бірдеңе тапсырыс беріңіз — төлем сынақ режимінде, ақша алынбайды.",
    foot: "© 2026 · Дипломдық жоба",
    r_label: "Чек", r_total: "Барлығы", r_included: "жазылымға кіреді",
    chat: {
      greet: "Сәлеметсіз бе! Мен Nurlight жеткізу қызметінің ботымын. Мұнда тағам таңдап, тапсырыс беруге болады.",
      kb: ["Мәзір", "Себет", "Менің тапсырыстарым"],
      catalog: "Мәзір",
      dish: "Пепперони", dish_desc: "Томат соусы, моцарелла, пепперони", to_cart: "Себетке",
      cart: "Пепперони × 1 — 3 400 ₸<br>Жеткізу — 500 ₸<br><b>Барлығы: 3 900 ₸</b>",
      checkout: "Геолокация жіберу",
      location: "Геолокация", location_note: "5-пәтер, 2-кіреберіс",
      invoice: "<b>Тапсырыс шоты</b><br>3 900 ₸ · картамен төлем", pay: "3 900 ₸ төлеу",
      created: "Төлем өтті. №1 тапсырыс мейрамханаға берілді.",
      order: "№1 тапсырыс", updated: " — мәртебе жаңартылды", done: " жеткізілді. Рақмет!",
      labels: ["Қабылданды", "Дайындалуда", "Дайын", "Жолда", "Жеткізілді"]
    }
  },
  en: {
    title: "Nurlight — an ordering Telegram bot for your restaurant",
    desc: "Your own Telegram bot for orders plus a panel for operators and the kitchen — under your restaurant's brand. Subscription, no commission on orders.",
    nav_product: "What you get", nav_flow: "How an order flows", nav_start: "Getting started",
    contact: "Contact us", try_demo: "Try the demo bot",
    eyebrow: "For restaurants and cafés",
    h1: 'Your own <span class="nw">Telegram bot</span> for orders — under your restaurant’s brand',
    lead: "Customers order and pay in the bot, your operator and kitchen run the order in the panel. Subscription with no commission on orders.",
    steps_title: "This is how your customer orders:",
    s1b: "Opens the bot", s1s: "Your menu, right in Telegram",
    s2b: "Fills the cart and pays", s2s: "Location instead of an address, card payment in the chat",
    s3b: "Tracks the order", s3s: "Status updates arrive as bot messages",
    phone_label: "Example of an order in a restaurant’s Telegram bot", phone_note: "Demo: this is how your restaurant’s bot will look",
    tg_sub: "bot", tg_input: "Message",
    product_title: "What the restaurant gets",
    p1h: "A bot for customers", p1p: "Menu, cart, card payment right in Telegram, order statuses. Russian, Kazakh and English. An AI assistant answers questions about the menu and delivery.",
    p2h: "Operator panel", p2p: "All orders in one list: accept, assign a courier, cancel. The customer’s location opens on a map.",
    p3h: "Kitchen screen", p3p: "Cooks see only their orders and move them with buttons: “Cooking”, “Packing”, “Ready”.",
    p4h: "Manager statistics", p4p: "Revenue, average order, popular dishes and courier load — for a week, a month or all time.",
    flow_title: "How an order flows",
    w_client: "Customer", w_operator: "Operator", w_kitchen: "Kitchen", w_courier: "Courier",
    f1: "Orders and pays in the bot", f2: "Accepts the order", f3: "Cooks and packs", f4: "Picks up and delivers", f5: "Receives the order",
    flow_note: "At every step the customer gets a message from the bot — no calls to check on the order.",
    mock_title: "Panel · Kitchen", m_no: "Number", m_dishes: "Dishes", m_status: "Status",
    m_row1: "Pepperoni × 1, Mors × 2", m_row2: "Margherita × 2", m_row3: "Four cheese × 1, Ayran × 1",
    st_cooking: "Cooking", st_packing: "Packing", st_accepted: "Accepted",
    a_cook: "Start cooking", a_pack: "Pack", a_ready: "Done",
    mock_caption: "Kitchen screen in the panel. Demo data.",
    model_title: "How we work",
    m1h: "Setup", m1p: "One-time: bot and panel with your brand, menu upload, team training.",
    m2h: "Subscription", m2p: "Monthly: running the bot and panel, updates and support.",
    on_request: "on request",
    t1: "No commission on orders", t2: "Couriers, menu and customer base stay with the restaurant", t3: "Card payments go through the restaurant’s payment provider",
    start_title: "Getting started",
    c1h: "Intro", c1p: "We show the demo bot and panel on your use cases.",
    c2h: "Menu and brand", c2p: "We collect the menu with prices and photos, delivery prices, name and logo.",
    c3h: "Setup", c3p: "We launch the restaurant’s bot and panel and add the operator, kitchen and couriers.",
    c4h: "Launch", c4p: "We train your team and run the first orders together.",
    cta_h: "See how it works", cta_p: "Open the demo bot and order something — payment is in test mode, no money is charged.",
    foot: "© 2026 · Diploma project",
    r_label: "Receipt", r_total: "Total", r_included: "included in the subscription",
    chat: {
      greet: "Hello! I am the Nurlight delivery bot. Here you can pick dishes and place an order.",
      kb: ["Menu", "Cart", "My orders"],
      catalog: "Menu",
      dish: "Pepperoni", dish_desc: "Tomato sauce, mozzarella, pepperoni", to_cart: "Add to cart",
      cart: "Pepperoni × 1 — 3,400 ₸<br>Delivery — 500 ₸<br><b>Total: 3,900 ₸</b>",
      checkout: "Send location",
      location: "Location", location_note: "apt 5, entrance 2",
      invoice: "<b>Order bill</b><br>3,900 ₸ · card payment", pay: "Pay 3,900 ₸",
      created: "Payment received. Order #1 sent to the restaurant.",
      order: "Order #1", updated: " — status updated", done: " delivered. Thank you!",
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
      [1, 500, typing()],
      [1, 700, invoice()],
      [1, 900, payTap()],
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
  // Счёт прямо в чате — оплата картой во встроенных платежах Telegram
  function invoice() {
    return function () {
      add(el("msg in", t.invoice + "<time>" + now() + '</time><div class="kb"><span data-pay>' + t.pay + "</span></div>"));
    };
  }
  function payTap() {
    return function () { var b = feed.querySelector("[data-pay]"); if (b) b.classList.add("tap"); };
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
  var items = document.querySelectorAll(".section .card, .section .receipt, .section-title, .cta");
  if (!reduced && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("shown"); io.unobserve(e.target); }
      });
    }, { threshold: 0.15 });
    items.forEach(function (el) { el.classList.add("will-show"); io.observe(el); });
  }
})();

// ---------- Фон с иконками: сдвигается медленнее страницы ----------
// Двигается один слой через transform — это делает видеокарта, без пересчёта страницы.
(function () {
  var layer = document.querySelector(".doodles");
  var TILE = 240; // размер плитки узора, см. style.css
  if (!layer || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var queued = false;
  function move() {
    queued = false;
    var shift = (window.scrollY * 0.25) % TILE;
    layer.style.transform = "translate3d(0," + (-shift).toFixed(1) + "px,0)";
  }
  window.addEventListener("scroll", function () {
    if (!queued) { queued = true; requestAnimationFrame(move); }
  }, { passive: true });
  move();
})();
