import { useCallback, useMemo, useRef, useState } from "react";
import { apiGet } from "@/ui/lib/http";

export type UserPublic = { id: number; username: string };

export function useUsernames(token: string | null) {
  const [names, setNames] = useState<Record<number, string>>({});
  const inflight = useRef<Set<number>>(new Set());

  const ensure = useCallback(
    async (ids: number[]) => {
      if (!token) return;
      const unique = Array.from(new Set(ids)).filter((id) => Number.isFinite(id) && id > 0);
      const missing = unique.filter((id) => !names[id] && !inflight.current.has(id));
      if (missing.length === 0) return;

      missing.forEach((id) => inflight.current.add(id));
      try {
        const results = await Promise.allSettled(missing.map((id) => apiGet<UserPublic>(`/users/${id}`, token)));
        setNames((prev) => {
          const next = { ...prev };
          for (const r of results) {
            if (r.status === "fulfilled") next[r.value.id] = r.value.username;
          }
          return next;
        });
      } finally {
        missing.forEach((id) => inflight.current.delete(id));
      }
    },
    [names, token],
  );

  const displayName = useMemo(() => {
    return (userId: number) => names[userId] ?? `#${userId}`;
  }, [names]);

  return { names, ensure, displayName };
}

