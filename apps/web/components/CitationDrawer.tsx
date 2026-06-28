import Link from "next/link";
import type React from "react";

import type { CitationPreviewDTO } from "../lib/sessionApi";

type CitationDrawerProps = {
  sessionId: string;
  citation: CitationPreviewDTO | null;
};

export function CitationDrawer({ sessionId, citation }: CitationDrawerProps) {
  if (!citation) {
    return null;
  }

  return (
    <div role="dialog" aria-label="Citation details" style={styles.drawer}>
      <div style={styles.header}>
        <div>
          <p style={styles.kicker}>Citation</p>
          <h2 style={styles.title}>{citation.source_filename}</h2>
        </div>
        <Link href={`/sessions/${sessionId}`} style={styles.closeLink}>
          Close
        </Link>
      </div>

      <p style={styles.meta}>
        Doc {citation.doc_id} · page {citation.page} · {citation.span}
      </p>

      <blockquote style={styles.passage}>
        <mark style={styles.mark}>{citation.passage}</mark>
      </blockquote>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  drawer: {
    border: "1px solid #d7e0ea",
    borderRadius: 8,
    background: "#ffffff",
    padding: 18,
    display: "grid",
    gap: 12,
    position: "sticky",
    top: 20,
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    gap: 12,
    alignItems: "flex-start",
  },
  kicker: {
    margin: 0,
    fontSize: 12,
    fontWeight: 700,
    textTransform: "uppercase",
    color: "#5c6b7a",
  },
  title: {
    margin: "6px 0 0",
    fontSize: 18,
    lineHeight: 1.3,
    letterSpacing: 0,
  },
  closeLink: {
    color: "#17385f",
    fontWeight: 700,
    textDecoration: "none",
    flex: "0 0 auto",
  },
  meta: {
    margin: 0,
    fontSize: 13,
    color: "#56687b",
  },
  passage: {
    margin: 0,
    padding: 0,
    lineHeight: 1.7,
    color: "#24364a",
  },
  mark: {
    background: "#fff2bf",
    padding: "0 3px",
  },
};
