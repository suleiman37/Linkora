import { Check, Copy, ExternalLink } from 'lucide-react';
import { useState } from 'react';
import type { CreateLinkResponse } from '../api/types';
import { copyText } from '../lib/clipboard';
import { formatDate } from '../lib/formatDate';

type LinkResultCardProps = {
  link: CreateLinkResponse;
  onCopied: () => void;
};

export function LinkResultCard({ link, onCopied }: LinkResultCardProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await copyText(link.short_url);
      setCopied(true);
      onCopied();
      window.setTimeout(() => setCopied(false), 2200);
    } catch {
      setCopied(false);
    }
  }

  return (
    <section className="surface-card result-card" aria-labelledby="result-heading">
      <div className="success-heading">
        <span className="status-icon status-icon-success"><Check size={16} /></span>
        <div><h2 id="result-heading">Link created successfully</h2><p>Ready to share with the world.</p></div>
      </div>
      <div className="result-link-row">
        <div className="result-link-wrap">
          <span className="detail-label">Short link</span>
          <a className="result-url" href={link.short_url} target="_blank" rel="noreferrer">{link.short_url} <ExternalLink size={15} /></a>
        </div>
        <button className="secondary-button copy-button" type="button" onClick={handleCopy}>
          {copied ? <Check size={16} /> : <Copy size={16} />}
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <div className="result-meta-grid">
        <div><span className="detail-label">Original URL</span><span className="detail-value detail-value-truncate" title={link.original_url}>{link.original_url}</span></div>
        <div><span className="detail-label">Created</span><span className="detail-value">{formatDate(link.created_at)}</span></div>
      </div>
    </section>
  );
}
