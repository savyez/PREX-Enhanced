import '../styles/component_style/pagination.css';

const Pagination = ({ currentPage, totalPages, onPageChange, ariaLabel = 'Pagination' }) => {
    if (totalPages <= 1) {
        return null;
    }

    const goToPreviousPage = () => {
        onPageChange(Math.max(1, currentPage - 1));
    };

    const goToNextPage = () => {
        onPageChange(Math.min(totalPages, currentPage + 1));
    };

    const getPageItems = () => {
        if (totalPages <= 5) {
            return Array.from({ length: totalPages }, (_, index) => index + 1);
        }

        if (currentPage <= 3) {
            return [1, 2, 3, 'ellipsis', totalPages];
        }

        if (currentPage >= totalPages - 2) {
            return [1, 'ellipsis', totalPages - 2, totalPages - 1, totalPages];
        }

        return [1, 'ellipsis', currentPage, 'ellipsis', totalPages];
    };

    const pageItems = getPageItems();

    return (
        <nav className="pagination" aria-label={ariaLabel}>
            <button
                className="pagination-arrow"
                type="button"
                onClick={goToPreviousPage}
                disabled={currentPage === 1}
                aria-label="Previous page"
            >
                &lt;
            </button>

            <div className="pagination-pages">
                {pageItems.map((item, index) => {
                    if (item === 'ellipsis') {
                        return (
                            <span
                                key={`ellipsis-${index}`}
                                className="pagination-ellipsis"
                                aria-hidden="true"
                            >
                                ...
                            </span>
                        );
                    }

                    return (
                        <button
                            key={item}
                            type="button"
                            className={`pagination-page ${item === currentPage ? 'is-active' : ''}`}
                            onClick={() => onPageChange(item)}
                            aria-current={item === currentPage ? 'page' : undefined}
                            aria-label={`Go to page ${item}`}
                        >
                            {item}
                        </button>
                    );
                })}
            </div>

            <button
                className="pagination-arrow"
                type="button"
                onClick={goToNextPage}
                disabled={currentPage === totalPages}
                aria-label="Next page"
            >
                &gt;
            </button>
        </nav>
    );
};

export default Pagination;
