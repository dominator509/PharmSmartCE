"use client";

import { useEffect } from "react";
import { useSearchParams } from "next/navigation";

const DEFAULT_NEXT_PATH = "/courses";

export function resolveNextPath(next: string | null): string {
  if (!next) {
    return DEFAULT_NEXT_PATH;
  }

  const normalized = next.trim();
  if (!normalized.startsWith("/") || normalized.startsWith("//")) {
    return DEFAULT_NEXT_PATH;
  }

  return normalized;
}

export default function AuthCompleteClient() {
  const searchParams = useSearchParams();

  useEffect(() => {
    const accessToken = searchParams.get("token");
    const expiresIn = searchParams.get("expiresIn");
    const next = resolveNextPath(searchParams.get("next"));

    if (accessToken) {
      const cookieParts = [
        `access=${encodeURIComponent(accessToken)}`,
        "Path=/",
        "SameSite=Lax",
      ];
      if (window.location.protocol === "https:") {
        cookieParts.push("Secure");
      }
      if (expiresIn) {
        cookieParts.push(`Max-Age=${expiresIn}`);
      }
      document.cookie = cookieParts.join("; ");
    }

    window.location.replace(next);
  }, [searchParams]);

  return (
    <main>
      <p>Signing you in...</p>
    </main>
  );
}
