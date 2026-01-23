import { useGetBookmarksQuery } from "@/api/bookmark.api";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { Card, CardContent } from "@/components/ui/card";

import AddBookmarkDialog from "./AddBookmarkDialog";
import BookmarkCard from "@/components/layout/BookmarkCard";

export default function DashboardBookmarks({
  folderId,
  tagId,
}: {
  folderId?: string;
  tagId?: string;
}) {
  const queryParams = {
    ...(folderId && { folder_id: folderId }),
    ...(tagId && { tag_id: tagId }),
  };

  const {
    data: bookmarks,
    isLoading,
    error,
  } = useGetBookmarksQuery(queryParams);

  if (error) {
    return (
      <div className="flex h-full items-center justify-center text-destructive">
        Failed to load bookmarks
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col rounded-xl border bg-background">
      <div className="flex items-center justify-between p-4">
        <h2 className="text-lg font-semibold">Bookmarks</h2>
        <AddBookmarkDialog folderId={folderId} />
      </div>

      <Separator />

      <ScrollArea className="flex-1 p-4">
        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <Skeleton key={i} className="h-32 rounded-xl" />
            ))}
          </div>
        ) : bookmarks?.length === 0 ? (
          <Card className="mx-auto max-w-md">
            <CardContent className="p-6 text-center text-muted-foreground">
              No bookmarks found
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {bookmarks?.map((bookmark) => (
              <BookmarkCard key={bookmark.id} bookmark={bookmark} />
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
