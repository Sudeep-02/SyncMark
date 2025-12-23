import { useGetBookmarksQuery } from "../api/bookmark.api";
import BookmarkCard from "../components/BookmarkCard";

export default function Dashboard() {
  const { data, isLoading, error } = useGetBookmarksQuery();

  if (isLoading) return <p className="p-4">Loading…</p>;
  if (error) return <p className="p-4 text-red-500">Server unreachable</p>;

  return (
    <div className="p-6 grid gap-4 grid-cols-1 md:grid-cols-3">
      {data?.map((b) => (
        <BookmarkCard key={b.id} bookmark={b} />
      ))}
    </div>
  );
}
