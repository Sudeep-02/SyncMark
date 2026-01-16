export interface Bookmark {
  id: string;
  url: string;
  title: string;
  description?: string;

  favicon_url?: string;

  folder_id?: string;
  tag_ids: string[];

  created_at: string;
  updated_at: string;

  is_featured: boolean;
}
