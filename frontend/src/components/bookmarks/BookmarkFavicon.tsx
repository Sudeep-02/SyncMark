import { Globe } from "lucide-react";
import { useMemo, useState } from "react";

type Props = {
  url: string;
  size?: number;
};

// ✅ explicit allow-list
const ALLOWED_TLDS = [
  "com",
  "org",
  "net",
  "io",
  "dev",
  "app",
  "co",
  "in",
  "ai",
  "edu",
];

function getSafeFavicon(url: string): string | null {
  try {
    const u = new URL(url);

    if (u.protocol !== "http:" && u.protocol !== "https:") return null;

    const parts = u.hostname.split(".");
    if (parts.length < 2) return null;

    const tld = parts[parts.length - 1].toLowerCase();

    // 🔕 SILENCE SOURCE HERE
    if (!ALLOWED_TLDS.includes(tld)) return null;

    return `${u.origin}/favicon.ico`;
  } catch {
    return null;
  }
}

export function BookmarkFavicon({ url, size = 16 }: Props) {
  const [failed, setFailed] = useState(false);

  const src = useMemo(() => getSafeFavicon(url), [url]);

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
      width={size}
      height={size}
      alt=""
      loading="lazy"
      onError={() => setFailed(true)}
    />
  );
}
