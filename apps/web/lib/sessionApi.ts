import { cookies } from "next/headers";

import { ApiError, apiFetch } from "./api";

export type SessionCitationDTO = {
  doc_id: string;
  page: number;
  span: string;
  url: string;
};

export type CitationLookup = Pick<
  SessionCitationDTO,
  "doc_id" | "page" | "span"
>;

export type SessionQuestionDTO = {
  id: string;
  text: string;
  options: string[];
  citation: SessionCitationDTO;
};

export type SessionDTO = {
  id: string;
  course_id: string;
  user_id: string;
  status: string;
  total_questions: number;
  answered_questions: number;
  score_pct: number | null;
  passed: boolean | null;
  record_id: string | null;
  questions: SessionQuestionDTO[];
};

export type AnswerResultDTO = {
  correct: boolean;
  correct_index: number;
  rationale: string;
  citation: SessionCitationDTO;
  session_progress: {
    answered: number;
    total: number;
  };
  score_pct: number | null;
  passed: boolean | null;
};

export type CitationPreviewDTO = {
  doc_id: string;
  page: number;
  span: string;
  source_filename: string;
  passage: string;
};

export type CERecordDTO = {
  id: string;
  session_id: string;
  pdf_storage_key: string;
  issued_at: string;
  download_url: string;
};

type CookieStore = {
  get(name: string): { value: string } | undefined;
};

async function authedOptions(options: RequestInit = {}): Promise<RequestInit> {
  const cookieStore = (await cookies()) as unknown as CookieStore;
  const accessToken = cookieStore.get("access")?.value;
  if (!accessToken) {
    throw new ApiError("Authentication required.", 401);
  }

  return {
    ...options,
    headers: {
      authorization: `Bearer ${accessToken}`,
      ...(options.headers ?? {}),
    },
  };
}

function jsonHeaders(): HeadersInit {
  return { "content-type": "application/json" };
}

export async function loadSession(sessionId: string): Promise<SessionDTO> {
  return apiFetch<SessionDTO>(
    `/api/sessions/${sessionId}`,
    await authedOptions(),
  );
}

export async function loadCitationPreview(
  sessionId: string,
  citation: CitationLookup,
): Promise<CitationPreviewDTO> {
  const searchParams = new URLSearchParams({
    doc_id: citation.doc_id,
    page: String(citation.page),
    span: citation.span,
  });
  return apiFetch<CitationPreviewDTO>(
    `/api/sessions/${sessionId}/citation?${searchParams.toString()}`,
    await authedOptions(),
  );
}

export async function submitSessionAnswer(
  sessionId: string,
  questionId: string,
  chosenIndex: number,
): Promise<AnswerResultDTO> {
  return apiFetch<AnswerResultDTO>(
    `/api/sessions/${sessionId}/answers`,
    await authedOptions({
      method: "POST",
      headers: jsonHeaders(),
      body: JSON.stringify({
        question_id: questionId,
        chosen_index: chosenIndex,
      }),
    }),
  );
}

export async function loadCeRecord(recordId: string): Promise<CERecordDTO> {
  return apiFetch<CERecordDTO>(
    `/api/ce-records/${recordId}`,
    await authedOptions(),
  );
}
