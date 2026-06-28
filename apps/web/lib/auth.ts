import { cookies } from "next/headers";

import { ApiError, getApiBaseUrl } from "./api";

export type AuthCredentials = {
  email: string;
  password: string;
};

export type AccessTokenDTO = {
  access_token: string;
  token_type: string;
  expires_in: number;
};

export type AuthResult = {
  accessToken: string;
  tokenType: string;
  expiresIn: number;
};

type CookieStore = {
  get(name: string): { value: string } | undefined;
  set(
    name: string,
    value: string,
    options: {
      httpOnly: boolean;
      secure: boolean;
      sameSite: "lax";
      path: string;
      maxAge: number;
    },
  ): void;
  delete(name: string, options: { path: string }): void;
};

type AuthDeps = {
  baseUrl?: string;
  fetchImpl?: typeof fetch;
  cookieStore?: CookieStore;
};

const REFRESH_COOKIE = "refresh";
const REFRESH_COOKIE_PATH = "/";
const REFRESH_COOKIE_MAX_AGE = 30 * 24 * 60 * 60;

export async function loginAction(formData: FormData): Promise<AuthResult> {
  return performLogin(parseCredentials(formData));
}

export async function registerAction(formData: FormData): Promise<AuthResult> {
  const credentials = parseCredentials(formData);
  await requestJson<{ id: string }>("/auth/register", {
    method: "POST",
    headers: jsonHeaders(),
    body: JSON.stringify(credentials),
  });
  return performLogin(credentials);
}

export async function refreshAction(): Promise<AuthResult> {
  return performRefresh();
}

export async function logoutAction(): Promise<void> {
  await performLogout();
}

export function createAuthActions(deps: AuthDeps = {}) {
  return {
    login: async (credentials: AuthCredentials): Promise<AuthResult> =>
      performLogin(credentials, deps),
    register: async (credentials: AuthCredentials): Promise<AuthResult> => {
      await requestJson<{ id: string }>("/auth/register", {
        ...deps,
        method: "POST",
        headers: jsonHeaders(),
        body: JSON.stringify(credentials),
      });
      return performLogin(credentials, deps);
    },
    refresh: async (): Promise<AuthResult> => performRefresh(deps),
    logout: async (): Promise<void> => performLogout(deps),
  };
}

async function performLogin(
  credentials: AuthCredentials,
  deps: AuthDeps = {},
): Promise<AuthResult> {
  const { payload, setCookie } = await requestJson<AccessTokenDTO>(
    "/auth/login",
    {
      ...deps,
      method: "POST",
      headers: jsonHeaders(),
      body: JSON.stringify(credentials),
    },
  );
  await storeRefreshCookie(setCookie, deps);
  return toAuthResult(payload);
}

async function performRefresh(deps: AuthDeps = {}): Promise<AuthResult> {
  const { payload, setCookie } = await requestJson<AccessTokenDTO>(
    "/auth/refresh",
    {
      ...deps,
      method: "POST",
      headers: await refreshHeaders(deps),
    },
  );
  await storeRefreshCookie(setCookie, deps);
  return toAuthResult(payload);
}

async function performLogout(deps: AuthDeps = {}): Promise<void> {
  await requestJson<void>("/auth/logout", {
    ...deps,
    method: "POST",
    headers: await refreshHeaders(deps),
  });
  try {
    const cookieStore = await getCookieStore(deps);
    cookieStore.delete(REFRESH_COOKIE, { path: REFRESH_COOKIE_PATH });
  } catch {
    // Best-effort when the runtime cannot mutate the request cookie jar.
  }
}

async function requestJson<T>(
  path: string,
  options: RequestInit & AuthDeps = {},
): Promise<{ payload: T; setCookie: string | null }> {
  const response = await (options.fetchImpl ?? fetch)(
    new URL(path, `${options.baseUrl ?? getApiBaseUrl()}/`),
    {
      method: options.method,
      headers: {
        accept: "application/json",
        ...(options.headers ?? {}),
      },
      body: options.body,
    },
  );
  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("json")
    ? await response.json()
    : undefined;

  if (!response.ok) {
    const problem = isProblemResponse(payload) ? payload : null;
    const detail =
      problem?.detail ??
      (typeof payload === "string" ? payload : response.statusText) ??
      "Request failed.";
    throw new ApiError(detail, response.status, problem);
  }

  return {
    payload: payload as T,
    setCookie: response.headers.get("set-cookie"),
  };
}

function parseCredentials(formData: FormData): AuthCredentials {
  return {
    email: String(formData.get("email") ?? ""),
    password: String(formData.get("password") ?? ""),
  };
}

async function refreshHeaders(deps: AuthDeps): Promise<HeadersInit> {
  const refresh = (await getCookieStore(deps)).get(REFRESH_COOKIE)?.value;
  return refresh ? { cookie: `${REFRESH_COOKIE}=${refresh}` } : {};
}

function jsonHeaders(): HeadersInit {
  return { "content-type": "application/json" };
}

async function storeRefreshCookie(
  setCookie: string | null,
  deps: AuthDeps,
): Promise<void> {
  const refreshValue = parseCookieValue(setCookie, REFRESH_COOKIE);
  if (!refreshValue) {
    return;
  }
  try {
    const cookieStore = await getCookieStore(deps);
    cookieStore.set(REFRESH_COOKIE, refreshValue, {
      httpOnly: true,
      secure: isSecureCookie(),
      sameSite: "lax",
      path: REFRESH_COOKIE_PATH,
      maxAge: REFRESH_COOKIE_MAX_AGE,
    });
  } catch {
    // Best-effort when the runtime cannot mutate the request cookie jar.
  }
}

async function getCookieStore(deps: AuthDeps): Promise<CookieStore> {
  return deps.cookieStore ?? ((await cookies()) as unknown as CookieStore);
}

function parseCookieValue(
  headerValue: string | null,
  name: string,
): string | null {
  if (!headerValue) {
    return null;
  }

  for (const part of headerValue.split(/,(?=\s*[^;]+?=)/)) {
    const trimmed = part.trim();
    if (trimmed.startsWith(`${name}=`)) {
      return trimmed.slice(name.length + 1).split(";", 1)[0] ?? null;
    }
  }

  return null;
}

function toAuthResult(payload: AccessTokenDTO): AuthResult {
  return {
    accessToken: payload.access_token,
    tokenType: payload.token_type,
    expiresIn: payload.expires_in,
  };
}

function isSecureCookie(): boolean {
  return process.env.NODE_ENV === "production";
}

function isProblemResponse(value: unknown): value is {
  type?: string;
  title?: string;
  status?: number;
  detail?: string;
  instance?: string;
} {
  return Boolean(value && typeof value === "object" && "status" in value);
}
