"""Переводы бота: русский (ru), казахский (kk), английский (en).

Язык клиента хранится в Client.language. Middleware (bot/middlewares.py) кладёт его
в current_lang перед каждым обработчиком, поэтому в обработчиках достаточно t("ключ").
Вне обработчиков (например, уведомления) язык передают явно: t("ключ", lang).

Правила:
- у каждого ключа должны быть все три языка, а плейсхолдеры {name} одинаковы;
  это проверяет скрипт bot/tests_i18n.py (python -m bot.tests_i18n);
- казахские тексты нужно проверить носителю языка.
"""
from contextvars import ContextVar

DEFAULT_LANG = "ru"
LANGS = ("ru", "kk", "en")
LANG_NAMES = {"ru": "🇷🇺 Русский", "kk": "🇰🇿 Қазақша", "en": "🇬🇧 English"}

# Язык текущего обновления Telegram (ставит LanguageMiddleware)
current_lang: ContextVar[str] = ContextVar("current_lang", default=DEFAULT_LANG)

# Старые тексты кнопок, которые ещё могут висеть в чатах у клиентов
LEGACY_VARIANTS = {"btn_ai": ["🤖 AI-помощник"]}


def _(ru: str, kk: str, en: str) -> dict[str, str]:
    return {"ru": ru, "kk": kk, "en": en}


