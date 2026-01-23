import { useState } from "react";
import { AppSidebar } from "@/components/sidebar/app-sidebar";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";

import DashboardBookmarks from "./DashboardBookmarks";

export default function DashboardPage() {
  const [folderId, setFolderId] = useState<string | undefined>();
  const [tagId, setTagId] = useState<string | undefined>();

  return (
    <SidebarProvider>
      <AppSidebar onFolderSelect={setFolderId} onTagSelect={setTagId} />

      <SidebarInset>
        <div className="flex h-full flex-col p-4">
          <DashboardBookmarks folderId={folderId} tagId={tagId} />
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
