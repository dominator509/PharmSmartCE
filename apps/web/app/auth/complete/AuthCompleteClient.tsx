"use client";

import { useEffect } from "react";
import { useSearchParams } from "next/navigation";

export default function AuthCompleteClient() {
  const searchParams = useSearchParams();

  useEffect(() => {
    const accessToken = searchParams.get("token");
    const expiresIn = searchParams.get("expiresIn");
    const next = searchParams.get("next") ?? "/courses";

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
