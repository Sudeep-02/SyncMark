const saveBtn = document.getElementById("saveBtn");
const statusDiv = document.getElementById("status");

saveBtn.addEventListener("click", async () => {
  statusDiv.textContent = "Saving...";

  const [tab] = await chrome.tabs.query({
    active: true,
    currentWindow: true,
  });

  // Safety: block non-http pages
  if (!tab.url.startsWith("http")) {
    statusDiv.textContent = "Cannot save this page";
    return;
  }

  chrome.runtime.sendMessage(
    {
      type: "SAVE_BOOKMARK",
      payload: {
        url: tab.url,
        title: tab.title,
      },
    },
    (response) => {
      statusDiv.textContent = response?.success
        ? "Saved ✅"
        : "Login required ❌";
    },
  );
});
