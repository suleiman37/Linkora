import { FileText, LoaderCircle, Plus, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import type { LinkSort } from '../api/types';
import { useLinks } from '../hooks/useLinks';
import { LinkHistoryFilters } from '../components/LinkHistoryFilters';
import { LinkHistoryRow } from '../components/LinkHistoryRow';
import { Pagination } from '../components/Pagination';
import { Toast } from '../components/Toast';

const PAGE_SIZE = 10;

export function LinksPage() {
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState<LinkSort>('created_desc');
  const [toast, setToast] = useState<string | null>(null);
  const linksQuery = useLinks({ page, pageSize: PAGE_SIZE, search, sort });

  function showToast(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(null), 3200);
  }

  function applySearch() {
    setSearch(searchInput.trim());
    setPage(1);
  }

  function handleSortChange(value: LinkSort) {
    setSort(value);
    setPage(1);
  }

  const pagination = linksQuery.data?.pagination;

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <div className="page-kicker"><span className="kicker-dot" /> Link workspace</div>
          <h1>Links</h1>
          <p>Review, search, and share every short link in your workspace.</p>
        </div>
        <Link className="primary-button" to="/"><Plus size={16} /> Create link</Link>
      </div>
      <section className="surface-card links-card" aria-labelledby="links-heading">
        <div className="card-heading">
          <span className="card-icon"><FileText size={18} /></span>
          <div><h2 id="links-heading">Link history</h2><p>{pagination ? `${pagination.total} link${pagination.total === 1 ? '' : 's'} total` : 'Your created links'}</p></div>
        </div>
        <LinkHistoryFilters
          searchInput={searchInput}
          sort={sort}
          onSearchInputChange={setSearchInput}
          onSearch={applySearch}
          onSortChange={handleSortChange}
        />
        {linksQuery.isLoading && !linksQuery.data && <div className="history-message"><LoaderCircle className="spin" size={20} /> Loading links</div>}
        {linksQuery.isError && <div className="history-message history-error"><p>Unable to load your links right now.</p><button className="secondary-button" type="button" onClick={() => void linksQuery.refetch()}><RefreshCw size={15} /> Try again</button></div>}
        {linksQuery.data && linksQuery.data.items.length === 0 && <div className="history-message"><p>{search ? 'No links match your search.' : 'No links created yet.'}</p><Link className="secondary-button" to="/">Create your first link</Link></div>}
        {linksQuery.data && linksQuery.data.items.length > 0 && (
          <>
            <div className="link-history-list">
              {linksQuery.data.items.map((link) => <LinkHistoryRow key={link.id} link={link} onCopied={() => showToast('Link copied to clipboard')} />)}
            </div>
            {pagination && <Pagination page={pagination.page} totalPages={pagination.total_pages} isLoading={linksQuery.isFetching} onPageChange={setPage} />}
          </>
        )}
      </section>
      <Toast message={toast} />
    </div>
  );
}
