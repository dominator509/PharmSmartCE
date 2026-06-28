import React from "react";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { ApiError } from "../../lib/api";
import { changePasswordAction, logoutAction } from "../../lib/auth";

async function submitChangePassword(formData: FormData): Promise<void> {
  "use server";

  let nextPath = "/account?success=password-changed";
  try {
    await changePasswordAction(formData);
  } catch (error) {
    if (error instanceof ApiError) {
      nextPath = `/account?error=${encodeURIComponent(
        error.problem?.detail ?? error.message,
      )}`;
    } else {
      throw error;
    }
  }

  redirect(nextPath);
}

async function submitLogout(): Promise<void> {
  "use server";

  await logoutAction();
  redirect("/login");
}

type AccountPageProps = {
  searchParams?: Promise<{
    error?: string | string[];
    success?: string | string[];
  }>;
};

export default async function AccountPage({ searchParams }: AccountPageProps) {
  const access = (await cookies()).get("access")?.value;
  if (!access) {
    redirect("/login");
  }

  const resolved = searchParams ? await searchParams : {};
  const error = Array.isArray(resolved.error)
    ? resolved.error[0]
    : resolved.error;
  const success = Array.isArray(resolved.success)
    ? resolved.success[0]
    : resolved.success;

  return (
    <main style={styles.page}>
      <section style={styles.hero}>
        <div>
          <p style={styles.kicker}>PharmSmartCE</p>
          <h1 style={styles.title}>Account</h1>
          <p style={styles.subtitle}>
            Update your password or sign out of this browser session.
          </p>
        </div>
      </section>

      {error ? (
        <section style={{ ...styles.panel, ...styles.error }} role="alert">
          {error}
        </section>
      ) : null}

      {success ? (
        <section style={{ ...styles.panel, ...styles.success }} role="status">
          Password updated.
        </section>
      ) : null}

      <section style={styles.grid}>
        <article style={styles.card}>
          <h2 style={styles.sectionTitle}>Change password</h2>
          <form action={submitChangePassword} style={styles.form}>
            <label htmlFor="current_password" style={styles.label}>
              Current password
            </label>
            <input
              id="current_password"
              name="current_password"
              type="password"
              autoComplete="current-password"
              minLength={12}
              required
              style={styles.input}
            />

            <label htmlFor="new_password" style={styles.label}>
              New password
            </label>
            <input
              id="new_password"
              name="new_password"
              type="password"
              autoComplete="new-password"
              minLength={12}
              required
              style={styles.input}
            />

            <button type="submit" style={styles.primaryButton}>
              Update password
            </button>
          </form>
        </article>

        <article style={styles.card}>
          <h2 style={styles.sectionTitle}>Session</h2>
          <p style={styles.body}>
            Sign out from this browser when you are done.
          </p>
          <form action={submitLogout}>
            <button type="submit" style={styles.secondaryButton}>
              Log out
            </button>
          </form>
        </article>
      </section>
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    maxWidth: "960px",
    margin: "0 auto",
    padding: "32px 20px 56px",
    color: "#102033",
    fontFamily:
      'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  },
  hero: {
    marginBottom: 24,
  },
  kicker: {
    margin: 0,
    fontSize: 12,
    fontWeight: 700,
    textTransform: "uppercase",
    color: "#5c6b7a",
  },
  title: {
    margin: "8px 0 0",
    fontSize: 40,
    lineHeight: 1.1,
  },
  subtitle: {
    margin: "10px 0 0",
    maxWidth: 640,
    lineHeight: 1.6,
    color: "#405062",
  },
  panel: {
    borderRadius: 8,
    padding: 14,
    marginBottom: 16,
    border: "1px solid transparent",
  },
  error: {
    background: "#fff0f0",
    borderColor: "#f2c1c1",
    color: "#9c1f1f",
  },
  success: {
    background: "#e8f6ee",
    borderColor: "#b9e1c9",
    color: "#16613a",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
    gap: 16,
  },
  card: {
    border: "1px solid #d7e0ea",
    borderRadius: 8,
    padding: 18,
    background: "#ffffff",
  },
  sectionTitle: {
    margin: 0,
    fontSize: 20,
    lineHeight: 1.3,
  },
  body: {
    margin: "10px 0 16px",
    lineHeight: 1.6,
    color: "#4b5b6d",
  },
  form: {
    display: "grid",
    gap: 12,
  },
  label: {
    fontSize: 13,
    fontWeight: 700,
    color: "#405062",
  },
  input: {
    border: "1px solid #cfd8e3",
    borderRadius: 8,
    padding: "10px 12px",
    fontSize: 16,
    lineHeight: 1.4,
    color: "#102033",
  },
  primaryButton: {
    border: "1px solid #17385f",
    borderRadius: 8,
    background: "#17385f",
    color: "#ffffff",
    padding: "10px 14px",
    fontSize: 15,
    fontWeight: 700,
    lineHeight: 1.4,
    cursor: "pointer",
  },
  secondaryButton: {
    border: "1px solid #cfd8e3",
    borderRadius: 8,
    background: "#ffffff",
    color: "#17385f",
    padding: "10px 14px",
    fontSize: 15,
    fontWeight: 700,
    lineHeight: 1.4,
    cursor: "pointer",
  },
};
