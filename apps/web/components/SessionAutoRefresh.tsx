"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

type SessionAutoRefreshProps = {
  enabled: boolean;
};

export function SessionAutoRefresh({ enabled }: SessionAutoRefreshProps) {
  const router = useRouter();

  useEffect(() => {
    if (!enabled) {
      return undefined;
    }

    const interval = window.setInterval(() => {
      router.refresh();
    }, 2000);

    return () => window.clearInterval(interval);
  }, [enabled, router]);

  return null;
}
