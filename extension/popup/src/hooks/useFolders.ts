import { useEffect, useState } from "react";

export type Folder = {
  id: string;
  name: string;
  parent_id?: string | null;
};

type UseFoldersResult = {
  loading: boolean;
  folders: Folder[];
  error: boolean;
};

export function useFolders(enabled: boolean): UseFoldersResult {
  const [loading, setLoading] = useState(false);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!enabled) {
      setFolders([]);
      setLoading(false);
      setError(false);
      return;
    }

    let cancelled = false;

    async function fetchFolders() {
      try {
        setLoading(true);
        setError(false);

        const response = await fetch("https://localhost:8000/folders/", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error("Failed to fetch folders");
        }

        const data: Folder[] = await response.json();

        if (!cancelled) {
          setFolders(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(true);
          setFolders([]);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchFolders();

    return () => {
      cancelled = true;
    };
  }, [enabled]);

  return {
    loading,
    folders,
    error,
  };
}
