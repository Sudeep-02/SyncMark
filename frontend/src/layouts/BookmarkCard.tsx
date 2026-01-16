import { Bookmark } from "@/packages/shared/types/bookmark";
import { useUpdateBookmarkMutation } from "@/api/bookmark.api";

import { Card, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function BookmarkCard({ bookmark }: { bookmark: Bookmark }) {
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
    <Card>
      <CardHeader className="flex flex-row justify-between gap-4">
        <div className="min-w-0">
          <h3 className="truncate font-medium">
            {bookmark.title || bookmark.url}
          </h3>
          <p className="truncate text-sm text-muted-foreground">
            {bookmark.url}
          </p>
        </div>

        <Button size="icon" variant="ghost" onClick={toggleFeatured}>
          {bookmark.is_featured ? "★" : "☆"}
        </Button>
      </CardHeader>
    </Card>
  );
}