TEXTS: dict[str, dict[str, str]] = {
    # ---------- Главное меню ----------
    "btn_catalog": _("🛍 Каталог", "🛍 Мәзір", "🛍 Catalog"),
    "btn_cart": _("🛒 Корзина", "🛒 Себет", "🛒 Cart"),
    "btn_orders": _("📦 Мои заказы", "📦 Тапсырыстарым", "📦 My orders"),
    "btn_faq": _("❓ Частые вопросы", "❓ Жиі қойылатын сұрақтар", "❓ FAQ"),
    "btn_ai": _("💬 Виртуальный оператор", "💬 Виртуалды оператор", "💬 Virtual operator"),
    "btn_lang": _("🌐 Язык", "🌐 Тіл", "🌐 Language"),

    # ---------- Язык и старт ----------
    "lang_choose": _(
        "🌐 Выберите язык / Тілді таңдаңыз / Choose your language:",
        "🌐 Выберите язык / Тілді таңдаңыз / Choose your language:",
        "🌐 Выберите язык / Тілді таңдаңыз / Choose your language:",
    ),
    "lang_changed": _("✅ Язык: Русский", "✅ Тіл: Қазақша", "✅ Language: English"),
    "start_greeting": _(
        "Здравствуйте, {name}! 👋\nЯ бот службы доставки Nurlight. Здесь можно выбрать товары и оформить заказ.",
        "Сәлеметсіз бе, {name}! 👋\nМен Nurlight жеткізу қызметінің ботымын. Мұнда тауарларды таңдап, тапсырыс бере аласыз.",
        "Hello, {name}! 👋\nI'm the Nurlight delivery bot. Here you can choose items and place an order.",
    ),

    # ---------- Каталог ----------
    "catalog_empty": _(
        "Каталог пока пуст. Загляните позже!",
        "Мәзір әзірге бос. Кейінірек қараңыз!",
        "The catalog is empty for now. Please check back later!",
    ),
    "choose_category": _("Выберите категорию:", "Санатты таңдаңыз:", "Choose a category:"),
    "choose_product": _("Выберите товар:", "Тауарды таңдаңыз:", "Choose an item:"),
    "category_empty": _(
        "В этой категории сейчас нет товаров.",
        "Бұл санатта қазір тауар жоқ.",
        "There are no items in this category right now.",
    ),
    "product_not_found": _("Товар не найден", "Тауар табылмады", "Item not found"),
    "product_price": _("Цена: {price} ₸", "Бағасы: {price} ₸", "Price: {price} ₸"),
    "out_of_stock": _("❌ <b>Нет в наличии</b>", "❌ <b>Қоймада жоқ</b>", "❌ <b>Out of stock</b>"),
    "product_btn_unavailable": _(
        "❌ {name} — нет в наличии",
        "❌ {name} — қоймада жоқ",
        "❌ {name} — out of stock",
    ),
    "btn_to_categories": _("⬅️ К категориям", "⬅️ Санаттарға", "⬅️ To categories"),
    "btn_back": _("⬅️ Назад", "⬅️ Артқа", "⬅️ Back"),
    "btn_open_cart": _("🛒 Открыть корзину", "🛒 Себетті ашу", "🛒 Open cart"),
    "qty_pcs": _("{qty} шт", "{qty} дана", "{qty} pcs"),

    # ---------- Корзина ----------
    "cart_empty": _(
        "Корзина пуста. Загляните в каталог 🛍",
        "Себет бос. Мәзірге кіріп көріңіз 🛍",
        "Your cart is empty. Take a look at the catalog 🛍",
    ),
    "cart_title": _("🛒 <b>Ваша корзина</b>\n", "🛒 <b>Сіздің себетіңіз</b>\n", "🛒 <b>Your cart</b>\n"),
    "cart_total": _("<b>Итого: {total} ₸</b>", "<b>Барлығы: {total} ₸</b>", "<b>Total: {total} ₸</b>"),
    "cart_empty_alert": _("Корзина пуста", "Себет бос", "Your cart is empty"),
    "product_unavailable_alert": _(
        "Товар больше недоступен",
        "Тауар енді қолжетімсіз",
        "This item is no longer available",
    ),
    "cart_cleared": _("Корзина очищена 🗑", "Себет тазаланды 🗑", "Cart cleared 🗑"),
    "btn_checkout": _("✅ Оформить заказ", "✅ Тапсырыс беру", "✅ Place order"),
    "btn_clear": _("🗑 Очистить", "🗑 Тазалау", "🗑 Clear"),

    # ---------- FAQ ----------
    "faq_title": _(
        "❓ <b>Частые вопросы Nurlight</b>\n\nВыберите интересующий вопрос:",
        "❓ <b>Nurlight жиі қойылатын сұрақтар</b>\n\nҚажетті сұрақты таңдаңыз:",
        "❓ <b>Nurlight FAQ</b>\n\nChoose a question:",
    ),
    "faq_empty": _(
        "❓ Пока нет доступных вопросов.",
        "❓ Әзірге сұрақтар жоқ.",
        "❓ No questions yet.",
    ),
    "faq_not_found": _(
        "Вопрос больше не доступен.",
        "Сұрақ табылмады.",
        "This question is no longer available.",
    ),
    "btn_faq_back": _("⬅️ Назад к вопросам", "⬅️ Сұрақтарға оралу", "⬅️ Back to questions"),

    # ---------- Виртуальный оператор (AI) ----------
    "ai_welcome": _(
        "💬 <b>Виртуальный оператор Nurlight</b>\n\n"
        "Привет! 👋 Я бот-помощник: подскажу по меню и ценам, доставке и вашим заказам.\n\n"
        "Просто напиши, что тебя интересует!\n\n"
        "🧹 /clear — начать новый разговор\n"
        "❌ /exit — завершить диалог",
        "💬 <b>Nurlight виртуалды операторы</b>\n\n"
        "Сәлеметсіз бе! 👋 Мен бот-көмекшімін: мәзір мен бағалар, жеткізу және тапсырыстарыңыз туралы айтып беремін.\n\n"
        "Қызықтыратын сұрағыңызды жазыңыз!\n\n"
        "🧹 /clear — жаңа әңгіме бастау\n"
        "❌ /exit — диалогты аяқтау",
        "💬 <b>Nurlight Virtual Operator</b>\n\n"
        "Hi! 👋 I'm a helper bot: I can tell you about the menu and prices, delivery and your orders.\n\n"
        "Just write what you are interested in!\n\n"
        "🧹 /clear — start a new conversation\n"
        "❌ /exit — end the chat",
    ),
    "ai_cleared": _(
        "🧹 <b>Память AI очищена!</b>\n\nМожем начать разговор заново.",
        "🧹 <b>AI жады тазаланды!</b>\n\nӘңгімені қайтадан бастай аламыз.",
        "🧹 <b>AI memory cleared!</b>\n\nWe can start the conversation again.",
    ),
    "ai_exit": _(
        "✅ AI-диалог завершён.\nМожешь пользоваться обычным меню.",
        "✅ AI диалогы аяқталды.\nЕнді қалыпты мәзірді пайдалана аласыз.",
        "✅ AI chat ended.\nYou can use the regular menu.",
    ),
    "ai_error": _(
        "⚠️ Произошла ошибка AI.\nПожалуйста, попробуйте позже.",
        "⚠️ AI қатесі орын алды.\nКейінірек қайталап көріңіз.",
        "⚠️ An AI error occurred.\nPlease try again later.",
    ),
    "ai_timeout": _(
        "⏳ AI отвечает слишком долго. Попробуйте ещё раз немного позже или напишите оператору.",
        "⏳ AI тым ұзақ жауап беріп жатыр. Сәл кейінірек қайталап көріңіз немесе операторға жазыңыз.",
        "⏳ The AI is taking too long to answer. Please try again a bit later or contact the operator.",
    ),
    "ai_unavailable": _(
        "⚠️ Сейчас не удалось связаться с AI. Попробуйте позже или напишите оператору.",
        "⚠️ Қазір AI-мен байланыса алмадық. Кейінірек қайталап көріңіз немесе операторға жазыңыз.",
        "⚠️ Could not reach the AI right now. Please try again later or contact the operator.",
    ),
    "ai_empty": _(
        "Не удалось получить ответ. Попробуйте ещё раз.",
        "Жауап алу мүмкін болмады. Қайталап көріңіз.",
        "Could not get an answer. Please try again.",
    ),

    # ---------- Оформление заказа ----------
    "checkout_interrupted": _(
        "❌ Оформление прервано. Корзина сохранена.",
        "❌ Рәсімдеу тоқтатылды. Себет сақталды.",
        "❌ Checkout interrupted. Your cart is saved.",
    ),
    "checkout_cancelled": _(
        "❌ Оформление отменено. Корзина сохранена.",
        "❌ Рәсімдеуден бас тартылды. Себет сақталды.",
        "❌ Checkout cancelled. Your cart is saved.",
    ),
    "items_became_unavailable": _(
        "⚠️ Некоторые товары стали недоступны:\n",
        "⚠️ Кейбір тауарлар қолжетімсіз болды:\n",
        "⚠️ Some items are no longer available:\n",
    ),
    "items_removed_from_cart": _(
        "⚠️ Недоступные товары убраны из корзины:\n",
        "⚠️ Қолжетімсіз тауарлар себеттен алынды:\n",
        "⚠️ Unavailable items were removed from your cart:\n",
    ),
    "cart_empty_to_catalog": _(
        "Корзина пуста. Вернитесь в каталог.",
        "Себет бос. Мәзірге оралыңыз.",
        "Your cart is empty. Go back to the catalog.",
    ),
    "cart_empty_choose": _(
        "Корзина пуста. Выберите товары в каталоге.",
        "Себет бос. Тауарларды мәзірден таңдаңыз.",
        "Your cart is empty. Choose items in the catalog.",
    ),
    "order_data": _("📋 Данные заказа:", "📋 Тапсырыс деректері:", "📋 Order details:"),
    "review_title": _("<b>Проверьте заказ</b>", "<b>Тапсырысты тексеріңіз</b>", "<b>Review your order</b>"),
    "label_items": _("Блюда: {amount}", "Тағамдар: {amount}", "Items: {amount}"),
    "label_total": _("<b>Итого: {amount}</b>", "<b>Барлығы: {amount}</b>", "<b>Total: {amount}</b>"),
    "summary_location": _(
        '📍 Геолокация: <a href="{url}">точка на карте</a>',
        '📍 Геолокация: <a href="{url}">картадағы нүкте</a>',
        '📍 Location: <a href="{url}">point on the map</a>',
    ),
    "summary_note": _("🏠 Уточнение: {text}", "🏠 Мекенжай нақтылауы: {text}", "🏠 Address details: {text}"),
    "summary_phone": _("📱 Телефон: {text}", "📱 Телефон: {text}", "📱 Phone: {text}"),
    "summary_comment": _("💬 Комментарий: {text}", "💬 Пікір: {text}", "💬 Comment: {text}"),
    "word_none_low": _("нет", "жоқ", "none"),
    "word_none_cap": _("Нет", "Жоқ", "None"),
    "confirm_question": _("Всё правильно?", "Бәрі дұрыс па?", "Is everything correct?"),
    "step_location": _(
        "📍 <b>Шаг 1. Геолокация</b>\n\nНажмите кнопку «📍 Отправить геолокацию», чтобы курьер нашёл вас на карте.",
        "📍 <b>1-қадам. Геолокация</b>\n\nКурьер сізді картадан табуы үшін «📍 Геолокация жіберу» түймесін басыңыз.",
        "📍 <b>Step 1. Location</b>\n\nTap the “📍 Send location” button so the courier can find you on the map.",
    ),
    "need_location": _(
        "Отправьте геолокацию кнопкой «📍 Отправить геолокацию».",
        "Геолокацияны «📍 Геолокация жіберу» түймесімен жіберіңіз.",
        "Please send your location with the “📍 Send location” button.",
    ),
    "step_note": _(
        "🏠 <b>Шаг 2. Уточнение адреса</b>\n\nУкажите подъезд, этаж, квартиру или домофон либо нажмите «Пропустить».\nНапример: подъезд 2, этаж 5, кв. 42",
        "🏠 <b>2-қадам. Мекенжайды нақтылау</b>\n\nКіреберіс, қабат, пәтер немесе домофонды көрсетіңіз не «Өткізіп жіберу» түймесін басыңыз.\nМысалы: 2-кіреберіс, 5-қабат, 42-пәтер",
        "🏠 <b>Step 2. Address details</b>\n\nEnter the entrance, floor, apartment or intercom code, or tap “Skip”.\nFor example: entrance 2, floor 5, apt 42",
    ),
    "need_note_text": _(
        "Напишите уточнение текстом или нажмите «Пропустить».",
        "Нақтылауды мәтінмен жазыңыз немесе «Өткізіп жіберу» түймесін басыңыз.",
        "Type the details or tap “Skip”.",
    ),
    "step_phone_saved": _(
        "📱 <b>Шаг 3. Номер телефона</b>\n\nВаш номер: <b>{phone}</b>\nОставьте его кнопкой ниже или введите другой (например: +7 777 123 45 67).",
        "📱 <b>3-қадам. Телефон нөмірі</b>\n\nСіздің нөміріңіз: <b>{phone}</b>\nТөмендегі түймемен қалдырыңыз немесе басқасын енгізіңіз (мысалы: +7 777 123 45 67).",
        "📱 <b>Step 3. Phone number</b>\n\nYour number: <b>{phone}</b>\nKeep it with the button below or enter another one (for example: +7 777 123 45 67).",
    ),
    "step_phone": _(
        "📱 <b>Шаг 3. Номер телефона</b>\n\nОтправьте номер кнопкой или введите вручную.\nНапример: +7 777 123 45 67",
        "📱 <b>3-қадам. Телефон нөмірі</b>\n\nНөмірді түймемен жіберіңіз немесе қолмен енгізіңіз.\nМысалы: +7 777 123 45 67",
        "📱 <b>Step 3. Phone number</b>\n\nSend your number with the button or type it.\nFor example: +7 777 123 45 67",
    ),
    "need_own_phone": _(
        "Пожалуйста, отправьте свой номер телефона.",
        "Өз телефон нөміріңізді жіберіңіз.",
        "Please send your own phone number.",
    ),
    "bad_phone_format": _("Неверный формат номера.", "Нөмір пішімі дұрыс емес.", "Invalid number format."),
    "phone_enter_or_contact": _(
        "Введите номер вручную или отправьте контакт кнопкой.",
        "Нөмірді қолмен енгізіңіз немесе контактіні түймемен жіберіңіз.",
        "Type your number or send your contact with the button.",
    ),
    "bad_phone_example": _(
        "Неверный номер. Например: +7 777 123 45 67",
        "Нөмір дұрыс емес. Мысалы: +7 777 123 45 67",
        "Invalid number. For example: +7 777 123 45 67",
    ),
    "phone_use_button": _(
        "Отправьте номер кнопкой или введите текстом.",
        "Нөмірді түймемен жіберіңіз немесе мәтінмен енгізіңіз.",
        "Send your number with the button or type it.",
    ),
    "step_comment": _(
        "💬 <b>Шаг 4. Комментарий</b>\n\nНапишите комментарий или нажмите «Без комментария».",
        "💬 <b>4-қадам. Пікір</b>\n\nПікір жазыңыз немесе «Пікірсіз» түймесін басыңыз.",
        "💬 <b>Step 4. Comment</b>\n\nWrite a comment or tap “No comment”.",
    ),
    "need_comment": _(
        "Напишите комментарий или нажмите «Без комментария».",
        "Пікір жазыңыз немесе «Пікірсіз» түймесін басыңыз.",
        "Write a comment or tap “No comment”.",
    ),
    "edit_title": _(
        "✏️ <b>Что хотите изменить?</b>",
        "✏️ <b>Нені өзгерткіңіз келеді?</b>",
        "✏️ <b>What would you like to change?</b>",
    ),
    "edit_location_prompt": _(
        "📍 Отправьте новую геолокацию кнопкой ниже:",
        "📍 Жаңа геолокацияны төмендегі түймемен жіберіңіз:",
        "📍 Send your new location with the button below:",
    ),
    "edit_note_prompt": _(
        "🏠 Введите уточнение адреса (подъезд, этаж, квартира) или нажмите «Пропустить»:",
        "🏠 Мекенжай нақтылауын енгізіңіз (кіреберіс, қабат, пәтер) немесе «Өткізіп жіберу» түймесін басыңыз:",
        "🏠 Enter address details (entrance, floor, apartment) or tap “Skip”:",
    ),
    "edit_phone_prompt": _(
        "📱 Введите новый номер телефона или отправьте контакт через кнопку:",
        "📱 Жаңа телефон нөмірін енгізіңіз немесе контактіні түймемен жіберіңіз:",
        "📱 Enter a new phone number or send your contact with the button:",
    ),
    "edit_comment_prompt": _(
        "💬 Введите новый комментарий или нажмите «Без комментария»:",
        "💬 Жаңа пікір енгізіңіз немесе «Пікірсіз» түймесін басыңыз:",
        "💬 Enter a new comment or tap “No comment”:",
    ),
    "use_buttons": _(
        "Используйте кнопки «Подтвердить», «Изменить» или «Отмена».",
        "«Растау», «Өзгерту» немесе «Бас тарту» түймелерін пайдаланыңыз.",
        "Please use the “Confirm”, “Edit” or “Cancel” buttons.",
    ),
    "order_in_progress": _(
        "Заказ уже обрабатывается или оформлен.",
        "Тапсырыс өңделіп жатыр немесе рәсімделген.",
        "The order is already being processed or placed.",
    ),
    "cart_changed": _(
        "⚠️ Состав корзины изменился. Проверьте заказ ещё раз.",
        "⚠️ Себеттің құрамы өзгерді. Тапсырысты қайта тексеріңіз.",
        "⚠️ Your cart has changed. Please review your order again.",
    ),
    "items_gone": _(
        "Товары больше недоступны. Выберите другие.",
        "Тауарлар енді қолжетімсіз. Басқаларын таңдаңыз.",
        "These items are no longer available. Please choose others.",
    ),
    "order_create_failed": _(
        "⚠️ Не удалось создать заказ. Попробуйте ещё раз.",
        "⚠️ Тапсырысты жасау мүмкін болмады. Қайталап көріңіз.",
        "⚠️ Could not create the order. Please try again.",
    ),
    "order_created": _(
        "✅ <b>Заказ создан!</b>\nНомер вашего заказа: <b>№{number}</b>\n\nЗаказ ожидает обработки оператором.",
        "✅ <b>Тапсырыс жасалды!</b>\nТапсырысыңыздың нөмірі: <b>№{number}</b>\n\nТапсырыс оператордың өңдеуін күтуде.",
        "✅ <b>Order created!</b>\nYour order number: <b>#{number}</b>\n\nThe order is waiting for the operator.",
    ),
    "pay_hint": _(
        "💳 Оплатить заказ можно счётом выше или позже в разделе «Мои заказы».",
        "💳 Тапсырысқа жоғарыдағы шотпен немесе кейін «Тапсырыстарым» бөлімінде төлей аласыз.",
        "💳 You can pay with the invoice above or later in “My orders”.",
    ),
    "pay_soon": _(
        "💳 Онлайн-оплата скоро появится. Способ оплаты уточнит оператор.",
        "💳 Онлайн-төлем жақында қосылады. Төлем тәсілін оператор нақтылайды.",
        "💳 Online payment is coming soon. The operator will confirm the payment method.",
    ),
    "old_button": _(
        "Эта кнопка больше неактуальна.",
        "Бұл түйме енді өзекті емес.",
        "This button is no longer valid.",
    ),
    "err_note_too_long": _(
        "Уточнение слишком длинное. Максимум 500 символов.",
        "Нақтылау тым ұзын. Ең көбі 500 таңба.",
        "Details are too long. Maximum 500 characters.",
    ),
    "err_comment_too_long": _(
        "Комментарий слишком длинный. Максимум 500 символов.",
        "Пікір тым ұзын. Ең көбі 500 таңба.",
        "Comment is too long. Maximum 500 characters.",
    ),

    # ---------- Кнопки оформления ----------
    "btn_cancel": _("⬅️ Отменить", "⬅️ Бас тарту", "⬅️ Cancel"),
    "btn_send_phone": _("📱 Отправить номер", "📱 Нөмірді жіберу", "📱 Send number"),
    "btn_no_comment": _("Без комментария", "Пікірсіз", "No comment"),
    "btn_send_location": _("📍 Отправить геолокацию", "📍 Геолокация жіберу", "📍 Send location"),
    "btn_skip": _("Пропустить", "Өткізіп жіберу", "Skip"),
    "btn_keep_prefix": _("✅ Оставить", "✅ Қалдыру", "✅ Keep"),
    "btn_confirm": _("✅ Подтвердить", "✅ Растау", "✅ Confirm"),
    "btn_edit": _("✏️ Изменить", "✏️ Өзгерту", "✏️ Edit"),
    "btn_cancel_inline": _("❌ Отмена", "❌ Бас тарту", "❌ Cancel"),
    "btn_edit_location": _("📍 Геолокация", "📍 Геолокация", "📍 Location"),
    "btn_edit_note": _("🏠 Уточнение адреса", "🏠 Мекенжай нақтылауы", "🏠 Address details"),
    "btn_edit_phone": _("📱 Телефон", "📱 Телефон", "📱 Phone"),
    "btn_edit_comment": _("💬 Комментарий", "💬 Пікір", "💬 Comment"),
    "btn_retry": _("🔁 Повторить", "🔁 Қайталау", "🔁 Retry"),

    # ---------- Доставка ----------
    "delivery_free": _("Доставка: бесплатно", "Жеткізу: тегін", "Delivery: free"),
    "delivery_fee": _(
        "Доставка: {fee} (бесплатно от {free_from})",
        "Жеткізу: {fee} ({free_from} бастап тегін)",
        "Delivery: {fee} (free from {free_from})",
    ),

    # ---------- Мои заказы ----------
    "orders_title": _("<b>📦 Мои заказы</b>", "<b>📦 Тапсырыстарым</b>", "<b>📦 My orders</b>"),
    "orders_limit": _(
        "Показаны последние {n} заказов.",
        "Соңғы {n} тапсырыс көрсетілген.",
        "Showing the last {n} orders.",
    ),
    "orders_empty": _(
        "Пока нет заказов. Самое время что-нибудь выбрать 🛍",
        "Әзірге тапсырыс жоқ. Бірдеңе таңдайтын уақыт келді 🛍",
        "No orders yet. Time to pick something 🛍",
    ),
    "orders_load_error": _(
        "Не удалось загрузить заказы. Попробуйте ещё раз.",
        "Тапсырыстарды жүктеу мүмкін болмады. Қайталап көріңіз.",
        "Could not load your orders. Please try again.",
    ),
    "order_not_found": _("Заказ не найден.", "Тапсырыс табылмады.", "Order not found."),
    "cancel_too_late": _(
        "Заказ уже принят оператором — отменить его нельзя.\nСвяжитесь с оператором, он поможет.",
        "Тапсырысты оператор қабылдады — оны бас тартуға болмайды.\nОператормен байланысыңыз, ол көмектеседі.",
        "The order has already been accepted by the operator and cannot be cancelled.\nContact the operator, they will help.",
    ),
    "cancel_paid": _(
        "Заказ уже оплачен. Отмену и возврат денег оформит оператор.\nСвяжитесь с оператором, он поможет.",
        "Тапсырыс төленген. Бас тарту мен ақшаны қайтаруды оператор рәсімдейді.\nОператормен байланысыңыз, ол көмектеседі.",
        "The order is already paid. The operator will handle the cancellation and refund.\nContact the operator, they will help.",
    ),
    "card_title": _("<b>📦 Заказ №{number}</b>", "<b>📦 №{number} тапсырыс</b>", "<b>📦 Order #{number}</b>"),
    "card_status": _("Статус: {status}", "Күйі: {status}", "Status: {status}"),
    "card_created": _("Создан: {date}", "Жасалды: {date}", "Created: {date}"),
    "card_items_header": _("Состав:", "Құрамы:", "Order contents:"),
    "card_note": _("Уточнение адреса: {text}", "Мекенжай нақтылауы: {text}", "Address details: {text}"),
    "card_phone": _("Телефон: {text}", "Телефон: {text}", "Phone: {text}"),
    "card_comment": _("Комментарий: {text}", "Пікір: {text}", "Comment: {text}"),
    "card_payment": _("Оплата: {state}", "Төлем: {state}", "Payment: {state}"),
    "pay_state_paid": _("✅ оплачен", "✅ төленді", "✅ paid"),
    "pay_state_unpaid": _("не оплачен", "төленбеген", "not paid"),
    "delivered_thanks": _(
        "🙏 Спасибо за заказ! Будем рады видеть снова.",
        "🙏 Тапсырысыңыз үшін рахмет! Сізді тағы күтеміз.",
        "🙏 Thank you for your order! We'll be happy to see you again.",
    ),
    "status_unchanged": _("Статус не изменился.", "Күйі өзгерген жоқ.", "The status has not changed."),
    "status_updated": _("Статус обновлён", "Күйі жаңартылды", "Status updated"),
    "invoice_failed": _(
        "Не удалось выставить счёт. Попробуйте позже.",
        "Шот шығару мүмкін болмады. Кейінірек қайталап көріңіз.",
        "Could not create the invoice. Please try again later.",
    ),
    "payment_unavailable": _(
        "Оплата для этого заказа сейчас недоступна.",
        "Бұл тапсырыс үшін төлем қазір қолжетімсіз.",
        "Payment for this order is not available right now.",
    ),
    "cancel_ask": _(
        "Отменить заказ №{number} на {amount}?\n\nЕсли передумали — вернитесь к заказу.",
        "{amount} сомасындағы №{number} тапсырыстан бас тартасыз ба?\n\nОйыңыз өзгерсе — тапсырысқа оралыңыз.",
        "Cancel order #{number} for {amount}?\n\nIf you changed your mind, go back to the order.",
    ),
    "cancel_failed": _(
        "Не удалось отменить заказ. Попробуйте ещё раз или свяжитесь с оператором.",
        "Тапсырыстан бас тарту мүмкін болмады. Қайталап көріңіз немесе операторға жазыңыз.",
        "Could not cancel the order. Please try again or contact the operator.",
    ),
    "cancel_done": _(
        "Заказ №{number} отменён.\n\nЕсли что-то пошло не так, напишите оператору.",
        "№{number} тапсырыстан бас тартылды.\n\nЕгер бірдеңе дұрыс болмаса, операторға жазыңыз.",
        "Order #{number} has been cancelled.\n\nIf something went wrong, contact the operator.",
    ),
    "already_cancelled": _("Заказ уже отменён.", "Тапсырыстан бұрын бас тартылған.", "The order is already cancelled."),
    "btn_refresh": _("🔄 Обновить", "🔄 Жаңарту", "🔄 Refresh"),
    "btn_pay_order": _("💳 Оплатить заказ", "💳 Тапсырысқа төлеу", "💳 Pay for the order"),
    "btn_cancel_order": _("❌ Отменить заказ", "❌ Тапсырыстан бас тарту", "❌ Cancel order"),
    "btn_order_again": _("🛍 Заказать ещё", "🛍 Тағы тапсырыс беру", "🛍 Order again"),
    "btn_to_list": _("⬅️ К списку", "⬅️ Тізімге", "⬅️ To the list"),
    "btn_yes_cancel": _("✅ Да, отменить", "✅ Иә, бас тарту", "✅ Yes, cancel"),
    "btn_no_keep": _("⬅️ Нет, оставить", "⬅️ Жоқ, қалдыру", "⬅️ No, keep it"),
    "btn_to_order": _("⬅️ К заказу", "⬅️ Тапсырысқа", "⬅️ To the order"),

    # ---------- Статусы заказа ----------
    "status_new": _("Новый", "Жаңа", "New"),
    "status_accepted": _("Принят", "Қабылданды", "Accepted"),
    "status_cooking": _("Готовится", "Дайындалуда", "Cooking"),
    "status_packing": _("Упаковывается", "Қапталуда", "Packing"),
    "status_ready": _("Готов", "Дайын", "Ready"),
    "status_handed_to_courier": _("Передан курьеру", "Курьерге берілді", "Handed to courier"),
    "status_in_transit": _("В пути", "Жолда", "On the way"),
    "status_delivered": _("Доставлен", "Жеткізілді", "Delivered"),
    "status_cancelled": _("Отменён", "Бас тартылды", "Cancelled"),

    # ---------- Оплата ----------
    "btn_pay_demo": _("✅ Оплатить (тест)", "✅ Төлеу (тест)", "✅ Pay (test)"),
    "btn_pay_window": _("💳 Оплатить картой (тест)", "💳 Картамен төлеу (тест)", "💳 Pay by card (test)"),
    "demo_window_hint": _(
        "Нажмите «💳 Оплатить картой (тест)» внизу экрана. Настоящую карту не вводите.",
        "Экранның төменгі жағындағы «💳 Картамен төлеу (тест)» түймесін басыңыз. Нағыз картаны енгізбеңіз.",
        "Tap “💳 Pay by card (test)” at the bottom of the screen. Do not enter a real card.",
    ),
    "demo_declined": _(
        "❌ Банк отклонил тестовый платёж. Заказ не оплачен, попробуйте другую тестовую карту.",
        "❌ Банк тест төлемінен бас тартты. Тапсырыс төленбеді, басқа тест картасын қолданып көріңіз.",
        "❌ The bank declined the test payment. The order is not paid, please try another test card.",
    ),
    "demo_off": _("Тестовая оплата выключена.", "Тест төлемі өшірулі.", "Test payment is turned off."),
    "pay_failed": _(
        "Не удалось выполнить оплату. Попробуйте позже.",
        "Төлемді орындау мүмкін болмады. Кейінірек қайталап көріңіз.",
        "Could not complete the payment. Please try again later.",
    ),
    "demo_done": _(
        "✅ Тестовая оплата прошла.\nДеньги не списывались, заказ отмечен оплаченным.",
        "✅ Тест төлемі өтті.\nАқша есептен шығарылған жоқ, тапсырыс төленген деп белгіленді.",
        "✅ Test payment completed.\nNo money was charged, the order is marked as paid.",
    ),
    "demo_invoice": _(
        "💳 <b>Тестовая оплата заказа №{number}</b>\nСумма: {amount}\n\nЭто демонстрационный режим: деньги не списываются.",
        "💳 <b>№{number} тапсырысқа тест төлемі</b>\nСомасы: {amount}\n\nБұл демонстрациялық режим: ақша есептен шығарылмайды.",
        "💳 <b>Test payment for order #{number}</b>\nAmount: {amount}\n\nThis is a demo mode: no money is charged.",
    ),
    "precheck_failed": _(
        "Не удалось проверить заказ. Попробуйте ещё раз позже.",
        "Тапсырысты тексеру мүмкін болмады. Кейінірек қайталап көріңіз.",
        "Could not verify the order. Please try again later.",
    ),
    "payment_manual": _(
        "✅ Платёж получен. Не удалось сразу отметить его в системе, оператор проверит оплату вручную.",
        "✅ Төлем алынды. Оны жүйеде бірден белгілеу мүмкін болмады, оператор төлемді қолмен тексереді.",
        "✅ Payment received. It could not be recorded right away, the operator will check it manually.",
    ),
    "payment_ok": _(
        "✅ Оплата прошла, спасибо! Заказ передан оператору.",
        "✅ Төлем өтті, рахмет! Тапсырыс операторға берілді.",
        "✅ Payment successful, thank you! The order was passed to the operator.",
    ),
    "invoice_title": _("Заказ №{number}", "№{number} тапсырыс", "Order #{number}"),
    "invoice_desc": _("Оплата заказа Nurlight", "Nurlight тапсырысына төлем", "Payment for your Nurlight order"),
    "invoice_items": _("Блюда", "Тағамдар", "Items"),
    "invoice_delivery": _("Доставка", "Жеткізу", "Delivery"),

    # ---------- Уведомления о статусе ----------
    "notify_accepted": _(
        "✅ <b>Заказ №{number} принят</b>\nОператор подтвердил заказ, скоро передадим его курьеру.",
        "✅ <b>№{number} тапсырыс қабылданды</b>\nОператор тапсырысты растады, жақында курьерге береміз.",
        "✅ <b>Order #{number} accepted</b>\nThe operator confirmed your order and will pass it to the courier soon.",
    ),
    "notify_cooking": _(
        "🍳 <b>Заказ №{number} готовится</b>\nКухня уже работает над вашим заказом.",
        "🍳 <b>№{number} тапсырыс дайындалуда</b>\nАспаз тапсырысыңызбен жұмыс істеп жатыр.",
        "🍳 <b>Order #{number} is being prepared</b>\nThe kitchen is already working on your order.",
    ),
    "notify_ready": _(
        "🍽 <b>Заказ №{number} готов</b>\nСейчас передадим его курьеру.",
        "🍽 <b>№{number} тапсырыс дайын</b>\nҚазір курьерге береміз.",
        "🍽 <b>Order #{number} is ready</b>\nWe will hand it to the courier shortly.",
    ),
    "notify_handed_to_courier": _(
        "🛵 <b>Заказ №{number} передан курьеру</b>\nКурьер скоро выедет к вам.",
        "🛵 <b>№{number} тапсырыс курьерге берілді</b>\nКурьер жақында сізге шығады.",
        "🛵 <b>Order #{number} handed to the courier</b>\nThe courier will be on the way soon.",
    ),
    "notify_in_transit": _(
        "🚚 <b>Заказ №{number} в пути</b>\nКурьер уже едет к вам.",
        "🚚 <b>№{number} тапсырыс жолда</b>\nКурьер сізге келе жатыр.",
        "🚚 <b>Order #{number} is on the way</b>\nThe courier is already heading to you.",
    ),
    "notify_delivered": _(
        "🎉 <b>Заказ №{number} доставлен</b>\nПриятного аппетита! Будем рады видеть вас снова.",
        "🎉 <b>№{number} тапсырыс жеткізілді</b>\nЖаныңызға жағсын! Сізді тағы күтеміз.",
        "🎉 <b>Order #{number} delivered</b>\nEnjoy your meal! We'll be happy to see you again.",
    ),
    "notify_cancelled": _(
        "❌ <b>Заказ №{number} отменён</b>\nЕсли это ошибка, свяжитесь с оператором.",
        "❌ <b>№{number} тапсырыстан бас тартылды</b>\nЕгер бұл қате болса, оператормен байланысыңыз.",
        "❌ <b>Order #{number} cancelled</b>\nIf this is a mistake, please contact the operator.",
    ),
}


