import { useParams, Link } from 'react-router-dom';
import { useState } from 'react';
import Form from '../components/Form';
import { confirmPasswordReset } from '../utils/api';
import '../styles/page_style/reset-password.css';
import Alert from '@mui/material/Alert';

const fields = [
  {
    name: 'new_password',
    label: 'New Password',
    type: 'password',
    required: true,
    autoComplete: 'new-password',
    placeholder: 'Enter new password',
  },
  {
    name: 'confirm_new_password',
    label: 'Confirm New Password',
    type: 'password',
    required: true,
    autoComplete: 'new-password',
    placeholder: 'Confirm new password',
  },
];

const ResetPasswordConfirm = () => {
  const { token } = useParams();
  const [values, setValues] = useState({
    new_password: '',
    confirm_new_password: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (values.new_password !== values.confirm_new_password) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);

    try {
      await confirmPasswordReset(token, values.new_password, values.confirm_new_password);
      setSuccess(true);
    } catch (err) {
      console.error('Password reset confirm error:', err);
      setError(err.message || 'Failed to reset password. The reset link may be invalid or expired.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reset-password-page">
      <h2>Set New Password</h2>

      {error && <Alert severity="error">{error}</Alert>}

      {success ? (
        <div style={{ textAlign: 'center' }}>
          <Alert severity="success" style={{ marginBottom: '1.25rem' }}>
            Password reset successfully! You can now log in with your new password.
          </Alert>
          <Link to="/login" className="button" style={{ display: 'inline-block', textDecoration: 'none', padding: '0.75rem 1.5rem' }}>
            Go to Login
          </Link>
        </div>
      ) : (
        <>
          <p className="subtitle">Please enter your new password below.</p>
          <Form
            fields={fields}
            values={values}
            onChange={handleChange}
            onSubmit={handleSubmit}
            submitLabel={loading ? 'Updating Password...' : 'Reset Password'}
            isSubmitting={loading}
          />
          <p>
            Remembered your password? <Link to="/login">Sign In</Link>
          </p>
        </>
      )}
    </div>
  );
};

export default ResetPasswordConfirm;
