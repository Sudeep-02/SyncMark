const DEVICE_ID_KEY = "device_id";

/**
 * Returns a stable browser-level device ID.
 * - Generated once per browser
 * - Persisted in localStorage
 * - Safe for production use
 */
export function getDeviceId(): string {
  // Safety guard (SSR / tests / non-browser)
  if (typeof window === "undefined") {
    return "unknown-device";
  }

  let deviceId = localStorage.getItem(DEVICE_ID_KEY);

  if (!deviceId) {
    deviceId = crypto.randomUUID();
    localStorage.setItem(DEVICE_ID_KEY, deviceId);
  }

  return deviceId;
}
