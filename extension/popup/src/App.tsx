import { useState } from "react";
import { PopupHeader } from "./components/PopupHeader";
import { useAuthStatus } from "./hooks/useAuthStatus";
import { useFolders } from "./hooks/useFolders";

function App() {
  const { loading: authLoading, isLoggedIn } = useAuthStatus();
  const { loading, folders } = useFolders(isLoggedIn);

  const [selectedFolderId, setSelectedFolderId] = useState<string | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const openSyncmark = () => {
    chrome.tabs.create({ url: "https://localhost:8000" });
  };

  const handleSave = async () => {
    if (saving) return;
    setSaving(true);

    try {
      const [tab] = await chrome.tabs.query({
        active: true,
        currentWindow: true,
      });

      if (!tab?.url || !tab.title) return;

      chrome.runtime.sendMessage(
        {
          type: "SAVE_BOOKMARK",
          payload: {
            url: tab.url,
            title: tab.title,
            ...(selectedFolderId ? { folder_id: selectedFolderId } : {}),
          },
        },
        () => {},
      );
    } finally {
      setSaving(false);
    }
  };

  const selectedFolderName =
    folders.find((f) => f.id === selectedFolderId)?.name ?? "No folder (Inbox)";

  const statusText = authLoading
    ? undefined
    : isLoggedIn
      ? `Saving to: ${selectedFolderName}`
      : "Login required";

  return (
    <div className="w-[420px] max-h-[680px] flex flex-col bg-[#0f0f11] text-white font-[system-ui]">
      <PopupHeader
        title="Syncmark"
        statusText={statusText}
        heightClass="h-14"
      />

      <div className="flex-1 p-3 space-y-3 overflow-y-auto">
        {!isLoggedIn ? (
          <button
            onClick={openSyncmark}
            className="w-full py-2 border border-gray-600 text-sm rounded-md"
          >
            Open Syncmark
          </button>
        ) : (
          <>
            {/* Custom dropdown (refined) */}
            <div className="relative">
              <div
                onClick={() => setDropdownOpen((v) => !v)}
                className="
                  w-full
                  px-2.5
                  py-1.5
                  border
                  border-gray-600
                  bg-[#1a1a1e]
                  text-[13px]
                  rounded-md
                  cursor-pointer
                "
              >
                {selectedFolderName}
              </div>

              {dropdownOpen && (
                <div
                  className="
                    absolute
                    z-10
                    mt-1
                    w-full
                    bg-[#1a1a1e]
                    border
                    border-gray-700
                    rounded-md
                    max-h-40
                    overflow-y-auto
                  "
                >
                  <div
                    onClick={() => {
                      setSelectedFolderId(null);
                      setDropdownOpen(false);
                    }}
                    className="
                      px-2.5
                      py-1
                      text-[13px]
                      hover:bg-[#26262b]
                      cursor-pointer
                      rounded-sm
                    "
                  >
                    No folder (Inbox)
                  </div>

                  {loading ? (
                    <div className="px-2.5 py-1 text-[13px] text-gray-400">
                      Loading…
                    </div>
                  ) : (
                    folders.map((folder) => (
                      <div
                        key={folder.id}
                        onClick={() => {
                          setSelectedFolderId(folder.id);
                          setDropdownOpen(false);
                        }}
                        className="
                          px-2.5
                          py-1
                          text-[13px]
                          hover:bg-[#26262b]
                          cursor-pointer
                          rounded-sm
                        "
                      >
                        {folder.name}
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>

            {/* Save button */}
            <button
              onClick={handleSave}
              disabled={saving}
              className={`w-full py-2 border border-gray-600 text-sm rounded-md ${
                saving ? "opacity-50" : "hover:bg-[#1a1a1e]"
              }`}
            >
              {saving ? "Saving…" : "Save Bookmark"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
