"use client";

import * as React from "react";

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
} from "@/components/ui/sidebar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { ChevronRight, Folder, MoreVertical, Pencil } from "lucide-react";

import {
  useGetFoldersQuery,
  useUpdateFolderMutation,
  useDeleteFolderMutation,
} from "@/api/folder.api";

import { FolderCombobox } from "@/features/bookmarks/FolderCombobox";

/* ---------------- TYPES ---------------- */

type FolderType = {
  id: string;
  name: string;
  parent_id?: string | null;
  children?: FolderType[];
};

/* ---------------- TREE BUILDER ---------------- */

function buildFolderTree(folders: FolderType[]) {
  const map = new Map<string, FolderType>();
  const roots: FolderType[] = [];

  folders.forEach((f) => {
    map.set(f.id, { ...f, children: [] });
  });

  folders.forEach((f) => {
    if (f.parent_id) {
      map.get(f.parent_id)?.children?.push(map.get(f.id)!);
    } else {
      roots.push(map.get(f.id)!);
    }
  });

  return roots;
}

function collectDescendantIds(folder: FolderType): Set<string> {
  const ids = new Set<string>();

  function walk(node: FolderType) {
    node.children?.forEach((child) => {
      ids.add(child.id);
      walk(child);
    });
  }

  walk(folder);
  return ids;
}

/* ---------------- ROOT NAV ---------------- */

export function NavFolders({
  onSelect,
  activeFolderId,
  onResetToRoot,
}: {
  onSelect: (id: string) => void;
  activeFolderId?: string;
  onResetToRoot: () => void;
}) {
  const { data: flatFolders = [] } = useGetFoldersQuery();
  const folders = React.useMemo(
    () => buildFolderTree(flatFolders),
    [flatFolders],
  );

  return (
    <SidebarGroup>
      <SidebarGroupLabel>Folders</SidebarGroupLabel>

      <SidebarGroupContent>
        <SidebarMenu>
          {/* ROOT */}
          <SidebarMenuItem>
            <SidebarMenuButton
              onClick={() => onSelect("")}
              data-active={!activeFolderId ? "true" : undefined}
            >
              <Folder />
              <span>All Bookmarks</span>
            </SidebarMenuButton>
          </SidebarMenuItem>

          {/* RECENT */}
          <SidebarMenuItem>
            <SidebarMenuButton
              onClick={() => onSelect("recent")}
              data-active={activeFolderId === "recent" ? "true" : undefined}
            >
              <Folder />
              <span>Recent</span>
            </SidebarMenuButton>
          </SidebarMenuItem>

          {folders.map((folder) => (
            <FolderTree
              key={folder.id}
              folder={folder}
              onSelect={onSelect}
              activeFolderId={activeFolderId}
              onResetToRoot={onResetToRoot}
            />
          ))}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}

/* ---------------- FOLDER TREE ---------------- */

function FolderTree({
  folder,
  onSelect,
  activeFolderId,
  onResetToRoot,
}: {
  folder: FolderType;
  onSelect: (id: string) => void;
  activeFolderId?: string;
  onResetToRoot: () => void;
}) {
  const [updateFolder] = useUpdateFolderMutation();
  const [deleteFolder] = useDeleteFolderMutation();

  const [renameOpen, setRenameOpen] = React.useState(false);
  const [moveOpen, setMoveOpen] = React.useState(false);
  const [deleteOpen, setDeleteOpen] = React.useState(false);

  const [name, setName] = React.useState(folder.name);
  const [targetFolderId, setTargetFolderId] = React.useState<
    string | undefined
  >(undefined);

  const blockedFolderIds = React.useMemo(() => {
    const set = collectDescendantIds(folder);
    set.add(folder.id); // block self
    return set;
  }, [folder]);

  /* -------- ACTIONS -------- */

  const handleRename = async () => {
    await updateFolder({
      folderId: folder.id,
      payload: { name },
    }).unwrap();
    setRenameOpen(false);
  };

  const handleMove = async () => {
    await updateFolder({
      folderId: folder.id,
      payload: { parent_id: targetFolderId ?? null },
    }).unwrap();
    setMoveOpen(false);
  };

  const handleDelete = async () => {
    await deleteFolder({
      folderId: folder.id,
      mode: "move_children_to_parent",
    }).unwrap();
    setDeleteOpen(false);

    onResetToRoot();
  };

  /* -------- ROW -------- */

  const Row = (
    <div className="flex items-center gap-1 w-full">
      <SidebarMenuButton
        onClick={() => onSelect(folder.id)}
        data-active={activeFolderId === folder.id ? "true" : undefined}
      >
        <ChevronRight className="mr-1 h-4 w-4 transition-transform group-data-[state=open]/collapsible:rotate-90" />
        <Folder />
        <span className="flex-1 truncate">{folder.name}</span>
      </SidebarMenuButton>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button
            type="button"
            className="h-8 w-8 rounded-md hover:bg-accent flex items-center justify-center"
            onClick={(e) => e.stopPropagation()}
          >
            <MoreVertical className="h-4 w-4" />
          </button>
        </DropdownMenuTrigger>

        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => setRenameOpen(true)}>
            <Pencil className="mr-2 h-4 w-4" />
            Rename
          </DropdownMenuItem>

          <DropdownMenuItem onClick={() => setMoveOpen(true)}>
            Move to…
          </DropdownMenuItem>

          <DropdownMenuItem
            className="text-destructive"
            onClick={() => setDeleteOpen(true)}
          >
            Delete
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );

  /* -------- DIALOGS -------- */

  const RenameDialog = (
    <Dialog open={renameOpen} onOpenChange={setRenameOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Rename folder</DialogTitle>
        </DialogHeader>

        <Input value={name} onChange={(e) => setName(e.target.value)} />

        <DialogFooter>
          <Button onClick={handleRename}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );

  const MoveDialog = (
    <Dialog open={moveOpen} onOpenChange={setMoveOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Move folder</DialogTitle>
          <DialogDescription>Choose a destination folder.</DialogDescription>
        </DialogHeader>

        <FolderCombobox
          value={targetFolderId}
          onChange={setTargetFolderId}
          disabledIds={blockedFolderIds}
        />

        <DialogFooter>
          <Button onClick={handleMove}>Move</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );

  const DeleteDialog = (
    <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete folder</DialogTitle>
          <DialogDescription>
            Subfolders and bookmarks will be moved to the parent folder.
          </DialogDescription>
        </DialogHeader>

        <DialogFooter>
          <Button variant="destructive" onClick={handleDelete}>
            Delete
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );

  /* -------- LEAF -------- */

  if (!folder.children?.length) {
    return (
      <>
        <SidebarMenuItem>{Row}</SidebarMenuItem>

        {RenameDialog}
        {MoveDialog}
        {DeleteDialog}
      </>
    );
  }

  /* -------- PARENT -------- */

  return (
    <>
      <SidebarMenuItem>
        <Collapsible className="group/collapsible">
          <CollapsibleTrigger asChild>{Row}</CollapsibleTrigger>

          <CollapsibleContent>
            <SidebarMenuSub>
              {folder.children.map((child) => (
                <FolderTree
                  key={child.id}
                  folder={child}
                  onSelect={onSelect}
                  activeFolderId={activeFolderId}
                  onResetToRoot={onResetToRoot}
                />
              ))}
            </SidebarMenuSub>
          </CollapsibleContent>
        </Collapsible>
      </SidebarMenuItem>

      {RenameDialog}
      {MoveDialog}
      {DeleteDialog}
    </>
  );
}
