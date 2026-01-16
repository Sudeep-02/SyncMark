import { api } from "./baseApi";
import type { Bookmark } from "../packages/shared/types/bookmark";

/* ---------- TYPES ---------- */

type CreateBookmarkRequest = {
  title: string;
  url: string;
  folder_id?: string;
  tag_ids?: string[];
  is_featured?: boolean;
};

type UpdateBookmarkRequest = {
  is_featured?: boolean;
  title?: string;
  url?: string;
  folder_id?: string | null;
  tag_ids?: string[];
};

type GetBookmarksParams = {
  featured?: boolean;
  folder_id?: string;
};

/* ---------- API ---------- */

export const bookmarkApi = api.injectEndpoints({
  endpoints: (builder) => ({
    /* GET /bookmarks */
    getBookmarks: builder.query<Bookmark[], GetBookmarksParams | void>({
      query: (params) => ({
        url: "/bookmarks",
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map((bookmark) => ({
                type: "Bookmark" as const,
                id: bookmark.id,
              })),
              { type: "Bookmark", id: "LIST" },
            ]
          : [{ type: "Bookmark", id: "LIST" }],
    }),

    /* POST /bookmarks */
    createBookmark: builder.mutation<Bookmark, CreateBookmarkRequest>({
      query: (payload) => ({
        url: "/bookmarks",
        method: "POST",
        body: payload,
      }),
      invalidatesTags: [{ type: "Bookmark", id: "LIST" }],
    }),

    /* PATCH /bookmarks/:id */
    updateBookmark: builder.mutation<
      Bookmark,
      { bookmarkId: string; payload: UpdateBookmarkRequest }
    >({
      query: ({ bookmarkId, payload }) => ({
        url: `/bookmarks/${bookmarkId}`,
        method: "PATCH",
        body: payload,
      }),
      invalidatesTags: (_r, _e, { bookmarkId }) => [
        { type: "Bookmark", id: bookmarkId },
      ],
    }),

    /* DELETE /bookmarks/:id */
    deleteBookmark: builder.mutation<void, string>({
      query: (bookmarkId) => ({
        url: `/bookmarks/${bookmarkId}`,
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "Bookmark", id: "LIST" }],
    }),
  }),
});

export const {
  useGetBookmarksQuery,
  useCreateBookmarkMutation,
  useUpdateBookmarkMutation,
  useDeleteBookmarkMutation,
} = bookmarkApi;
