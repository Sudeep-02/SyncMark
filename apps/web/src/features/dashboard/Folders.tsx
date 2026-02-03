// pages/Folders.tsx
import { useGetFoldersQuery } from "../../api/folder.api";

export default function Folders() {
  const { data } = useGetFoldersQuery();

  return (
    <div className="p-6">
      <h2 className="font-semibold mb-3">Folders</h2>
      {data?.map((f) => (
        <div key={f.id} className="bg-white p-3 mb-2 rounded shadow">
          {f.name}
        </div>
      ))}
    </div>
  );
}
