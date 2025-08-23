// Function to analyze a URL
function analyzeURL(url, tabId) {
  if (!url || !url.startsWith("http")) return; // Ignore invalid URLs

  console.log(`🔍 Analyzing URL: ${url}`);

  // Show notification that the link is being analyzed
  chrome.notifications.create({
    type: "basic",
    iconUrl: "icon48.png",
    title: "🔍 Link Analyzer",
    message: `Analyzing: ${url}`,
  });

  // Send the URL to Flask backend
  fetch(`http://localhost:5000/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: url }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("🔹 Received Analysis:", data);

      if (typeof data.safe === "undefined") {
        console.error("❌ Invalid API response: Missing 'safe'");
        return;
      }

      if (!data.safe) {
        // If unsafe, block the site
        chrome.notifications.create({
          type: "basic",
          iconUrl: "icon48.png",
          title: "⚠️ Unsafe Website",
          message: `Blocked: ${url}`,
        });

        // Redirect to a warning page by opening a new tab
        chrome.tabs.create({ url: "blocked_page.html" });

        // Close the original unsafe tab after a short delay
        // Close the original unsafe tab safely
        setTimeout(() => {
          chrome.tabs.get(tabId, (tab) => {
            if (chrome.runtime.lastError) {
              console.warn(`Tab ${tabId} does not exist or is already closed.`);
              return;
            }
            chrome.tabs.remove(tabId);
          });
        }, 2000);
      } else {
        console.log("✅ Safe to proceed.");
      }
    })
    .catch((error) => {
      console.error("❌ Error:", error);
      chrome.notifications.create({
        type: "basic",
        iconUrl: "icon48.png",
        title: "Error ❌",
        message: `Could not analyze: ${url}`,
      });
    });
}

// 🔹 Capture all navigations (including bookmarks, notepad, etc.)
chrome.webNavigation.onCommitted.addListener((details) => {
  if (details.frameId === 0) {
    analyzeURL(details.url, details.tabId);
  }
});

// 🔹 Capture when the tab URL changes (important for some external links)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url) {
    analyzeURL(changeInfo.url, tabId);
  }
});
