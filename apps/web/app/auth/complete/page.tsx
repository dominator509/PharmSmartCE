import { Suspense } from "react";

import AuthCompleteClient from "./AuthCompleteClient";

export default function AuthCompletePage() {
  return (
    <Suspense
      fallback={
        <main>
          <p>Signing you in...</p>
        </main>
      }
    >
      <AuthCompleteClient />
    </Suspense>
  );
}
