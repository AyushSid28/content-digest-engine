const API_BASE = "http://127.0.0.1:11919";

const btn = document.getElementById("summarise-btn");
const statusEl = document.getElementById("status");
const outputEl = document.getElementById("output");
const themeSelect = document.getElementById("theme");
const providerSelect = document.getElementById("provider");

btn.addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.url) {
    statusEl.textContent = "No active tab found";
    statusEl.className = "status error";
    return;
  }

  summarise(tab.url);
});

async function summarise(url) {
  btn.disabled = true;
  outputEl.innerHTML = "";
  statusEl.textContent = "Connecting...";
  statusEl.className = "status";

  const theme = themeSelect.value;
  const provider = providerSelect.value;

  const params = new URLSearchParams({ url, theme, provider });
  let fullText = "";

  try {
    const response = await fetch(`${API_BASE}/summarise?${params}`);

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value, { stream: true });
      const lines = text.split("\n");

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const jsonStr = line.slice(6);

        try {
          const data = JSON.parse(jsonStr);

          if (data.error) {
            statusEl.textContent = `Error: ${data.error}`;
            statusEl.className = "status error";
            btn.disabled = false;
            return;
          }

          if (data.status === "detected") {
            statusEl.textContent = `Detected: ${data.type}`;
          } else if (data.status === "metadata") {
            statusEl.textContent = `Found: ${data.title || data.name || ""}`;
          } else if (data.status === "summarising") {
            statusEl.textContent = "Summarising...";
          } else if (data.status === "done") {
            statusEl.textContent = "Done";
          }

          if (data.token) {
            fullText += data.token;
            outputEl.innerHTML = marked.parse(fullText);
          }
        } catch (e) {
          // skip unparseable SSE lines
        }
      }
    }
  } catch (e) {
    statusEl.textContent = "Connection failed. Is the server running?";
    statusEl.className = "status error";
  }

  btn.disabled = false;
}
