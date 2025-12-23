import { api } from "./baseApi";
import type { Tag } from "../packages/shared/types/tag";

export const tagApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getTags: builder.query<Tag[], void>({
      query: () => "/tags",
      providesTags: ["Tag"],
    }),
  }),
});

export const { useGetTagsQuery } = tagApi;
