import { Bookmark } from "@/packages/shared/types/bookmark";
import { useToggleFeaturedMutation } from "@/api/bookmark.api";

import { Card, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function BookmarkCard({ bookmark }: { bookmark: Bookmark }) {
  const [toggleFeatured] = useToggleFeaturedMutation();

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div className="min-w-0">
          <h3 className="truncate font-medium">
            {bookmark.title || bookmark.url}
          </h3>
          <p className="truncate text-sm text-muted-foreground">
            {bookmark.url}
          </p>
        </div>

        <Button
          size="icon"
          variant="ghost"
          onClick={() =>
            toggleFeatured({
              id: bookmark.id,
              is_featured: !bookmark.is_featured,
            })
          }
        >
          {bookmark.is_featured ? "★" : "☆"}
        </Button>
      </CardHeader>
    </Card>
  );
}
