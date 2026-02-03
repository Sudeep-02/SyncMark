type PopupHeaderProps = {
  title: string;
  statusText?: string;
  heightClass?: string;
};

export function PopupHeader({
  title,
  statusText,
  heightClass = "h-12",
}: PopupHeaderProps) {
  return (
    <div
      className={`
        ${heightClass}
        px-3
        flex
        items-center
        justify-between
        border-b
        border-gray-700
        font-semibold
        text-[14px]
      `}
    >
      <span>{title}</span>

      {statusText ? (
        <span className="text-[12px] font-normal text-gray-400">
          {statusText}
        </span>
      ) : null}
    </div>
  );
}
