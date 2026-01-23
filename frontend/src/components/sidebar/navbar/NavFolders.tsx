"use client";

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
import { ChevronRight, Folder } from "lucide-react";
import { useGetFoldersQuery } from "@/api/folder.api";

type FolderType = {
  id: string;
  name: string;
  children?: FolderType[];
};

export function NavFolders({ onSelect }: { onSelect: (id: string) => void }) {
  const { data: folders = [] } = useGetFoldersQuery();

  return (
    <SidebarGroup>
      <SidebarGroupLabel>Folders</SidebarGroupLabel>
      <SidebarGroupContent>
        <SidebarMenu>
          {folders.map((folder) => (
            <FolderTree key={folder.id} folder={folder} onSelect={onSelect} />
          ))}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}

function FolderTree({
  folder,
  onSelect,
}: {
  folder: FolderType;
  onSelect: (id: string) => void;
}) {
  if (!folder.children?.length) {
    return (
      <SidebarMenuButton onClick={() => onSelect(folder.id)}>
        <Folder />
        {folder.name}
      </SidebarMenuButton>
    );
  }

  return (
    <SidebarMenuItem>
      <Collapsible className="group/collapsible">
        <CollapsibleTrigger asChild>
          <SidebarMenuButton>
            <ChevronRight className="transition-transform group-data-[state=open]/collapsible:rotate-90" />
            <Folder />
            {folder.name}
          </SidebarMenuButton>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <SidebarMenuSub>
            {folder.children.map((child) => (
              <FolderTree key={child.id} folder={child} onSelect={onSelect} />
            ))}
          </SidebarMenuSub>
        </CollapsibleContent>
      </Collapsible>
    </SidebarMenuItem>
  );
}
