import '../styles/component_style/card.css';

function Card({ children, className = '' }) {
    const cardClassName = ['card', className].filter(Boolean).join(' ');

    return (
        <article className={cardClassName}>
            {children}
        </article>
    );
}

export default Card;
