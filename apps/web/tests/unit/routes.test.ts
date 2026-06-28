import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import CoursesPage from "../../app/courses/page";
import CourseDetailPage from "../../app/courses/[id]/page";
import Home from "../../app/page";
import RootLayout from "../../app/layout";
import LoginPage from "../../app/login/page";
import RegisterPage from "../../app/register/page";
import SessionPage from "../../app/sessions/[id]/page";
import SessionResultsPage from "../../app/sessions/[id]/results/page";

vi.mock("../../lib/courseApi", () => ({
  loadCourses: async () => ({
    items: [
      {
        id: "course-1",
        org_id: "org-1",
        title: "Cardiology CE",
        n_questions: 6,
        pass_pct: 70,
        status: "draft",
        created_at: "2026-06-27T00:00:00.000Z",
      },
    ],
  }),
  loadCourse: async () => ({
    id: "course-1",
    org_id: "org-1",
    title: "Cardiology CE",
    n_questions: 6,
    pass_pct: 70,
    status: "draft",
    created_at: "2026-06-27T00:00:00.000Z",
    sources: [
      {
        id: "source-1",
        course_id: "course-1",
        filename: "source.pdf",
        bytes: 48,
        sha256: "abc123",
        status: "uploaded",
        created_at: "2026-06-27T00:00:00.000Z",
      },
    ],
  }),
  uploadCourseSource: async () => ({
    id: "source-1",
    course_id: "course-1",
    filename: "source.pdf",
    bytes: 48,
    sha256: "abc123",
    status: "uploaded",
    created_at: "2026-06-27T00:00:00.000Z",
  }),
}));

vi.mock("../../lib/sessionApi", () => ({
  loadSession: async () => ({
    id: "session-1",
    course_id: "course-1",
    user_id: "user-1",
    status: "completed",
    total_questions: 1,
    answered_questions: 1,
    score_pct: 100,
    passed: true,
    record_id: "record-1",
    questions: [
      {
        id: "question-1",
        text: "What is the right answer?",
        options: ["Choice A", "Choice B"],
        citation: {
          doc_id: "source-1",
          page: 1,
          span: "p1:s1-s5",
          url: "/sessions/session-1?cite=source-1:1:p1:s1-s5",
        },
      },
    ],
  }),
  loadCitationPreview: async () => ({
    doc_id: "source-1",
    page: 1,
    span: "p1:s1-s5",
    source_filename: "source.pdf",
    passage: "What is the right answer?",
  }),
  loadCeRecord: async () => ({
    id: "record-1",
    session_id: "session-1",
    pdf_storage_key: "records/session-1.pdf",
    issued_at: "2026-06-27T00:00:00.000Z",
    download_url: "/api/ce-records/record-1/download",
  }),
}));

vi.mock("../../components/QuestionView", () => ({
  QuestionView: ({ question }: { question: { id: string; text: string } }) =>
    createElement(
      "article",
      { "data-question-id": question.id },
      question.text,
    ),
}));

vi.mock("../../components/CitationDrawer", () => ({
  CitationDrawer: ({
    citation,
  }: {
    citation: { doc_id: string; page: number; span: string } | null;
  }) =>
    createElement(
      "aside",
      null,
      citation ? `${citation.doc_id}:${citation.page}:${citation.span}` : "",
    ),
}));

vi.mock("../../components/SessionAutoRefresh", () => ({
  SessionAutoRefresh: () => null,
}));

describe("app routes", () => {
  it("renders the shell and top-level routes", async () => {
    const layoutHtml = renderToStaticMarkup(
      RootLayout({ children: createElement("main", null, "Child") }),
    );
    const homeHtml = renderToStaticMarkup(Home());
    const loginHtml = renderToStaticMarkup(
      await LoginPage({ searchParams: Promise.resolve({}) }),
    );
    const registerHtml = renderToStaticMarkup(
      await RegisterPage({ searchParams: Promise.resolve({}) }),
    );
    const coursesHtml = renderToStaticMarkup(await CoursesPage());
    const courseDetailHtml = renderToStaticMarkup(
      await CourseDetailPage({
        params: Promise.resolve({ id: "course-1" }),
        searchParams: Promise.resolve({ uploaded: "1" }),
      }),
    );
    const sessionHtml = renderToStaticMarkup(
      await SessionPage({
        params: Promise.resolve({ id: "session-1" }),
        searchParams: Promise.resolve({ cite: "doc-1:1:p1:s1" }),
      }),
    );
    const sessionResultsHtml = renderToStaticMarkup(
      await SessionResultsPage({
        params: Promise.resolve({ id: "session-1" }),
      }),
    );

    expect(layoutHtml).toContain("<html");
    expect(homeHtml).toContain("PharmSmartCE");
    expect(loginHtml).toContain("Login");
    expect(registerHtml).toContain("Register");
    expect(coursesHtml).toContain("Courses");
    expect(courseDetailHtml).toContain("Cardiology CE");
    expect(courseDetailHtml).toContain("source.pdf");
    expect(sessionHtml).toContain("session-1");
    expect(sessionHtml).toContain("source-1:1:p1:s1-s5");
    expect(sessionResultsHtml).toContain("Download CE record");
  });
});
