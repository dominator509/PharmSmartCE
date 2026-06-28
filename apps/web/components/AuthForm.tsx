import React from "react";

export type AuthFormState = {
  error?: string;
};

type AuthFormProps = {
  title: string;
  submitLabel: string;
  action: (formData: FormData) => Promise<void>;
  helperText: string;
  error?: string;
};

export function AuthForm({
  title,
  submitLabel,
  action,
  helperText,
  error,
}: AuthFormProps) {
  return (
    <section aria-labelledby={`${title.toLowerCase()}-heading`}>
      <h1 id={`${title.toLowerCase()}-heading`}>{title}</h1>
      <p>{helperText}</p>
      <form action={action}>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          required
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          minLength={12}
          required
        />

        {error ? <p role="alert">{error}</p> : null}

        <button type="submit">{submitLabel}</button>
      </form>
    </section>
  );
}
