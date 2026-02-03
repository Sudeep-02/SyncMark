"use client";

import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { Tag } from "lucide-react";
import { useGetTagsQuery } from "@/api/tag.api";

export function NavTags({ onSelect }: { onSelect: (id: string) => void }) {
  const { data: tags = [] } = useGetTagsQuery();

  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden">
      <SidebarGroupLabel>Tags</SidebarGroupLabel>
      <SidebarMenu>
        {tags.map((tag) => (
          <SidebarMenuItem key={tag.id}>
            <SidebarMenuButton onClick={() => onSelect(tag.id)}>
              <Tag />
              <span>{tag.name}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
    </SidebarGroup>
  );
}
