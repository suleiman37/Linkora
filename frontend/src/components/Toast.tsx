type ToastProps = {
  message: string | null;
};

export function Toast({ message }: ToastProps) {
  if (!message) return null;
  return (
    <div className="toast" role="status" aria-live="polite">
      <span className="toast-mark">✓</span>
      {message}
    </div>
  );
}
