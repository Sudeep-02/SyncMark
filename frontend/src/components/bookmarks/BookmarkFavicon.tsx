import { Globe } from "lucide-react";
import { useState } from "react";

type Props = {
  url: string;
  faviconUrl?: string | null;
  size?: number;
};

function getDomain(url: string) {
  try {
    return new URL(url).hostname;
  } catch {
    return null;
  }
}

function isBlockedFavicon(url?: string | null) {
  return !!url && url.includes("gstatic.com/faviconV2");
}

export function BookmarkFavicon({ url, faviconUrl, size = 16 }: Props) {
  const domain = getDomain(url);
  const [failed, setFailed] = useState(false);

  // 🚨 HARD BLOCK legacy Google favicon service
  const safeFaviconUrl =
    faviconUrl && !isBlockedFavicon(faviconUrl) ? faviconUrl : null;

  const src =
    safeFaviconUrl ||
    (domain
      ? `https://www.google.com/s2/favicons?domain=${domain}&sz=64`
      : null);

  console.log("faviconUrl prop =", src);
  if (!src || failed) {
    return (
      <Globe
        className="shrink-0 text-muted-foreground"
        style={{ width: size, height: size }}
        aria-hidden
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
      onError={() => setFailed(true)}
    />
  );
}
