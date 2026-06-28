import Link from "next/link";
import { redirect } from "next/navigation";
import React from "react";

import { ApiError } from "../../../lib/api";
import {
  loadCitationPreview,
  loadSession,
  type SessionDTO,
  type SessionQuestionDTO,
} from "../../../lib/sessionApi";
import { CitationDrawer } from "../../../components/CitationDrawer";
import { QuestionView } from "../../../components/QuestionView";
import { SessionAutoRefresh } from "../../../components/SessionAutoRefresh";

type SessionPageProps = {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ cite?: string | string[] }>;
};

export default async function SessionPage({
  params,
  searchParams,
}: SessionPageProps) {
  const resolvedParams = await params;
  const resolvedSearchParams = await searchParams;
  const cite = Array.isArray(resolvedSearchParams.cite)
    ? resolvedSearchParams.cite[0]
    : resolvedSearchParams.cite;

  let session: SessionDTO;
  try {
    session = await loadSession(resolvedParams.id);
  } catch (error) {
    if (
      error instanceof ApiError &&
      (error.status === 401 || error.status === 403)
    ) {
      redirect("/login");
    }
    throw error;
  }

  const citation = cite
    ? await loadCitationPreviewForQuery(session.id, cite)
    : null;

  return (
    <main style={styles.page}>
      <section style={styles.hero}>
        <div>
          <p style={styles.kicker}>Session</p>
          <h1 style={styles.title}>{resolvedParams.id}</h1>
          <p style={styles.subtitle}>
            Course {session.course_id} · {session.answered_questions}/
            {session.total_questions} answered
          </p>
        </div>
        <StatusBadge status={session.status} />
      </section>

      {session.status === "completed" ? (
        <section style={styles.summary}>
          <p style={styles.summaryLabel}>Results</p>
          <p style={styles.summaryBody}>
            Score {session.score_pct ?? 0}%{" "}
            {session.passed ? "(passed)" : "(not yet passing)"}
          </p>
          {session.record_id ? (
            <Link
              href={`/sessions/${session.id}/results`}
              style={styles.resultsLink}
            >
              View results and download CE record
            </Link>
          ) : null}
        </section>
      ) : null}

      <SessionAutoRefresh
        enabled={
          session.questions.length === 0 && session.status !== "completed"
        }
      />

      {session.questions.length === 0 ? (
        <section style={styles.loading}>
          <p style={styles.loadingTitle}>Generating session...</p>
          <p style={styles.loadingBody}>
            We will refresh automatically when the questions are ready.
          </p>
        </section>
      ) : (
        <section style={styles.layout}>
          <div style={styles.questions}>
            {session.questions.map((question: SessionQuestionDTO) => (
              <QuestionView
                key={question.id}
                sessionId={session.id}
                question={question}
              />
            ))}
          </div>

          <CitationDrawer sessionId={session.id} citation={citation} />
        </section>
      )}
    </main>
  );
}

async function loadCitationPreviewForQuery(sessionId: string, cite: string) {
  const parsed = parseCitationQuery(cite);
  if (!parsed) {
    return null;
  }

  try {
    return await loadCitationPreview(sessionId, parsed);
  } catch (error) {
    if (
      error instanceof ApiError &&
      (error.status === 401 || error.status === 403)
    ) {
      redirect("/login");
    }
    return null;
  }
}

function parseCitationQuery(
  cite: string,
): { doc_id: string; page: number; span: string } | null {
  const firstSeparator = cite.indexOf(":");
  const secondSeparator = cite.indexOf(":", firstSeparator + 1);
  if (firstSeparator <= 0 || secondSeparator <= firstSeparator + 1) {
    return null;
  }

  const docId = cite.slice(0, firstSeparator);
  const page = Number(cite.slice(firstSeparator + 1, secondSeparator));
  const span = cite.slice(secondSeparator + 1);
  if (!docId || !Number.isInteger(page) || page < 1 || !span) {
    return null;
  }

  return { doc_id: docId, page, span };
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span style={{ ...styles.badge, ...badgeStyle(status) }}>{status}</span>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    maxWidth: "1180px",
    margin: "0 auto",
    padding: "32px 20px 56px",
    color: "#102033",
    fontFamily:
      'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
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
  summary: {
    border: "1px solid #d7e0ea",
    borderRadius: 8,
    background: "#fdfefe",
    padding: 16,
    display: "grid",
    gap: 8,
    marginBottom: 20,
  },
  summaryLabel: {
    margin: 0,
    fontSize: 12,
    fontWeight: 700,
    textTransform: "uppercase",
    color: "#5c6b7a",
  },
  summaryBody: {
    margin: 0,
    fontWeight: 600,
  },
  resultsLink: {
    color: "#17385f",
    fontWeight: 700,
    textDecoration: "none",
    width: "fit-content",
  },
  loading: {
    border: "1px solid #d7e0ea",
    borderRadius: 8,
    background: "#ffffff",
    padding: 18,
    display: "grid",
    gap: 8,
  },
  loadingTitle: {
    margin: 0,
    fontSize: 18,
    fontWeight: 700,
  },
  loadingBody: {
    margin: 0,
    color: "#405062",
    lineHeight: 1.6,
  },
  layout: {
    display: "grid",
    gridTemplateColumns: "minmax(0, 1fr) 360px",
    gap: 16,
    alignItems: "start",
  },
  questions: {
    display: "grid",
    gap: 16,
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
    case "completed":
      return {
        background: "#e8f6ee",
        color: "#16613a",
        borderColor: "#b9e1c9",
      };
    case "in_progress":
      return {
        background: "#eef4ff",
        color: "#1f4c88",
        borderColor: "#c8d9ff",
      };
    default:
      return {
        background: "#edf0f4",
        color: "#415062",
        borderColor: "#d4dbe3",
      };
  }
}
