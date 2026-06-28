import React from "react";
import { redirect } from "next/navigation";

import { AuthForm } from "../../components/AuthForm";
import { ApiError } from "../../lib/api";
import { registerAction } from "../../lib/auth";

async function submitRegister(formData: FormData): Promise<void> {
  "use server";

  let auth;
  try {
    auth = await registerAction(formData);
  } catch (error) {
    if (error instanceof ApiError) {
      redirect(
        `/register?error=${encodeURIComponent(error.problem?.detail ?? error.message)}`,
      );
    }
    throw error;
  }

  const params = new URLSearchParams({
    token: auth.accessToken,
    expiresIn: String(auth.expiresIn),
    next: "/courses",
  });
  redirect(`/auth/complete?${params.toString()}`);
}

type RegisterPageProps = {
  searchParams?: Promise<{ error?: string | string[] }>;
};

export default async function RegisterPage({
  searchParams,
}: RegisterPageProps) {
  const resolved = searchParams ? await searchParams : {};
  const error = Array.isArray(resolved.error)
    ? resolved.error[0]
    : resolved.error;

  return (
    <main>
      <AuthForm
        title="Register"
        submitLabel="Create account"
        action={submitRegister}
        helperText="Create a new pharmacist account to start."
        error={error}
      />
    </main>
  );
}
