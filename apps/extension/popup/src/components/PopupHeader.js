import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export function PopupHeader({ title, statusText, heightClass = "h-12", }) {
    return (_jsxs("div", { className: `
        ${heightClass}
        px-3
        flex
        items-center
        justify-between
        border-b
        border-gray-700
        font-semibold
        text-[14px]
      `, children: [_jsx("span", { children: title }), statusText ? (_jsx("span", { className: "text-[12px] font-normal text-gray-400", children: statusText })) : null] }));
}
