import { api } from "./baseApi";
import type { Tag } from "../shared/types/tag";

type CreateTagPayload = {
  name: string;
};

export const tagApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getTags: builder.query<Tag[], void>({
      query: () => "/tags/",
      providesTags: ["Tag"],
    }),

    createTag: builder.mutation<Tag, CreateTagPayload>({
      query: (payload) => ({
        url: "/tags/",
        method: "POST",
        body: payload,
      }),
      invalidatesTags: ["Tag"],
    }),
  }),
});

export const { useGetTagsQuery, useCreateTagMutation } = tagApi;
