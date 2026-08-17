(() => {
  if (window.top !== window) return;
  if (document.getElementById("dicd-ai-root")) return;

  const STORAGE_KEY = "dicd_ai_conversation";

  const state = {
    open: false,
    busy: false,
    messages: []
  };

  const root = document.createElement("div");

  root.id = "dicd-ai-root";

  root.innerHTML = `
    <button id="dicd-ai-launcher"
            aria-label="Open DICD AI Assistant"
            title="DICD AI Assistant">
      <span>✦</span>
    </button>

    <section id="dicd-ai-panel" aria-label="DICD AI Assistant">

      <header class="dicd-ai-header">

        <div>
          <div class="dicd-ai-title">
            DICD AI Assistant
          </div>

          <div class="dicd-ai-subtitle">
            Aware of the page you're viewing
          </div>
        </div>

        <button
          id="dicd-ai-clear"
          class="dicd-ai-icon-button"
          aria-label="Clear conversation"
          title="Clear conversation">
          ↺
        </button>

        <button
          id="dicd-ai-close"
          class="dicd-ai-icon-button"
          aria-label="Close">
          ×
        </button>

      </header>

      <div id="dicd-ai-page" class="dicd-ai-page"></div>

      <div id="dicd-ai-messages" class="dicd-ai-messages"></div>

      <form id="dicd-ai-form" class="dicd-ai-form">

        <textarea
          id="dicd-ai-input"
          rows="2"
          placeholder="Ask about this page..."
          aria-label="Message">
        </textarea>

        <button id="dicd-ai-send" type="submit">
          Send
        </button>

      </form>

    </section>
  `;

  document.documentElement.appendChild(root);

  const launcher = root.querySelector("#dicd-ai-launcher");
  const panel = root.querySelector("#dicd-ai-panel");
  const close = root.querySelector("#dicd-ai-close");
  const clear = root.querySelector("#dicd-ai-clear");

  const pageEl = root.querySelector("#dicd-ai-page");
  const messagesEl = root.querySelector("#dicd-ai-messages");

  const form = root.querySelector("#dicd-ai-form");
  const input = root.querySelector("#dicd-ai-input");
  const send = root.querySelector("#dicd-ai-send");


  // --------------------------------------------------
  // PAGE CONTEXT
  // --------------------------------------------------

  function getPageContext() {

    const main =
      document.querySelector("main") ||
      document.querySelector("article") ||
      document.querySelector('[role="main"]') ||
      document.body;

    let text = main.innerText || "";

    text = text
      .replace(/\n{3,}/g, "\n\n")
      .trim();

    if (text.length > 18000) {
      text =
        text.slice(0, 18000) +
        "\n[Page text truncated]";
    }

    return {
      url: window.location.href,
      title: document.title,
      text
    };
  }


  function renderPageContext() {

    const ctx = getPageContext();

    pageEl.innerHTML = `
      <span class="dicd-ai-page-dot"></span>

      <span>
        Current page:
        <strong>${escapeHtml(ctx.title || "DICD")}</strong>
      </span>
    `;
  }


  // --------------------------------------------------
  // STORAGE
  // --------------------------------------------------

  async function loadConversation() {

    try {

      const result =
        await chrome.storage.local.get(STORAGE_KEY);

      if (
        result[STORAGE_KEY] &&
        Array.isArray(result[STORAGE_KEY])
      ) {

        state.messages =
          result[STORAGE_KEY];

      }

    } catch (error) {

      console.error(
        "DICD AI: Could not load conversation",
        error
      );

    }
  }


  async function saveConversation() {

    try {

      await chrome.storage.local.set({
        [STORAGE_KEY]: state.messages
      });

    } catch (error) {

      console.error(
        "DICD AI: Could not save conversation",
        error
      );

    }
  }


  async function clearConversation() {

    state.messages = [];

    await chrome.storage.local.remove(
      STORAGE_KEY
    );

    renderMessages();

    addMessage(
      "assistant",
      "Conversația a fost ștearsă. Cu ce te pot ajuta?"
    );
  }


  // --------------------------------------------------
  // MESSAGES
  // --------------------------------------------------

  function renderMessages() {

    messagesEl.innerHTML = "";

    for (const message of state.messages) {

      const item =
        document.createElement("div");

      item.className =
        `dicd-ai-message ${message.role}`;

      item.textContent =
        message.text;

      messagesEl.appendChild(item);
    }

    messagesEl.scrollTop =
      messagesEl.scrollHeight;
  }


  async function addMessage(role, text) {

    state.messages.push({
      role,
      text
    });

    const item =
      document.createElement("div");

    item.className =
      `dicd-ai-message ${role}`;

    item.textContent =
      text;

    messagesEl.appendChild(item);

    messagesEl.scrollTop =
      messagesEl.scrollHeight;

    await saveConversation();
  }


  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  function setBusy(busy) {

    state.busy = busy;

    input.disabled = busy;
    send.disabled = busy;

    send.textContent =
      busy ? "…" : "Send";
  }


  // --------------------------------------------------
  // SEND MESSAGE
  // --------------------------------------------------

  async function sendMessage(message) {

    const page =
      getPageContext();

    await addMessage(
      "user",
      message
    );

    setBusy(true);

    try {

      const response =
        await fetch(
          "http://localhost:8000/api/chat",
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json"
            },

            body: JSON.stringify({

              message,

              page,

              history:
                state.messages.slice(-20)

            })
          }
        );


      if (!response.ok) {

        throw new Error(
          `Backend returned ${response.status}`
        );

      }


      const data =
        await response.json();


      await addMessage(
        "assistant",
        data.answer ||
        "I couldn't generate an answer."
      );


    } catch (error) {

      console.error(
        "DICD AI:",
        error
      );

      await addMessage(
        "assistant",
        "Am întâmpinat o problemă la conectarea cu serverul AI."
      );

    } finally {

      setBusy(false);

      input.focus();

    }
  }


  // --------------------------------------------------
  // EVENTS
  // --------------------------------------------------

  launcher.addEventListener(
    "click",
    () => {

      state.open =
        !state.open;

      panel.classList.toggle(
        "open",
        state.open
      );

      launcher.classList.toggle(
        "hidden",
        state.open
      );

      if (state.open) {

        renderPageContext();

        input.focus();

      }

    }
  );


  close.addEventListener(
    "click",
    () => {

      state.open = false;

      panel.classList.remove(
        "open"
      );

      launcher.classList.remove(
        "hidden"
      );

    }
  );


  clear.addEventListener(
    "click",
    async () => {

      const confirmed =
        confirm(
          "Ștergi întreaga conversație?"
        );

      if (confirmed) {

        await clearConversation();

      }

    }
  );


  form.addEventListener(
    "submit",
    async event => {

      event.preventDefault();

      const message =
        input.value.trim();

      if (
        !message ||
        state.busy
      ) {
        return;
      }

      input.value = "";

      await sendMessage(message);

    }
  );


  input.addEventListener(
    "keydown",
    event => {

      if (
        event.key === "Enter" &&
        !event.shiftKey
      ) {

        event.preventDefault();

        form.requestSubmit();

      }

    }
  );


  // --------------------------------------------------
  // INITIALIZE
  // --------------------------------------------------

  async function initialize() {

    await loadConversation();

    renderMessages();

    renderPageContext();

    if (state.messages.length === 0) {

      await addMessage(
        "assistant",
        "Salut! Sunt asistentul DICD. Văd pagina pe care ești și te pot ajuta să înțelegi informațiile sau să găsești următorul pas."
      );

    }

  }


  initialize();

})();


function escapeHtml(value) {

  return String(value)

    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

}