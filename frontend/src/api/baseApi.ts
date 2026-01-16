import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const api = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({
    baseUrl: import.meta.env.VITE_API_URL,
    credentials: "include", // for refresh and access cookies
  }),
  tagTypes: ["Bookmark", "Tag", "Folder"],
  endpoints: () => ({}),
});
