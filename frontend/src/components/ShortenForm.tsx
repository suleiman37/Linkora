import { ArrowUpRight, LoaderCircle, Sparkles } from 'lucide-react';
import { FormEvent, useState } from 'react';
import type { ApiFailure, CreateLinkResponse } from '../api/types';
import { useCreateLink } from '../hooks/useCreateLink';
import { ErrorBanner } from './ErrorBanner';

type ShortenFormProps = {
  onCreated: (link: CreateLinkResponse) => void;
};

export function ShortenForm({ onCreated }: ShortenFormProps) {
  const [url, setUrl] = useState('');
  const mutation = useCreateLink();
  const fieldError = url.length > 2048 ? 'URLs must be 2048 characters or fewer.' : undefined;

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = url.trim();
    if (!trimmed || fieldError) return;
    mutation.mutate(trimmed, { onSuccess: onCreated });
  }

  return (
    <section className="surface-card quick-shortener" aria-labelledby="shorten-heading">
      <div className="section-heading-row">
        <div>
          <div className="eyebrow"><Sparkles size={14} /> Quick shortener</div>
          <h2 id="shorten-heading">Turn a long URL into a clear, shareable link.</h2>
          <p className="section-copy">Create a polished short link in a second. Your original URL stays intact.</p>
        </div>
      </div>
      <form onSubmit={handleSubmit} noValidate>
        <label className="field-label" htmlFor="url-input">Long URL</label>
        <div className="shorten-row">
          <input
            id="url-input"
            className={`url-input${fieldError ? ' input-error' : ''}`}
            type="url"
            value={url}
            onChange={(event) => { setUrl(event.target.value); mutation.reset(); }}
            placeholder="Paste your long URL"
            aria-describedby={fieldError ? 'url-error' : undefined}
            aria-invalid={Boolean(fieldError)}
            autoComplete="url"
          />
          <button className="primary-button shorten-button" type="submit" disabled={mutation.isPending || !url.trim() || Boolean(fieldError)}>
            {mutation.isPending ? <><LoaderCircle className="spin" size={17} /> Creating...</> : <>Shorten URL <ArrowUpRight size={17} /></>}
          </button>
        </div>
        {fieldError && <p id="url-error" className="field-error" role="alert">{fieldError}</p>}
        {mutation.error && <ErrorBanner error={mutation.error as ApiFailure} />}
      </form>
    </section>
  );
}
