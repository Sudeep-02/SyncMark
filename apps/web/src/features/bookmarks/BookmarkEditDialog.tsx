import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { useEffect, useMemo, useState } from "react";
import React from "react";
import { ChevronRight, CornerDownRight } from "lucide-react";

import type { Bookmark } from "@/shared/types/bookmark";
import type { Folder } from "@/shared/types/folder";
import { useUpdateBookmarkMutation } from "@/api/bookmark.api";
import { useGetFoldersQuery } from "@/api/folder.api";

type Props = {
  bookmark: Bookmark | null;
  open: boolean;
  onClose: () => void;
};

/* ---------- UI TYPES ---------- */

type UIFolder = {
  id: string;
  name: string;
  parent_id: string | null;
};

type FolderNode = UIFolder & { children: FolderNode[] };

/* ---------- TREE BUILD ---------- */

function buildFolderTree(folders: UIFolder[]): FolderNode[] {
  const map = new Map<string, FolderNode>();
  const roots: FolderNode[] = [];

  folders.forEach((f) => {
    map.set(f.id, { ...f, children: [] });
  });

  map.forEach((folder) => {
    if (folder.parent_id) {
      map.get(folder.parent_id)?.children.push(folder);
    } else {
      roots.push(folder);
    }
  });

  return roots;
}

/* ---------- TREE RENDER ---------- */

function renderFolderOptions(
  nodes: FolderNode[],
  depth = 0,
): React.ReactNode[] {
  return nodes.flatMap((folder) => {
    const isChild = depth > 0;

    return [
      <SelectItem key={folder.id} value={folder.id}>
        <div
          className="flex items-center gap-2"
          style={{ paddingLeft: depth * 12 }}
        >
          {isChild ? (
            <CornerDownRight className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          )}
          <span>{folder.name}</span>
        </div>
      </SelectItem>,

      ...renderFolderOptions(folder.children, depth + 1),
    ];
  });
}

/* ---------- COMPONENT ---------- */

export function BookmarkEditDialog({ bookmark, open, onClose }: Props) {
  const [updateBookmark, { isLoading }] = useUpdateBookmarkMutation();
  const { data: folders = [] } = useGetFoldersQuery();

  const [title, setTitle] = useState("");
  const [url, setUrl] = useState("");
  const [description, setDescription] = useState("");
  const [folderId, setFolderId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const uiFolders: UIFolder[] = useMemo(
    () =>
      folders.map((f: Folder) => ({
        id: f.id,
        name: f.name,
        parent_id: (f as any).parent_id ?? null,
      })),
    [folders],
  );

  const folderTree = useMemo(() => buildFolderTree(uiFolders), [uiFolders]);

  useEffect(() => {
    if (!bookmark) return;

    setTitle(bookmark.title ?? "");
    setUrl(bookmark.url);
    setDescription(bookmark.description ?? "");
    setFolderId(bookmark.folder_id ?? null);
  }, [bookmark]);

  if (!bookmark) return null;

  const handleSave = async () => {
    setError(null);

    try {
      await updateBookmark({
        bookmarkId: bookmark.id,
        payload: {
          title: title || undefined,
          url,
          description: description || undefined,
          folder_id: folderId,
        },
      }).unwrap();

      onClose();
    } catch {
      setError("Failed to update bookmark");
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Bookmark</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <Input
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />

          <Input
            placeholder="URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />

          {/* Folder selector */}
          <Select
            value={folderId ?? "root"}
            onValueChange={(value) =>
              setFolderId(value === "root" ? null : value)
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Select folder" />
            </SelectTrigger>

            <SelectContent>
              <SelectItem value="root">Root</SelectItem>
              {renderFolderOptions(folderTree)}
            </SelectContent>
          </Select>

          <Textarea
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          {error && <p className="text-sm text-destructive">{error}</p>}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={isLoading}>
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
