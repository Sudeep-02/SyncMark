import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import type { Bookmark } from "@/packages/shared/types/bookmark";
import { useDeleteBookmarkMutation } from "@/api/bookmark.api";

type Props = {
  bookmark: Bookmark | null;
  open: boolean;
  onClose: () => void;
};

export function BookmarkDeleteDialog({ bookmark, open, onClose }: Props) {
  const [deleteBookmark, { isLoading }] = useDeleteBookmarkMutation();

  if (!bookmark) return null;

  const handleDelete = async () => {
    await deleteBookmark(bookmark.id).unwrap();
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete “{bookmark.title || bookmark.url}”?</DialogTitle>
        </DialogHeader>

        <p className="text-sm text-muted-foreground">
          This action cannot be undone.
        </p>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={isLoading}
          >
            Delete
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
