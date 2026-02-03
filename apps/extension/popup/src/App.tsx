import { useState, useEffect, useRef } from "react";
import { PopupHeader } from "./components/PopupHeader";
import { useAuthStatus } from "./hooks/useAuthStatus";
import { useFolders } from "./hooks/useFolders";
import { Toaster, toast } from "sonner";

function App() {
  const { loading: authLoading, isLoggedIn } = useAuthStatus();
  const { loading, folders } = useFolders(isLoggedIn);

  const [selectedFolderId, setSelectedFolderId] = useState<string | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [currentUrl, setCurrentUrl] = useState<string | null>(null);

  // 🔥 single terminal state
  const [saveState, setSaveState] = useState<
    "idle" | "saving" | "saved" | "duplicate"
  >("idle");

  const dropdownRef = useRef<HTMLDivElement | null>(null);

  /* ------------------------------
     Get active tab
  ------------------------------- */
  useEffect(() => {
    chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
      if (tab?.url) {
        setCurrentUrl(tab.url);
        setSaveState("idle");
      }
    });
  }, []);

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
    chrome.tabs.create({ url: "http://localhost:5173/login" });
  };

  /* ------------------------------
     Save bookmark
  ------------------------------- */
  const handleSave = async () => {
    if (saveState !== "idle") return;
    setSaveState("saving");

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
          if (!res) {
            setSaveState("idle");
            return;
          }

          if (res.ok) {
            setSaveState("saved");
            toast.success("Bookmark saved");
            setTimeout(() => window.close(), 1500);
            return;
          }

          if (res.reason === "DUPLICATE") {
            setSaveState("duplicate");
            toast("Already saved", {
              description: "This bookmark already exists.",
            });
            setTimeout(() => window.close(), 2800);
            return;
          }

          toast.error("Failed to save bookmark");
          setSaveState("idle");
        },
      );
    } catch {
      toast.error("Failed to save bookmark");
      setSaveState("idle");
    }
  };

  const selectedFolderName =
    folders.find((f) => f.id === selectedFolderId)?.name ?? "No folder (Inbox)";

  const statusText = authLoading
    ? undefined
    : !isLoggedIn
      ? "Login required"
      : saveState === "saved"
        ? "Bookmark saved"
        : saveState === "duplicate"
          ? "Duplicate"
          : `Saving to: ${selectedFolderName}`;

  const buttonLabel =
    saveState === "saved"
      ? "✓ Saved"
      : saveState === "duplicate"
        ? "Bookmark exists"
        : saveState === "saving"
          ? "Saving…"
          : "Save Bookmark";

  return (
    <div className="w-80 max-h-200 flex flex-col bg-[#0f0f11] text-white font-[system-ui]">
      {/*  REQUIRED FOR SONNER */}
      {/* <Toaster richColors position="bottom-left" /> */}

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
              disabled={saveState !== "idle"}
              className={`w-full py-2 border text-sm rounded-md transition ${
                saveState === "saved" || saveState === "duplicate"
                  ? "border-green-600 text-green-400 cursor-default"
                  : saveState === "saving"
                    ? "border-gray-600 opacity-50"
                    : "border-gray-600 hover:bg-[#1a1a1e]"
              }`}
            >
              {buttonLabel}
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
