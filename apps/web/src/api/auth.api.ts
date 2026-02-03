import { api } from "./baseApi";

export const authApi = api.injectEndpoints({
  endpoints: (builder) => ({
    // ---------- LOGIN ----------
    login: builder.mutation<void, { email: string; password: string }>({
      query: (body) => ({
        url: "/auth/login",
        method: "POST",
        body,
        credentials: "include",
      }),
      invalidatesTags: ["Auth"],
    }),

    // ---------- REGISTER ----------
    register: builder.mutation<
      void,
      {
        email: string;
        username: string;
        password_hash: string;
      }
    >({
      query: (body) => ({
        url: "/auth/register",
        method: "POST",
        body,
      }),
    }),

    // ---------- GET CURRENT USER ----------
    getMe: builder.query<{ id: number; email: string }, void>({
      query: () => ({
        url: "/auth/me",
        method: "GET",
        credentials: "include",
      }),
      providesTags: ["Auth"],
    }),

    // ---------- LOGOUT ----------
    logout: builder.mutation<void, void>({
      query: () => ({
        url: "/auth/logout",
        method: "POST",
        credentials: "include",
      }),
      invalidatesTags: ["Auth"],
    }),
  }),
});

export const {
  useLoginMutation,
  useRegisterMutation,
  useGetMeQuery,
  useLogoutMutation,
} = authApi;
