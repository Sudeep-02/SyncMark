import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect, useRef } from "react";
import { PopupHeader } from "./components/PopupHeader";
import { useAuthStatus } from "./hooks/useAuthStatus";
import { useFolders } from "./hooks/useFolders";
import { toast } from "sonner";
function App() {
    const { loading: authLoading, isLoggedIn } = useAuthStatus();
    const { loading, folders } = useFolders(isLoggedIn);
    const [selectedFolderId, setSelectedFolderId] = useState(null);
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const [saving, setSaving] = useState(false);
    const [currentUrl, setCurrentUrl] = useState(null);
    // 🔥 single terminal state
    const [saveState, setSaveState] = useState("idle");
    const dropdownRef = useRef(null);
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
        function handleClickOutside(e) {
            if (dropdownRef.current &&
                !dropdownRef.current.contains(e.target)) {
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
        if (saveState !== "idle")
            return;
        setSaveState("saving");
        try {
            const [tab] = await chrome.tabs.query({
                active: true,
                currentWindow: true,
            });
            if (!tab?.url || !tab.title)
                return;
            chrome.runtime.sendMessage({
                type: "SAVE_BOOKMARK",
                payload: {
                    url: tab.url,
                    title: tab.title,
                    ...(selectedFolderId ? { folder_id: selectedFolderId } : {}),
                },
            }, (res) => {
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
            });
        }
        catch {
            toast.error("Failed to save bookmark");
            setSaveState("idle");
        }
    };
    const selectedFolderName = folders.find((f) => f.id === selectedFolderId)?.name ?? "No folder (Inbox)";
    const statusText = authLoading
        ? undefined
        : !isLoggedIn
            ? "Login required"
            : saveState === "saved"
                ? "Bookmark saved"
                : saveState === "duplicate"
                    ? "Duplicate"
                    : `Saving to: ${selectedFolderName}`;
    const buttonLabel = saveState === "saved"
        ? "✓ Saved"
        : saveState === "duplicate"
            ? "Bookmark exists"
            : saveState === "saving"
                ? "Saving…"
                : "Save Bookmark";
    return (_jsxs("div", { className: "w-80 max-h-200 flex flex-col bg-[#0f0f11] text-white font-[system-ui]", children: [_jsx(PopupHeader, { title: "Syncmark", statusText: statusText, heightClass: "h-14" }), _jsx("div", { className: "flex-1 p-3 space-y-2 overflow-y-auto", children: !isLoggedIn ? (_jsx("button", { onClick: openSyncmark, className: "w-full py-2 border border-gray-600 text-sm rounded-md", children: "Open Syncmark" })) : (_jsxs(_Fragment, { children: [_jsxs("div", { ref: dropdownRef, className: "relative", children: [_jsx("div", { onClick: () => setDropdownOpen((v) => !v), className: "w-full px-2.5 py-1.5 border border-gray-600 bg-[#1a1a1e] text-[13px] rounded-md cursor-pointer hover:bg-[#202025]", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsx("span", { className: "truncate", children: selectedFolderName }), _jsx("span", { className: "text-gray-400", children: "\u25BE" })] }) }), dropdownOpen && (_jsxs("div", { className: "absolute z-10 mt-1 w-full bg-[#1a1a1e] border border-gray-700 rounded-md max-h-40 overflow-y-auto", children: [_jsx("div", { onClick: () => {
                                                setSelectedFolderId(null);
                                                setDropdownOpen(false);
                                            }, className: "px-2.5 py-1 text-[13px] hover:bg-[#26262b] cursor-pointer", children: "No folder (Inbox)" }), loading ? (_jsx("div", { className: "px-2.5 py-1 text-[13px] text-gray-400", children: "Loading\u2026" })) : (folders.map((folder) => (_jsx("div", { onClick: () => {
                                                setSelectedFolderId(folder.id);
                                                setDropdownOpen(false);
                                            }, className: "px-2.5 py-1 text-[13px] hover:bg-[#26262b] cursor-pointer", children: folder.name }, folder.id))))] }))] }), _jsx("button", { onClick: handleSave, disabled: saveState !== "idle", className: `w-full py-2 border text-sm rounded-md transition ${saveState === "saved" || saveState === "duplicate"
                                ? "border-green-600 text-green-400 cursor-default"
                                : saveState === "saving"
                                    ? "border-gray-600 opacity-50"
                                    : "border-gray-600 hover:bg-[#1a1a1e]"}`, children: buttonLabel })] })) })] }));
}
export default App;
