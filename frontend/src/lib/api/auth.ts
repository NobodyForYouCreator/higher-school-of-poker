import type { JwtTokenResponse, User } from "../../types/api";
import { apiGet, apiPost } from "./client";

export type LoginRequest = {
  username: string;
  password: string;
};

export type RegisterRequest = {
  username: string;
  password: string;
};

export const authApi = {
  login(payload: LoginRequest) {
    return apiPost<JwtTokenResponse>("/auth/login", payload, { auth: false });
  },
  register(payload: RegisterRequest) {
    return apiPost<JwtTokenResponse>("/auth/register", payload, { auth: false });
  },
  me() {
    return apiGet<User>("/auth/me");
  }
};
