import { Check, Copy, ExternalLink } from 'lucide-react';
import { useState } from 'react';
import type { LinkHistoryItem } from '../api/types';
import { copyText } from '../lib/clipboard';
import { formatDate } from '../lib/formatDate';

type LinkHistoryRowProps = {
  link: LinkHistoryItem;
  onCopied: () => void;
};

export function LinkHistoryRow({ link, onCopied }: LinkHistoryRowProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await copyText(link.short_url);
      setCopied(true);
      onCopied();
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      setCopied(false);
    }
  }

  return (
    <article className="link-history-row">
      <div className="link-history-main">
        <a className="result-url" href={link.short_url} target="_blank" rel="noreferrer">
          {link.short_url} <ExternalLink size={14} />
        </a>
        <span className="detail-value detail-value-truncate" title={link.original_url}>{link.original_url}</span>
      </div>
      <div className="link-history-meta">
        <div><span className="detail-label">Created</span><span className="detail-value">{formatDate(link.created_at)}</span></div>
        <div><span className="detail-label">Clicks</span><strong className="stat-number">{link.click_count.toLocaleString()}</strong></div>
        <div><span className="detail-label">Last clicked</span><span className="detail-value">{formatDate(link.last_clicked_at)}</span></div>
      </div>
      <button className="secondary-button link-copy-button" type="button" onClick={handleCopy}>
        {copied ? <Check size={15} /> : <Copy size={15} />}
        {copied ? 'Copied' : 'Copy'}
      </button>
    </article>
  );
}
