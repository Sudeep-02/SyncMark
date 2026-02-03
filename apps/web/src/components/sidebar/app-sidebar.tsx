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
  activeFolderId,
  onResetToRoot,
  ...props
}: {
  onFolderSelect: (id: string) => void;
  onTagSelect: (id: string) => void;
  activeFolderId?: string;
  onResetToRoot: () => void;
} & React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <NavUser />
      </SidebarHeader>

      <SidebarContent>
        <NavFolders
          onSelect={onFolderSelect}
          activeFolderId={activeFolderId}
          onResetToRoot={onResetToRoot}
        />
        <NavTags onSelect={onTagSelect} />
      </SidebarContent>

      <SidebarRail />
    </Sidebar>
  );
}
