import Link from "next/link";
import { redirect } from "next/navigation";
import React from "react";

import { ApiError } from "../../lib/api";
import { loadCourses, type CourseListItemDTO } from "../../lib/courseApi";

export default async function CoursesPage() {
  let items: CourseListItemDTO[] = [];

  try {
    const response = await loadCourses();
    items = response.items;
  } catch (error) {
    if (
      error instanceof ApiError &&
      (error.status === 401 || error.status === 403)
    ) {
      redirect("/login");
    }
    throw error;
  }

  return (
    <main style={styles.page}>
      <section style={styles.hero}>
        <div>
          <p style={styles.kicker}>PharmSmartCE</p>
          <h1 style={styles.title}>Courses</h1>
          <p style={styles.subtitle}>
            Review your continuing education courses, inspect their source
            material, and upload new documents when you are ready.
          </p>
        </div>
      </section>

      {items.length === 0 ? (
        <section style={styles.emptyState} aria-label="Empty course list">
          <h2 style={styles.sectionTitle}>No courses yet</h2>
          <p style={styles.body}>
            Create a course through the API, then come back here to inspect the
            uploaded sources.
          </p>
        </section>
      ) : (
        <section aria-label="Course list" style={styles.grid}>
          {items.map((course) => (
            <article key={course.id} style={styles.card}>
              <div style={styles.cardHeader}>
                <div>
                  <h2 style={styles.cardTitle}>
                    <Link href={`/courses/${course.id}`} style={styles.link}>
                      {course.title}
                    </Link>
                  </h2>
                  <p style={styles.muted}>Course ID {course.id}</p>
                </div>
                <StatusBadge status={course.status} />
              </div>

              <dl style={styles.definitionList}>
                <Definition label="Questions" value={`${course.n_questions}`} />
                <Definition
                  label="Passing score"
                  value={`${course.pass_pct}%`}
                />
              </dl>
            </article>
          ))}
        </section>
      )}
    </main>
  );
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span style={{ ...styles.badge, ...badgeStyle(status) }}>{status}</span>
  );
}

function Definition({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt style={styles.definitionLabel}>{label}</dt>
      <dd style={styles.definitionValue}>{value}</dd>
    </div>
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
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "space-between",
    gap: 24,
    flexWrap: "wrap",
    marginBottom: 24,
  },
  kicker: {
    margin: 0,
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: 0,
    textTransform: "uppercase",
    color: "#5c6b7a",
  },
  title: {
    margin: "8px 0 0",
    fontSize: 40,
    lineHeight: 1.1,
    letterSpacing: 0,
  },
  subtitle: {
    margin: "10px 0 0",
    maxWidth: 640,
    lineHeight: 1.6,
    color: "#405062",
  },
  emptyState: {
    border: "1px solid #d7e0ea",
    borderRadius: 8,
    padding: 20,
    background: "#f8fbff",
  },
  sectionTitle: {
    margin: 0,
    fontSize: 20,
    lineHeight: 1.3,
  },
  body: {
    margin: "10px 0 0",
    lineHeight: 1.6,
    color: "#4b5b6d",
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
  cardHeader: {
    display: "flex",
    justifyContent: "space-between",
    gap: 12,
    alignItems: "flex-start",
    marginBottom: 16,
  },
  cardTitle: {
    margin: 0,
    fontSize: 20,
    lineHeight: 1.25,
  },
  link: {
    color: "#17385f",
    textDecoration: "none",
  },
  muted: {
    margin: "6px 0 0",
    fontSize: 13,
    color: "#607184",
    lineHeight: 1.4,
  },
  definitionList: {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: 12,
    margin: 0,
  },
  definitionLabel: {
    fontSize: 12,
    margin: 0,
    color: "#607184",
    textTransform: "uppercase",
    letterSpacing: 0,
  },
  definitionValue: {
    margin: "4px 0 0",
    fontSize: 16,
    fontWeight: 700,
    color: "#102033",
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