def lang_or_default(lang: str | None) -> str:
    return lang if lang in LANGS else DEFAULT_LANG


def t(key: str, lang: str | None = None, **kwargs) -> str:
    """Текст по ключу на языке клиента (по умолчанию — язык текущего обновления)."""
    lang = lang_or_default(lang or current_lang.get())
    text = TEXTS[key].get(lang) or TEXTS[key][DEFAULT_LANG]
    return text.format(**kwargs) if kwargs else text


def variants(key: str) -> frozenset[str]:
    """Все переводы ключа: нужны, чтобы кнопка меню работала на любом языке."""
    found = set(TEXTS[key].values())
    found.update(LEGACY_VARIANTS.get(key, []))
    return frozenset(found)


def localized(obj, field: str, lang: str | None = None) -> str:
    """Название или описание из базы на языке клиента.

    У категорий и товаров есть поля name_kk, name_en, description_kk, description_en
    (их заполняют в панели). Если перевода нет, показывается русский текст.
    """
    lang = lang_or_default(lang or current_lang.get())

    if lang != DEFAULT_LANG:
        text = getattr(obj, f"{field}_{lang}", "") or ""

        if text.strip():
            return text

    return getattr(obj, field, "") or ""


def status_label(status: str, lang: str | None = None) -> str:
    """Название статуса заказа на языке клиента."""
    key = f"status_{status}"
    return t(key, lang) if key in TEXTS else str(status)
