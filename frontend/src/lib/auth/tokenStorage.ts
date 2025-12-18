const ACCESS_TOKEN_KEY = "hsepoker.access_token";

function notifyAuthChanged() {
  try {
    window.dispatchEvent(new Event("hsepoker:auth"));
  } catch {
    // ignore
  }
}

export const tokenStorage = {
  get(): string | null {
    try {
      return localStorage.getItem(ACCESS_TOKEN_KEY);
    } catch {
      return null;
    }
  },
  set(token: string) {
    try {
      localStorage.setItem(ACCESS_TOKEN_KEY, token);
      notifyAuthChanged();
    } catch {
      // ignore
    }
  },
  clear() {
    try {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      notifyAuthChanged();
    } catch {
      // ignore
    }
  }
};
