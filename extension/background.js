chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "extractContent") {
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
      const tab = tabs[0];
      if (!tab?.id) {
        sendResponse({ error: "No active tab" });
        return;
      }

      if (tab.url.startsWith("chrome://") || tab.url.startsWith("chrome-extension://") || tab.url.startsWith("about:")) {
        sendResponse({ error: "Cannot summarise browser internal pages" });
        return;
      }

      try {
        const results = await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          func: () => {
            const selectors = ["article", "main", "[role='main']", ".post-content", ".entry-content", ".article-body"];
            let el = null;
            for (const sel of selectors) {
              el = document.querySelector(sel);
              if (el) break;
            }
            if (!el) el = document.body;

            const remove = el.querySelectorAll("script, style, nav, footer, header, aside, .sidebar, .comments, .ad, [role='navigation']");
            const clone = el.cloneNode(true);
            clone.querySelectorAll("script, style, nav, footer, header, aside, .sidebar, .comments, .ad, [role='navigation']").forEach(n => n.remove());

            return {
              title: document.title,
              url: window.location.href,
              text: clone.innerText.trim().slice(0, 30000),
            };
          },
        });

        if (results && results[0]?.result) {
          sendResponse({ content: results[0].result });
        } else {
          sendResponse({ error: "Could not extract page content" });
        }
      } catch (e) {
        sendResponse({ error: "Failed to access page: " + e.message });
      }
    });
    return true;
  }
});
