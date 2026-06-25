import { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Button from '../components/Button.jsx';
import Form from '../components/Form.jsx';
import { requestPasswordReset } from '../utils/api.js';
import { getUser, isAuthenticated, clearAuth } from '../utils/auth.js';
import '../styles/page_style/settings.css';

function Settings() {
  const navigate = useNavigate();
  const user = useMemo(() => getUser(), []);
  const [values, setValues] = useState({ email: user?.email || '' });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setValues((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handlePasswordReset = async (event) => {
    event.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);

    try {
      const response = await requestPasswordReset(values.email.trim());
      setMessage(response?.message || 'Password reset instructions sent.');
    } catch (err) {
      setError(err.message || 'Unable to send password reset email.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  const resetFields = [
    {
      name: 'email',
      label: 'Account Email',
      type: 'email',
      required: true,
      autoComplete: 'email',
    },
  ];

  return (
    <main className="settings-page">
      <section className="settings-shell">
        <header className="settings-hero">
          <p className="settings-kicker">Account</p>
          <h1>Settings</h1>
          <p className="settings-subtitle">
            Keep your account secure and manage the few actions that matter here.
          </p>
        </header>

        {!isAuthenticated() ? (
          <div className="settings-card settings-auth-card">
            <h2>You need to log in</h2>
            <p>Sign in to manage account actions like password reset and logout.</p>
            <Link className="button explore-prices" to="/login">
              Login
            </Link>
          </div>
        ) : (
          <div className="settings-grid">
            <section className="settings-card">
              <h2>Account Snapshot</h2>
              <div className="settings-details">
                <p><span>Username</span><strong>{user?.username || 'Unknown'}</strong></p>
                <p><span>Email</span><strong>{user?.email || 'Unknown'}</strong></p>
                <p><span>Status</span><strong>{user?.email_confirmed ? 'Verified' : 'Not verified'}</strong></p>
              </div>
            </section>

            <section className="settings-card">
              <h2>Password Reset</h2>
              <p className="settings-help">
                Send yourself a reset link if you want to change your password.
              </p>
              <Form
                fields={resetFields}
                values={values}
                onChange={handleChange}
                onSubmit={handlePasswordReset}
                submitLabel={loading ? 'Sending...' : 'Send Reset Email'}
                isSubmitting={loading}
                error={error}
                footer={message}
              />
            </section>

            <section className="settings-card">
              <h2>Quick Actions</h2>
              <div className="settings-actions">
                <Button className="settings-action-link" href="/profile" name="Edit Profile" />
                <Button className="settings-action-link" href="/prices" name="Browse Prices" />
                <Button className="settings-logout" onClick={handleLogout} name="Logout" />
              </div>
            </section>
          </div>
        )}
      </section>
    </main>
  );
}

export default Settings;
