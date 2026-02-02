import type { Bookmark } from "@/packages/shared/types/bookmark";
import { useUpdateBookmarkMutation } from "@/api/bookmark.api";
import { Button } from "@/components/ui/button";
import { BookmarkFavicon } from "@/components/bookmarks/BookmarkFavicon";

export type BookmarkCardProps = {
  bookmark: Bookmark;
  onClick?: () => void;
};

export default function BookmarkCard({ bookmark, onClick }: BookmarkCardProps) {
  const [updateBookmark] = useUpdateBookmarkMutation();

  const toggleFeatured = () => {
    updateBookmark({
      bookmarkId: bookmark.id,
      payload: {
        is_featured: !bookmark.is_featured,
      },
    });
  };

  return (
    <div
      onClick={onClick}
      className="flex items-center justify-between gap-4 px-3 py-3 hover:bg-muted/50 cursor-pointer"
    >
      {/* LEFT: favicon + text */}
      <div className="flex items-center gap-3 min-w-0">
        <BookmarkFavicon url={bookmark.url} faviconUrl={bookmark.favicon_url} />

        <div className="min-w-0">
          <div className="truncate font-medium">
            {bookmark.title || bookmark.url}
          </div>
          <div className="truncate text-sm text-muted-foreground">
            {bookmark.url}
          </div>
        </div>
      </div>

      {/* RIGHT: star */}
      <Button
        size="icon"
        variant="ghost"
        onClick={(e) => {
          e.stopPropagation();
          toggleFeatured();
        }}
        aria-label="Toggle featured"
        className="shrink-0"
      >
        {bookmark.is_featured ? "★" : "☆"}
      </Button>
    </div>
  );
}
