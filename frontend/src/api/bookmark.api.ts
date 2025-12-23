import { api } from "./baseApi";
import type { Bookmark } from "../packages/shared/types/bookmark";

type CreateBookmarkRequest = {
  title: string;
  url: string;
};

export const bookmarkApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getBookmarks: builder.query<Bookmark[], void>({
      query: () => "/bookmarks",
      providesTags: ["Bookmark"],
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
  }),
});

export const {
  useGetBookmarksQuery,
  useCreateBookmarkMutation,
  useDeleteBookmarkMutation,
} = bookmarkApi;
