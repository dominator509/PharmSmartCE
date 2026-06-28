import Link from "next/link";
import { redirect } from "next/navigation";
import React from "react";

import { ApiError } from "../../../lib/api";
import { loadCourse, uploadCourseSource } from "../../../lib/courseApi";
import { UploadSource } from "./UploadSource";

type CoursePageProps = {
  params: Promise<{ id: string }>;
  searchParams: Promise<{
    error?: string | string[];
    uploaded?: string | string[];
  }>;
};

export default async function CoursePage({
  params,
  searchParams,
}: CoursePageProps) {
  const resolvedParams = await params;
  const resolvedSearchParams = await searchParams;
  const error = getSingleQueryParam(resolvedSearchParams.error);
  const uploaded = getSingleQueryParam(resolvedSearchParams.uploaded);

  let course: Awaited<ReturnType<typeof loadCourse>>;
  try {
    course = await loadCourse(resolvedParams.id);
  } catch (error) {
    if (
      error instanceof ApiError &&
      (error.status === 401 || error.status === 403)
    ) {
      redirect("/login");
    }
    throw error;
  }

  async function submitUpload(formData: FormData): Promise<void> {
    "use server";

    try {
      await uploadCourseSource(course.id, formData);
    } catch (error) {
      if (error instanceof ApiError) {
        redirect(
          `/courses/${course.id}?error=${encodeURIComponent(error.problem?.detail ?? error.message)}`,
        );
      }
      throw error;
    }

    redirect(`/courses/${course.id}?uploaded=1`);
  }

  return (
    <main style={styles.page}>
      <nav style={styles.nav} aria-label="Breadcrumb">
        <Link href="/courses" style={styles.backLink}>
          Courses
        </Link>
      </nav>

      <section style={styles.hero}>
        <div>
          <p style={styles.kicker}>Course detail</p>
          <h1 style={styles.title}>{course.title}</h1>
          <p style={styles.subtitle}>
            {course.n_questions} questions, {course.pass_pct}% passing score,{" "}
            {course.sources.length} source
            {course.sources.length === 1 ? "" : "s"} linked.
          </p>
        </div>
        <StatusBadge status={course.status} />
      </section>

      <section style={styles.layout}>
        <UploadSource
          action={submitUpload}
          error={error}
          notice={uploaded ? "Source uploaded." : undefined}
        />

        <section style={styles.panel} aria-label="Sources">
          <h2 style={styles.sectionTitle}>Sources</h2>

          {course.sources.length === 0 ? (
            <p style={styles.body}>
              No source documents have been uploaded yet.
            </p>
          ) : (
            <ul style={styles.list}>
              {course.sources.map((source) => (
                <li key={source.id} style={styles.listItem}>
                  <div style={styles.listHeader}>
                    <div>
                      <p style={styles.itemTitle}>{source.filename}</p>
                      <p style={styles.itemMeta}>
                        {formatBytes(source.bytes)} and uploaded{" "}
                        {formatDate(source.created_at)}
                      </p>
                    </div>
                    <StatusBadge status={source.status} />
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </section>
    </main>
  );
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span style={{ ...styles.badge, ...badgeStyle(status) }}>{status}</span>
  );
}

function getSingleQueryParam(value?: string | string[]): string | undefined {
  if (Array.isArray(value)) {
    return value[0];
  }
  return value;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  const kib = bytes / 1024;
  if (kib < 1024) {
    return `${kib.toFixed(1)} KiB`;
  }
  return `${(kib / 1024).toFixed(1)} MiB`;
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    maxWidth: "1024px",
    margin: "0 auto",
    padding: "32px 20px 56px",
    color: "#102033",
    fontFamily:
      'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  },
  nav: {
    marginBottom: 16,
  },
  backLink: {
    color: "#17385f",
    textDecoration: "none",
    fontWeight: 700,
  },
  hero: {
    display: "flex",
    justifyContent: "space-between",
    gap: 20,
    alignItems: "flex-start",
    flexWrap: "wrap",
    marginBottom: 20,
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
    fontSize: 36,
    lineHeight: 1.12,
    letterSpacing: 0,
  },
  subtitle: {
    margin: "10px 0 0",
    color: "#405062",
    lineHeight: 1.6,
  },
  layout: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
    gap: 16,
    alignItems: "start",
  },
  panel: {
    border: "1px solid #d7e0ea",
    borderRadius: 8,
    background: "#ffffff",
    padding: 18,
  },
  sectionTitle: {
    margin: 0,
    fontSize: 20,
    lineHeight: 1.25,
  },
  body: {
    margin: "10px 0 0",
    color: "#4b5b6d",
    lineHeight: 1.6,
  },
  list: {
    listStyle: "none",
    padding: 0,
    margin: "12px 0 0",
    display: "grid",
    gap: 12,
  },
  listItem: {
    border: "1px solid #e0e7ef",
    borderRadius: 8,
    padding: 14,
    background: "#fdfefe",
  },
  listHeader: {
    display: "flex",
    justifyContent: "space-between",
    gap: 12,
    alignItems: "flex-start",
  },
  itemTitle: {
    margin: 0,
    fontSize: 16,
    fontWeight: 700,
  },
  itemMeta: {
    margin: "6px 0 0",
    fontSize: 13,
    color: "#607184",
    lineHeight: 1.5,
  },
  badge: {
    display: "inline-flex",
    alignItems: "center",
    borderRadius: 999,
    border: "1px solid transparent",
    padding: "4px 10px",
    fontSize: 12,
    fontWeight: 700,
    textTransform: "uppercase",
    letterSpacing: 0,
  },
};

function badgeStyle(status: string): React.CSSProperties {
  switch (status) {
    case "ready":
      return {
        background: "#e8f6ee",
        color: "#16613a",
        borderColor: "#b9e1c9",
      };
    case "uploaded":
      return {
        background: "#eef4ff",
        color: "#1f4c88",
        borderColor: "#c8d9ff",
      };
    case "failed":
      return {
        background: "#fff0f0",
        color: "#9c1f1f",
        borderColor: "#f2c1c1",
      };
    case "quarantined":
      return {
        background: "#fff7e8",
        color: "#805100",
        borderColor: "#f2d29a",
      };
    case "ingesting":
      return {
        background: "#eef8fb",
        color: "#0d6778",
        borderColor: "#b8e1e9",
      };
    default:
      return {
        background: "#edf0f4",
        color: "#415062",
        borderColor: "#d4dbe3",
      };
  }
}
