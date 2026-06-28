import React from "react";
import { redirect } from "next/navigation";

import { AuthForm } from "../../components/AuthForm";
import { ApiError } from "../../lib/api";
import { loginAction, storeAccessCookie } from "../../lib/auth";

async function submitLogin(formData: FormData): Promise<void> {
  "use server";

  let auth;
  try {
    auth = await loginAction(formData);
  } catch (error) {
    if (error instanceof ApiError) {
      redirect(
        `/login?error=${encodeURIComponent(error.problem?.detail ?? error.message)}`,
      );
    }
    throw error;
  }

  await storeAccessCookie(auth.accessToken, auth.expiresIn);
  redirect("/courses");
}

type LoginPageProps = {
  searchParams?: Promise<{ error?: string | string[] }>;
};

export default async function LoginPage({ searchParams }: LoginPageProps) {
  const resolved = searchParams ? await searchParams : {};
  const error = Array.isArray(resolved.error)
    ? resolved.error[0]
    : resolved.error;

  return (
    <main>
      <AuthForm
        title="Login"
        submitLabel="Log in"
        action={submitLogin}
        helperText="Use your pharmacist account to continue."
        error={error}
      />
    </main>
  );
}
