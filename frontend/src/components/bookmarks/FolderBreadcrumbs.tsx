"use client";

import * as React from "react";
import { ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSearchParams } from "react-router-dom";
import { useGetFoldersQuery } from "@/api/folder.api";

type Folder = {
  id: string;
  name: string;
  parent_id?: string | null;
};

export function FolderBreadcrumbs({ folderId }: { folderId?: string }) {
  const { data: folders = [] } = useGetFoldersQuery();
  const [searchParams, setSearchParams] = useSearchParams();

  const path = React.useMemo(() => {
    if (!folderId) return [];

    const map = new Map<string, Folder>();
    folders.forEach((f) => map.set(f.id, f));

    const result: Folder[] = [];
    let current = map.get(folderId);

    while (current) {
      result.push(current);
      current = current.parent_id ? map.get(current.parent_id) : undefined;
    }

    return result.reverse();
  }, [folderId, folders]);

  const navigateTo = (id?: string) => {
    const next = new URLSearchParams(searchParams);

    if (!id) {
      next.delete("folder");
    } else {
      next.set("folder", id);
    }

    setSearchParams(next);
  };

  return (
    <div className="flex items-center gap-1 text-sm text-muted-foreground">
      <Button variant="ghost" size="sm" onClick={() => navigateTo(undefined)}>
        All Bookmarks
      </Button>

      {path.map((folder) => (
        <React.Fragment key={folder.id}>
          <ChevronRight className="h-4 w-4" />
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigateTo(folder.id)}
          >
            {folder.name}
          </Button>
        </React.Fragment>
      ))}
    </div>
  );
}
