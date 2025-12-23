export interface Bookmark {
  id: string;
  title: string;
  url: string;
  description?: string;
  folder_id?: string;
  tag_ids: string[];
  created_at: string;
}
