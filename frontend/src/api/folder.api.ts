import { api } from "./baseApi";
import type { Folder } from "../packages/shared/types/folder";

export const folderApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getFolders: builder.query<Folder[], void>({
      query: () => "/folders",
      providesTags: ["Folder"],
    }),
  }),
});

export const { useGetFoldersQuery } = folderApi;
