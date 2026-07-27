import { Link } from 'react-router-dom';
import { useState } from 'react';
import Form from '../components/Form';
import { requestPasswordReset } from '../utils/api';
import '../styles/page_style/reset-password.css';
import Alert from '@mui/material/Alert';

const fields = [
  {
    name: 'email',
    label: 'Email Address',
    type: 'email',
    required: true,
    autoComplete: 'email',
    placeholder: 'Enter your registered email',
  },
];

const ResetPasswordRequest = () => {
  const [values, setValues] = useState({ email: '' });
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);

    try {
      const res = await requestPasswordReset(values.email);
      setMessage(res.message || 'Password reset instructions have been sent to your email.');
    } catch (err) {
      console.error('Password reset request error:', err);
      setError(err.message || 'Failed to send password reset email.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reset-password-page">
      <h2>Reset Your Password</h2>
      <p className="subtitle">
        Enter the email address associated with your PREX account and we will send you instructions to reset your password.
      </p>

      {error && <Alert severity="error">{error}</Alert>}
      {message && <Alert severity="success">{message}</Alert>}

      <Form
        fields={fields}
        values={values}
        onChange={handleChange}
        onSubmit={handleSubmit}
        submitLabel={loading ? 'Sending...' : 'Send Reset Link'}
        isSubmitting={loading}
      />

      <p>
        Remembered your password? <Link to="/login">Sign In</Link>
      </p>
    </div>
  );
};

export default ResetPasswordRequest;
