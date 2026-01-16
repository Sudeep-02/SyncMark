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
import { Textarea } from "@/components/ui/textarea";

export default function AddBookmarkDialog() {
  const [createBookmark, { isLoading }] = useCreateBookmarkMutation();

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);

    await createBookmark({
      title: String(form.get("title")),
      url: String(form.get("url")),
      is_featured: false,
    });

    e.currentTarget.reset();
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

        <form onSubmit={onSubmit} className="space-y-4">
          <Input name="title" placeholder="Title" required />
          <Input name="url" placeholder="https://example.com" required />
          <Textarea name="description" placeholder="Description (optional)" />

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
