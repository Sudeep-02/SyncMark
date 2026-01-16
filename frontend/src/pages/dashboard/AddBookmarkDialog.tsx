import { useCreateBookmarkMutation } from "@/api/bookmark.api";

import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function AddBookmarkDialog({ folderId }: { folderId?: string }) {
  const [createBookmark, { isLoading }] = useCreateBookmarkMutation();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);

    await createBookmark({
      title: String(formData.get("title")),
      url: String(formData.get("url")),
      folder_id: folderId,
      is_featured: false,
    });

    event.currentTarget.reset();
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button size="sm">Add Bookmark</Button>
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Bookmark</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input name="title" placeholder="Title" required />
          <Input name="url" placeholder="https://example.com" required />

          <DialogFooter>
            <Button type="submit" disabled={isLoading}>
              Save
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
