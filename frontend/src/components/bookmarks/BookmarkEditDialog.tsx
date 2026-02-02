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
import { useEffect, useState } from "react";

import type { Bookmark } from "@/packages/shared/types/bookmark";
import { useUpdateBookmarkMutation } from "@/api/bookmark.api";

type Props = {
  bookmark: Bookmark | null;
  open: boolean;
  onClose: () => void;
};

export function BookmarkEditDialog({ bookmark, open, onClose }: Props) {
  const [updateBookmark, { isLoading }] = useUpdateBookmarkMutation();

  const [title, setTitle] = useState("");
  const [url, setUrl] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  // Prefill form when bookmark changes
  useEffect(() => {
    if (!bookmark) return;
    setTitle(bookmark.title ?? "");
    setUrl(bookmark.url);
    setDescription(bookmark.description ?? "");
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
