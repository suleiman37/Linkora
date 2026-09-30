import { ChevronLeft, ChevronRight } from 'lucide-react';

type PaginationProps = {
  page: number;
  totalPages: number;
  isLoading: boolean;
  onPageChange: (page: number) => void;
};

export function Pagination({ page, totalPages, isLoading, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null;
  return (
    <div className="pagination" aria-label="Link history pagination">
      <button className="secondary-button" type="button" disabled={isLoading || page === 1} onClick={() => onPageChange(page - 1)}>
        <ChevronLeft size={15} /> Previous
      </button>
      <span>Page {page} of {totalPages}</span>
      <button className="secondary-button" type="button" disabled={isLoading || page === totalPages} onClick={() => onPageChange(page + 1)}>
        Next <ChevronRight size={15} />
      </button>
    </div>
  );
}
