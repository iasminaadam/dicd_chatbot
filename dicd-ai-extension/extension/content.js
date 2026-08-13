(() => {
  if (window.top !== window) return;
  if (document.getElementById("dicd-ai-root")) return;

  const state = {
    open: false,
    busy: false,
    messages: []
  };

  const root = document.createElement("div");
  root.id = "dicd-ai-root";
  root.innerHTML = `
    <button id="dicd-ai-launcher" aria-label="Open DICD AI Assistant" title="DICD AI Assistant">
      <span>✦</span>
    </button>

    <section id="dicd-ai-panel" aria-label="DICD AI Assistant">
      <header class="dicd-ai-header">
        <div>
          <div class="dicd-ai-title">DICD AI Assistant</div>
          <div class="dicd-ai-subtitle">Aware of the page you're viewing</div>
        </div>
        <button id="dicd-ai-close" class="dicd-ai-icon-button" aria-label="Close">×</button>
      </header>

      <div id="dicd-ai-page" class="dicd-ai-page"></div>
      <div id="dicd-ai-messages" class="dicd-ai-messages"></div>

      <form id="dicd-ai-form" class="dicd-ai-form">
        <textarea id="dicd-ai-input" rows="2" placeholder="Ask about this page..." aria-label="Message"></textarea>
        <button id="dicd-ai-send" type="submit">Send</button>
      </form>
    </section>
  `;

  document.documentElement.appendChild(root);

  const launcher = root.querySelector("#dicd-ai-launcher");
  const panel = root.querySelector("#dicd-ai-panel");
  const close = root.querySelector("#dicd-ai-close");
  const pageEl = root.querySelector("#dicd-ai-page");
  const messagesEl = root.querySelector("#dicd-ai-messages");
  const form = root.querySelector("#dicd-ai-form");
  const input = root.querySelector("#dicd-ai-input");
  const send = root.querySelector("#dicd-ai-send");

  function getPageContext() {
    const main =
      document.querySelector("main") ||
      document.querySelector("article") ||
      document.querySelector('[role="main"]') ||
      document.body;

    let text = main.innerText || "";
    text = text.replace(/\n{3,}/g, "\n\n").trim();

    // Keep the first MVP bounded. The backend can later retrieve a fuller
    // site-wide knowledge base separately.
    if (text.length > 18000) {
      text = text.slice(0, 18000) + "\n[Page text truncated]";
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
      <span>Current page: <strong>${escapeHtml(ctx.title || "DICD")}</strong></span>
    `;
  }

  function addMessage(role, text) {
    state.messages.push({ role, text });
    const item = document.createElement("div");
    item.className = `dicd-ai-message ${role}`;
    item.textContent = text;
    messagesEl.appendChild(item);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function setBusy(busy) {
    state.busy = busy;
    input.disabled = busy;
    send.disabled = busy;
    send.textContent = busy ? "…" : "Send";
  }

  async function sendMessage(message) {
    const page = getPageContext();
    addMessage("user", message);
    setBusy(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          page,
          history: state.messages.slice(-10)
        })
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const data = await response.json();
      addMessage("assistant", data.answer || "I couldn't generate an answer.");
    } catch (error) {
      console.error("DICD AI:", error);
      addMessage(
        "assistant",
        "The assistant backend is not connected yet. Start the local backend on http://localhost:8000 and try again."
      );
    } finally {
      setBusy(false);
      input.focus();
    }
  }

  launcher.addEventListener("click", () => {
    state.open = !state.open;
    panel.classList.toggle("open", state.open);
    launcher.classList.toggle("hidden", state.open);
    if (state.open) {
      renderPageContext();
      input.focus();
    }
  });

  close.addEventListener("click", () => {
    state.open = false;
    panel.classList.remove("open");
    launcher.classList.remove("hidden");
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message || state.busy) return;
    input.value = "";
    await sendMessage(message);
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  addMessage(
    "assistant",
    "Salut! Sunt asistentul DICD. Văd pagina pe care ești și te pot ajuta să înțelegi informațiile sau să găsești următorul pas."
  );
  renderPageContext();
})();

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
