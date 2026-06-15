import '../styles/component_style/card.css';

function Card({ children, className = '', onClick, }) {
    const cardClassName = ['card', className]
        .filter(Boolean)
        .join(' ');

    return (
        <article
            className={cardClassName}
            onClick={onClick}
        >
            {children}
        </article>
    );
}

export default Card;
