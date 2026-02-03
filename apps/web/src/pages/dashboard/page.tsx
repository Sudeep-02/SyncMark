// import { useState } from "react";
import { AppSidebar } from "@/components/sidebar/app-sidebar";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { useSearchParams } from "react-router-dom";

import DashboardBookmarks from "./DashboardBookmarks";

export default function DashboardPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const folderId = searchParams.get("folder") ?? undefined;
  const tagId = searchParams.get("tag") ?? undefined;

  const handleTagSelect = (id: string) => {
    const next = new URLSearchParams(searchParams);

    if (!id) {
      next.delete("tag");
    } else {
      next.set("tag", id);
    }

    setSearchParams(next);
  };

  const handleFolderSelect = (id: string) => {
    const next = new URLSearchParams(searchParams);

    if (!id) {
      next.delete("folder");
    } else {
      next.set("folder", id);
    }

    next.delete("tag");

    setSearchParams(next);
  };

  const handleResetToRoot = () => {
    const next = new URLSearchParams(searchParams);
    next.delete("folder");
    setSearchParams(next);
  };

  return (
    <SidebarProvider>
      <AppSidebar
        onFolderSelect={handleFolderSelect}
        onTagSelect={handleTagSelect}
        activeFolderId={folderId}
        onResetToRoot={handleResetToRoot}
      />

      <SidebarInset>
        <div className="flex h-full flex-col p-4">
          <DashboardBookmarks folderId={folderId} tagId={tagId} />
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
