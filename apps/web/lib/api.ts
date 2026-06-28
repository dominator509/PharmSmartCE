export type ProblemResponse = {
  type?: string;
  title?: string;
  status?: number;
  detail?: string;
  instance?: string;
};

export class ApiError extends Error {
  readonly status: number;
  readonly problem: ProblemResponse | null;

  constructor(
    message: string,
    status: number,
    problem: ProblemResponse | null = null,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.problem = problem;
  }
}

export type ApiFetchOptions = RequestInit & {
  baseUrl?: string;
};

export function getApiBaseUrl(): string {
  return (
    process.env.WEB_PUBLIC_API_URL?.replace(/\/$/, "") ??
    "http://127.0.0.1:8000"
  );
}

export async function apiFetch<T>(
  path: string,
  options: ApiFetchOptions = {},
): Promise<T> {
  const baseUrl = options.baseUrl ?? getApiBaseUrl();
  const url = new URL(path, `${baseUrl}/`);
  const response = await fetch(url, {
    ...options,
    headers: {
      accept: "application/json",
      ...options.headers,
    },
  });
  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const problem = isProblemResponse(payload) ? payload : null;
    const detail = problem?.detail ?? response.statusText ?? "Request failed.";
    throw new ApiError(detail, response.status, problem);
  }

  return payload as T;
}

function isProblemResponse(value: unknown): value is ProblemResponse {
  return Boolean(value && typeof value === "object" && "status" in value);
}
