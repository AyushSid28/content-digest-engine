const btn = document.getElementById("summarise-btn");
const statusEl = document.getElementById("status");
const outputEl = document.getElementById("output");
const pageInfoEl = document.getElementById("page-info");
const setupMsg = document.getElementById("setup-msg");

const THEMES = {
  default: "You are a summarisation assistant. Summarise the following content clearly and concisely in Markdown format. Use headings, bullet points, and emphasis where appropriate.",
  minimal: "You are a summarisation assistant. Summarise the following content in 3-5 concise bullet points. Be extremely brief.",
  detailed: "You are a summarisation assistant. Summarise the following content in a detailed, comprehensive way using Markdown format. Use headings, subheadings, bullet points, and emphasis. Include key details and nuance.",
  "bullet-points": "You are a summarisation assistant. Summarise the following content as a structured list of bullet points grouped by topic. Use Markdown format with headings for each group.",
};

const PROVIDERS = {
  groq: {
    url: "https://api.groq.com/openai/v1/chat/completions",
    model: "llama-3.3-70b-versatile",
  },
  openai: {
    url: "https://api.openai.com/v1/chat/completions",
    model: "gpt-4o-mini",
  },
};

function renderMarkdown(text) {
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  html = html
    .replace(/^### (.+)$/gm, "<h3>$1</h3>")
    .replace(/^## (.+)$/gm, "<h2>$1</h2>")
    .replace(/^# (.+)$/gm, "<h1>$1</h1>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/^\s*[-*] (.+)$/gm, "<li>$1</li>")
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br>");

  return "<p>" + html + "</p>";
}

async function getSettings() {
  return new Promise((resolve) => {
    chrome.storage.local.get(["apiKey", "provider", "theme"], (data) => {
      resolve({
        apiKey: data.apiKey || "",
        provider: data.provider || "groq",
        theme: data.theme || "default",
      });
    });
  });
}

async function extractPageContent() {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ action: "extractContent" }, (response) => {
      if (chrome.runtime.lastError) {
        resolve({ error: chrome.runtime.lastError.message });
        return;
      }
      resolve(response || { error: "No response from background script" });
    });
  });
}

async function streamFromAPI(apiUrl, apiKey, model, systemPrompt, userContent) {
  const response = await fetch(apiUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: model,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userContent },
      ],
      stream: true,
    }),
  });

  if (!response.ok) {
    const errBody = await response.text();
    let errMsg = `API error ${response.status}`;
    try {
      const errJson = JSON.parse(errBody);
      errMsg = errJson.error?.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }

  return response.body.getReader();
}

btn.addEventListener("click", summarise);

async function summarise() {
  const settings = await getSettings();

  if (!settings.apiKey) {
    setupMsg.style.display = "block";
    outputEl.innerHTML = "";
    statusEl.textContent = "";
    return;
  }

  setupMsg.style.display = "none";
  btn.disabled = true;
  btn.textContent = "Summarising...";
  outputEl.innerHTML = "";
  statusEl.textContent = "Extracting page content...";
  statusEl.className = "status";
  pageInfoEl.textContent = "";

  const pageData = await extractPageContent();

  if (pageData.error) {
    statusEl.textContent = pageData.error;
    statusEl.className = "status error";
    btn.disabled = false;
    btn.textContent = "Summarise this page";
    return;
  }

  const content = pageData.content;
  pageInfoEl.textContent = content.title;

  if (!content.text || content.text.length < 20) {
    statusEl.textContent = "Page has too little text to summarise";
    statusEl.className = "status error";
    btn.disabled = false;
    btn.textContent = "Summarise this page";
    return;
  }

  const providerConfig = PROVIDERS[settings.provider] || PROVIDERS.groq;
  const systemPrompt = THEMES[settings.theme] || THEMES.default;
  const userText = `Title: ${content.title}\nURL: ${content.url}\n\n${content.text}`;

  statusEl.textContent = "Summarising...";

  let fullText = "";

  try {
    const reader = await streamFromAPI(
      providerConfig.url, settings.apiKey, providerConfig.model,
      systemPrompt, userText,
    );

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith("data: ")) continue;
        const payload = trimmed.slice(6);
        if (payload === "[DONE]") continue;

        try {
          const json = JSON.parse(payload);
          const token = json.choices?.[0]?.delta?.content;
          if (token) {
            fullText += token;
            outputEl.innerHTML = renderMarkdown(fullText);
            outputEl.scrollTop = outputEl.scrollHeight;
          }
        } catch {}
      }
    }

    statusEl.textContent = `Done — ${fullText.length} chars`;
    statusEl.className = "status done";
  } catch (e) {
    statusEl.textContent = "Error: " + e.message;
    statusEl.className = "status error";

    if (e.message.includes("API key") || e.message.includes("401") || e.message.includes("Incorrect")) {
      statusEl.textContent += " — check your API key in settings";
    }
  }

  btn.disabled = false;
  btn.textContent = "Summarise this page";
}
