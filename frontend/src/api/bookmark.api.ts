import { api } from "./baseApi";
import type { Bookmark } from "../packages/shared/types/bookmark";

type CreateBookmarkRequest = {
  title: string;
  url: string;
};

type GetBookmarksParams = {
  featured?: boolean;
  folder_id?: string;
};

export const bookmarkApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getBookmarks: builder.query<Bookmark[], GetBookmarksParams | void>({
      query: (params) => ({
        url: "/bookmarks",
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map((b) => ({ type: "Bookmark" as const, id: b.id })),
              { type: "Bookmark", id: "LIST" },
            ]
          : [{ type: "Bookmark", id: "LIST" }],
    }),

    createBookmark: builder.mutation<Bookmark, CreateBookmarkRequest>({
      query: (body) => ({
        url: "/bookmarks",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Bookmark"],
    }),

    deleteBookmark: builder.mutation<void, string>({
      query: (id) => ({
        url: `/bookmarks/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Bookmark"],
    }),

    toggleFeatured: builder.mutation<
      Bookmark,
      { id: string; is_featured: boolean }
    >({
      query: ({ id, is_featured }) => ({
        url: `/bookmarks/${id}`,
        method: "PATCH",
        body: { is_featured },
      }),
      invalidatesTags: (_r, _e, { id }) => [{ type: "Bookmark", id }],
    }),
  }),
});
export const {
  useGetBookmarksQuery,
  useCreateBookmarkMutation,
  useDeleteBookmarkMutation,
  useToggleFeaturedMutation,
} = bookmarkApi;
