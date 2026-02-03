import { api } from "./baseApi";
import type { Folder } from "../shared/types/folder";

type CreateFolderPayload = {
  name: string;
  parent_id?: string | null;
};

export const folderApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getFolders: builder.query<Folder[], void>({
      query: () => "/folders/",
      providesTags: ["Folder"],
    }),

    createFolder: builder.mutation<Folder, CreateFolderPayload>({
      query: (payload) => ({
        url: "/folders/",
        method: "POST",
        body: payload,
      }),
      invalidatesTags: ["Folder"],
    }),

    updateFolder: builder.mutation<
      Folder,
      {
        folderId: string;
        payload: { parent_id?: string | null; name?: string };
      }
    >({
      query: ({ folderId, payload }) => ({
        url: `/folders/${folderId}/`,
        method: "PATCH",
        body: payload,
      }),
      invalidatesTags: ["Folder"],
    }),

    deleteFolder: builder.mutation<
      void,
      {
        folderId: string;
        mode?:
          | "reject"
          | "move_children_to_parent"
          | "move_to_root"
          | "cascade";
      }
    >({
      query: ({ folderId, mode = "reject" }) => ({
        url: `/folders/${folderId}/`,
        method: "DELETE",
        params: { mode },
      }),
      invalidatesTags: ["Folder"],
    }),
  }),
});

export const {
  useGetFoldersQuery,
  useCreateFolderMutation,
  useUpdateFolderMutation,
  useDeleteFolderMutation,
} = folderApi;
