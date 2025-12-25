import type { Bookmark } from "../../packages/shared/types/bookmark";

export default function BookmarkCard({ bookmark }: { bookmark: Bookmark }) {
  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="font-semibold">{bookmark.title}</h2>
      <a
        href={bookmark.url}
        className="text-sm text-blue-600 break-all"
        target="_blank"
      >
        {bookmark.url}
      </a>
    </div>
  );
}
