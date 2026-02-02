import { useGetBookmarksQuery } from "@/api/bookmark.api";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { Card, CardContent } from "@/components/ui/card";
import { useState } from "react";
import type { Bookmark } from "@/packages/shared/types/bookmark";

import { BookmarkViewDialog } from "@/components/bookmarks/BookmarkViewDialog";
import { BookmarkEditDialog } from "@/components/bookmarks/BookmarkEditDialog";
import { BookmarkDeleteDialog } from "@/components/bookmarks/BookmarkDeleteDialog";
import { AddBookmarkDialog } from "@/components/bookmarks/AddBookmarkDialog";
import BookmarkCard from "@/components/layout/BookmarkCard";
import { FolderBreadcrumbs } from "@/components/bookmarks/FolderBreadcrumbs";

export default function DashboardBookmarks({
  folderId,
  tagId,
}: {
  folderId?: string;
  tagId?: string;
}) {
  /* ------------------ MODE DETECTION ------------------ */
  const isRecent = folderId === "recent";

  /* ------------------ QUERY PARAMS ------------------ */
  const queryParams = isRecent
    ? undefined
    : {
        ...(folderId && { folder_id: folderId }),
        ...(tagId && { tag_id: tagId }),
      };

  /* ------------------ LOCAL STATE ------------------ */
  const [search, setSearch] = useState("");

  const [selectedBookmark, setSelectedBookmark] = useState<Bookmark | null>(
    null,
  );
  const [viewOpen, setViewOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);

  /* ------------------ DATA FETCH ------------------ */
  const {
    data: bookmarks,
    isLoading,
    error,
  } = useGetBookmarksQuery(queryParams);

  /* ------------------ ERROR STATE ------------------ */
  if (error) {
    return (
      <div className="flex h-full items-center justify-center text-destructive">
        Failed to load bookmarks
      </div>
    );
  }

  /* ------------------ SEARCH FILTER ------------------ */
  const filteredBookmarks = bookmarks?.filter((b) => {
    const q = search.toLowerCase();
    return (
      b.title?.toLowerCase().includes(q) ||
      b.url.toLowerCase().includes(q) ||
      b.description?.toLowerCase().includes(q)
    );
  });

  /* ------------------ RECENT SORT ------------------ */
  const visibleBookmarks = isRecent
    ? [...(filteredBookmarks ?? [])].sort(
        (a, b) =>
          new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime(),
      )
    : filteredBookmarks;

  /* ------------------ RENDER ------------------ */
  return (
    <div className="flex h-full flex-col rounded-xl border bg-background/60 backdrop-blur">
      {/* Header */}
      <div className="flex flex-col gap-2 p-4">
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">
              {isRecent ? "Recent Bookmarks" : "Bookmarks"}
            </h2>
            <AddBookmarkDialog folderId={folderId} />
          </div>

          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search bookmarks…"
            className="w-full rounded-md border px-3 py-2 text-sm"
          />
        </div>

        <FolderBreadcrumbs folderId={folderId} />
      </div>

      <Separator />

      {/* Content */}
      <ScrollArea className="flex-1 p-4">
        {isLoading ? (
          <div
            aria-busy="true"
            className="grid gap-4 md:grid-cols-2 lg:grid-cols-3"
          >
            {[...Array(6)].map((_, i) => (
              <Skeleton key={i} className="h-32 rounded-xl" />
            ))}
          </div>
        ) : visibleBookmarks?.length === 0 ? (
          <Card className="mx-auto max-w-md">
            <CardContent className="p-6 text-center text-muted-foreground">
              {search
                ? "No bookmarks match your search"
                : isRecent
                  ? "No recent bookmarks"
                  : "No bookmarks in this folder"}
            </CardContent>
          </Card>
        ) : (
          // <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <div className="flex flex-col divide-y">
            {visibleBookmarks?.map((bookmark) => (
              <BookmarkCard
                key={bookmark.id}
                bookmark={bookmark}
                onClick={() => {
                  setSelectedBookmark(bookmark);
                  setViewOpen(true);
                }}
              />
            ))}
          </div>
        )}
      </ScrollArea>

      {/* Dialogs */}
      <BookmarkViewDialog
        bookmark={selectedBookmark}
        open={viewOpen}
        onClose={() => {
          setViewOpen(false);
          setSelectedBookmark(null);
        }}
        onEdit={() => {
          setViewOpen(false);
          setEditOpen(true);
        }}
        onDelete={() => {
          setViewOpen(false);
          setDeleteOpen(true);
        }}
      />

      <BookmarkEditDialog
        bookmark={selectedBookmark}
        open={editOpen}
        onClose={() => {
          setEditOpen(false);
          setSelectedBookmark(null);
        }}
      />

      <BookmarkDeleteDialog
        bookmark={selectedBookmark}
        open={deleteOpen}
        onClose={() => {
          setDeleteOpen(false);
          setSelectedBookmark(null);
        }}
      />
    </div>
  );
}
