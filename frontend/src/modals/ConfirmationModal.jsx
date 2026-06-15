import '../styles/modal_style/confirmation-modal.css';

function ConfirmationModal({
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  variant = 'primary',
  loading = false,
  onCancel,
  onConfirm,
}) {
  const handleKeyDown = (e) => {
    if (e.key === 'Escape' && !loading) {
      onCancel();
    }
  };

  return (
    <div
      className="confirmation-modal-overlay"
      onClick={loading ? undefined : onCancel}
      onKeyDown={handleKeyDown}
      role="presentation"
    >
      <div
        className="confirmation-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirmation-modal-title"
      >
        <div className="confirmation-modal-header">
          <h2 id="confirmation-modal-title">{title}</h2>
          <button
            className="confirmation-modal-close"
            onClick={onCancel}
            disabled={loading}
            aria-label="Close confirmation dialog"
          >
            &times;
          </button>
        </div>

        <div className="confirmation-modal-body">
          <p>{message}</p>
        </div>

        <div className="confirmation-modal-actions">
          <button
            className="confirmation-modal-cancel"
            onClick={onCancel}
            disabled={loading}
          >
            {cancelLabel}
          </button>
          <button
            className={`confirmation-modal-confirm ${variant}`}
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? 'Working...' : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmationModal;
