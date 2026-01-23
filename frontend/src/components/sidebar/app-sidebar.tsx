"use client";

import * as React from "react";

import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";
import { NavFolders } from "../sidebar/navbar/NavFolders";
import { NavTags } from "../sidebar/navbar/NavTags";
import { NavUser } from "../sidebar/navbar/NavUser";

export function AppSidebar({
  onFolderSelect,
  onTagSelect,
  ...props
}: {
  onFolderSelect: (id: string) => void;
  onTagSelect: (id: string) => void;
} & React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <NavUser />
      </SidebarHeader>

      <SidebarContent>
        <NavFolders onSelect={onFolderSelect} />
        <NavTags onSelect={onTagSelect} />
      </SidebarContent>

      <SidebarRail />
    </Sidebar>
  );
}
