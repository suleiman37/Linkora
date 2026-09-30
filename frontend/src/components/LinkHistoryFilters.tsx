import type { FormEvent } from 'react';
import type { LinkSort } from '../api/types';

type LinkHistoryFiltersProps = {
  searchInput: string;
  sort: LinkSort;
  onSearchInputChange: (value: string) => void;
  onSearch: () => void;
  onSortChange: (value: LinkSort) => void;
};

export function LinkHistoryFilters({
  searchInput,
  sort,
  onSearchInputChange,
  onSearch,
  onSortChange,
}: LinkHistoryFiltersProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch();
  }

  return (
    <form className="link-filters" onSubmit={handleSubmit}>
      <label className="link-search-field">
        <span className="detail-label">Search links</span>
        <input
          className="url-input"
          type="search"
          value={searchInput}
          onChange={(event) => onSearchInputChange(event.target.value)}
          placeholder="Search URL or short code"
        />
      </label>
      <label className="link-sort-field">
        <span className="detail-label">Sort by</span>
        <select className="url-input" value={sort} onChange={(event) => onSortChange(event.target.value as LinkSort)}>
          <option value="created_desc">Newest first</option>
          <option value="created_asc">Oldest first</option>
          <option value="clicks_desc">Most clicks</option>
        </select>
      </label>
      <button className="secondary-button filter-button" type="submit">Search</button>
    </form>
  );
}
