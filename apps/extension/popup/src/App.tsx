import { useState, useEffect, useRef } from "react";
import { PopupHeader } from "./components/PopupHeader";
import { useAuthStatus } from "./hooks/useAuthStatus";
import { useFolders } from "./hooks/useFolders";

function App() {
  const { loading: authLoading, isLoggedIn } = useAuthStatus();
  const { loading, folders } = useFolders(isLoggedIn);

  const [selectedFolderId, setSelectedFolderId] = useState<string | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [currentUrl, setCurrentUrl] = useState<string | null>(null);
  const [isSaved, setIsSaved] = useState(false);

  const dropdownRef = useRef<HTMLDivElement | null>(null);

  /* ------------------------------
     Get active tab on open
  ------------------------------- */
  useEffect(() => {
    chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
      if (tab?.url) {
        setCurrentUrl(tab.url);
        setIsSaved(false);
      }
    });
  }, []);

  /* ------------------------------
     Check if bookmark already exists
  ------------------------------- */
  useEffect(() => {
    if (!currentUrl || !isLoggedIn) return;

    chrome.runtime.sendMessage(
      {
        type: "CHECK_BOOKMARK_EXISTS",
        payload: { url: currentUrl },
      },
      (res) => {
        if (res?.exists) {
          setIsSaved(true);
        }
      },
    );
  }, [currentUrl, isLoggedIn]);

  /* ------------------------------
     Close dropdown on outside click
  ------------------------------- */
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node)
      ) {
        setDropdownOpen(false);
      }
    }

    if (dropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [dropdownOpen]);

  const openSyncmark = () => {
    chrome.tabs.create({ url: "https://localhost:8000" });
  };

  const handleSave = async () => {
    if (saving || isSaved) return;
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
        (res) => {
          if (res?.success) {
            setIsSaved(true);
            setTimeout(() => window.close(), 600);
          }
        },
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
      ? isSaved
        ? "Bookmark saved"
        : `Saving to: ${selectedFolderName}`
      : "Login required";

  return (
    <div className="w-80 max-h-200 flex flex-col bg-[#0f0f11] text-white font-[system-ui]">
      <PopupHeader
        title="Syncmark"
        statusText={statusText}
        heightClass="h-14"
      />

      <div className="flex-1 p-3 space-y-2 overflow-y-auto">
        {!isLoggedIn ? (
          <button
            onClick={openSyncmark}
            className="w-full py-2 border border-gray-600 text-sm rounded-md"
          >
            Open Syncmark
          </button>
        ) : (
          <>
            {/* Folder dropdown */}
            <div ref={dropdownRef} className="relative">
              <div
                onClick={() => setDropdownOpen((v) => !v)}
                className="w-full px-2.5 py-1.5 border border-gray-600 bg-[#1a1a1e] text-[13px] rounded-md cursor-pointer hover:bg-[#202025]"
              >
                <div className="flex items-center justify-between">
                  <span className="truncate">{selectedFolderName}</span>
                  <span className="text-gray-400">▾</span>
                </div>
              </div>

              {dropdownOpen && (
                <div className="absolute z-10 mt-1 w-full bg-[#1a1a1e] border border-gray-700 rounded-md max-h-40 overflow-y-auto">
                  <div
                    onClick={() => {
                      setSelectedFolderId(null);
                      setDropdownOpen(false);
                    }}
                    className="px-2.5 py-1 text-[13px] hover:bg-[#26262b] cursor-pointer"
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
                        className="px-2.5 py-1 text-[13px] hover:bg-[#26262b] cursor-pointer"
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
              disabled={saving || isSaved}
              className={`w-full py-2 border text-sm rounded-md transition ${
                isSaved
                  ? "border-green-600 text-green-400 cursor-default"
                  : saving
                    ? "border-gray-600 opacity-50"
                    : "border-gray-600 hover:bg-[#1a1a1e]"
              }`}
            >
              {isSaved ? "✓ Saved" : saving ? "Saving…" : "Save Bookmark"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
