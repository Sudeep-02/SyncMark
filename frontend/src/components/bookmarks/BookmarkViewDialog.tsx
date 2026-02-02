import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import type { Bookmark } from "@/packages/shared/types/bookmark";
import { BookmarkFavicon } from "@/components/bookmarks/BookmarkFavicon";

type Props = {
  bookmark: Bookmark | null;
  open: boolean;
  onClose: () => void;
  onEdit: () => void;
  onDelete: () => void;
};

export function BookmarkViewDialog({
  bookmark,
  open,
  onClose,
  onEdit,
  onDelete,
}: Props) {
  if (!bookmark) return null;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl bg-background/80 backdrop-blur-md p-6 rounded-xl">
        {/* ---------- HEADER ---------- */}
        <DialogHeader className="space-y-2">
          <DialogTitle className="flex items-center gap-3 text-lg">
            <BookmarkFavicon
              url={bookmark.url}
              faviconUrl={bookmark.favicon_url}
              size={20}
            />
            <span className="truncate">
              {bookmark.title || "Untitled bookmark"}
            </span>
          </DialogTitle>

          <DialogDescription className="sr-only">
            View bookmark details including description and metadata.
          </DialogDescription>

          <a
            href={bookmark.url}
            target="_blank"
            rel="noreferrer"
            className="text-sm text-muted-foreground hover:underline break-all"
          >
            {bookmark.url}
          </a>
        </DialogHeader>

        {/* ---------- CONTENT ---------- */}
        <div className="mt-6 space-y-6 text-sm">
          {bookmark.description ? (
            <p className="leading-relaxed text-foreground">
              {bookmark.description}
            </p>
          ) : (
            <p className="italic text-muted-foreground">
              No description provided
            </p>
          )}

          {/* ---------- META ---------- */}
          <div className="text-xs text-muted-foreground">
            Added on {new Date(bookmark.created_at).toLocaleDateString()}
          </div>
        </div>

        {/* ---------- FOOTER ---------- */}
        <DialogFooter className="mt-8 flex justify-between">
          <Button variant="destructive" onClick={onDelete}>
            Delete
          </Button>

          <div className="flex gap-2">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            <Button onClick={onEdit}>Edit</Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
