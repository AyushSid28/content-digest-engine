const apiKeyInput = document.getElementById("apiKey");
const providerSelect = document.getElementById("provider");
const themeSelect = document.getElementById("theme");
const saveBtn = document.getElementById("saveBtn");
const panelBtn = document.getElementById("panelBtn");
const msg = document.getElementById("msg");
const keyStatus = document.getElementById("keyStatus");

function showStatus(hasKey) {
  const dot = hasKey ? "ok" : "missing";
  const text = hasKey ? "API key configured" : "No API key set — add one above";
  keyStatus.innerHTML = `<span class="status-dot ${dot}"></span>${text}`;
}

chrome.storage.local.get(["apiKey", "provider", "theme"], (data) => {
  if (data.apiKey) apiKeyInput.value = data.apiKey;
  if (data.provider) providerSelect.value = data.provider;
  if (data.theme) themeSelect.value = data.theme;
  showStatus(!!data.apiKey);
});

saveBtn.addEventListener("click", () => {
  const key = apiKeyInput.value.trim();
  if (!key) {
    msg.textContent = "Please enter an API key";
    msg.className = "msg error";
    msg.style.display = "block";
    return;
  }
  chrome.storage.local.set({
    apiKey: key,
    provider: providerSelect.value,
    theme: themeSelect.value,
  }, () => {
    msg.textContent = "Settings saved!";
    msg.className = "msg";
    msg.style.display = "block";
    showStatus(true);
    setTimeout(() => { msg.style.display = "none"; }, 2000);
  });
});

panelBtn.addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab) {
    chrome.sidePanel.open({ windowId: tab.windowId });
    window.close();
  }
});
