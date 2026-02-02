import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState } from "react";
import { PopupHeader } from "./components/PopupHeader";
import { useAuthStatus } from "./hooks/useAuthStatus";
import { useFolders } from "./hooks/useFolders";
function App() {
    const { loading: authLoading, isLoggedIn } = useAuthStatus();
    const { loading, folders } = useFolders(isLoggedIn);
    const [selectedFolderId, setSelectedFolderId] = useState(null);
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const [saving, setSaving] = useState(false);
    const openSyncmark = () => {
        chrome.tabs.create({ url: "https://localhost:8000" });
    };
    const handleSave = async () => {
        if (saving)
            return;
        setSaving(true);
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
            }, () => { });
        }
        finally {
            setSaving(false);
        }
    };
    const selectedFolderName = folders.find((f) => f.id === selectedFolderId)?.name ?? "No folder (Inbox)";
    const statusText = authLoading
        ? undefined
        : isLoggedIn
            ? `Saving to: ${selectedFolderName}`
            : "Login required";
    return (_jsxs("div", { className: "w-[420px] max-h-[680px] flex flex-col bg-[#0f0f11] text-white font-[system-ui]", children: [_jsx(PopupHeader, { title: "Syncmark", statusText: statusText, heightClass: "h-14" }), _jsx("div", { className: "flex-1 p-3 space-y-3 overflow-y-auto", children: !isLoggedIn ? (_jsx("button", { onClick: openSyncmark, className: "w-full py-2 border border-gray-600 text-sm rounded-md", children: "Open Syncmark" })) : (_jsxs(_Fragment, { children: [_jsxs("div", { className: "relative", children: [_jsx("div", { onClick: () => setDropdownOpen((v) => !v), className: "\n                  w-full\n                  px-2.5\n                  py-1.5\n                  border\n                  border-gray-600\n                  bg-[#1a1a1e]\n                  text-[13px]\n                  rounded-md\n                  cursor-pointer\n                ", children: selectedFolderName }), dropdownOpen && (_jsxs("div", { className: "\n                    absolute\n                    z-10\n                    mt-1\n                    w-full\n                    bg-[#1a1a1e]\n                    border\n                    border-gray-700\n                    rounded-md\n                    max-h-40\n                    overflow-y-auto\n                  ", children: [_jsx("div", { onClick: () => {
                                                setSelectedFolderId(null);
                                                setDropdownOpen(false);
                                            }, className: "\n                      px-2.5\n                      py-1\n                      text-[13px]\n                      hover:bg-[#26262b]\n                      cursor-pointer\n                      rounded-sm\n                    ", children: "No folder (Inbox)" }), loading ? (_jsx("div", { className: "px-2.5 py-1 text-[13px] text-gray-400", children: "Loading\u2026" })) : (folders.map((folder) => (_jsx("div", { onClick: () => {
                                                setSelectedFolderId(folder.id);
                                                setDropdownOpen(false);
                                            }, className: "\n                          px-2.5\n                          py-1\n                          text-[13px]\n                          hover:bg-[#26262b]\n                          cursor-pointer\n                          rounded-sm\n                        ", children: folder.name }, folder.id))))] }))] }), _jsx("button", { onClick: handleSave, disabled: saving, className: `w-full py-2 border border-gray-600 text-sm rounded-md ${saving ? "opacity-50" : "hover:bg-[#1a1a1e]"}`, children: saving ? "Saving…" : "Save Bookmark" })] })) })] }));
}
export default App;
