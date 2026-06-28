import Link from "next/link";
import { redirect } from "next/navigation";
import React from "react";

import { ApiError } from "../../../../lib/api";
import {
  loadCeRecord,
  loadSession,
  type SessionDTO,
} from "../../../../lib/sessionApi";

type SessionResultsPageProps = {
  params: Promise<{ id: string }>;
};

export default async function SessionResultsPage({
  params,
}: SessionResultsPageProps) {
  const resolvedParams = await params;

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

  if (session.record_id === null) {
    return (
      <main style={styles.page}>
        <section style={styles.panel}>
          <p style={styles.kicker}>Results</p>
          <h1 style={styles.title}>Session {session.id}</h1>
          <p style={styles.body}>Results are not ready yet.</p>
          <Link href={`/sessions/${session.id}`} style={styles.link}>
            Back to session
          </Link>
        </section>
      </main>
    );
  }

  let record;
  try {
    record = await loadCeRecord(session.record_id);
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
      <section style={styles.panel}>
        <p style={styles.kicker}>Results</p>
        <h1 style={styles.title}>Session {session.id}</h1>
        <p style={styles.body}>
          Score {session.score_pct ?? 0}%{" "}
          {session.passed ? "(passed)" : "(not yet passing)"}
        </p>
        <p style={styles.body}>
          {session.answered_questions}/{session.total_questions} answered
        </p>
        {session.passed ? (
          <Link href={record.download_url} style={styles.link}>
            Download CE record
          </Link>
        ) : (
          <p style={styles.body}>
            CE record will be available once the passing score is reached.
          </p>
        )}
      </section>
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    maxWidth: "800px",
    margin: "0 auto",
    padding: "32px 20px 56px",
    color: "#102033",
    fontFamily:
      'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  },
  panel: {
    border: "1px solid #d7e0ea",
    borderRadius: 8,
    background: "#ffffff",
    padding: 18,
    display: "grid",
    gap: 10,
  },
  kicker: {
    margin: 0,
    fontSize: 12,
    fontWeight: 700,
    textTransform: "uppercase",
    color: "#5c6b7a",
  },
  title: {
    margin: "4px 0 0",
    fontSize: 28,
    lineHeight: 1.2,
    letterSpacing: 0,
  },
  body: {
    margin: 0,
    color: "#405062",
    lineHeight: 1.6,
  },
  link: {
    color: "#17385f",
    fontWeight: 700,
    textDecoration: "none",
    width: "fit-content",
  },
};
