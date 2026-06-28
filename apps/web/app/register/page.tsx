import React from "react";
import { redirect } from "next/navigation";

import { AuthForm } from "../../components/AuthForm";
import { ApiError } from "../../lib/api";
import { registerAction, storeAccessCookie } from "../../lib/auth";

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

  await storeAccessCookie(auth.accessToken, auth.expiresIn);
  redirect("/courses");
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
