export type Bookmark = {
  id: string;
  url: string;
  title?: string;
  description?: string;
  favicon_url?: string;

  folder_id?: string | null;
  is_featured: boolean;

  created_at: string;
  updated_at: string;
};
