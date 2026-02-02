import { Globe } from "lucide-react";

type Props = {
  url: string;
  faviconUrl?: string;
  size?: number;
};

function getDomain(url: string) {
  try {
    return new URL(url).hostname;
  } catch {
    return null;
  }
}

export function BookmarkFavicon({ url, faviconUrl, size = 16 }: Props) {
  const domain = getDomain(url);

  const src =
    faviconUrl ||
    (domain
      ? `https://www.google.com/s2/favicons?domain=${domain}&sz=64`
      : null);

  if (!src) {
    return (
      <Globe
        className="text-muted-foreground"
        style={{ width: size, height: size }}
      />
    );
  }

  return (
    <img
      src={src}
      alt=""
      width={size}
      height={size}
      className="shrink-0"
      onError={(e) => {
        // fallback icon if image fails
        e.currentTarget.style.display = "none";
      }}
    />
  );
}
