import * as React from "react";

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

import { FolderCombobox } from "./FolderCombobox";
import { TagsInput } from "./TagsInput";

import { useCreateBookmarkMutation } from "@/api/bookmark.api";

type AddBookmarkDialogProps = {
  folderId?: string;
};

export function AddBookmarkDialog({ folderId }: AddBookmarkDialogProps) {
  const [createBookmark, { isLoading }] = useCreateBookmarkMutation();
  const [open, setOpen] = React.useState(false);

  const [title, setTitle] = React.useState("");
  const [url, setUrl] = React.useState("");
  const [selectedFolderId, setSelectedFolderId] = React.useState<string>();
  const [tagIds, setTagIds] = React.useState<string[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    await createBookmark({
      title,
      url,
      folder_id: selectedFolderId,
      tag_ids: tagIds,
      is_featured: false,
    }).unwrap();

    setTitle("");
    setUrl("");
    setSelectedFolderId(undefined);
    setTagIds([]);

    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">Add Bookmark</Button>
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Bookmark</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />

          <Input
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
          />

          <FolderCombobox
            value={selectedFolderId}
            onChange={setSelectedFolderId}
          />

          <TagsInput value={tagIds} onChange={setTagIds} />

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
