import { useState } from 'react';
import Button from '../components/Button.jsx';
import '../styles/page_style/verification-pending.css';

const VerificationPending = () => {
  const [resendMessage, setResendMessage] = useState('');
  const [resendLoading, setResendLoading] = useState(false);

  const handleResendEmail = async () => {
    setResendLoading(true);
    setResendMessage('');

    try {
      // Since we don't have the email stored, show an informative message
      setResendMessage('Please check your inbox for the verification email. If you don\'t see it, check your spam folder.');
      setTimeout(() => {
        setResendMessage('');
      }, 5000);
    } finally {
      setResendLoading(false);
    }
  };

  return (
    <main className="verification-pending-page">
      <div className="verification-pending-container">
        <div className="verification-pending-icon">✓</div>
        <h1>Verify Your Email</h1>
        <p className="verification-pending-subtitle">
          A verification email has been sent to your email address.
        </p>
        <div className="verification-pending-steps">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Check Your Email</h3>
              <p>Look for an email from PREX in your inbox (or spam folder)</p>
            </div>
          </div>
          <div className="step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Click the Verification Link</h3>
              <p>Click the link in the email to verify your account</p>
            </div>
          </div>
          <div className="step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Login to Your Account</h3>
              <p>Once verified, you can login with your credentials</p>
            </div>
          </div>
        </div>

        {resendMessage && (
          <p className="resend-message">{resendMessage}</p>
        )}

        <div className="verification-pending-actions">
          <Button
            className="resend-button"
            name={resendLoading ? 'Sending...' : 'Resend Verification Email'}
            onClick={handleResendEmail}
            disabled={resendLoading}
          />
          <Button
            className="back-button"
            name="Back to Login"
            href="/login"
          />
        </div>

        <p className="verification-pending-note">
          This link will expire in 10 minutes. If your link expires, you can request a new one.
        </p>
      </div>
    </main>
  );
};

export default VerificationPending;
