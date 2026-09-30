import type { ApiFailure } from '../api/types';

type ErrorBannerProps = {
  error: ApiFailure | Error | null;
};

export function ErrorBanner({ error }: ErrorBannerProps) {
  if (!error) return null;
  const apiError = error as ApiFailure;
  const message = apiError.isNetworkError
    ? 'Unable to reach the API. Check your connection and try again.'
    : apiError.code === 'validation_error'
      ? 'Please check the URL and try again.'
      : 'The link could not be created right now. Please try again.';

  return (
    <div className="error-banner" role="alert">
      <span className="status-icon status-icon-error">!</span>
      <div>
        <strong>Something needs attention</strong>
        <p>{message}</p>
        {apiError.requestId && <small>Request ID: {apiError.requestId}</small>}
      </div>
    </div>
  );
}
