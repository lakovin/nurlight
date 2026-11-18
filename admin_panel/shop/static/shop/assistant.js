// Окно AI-консультанта: вопросы уходят на /assistant/, история диалога хранится в сессии на сервере
(function () {
  const root = document.querySelector(".assistant");
  if (!root) return;
  const toggle = root.querySelector(".assistant-toggle");
  const panel = root.querySelector(".assistant-panel");
  const log = root.querySelector(".assistant-log");
  const form = root.querySelector(".assistant-form");
  const input = form.querySelector('input[name="message"]');
  const send = form.querySelector("button");
  const url = root.dataset.url;

  const csrf = () => form.querySelector('input[name="csrfmiddlewaretoken"]').value;

  function setOpen(open) {
    panel.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    if (open) input.focus();
  }

  function bubble(text, who) {
    const p = document.createElement("p");
    p.className = "bubble " + who;
    p.textContent = text; // только текст: ответ модели не вставляется как HTML
    log.appendChild(p);
    log.scrollTop = log.scrollHeight;
    return p;
  }

  async function post(body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf() },
      body: JSON.stringify(body),
      credentials: "same-origin",
    });
    const data = await res.json().catch(() => ({}));
    return { ok: res.ok, data };
  }

  toggle.addEventListener("click", () => setOpen(panel.hidden));
  root.querySelector(".assistant-close").addEventListener("click", () => { setOpen(false); toggle.focus(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !panel.hidden) { setOpen(false); toggle.focus(); } });

  root.querySelector('[data-action="clear"]').addEventListener("click", async () => {
    await post({ action: "clear" }).catch(() => {});
    log.replaceChildren();
    bubble("Начнём заново. Чем помочь?", "bot");
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    bubble(text, "user");
    input.value = "";
    input.disabled = send.disabled = true;
    const typing = bubble("Печатает…", "bot typing");
    try {
      const { ok, data } = await post({ message: text });
      typing.remove();
      bubble(ok ? data.answer : data.error || "Не получилось ответить, попробуйте ещё раз.", ok && data.ok ? "bot" : "bot error");
    } catch {
      typing.remove();
      bubble("Нет связи с сервером. Проверьте интернет и попробуйте ещё раз.", "bot error");
    } finally {
      input.disabled = send.disabled = false;
      input.focus();
    }
  });
})();
