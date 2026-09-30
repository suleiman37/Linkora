import { Link2 } from 'lucide-react';

export function EmptyState() {
  return (
    <section className="empty-state" aria-label="No link created yet">
      <span className="empty-icon"><Link2 size={22} /></span>
      <div><h2>Your workspace is ready</h2><p>Create your first short link above and its performance will appear here.</p></div>
    </section>
  );
}
