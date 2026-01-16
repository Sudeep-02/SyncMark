// src/api/baseApi.ts

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { getDeviceId } from "@/utils/device";

export const api = createApi({
  reducerPath: "api",

  baseQuery: fetchBaseQuery({
    baseUrl: import.meta.env.VITE_API_URL,

    // Required for HttpOnly cookies (access / refresh tokens)
    credentials: "include",

    prepareHeaders: (headers) => {
      // Standardized, production-safe header
      headers.set("x-device-id", getDeviceId());
      return headers;
    },
  }),

  tagTypes: ["Bookmark", "Tag", "Folder"],

  endpoints: () => ({}),
});
