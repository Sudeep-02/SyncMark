import { Globe } from "lucide-react";
import { useMemo, useState } from "react";

type Props = {
  url: string;
  faviconUrl?: string | null;
  size?: number;
};

/**
 * Explicit allow-list to avoid noisy favicon requests
 * (silences localhost, random strings, junk domains)
 */
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

    // Only allow http(s)
    if (u.protocol !== "http:" && u.protocol !== "https:") {
      return null;
    }

    const parts = u.hostname.split(".");
    if (parts.length < 2) return null;

    const tld = parts[parts.length - 1].toLowerCase();

    //Silence favicon fetch for unknown domains
    if (!ALLOWED_TLDS.includes(tld)) {
      return null;
    }

    return `${u.origin}/favicon.ico`;
  } catch {
    return null;
  }
}

export function BookmarkFavicon({ url, faviconUrl, size = 16 }: Props) {
  const [failed, setFailed] = useState(false);

  /**
   * Priority:
   * 1. Backend-provided favicon
   * 2. Safe favicon.ico fallback
   * 3. Globe icon
   */
  const src = useMemo(() => {
    if (faviconUrl) return faviconUrl;
    return getSafeFavicon(url);
  }, [url, faviconUrl]);

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
      referrerPolicy="no-referrer"
      onError={() => setFailed(true)}
    />
  );
}
