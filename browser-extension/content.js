document.addEventListener("click", function (event) {
  try {
    let target = event.target;

    // Find the closest <a> tag (if the user clicks a nested element)
    while (target && target.tagName !== "A") {
      target = target.parentElement;
    }

    if (target && target.href) {
      event.preventDefault(); // Stop default navigation

      // Send message to background.js
      chrome.runtime.sendMessage({
        action: "analyzeLink",
        link: target.href,
      });
    }
  } catch (error) {
    console.error("Error in content.js:", error);
  }
});
