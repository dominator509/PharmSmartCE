"use server";

import { ApiError } from "./api";
import { submitSessionAnswer, type AnswerResultDTO } from "./sessionApi";

export type AnswerFeedbackState = {
  error?: string;
  correct?: boolean;
  correct_index?: number;
  rationale?: string;
  citation?: AnswerResultDTO["citation"];
  session_progress?: AnswerResultDTO["session_progress"];
  score_pct?: number | null;
  passed?: boolean | null;
};

const EMPTY_STATE: AnswerFeedbackState = {};

export async function recordSessionAnswerAction(
  _previousState: AnswerFeedbackState,
  formData: FormData,
): Promise<AnswerFeedbackState> {
  const sessionId = String(formData.get("session_id") ?? "");
  const questionId = String(formData.get("question_id") ?? "");
  const chosenIndexRaw = Number(formData.get("chosen_index"));

  if (!sessionId || !questionId || !Number.isInteger(chosenIndexRaw)) {
    return { error: "Please choose an answer before submitting." };
  }

  try {
    const result = await submitSessionAnswer(
      sessionId,
      questionId,
      chosenIndexRaw,
    );
    return {
      correct: result.correct,
      correct_index: result.correct_index,
      rationale: result.rationale,
      citation: result.citation,
      session_progress: result.session_progress,
      score_pct: result.score_pct,
      passed: result.passed,
    };
  } catch (error) {
    if (error instanceof ApiError) {
      return { ...EMPTY_STATE, error: error.problem?.detail ?? error.message };
    }
    throw error;
  }
}
