import { useGetTagsQuery } from "../api/tag.api";

export default function Tags() {
  const { data, isLoading } = useGetTagsQuery();

  if (isLoading) return <p className="p-4">Loading…</p>;

  return (
    <div className="p-6">
      <h2 className="font-semibold mb-3">Tags</h2>
      <ul className="space-y-2">
        {data?.map((t) => (
          <li key={t.id} className="bg-white p-2 rounded shadow">
            {t.name}
          </li>
        ))}
      </ul>
    </div>
  );
}
