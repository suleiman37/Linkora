import type { ApiFailure, BackendError } from './types';

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '');

export const API_BASE_URL = apiBaseUrl;

export async function apiRequest<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}${path}`, {
      ...options,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });
  } catch {
    const error = new Error('Unable to reach the API. Check your connection and try again.') as ApiFailure;
    error.isNetworkError = true;
    throw error;
  }

  if (!response.ok) {
    let payload: Partial<BackendError> = {};
    try {
      payload = (await response.json()) as Partial<BackendError>;
    } catch {
      // Keep a safe fallback for non-JSON responses.
    }

    const error = new Error(
      payload.error?.message ?? 'The service returned an unexpected response.',
    ) as ApiFailure;
    error.status = response.status;
    error.code = payload.error?.code;
    error.requestId = payload.error?.request_id ?? response.headers.get('X-Request-ID') ?? undefined;
    throw error;
  }

  return (await response.json()) as T;
}
