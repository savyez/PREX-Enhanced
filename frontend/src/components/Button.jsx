function Button({ name, href, onClick, children }) {
  const label = children || name;

  if (href) {
    return (
      <a className="button" href={href}>
        {label}
      </a>
    );
  }

  return (
    <button className="button" type="button" onClick={onClick}>
      {label}
    </button>
  );
}

export default Button;
