import { cookies } from "next/headers";

import { ApiError, apiFetch } from "./api";

export type CourseSourceDTO = {
  id: string;
  course_id: string;
  filename: string;
  bytes: number;
  sha256: string;
  status: string;
  created_at: string;
};

export type CourseDTO = {
  id: string;
  org_id: string;
  title: string;
  n_questions: number;
  pass_pct: number;
  status: string;
  created_at: string;
  sources: CourseSourceDTO[];
};

export type CourseListItemDTO = Omit<CourseDTO, "sources">;

export type CourseListDTO = {
  items: CourseListItemDTO[];
};

async function authedOptions(options: RequestInit = {}): Promise<RequestInit> {
  const cookieStore = await cookies();
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

export async function loadCourses(): Promise<CourseListDTO> {
  return apiFetch<CourseListDTO>("/api/courses", await authedOptions());
}

export async function loadCourse(courseId: string): Promise<CourseDTO> {
  return apiFetch<CourseDTO>(`/api/courses/${courseId}`, await authedOptions());
}

export async function uploadCourseSource(
  courseId: string,
  formData: FormData,
): Promise<CourseSourceDTO> {
  return apiFetch<CourseSourceDTO>(
    `/api/courses/${courseId}/sources`,
    await authedOptions({
      method: "POST",
      body: formData,
    }),
  );
}
