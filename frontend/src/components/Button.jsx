import '../styles/button.css';
import { Link } from 'react-router-dom';

function Button({ name, href, onClick, children, className = '', type = 'button', disabled = false }) {
  const label = children || name;
  const buttonClassName = ['button', className].filter(Boolean).join(' ');

  if (href) {
    if (href.startsWith('/')) {
      return (
        <Link className={buttonClassName} to={href}>
          {label}
        </Link>
      );
    }

    return (
      <a className={buttonClassName} href={href}>
        {label}
      </a>
    );
  }

  return (
    <button className={buttonClassName} type={type} onClick={onClick} disabled={disabled}>
      {label}
    </button>
  );
}

export default Button;
