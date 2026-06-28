"use client";

import Link from "next/link";
import { useFormState, useFormStatus } from "react-dom";
import type React from "react";

import {
  recordSessionAnswerAction,
  type AnswerFeedbackState,
} from "../lib/sessionActions";
import type { SessionQuestionDTO } from "../lib/sessionApi";

type QuestionViewProps = {
  sessionId: string;
  question: SessionQuestionDTO;
};

const INITIAL_STATE: AnswerFeedbackState = {};

export function QuestionView({ sessionId, question }: QuestionViewProps) {
  const [state, formAction] = useFormState(
    recordSessionAnswerAction,
    INITIAL_STATE,
  );
  const answered = state.correct !== undefined;

  return (
    <article style={styles.card} data-question-id={question.id}>
      <header style={styles.header}>
        <div>
          <p style={styles.kicker}>Question</p>
          <h2 style={styles.title}>
            {question.text} <CitationLink citationUrl={question.citation.url} />
          </h2>
        </div>
        <span style={styles.badge}>[1]</span>
      </header>

      <form action={formAction} style={styles.form}>
        <input type="hidden" name="session_id" value={sessionId} />
        <input type="hidden" name="question_id" value={question.id} />

        <fieldset style={styles.fieldset} disabled={answered}>
          <legend style={styles.legend}>Choose one answer</legend>
          <div style={styles.options}>
            {question.options.map((option, index) => (
              <label key={`${question.id}-${index}`} style={styles.option}>
                <input
                  type="radio"
                  name="chosen_index"
                  value={index}
                  required
                />
                <span>{option}</span>
              </label>
            ))}
          </div>
        </fieldset>

        {state.error ? (
          <p role="alert" style={styles.error}>
            {state.error}
          </p>
        ) : null}

        {!answered ? <SubmitButton /> : <AnswerFeedback state={state} />}
      </form>
    </article>
  );
}

function CitationLink({ citationUrl }: { citationUrl: string }) {
  return (
    <sup>
      <Link href={citationUrl} style={styles.citationLink}>
        [1]
      </Link>
    </sup>
  );
}

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button type="submit" style={styles.button} disabled={pending}>
      {pending ? "Submitting..." : "Submit answer"}
    </button>
  );
}

function AnswerFeedback({ state }: { state: AnswerFeedbackState }) {
  const correct = Boolean(state.correct);

  return (
    <section
      aria-live="polite"
      style={{
        ...styles.feedback,
        ...(correct ? styles.feedbackCorrect : styles.feedbackIncorrect),
      }}
    >
      <p style={styles.feedbackTitle}>{correct ? "Correct" : "Not quite"}</p>
      <p style={styles.feedbackBody}>
        Correct answer: choice{" "}
        {state.correct_index != null ? state.correct_index + 1 : "?"}.
      </p>
      <p style={styles.feedbackBody}>{state.rationale}</p>
      {state.citation ? (
        <p style={styles.feedbackBody}>
          Citation: <CitationLink citationUrl={state.citation.url} />
        </p>
      ) : null}
      {state.session_progress ? (
        <p style={styles.feedbackMeta}>
          Progress: {state.session_progress.answered}/
          {state.session_progress.total}
        </p>
      ) : null}
      {state.score_pct != null || state.passed != null ? (
        <p style={styles.feedbackMeta}>
          Score: {state.score_pct ?? 0}%{" "}
          {state.passed ? "(passing)" : "(not yet passing)"}
        </p>
      ) : null}
    </section>
  );
}

const styles: Record<string, React.CSSProperties> = {
  card: {
    border: "1px solid #d7e0ea",
    borderRadius: 8,
    background: "#ffffff",
    padding: 18,
    display: "grid",
    gap: 16,
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
    fontSize: 20,
    lineHeight: 1.4,
    letterSpacing: 0,
    color: "#102033",
  },
  badge: {
    flex: "0 0 auto",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    width: 30,
    height: 30,
    borderRadius: 999,
    border: "1px solid #c8d9ff",
    background: "#eef4ff",
    color: "#1f4c88",
    fontSize: 13,
    fontWeight: 700,
  },
  form: {
    display: "grid",
    gap: 14,
  },
  fieldset: {
    border: "none",
    padding: 0,
    margin: 0,
    display: "grid",
    gap: 10,
  },
  legend: {
    marginBottom: 4,
    fontSize: 14,
    fontWeight: 700,
    color: "#33475a",
  },
  options: {
    display: "grid",
    gap: 10,
  },
  option: {
    display: "flex",
    gap: 10,
    alignItems: "flex-start",
    border: "1px solid #e0e7ef",
    borderRadius: 8,
    padding: "10px 12px",
    background: "#fbfdff",
  },
  button: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    border: "1px solid #17385f",
    borderRadius: 8,
    background: "#17385f",
    color: "#ffffff",
    fontSize: 14,
    fontWeight: 700,
    padding: "10px 14px",
    width: "fit-content",
  },
  error: {
    margin: 0,
    color: "#9c1f1f",
    fontWeight: 600,
  },
  feedback: {
    borderRadius: 8,
    border: "1px solid transparent",
    padding: 14,
    display: "grid",
    gap: 8,
  },
  feedbackCorrect: {
    background: "#edf9f0",
    borderColor: "#b7e0c2",
    color: "#124d2d",
  },
  feedbackIncorrect: {
    background: "#fff4f4",
    borderColor: "#f0c0c0",
    color: "#8f2424",
  },
  feedbackTitle: {
    margin: 0,
    fontSize: 14,
    fontWeight: 800,
  },
  feedbackBody: {
    margin: 0,
    lineHeight: 1.6,
  },
  feedbackMeta: {
    margin: 0,
    fontSize: 13,
    opacity: 0.85,
  },
  citationLink: {
    color: "#17385f",
    textDecoration: "none",
    fontWeight: 800,
  },
};
