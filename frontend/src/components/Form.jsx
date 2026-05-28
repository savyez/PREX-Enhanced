import Button from './Button';
import '../styles/form.css';

const Form = ({
  fields,
  values,
  onChange,
  onSubmit,
  submitLabel,
  isSubmitting = false,
  error = '',
  footer,
  className = '',
  submitClassName = '',
}) => {
  const formClassName = ['form', className].filter(Boolean).join(' ');

  return (
    <form className={formClassName} onSubmit={onSubmit}>
      {fields.map((field) => (
        <label key={field.name} className={field.type === 'checkbox' ? 'form-checkbox-row' : undefined}>
          <input
            name={field.name}
            type={field.type}
            value={field.type === 'checkbox' ? undefined : values[field.name]}
            checked={field.type === 'checkbox' ? values[field.name] : undefined}
            onChange={onChange}
            placeholder={field.placeholder}
            required={field.required}
            autoComplete={field.autoComplete}
          />
          {field.label}
        </label>
      ))}

      {error && <p className="form-error">{error}</p>}

      <Button className={submitClassName} name={submitLabel} type="submit" disabled={isSubmitting} />

      {footer && <small>{footer}</small>}
    </form>
  );
};

export default Form;
