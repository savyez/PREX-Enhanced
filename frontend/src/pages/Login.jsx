import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import Form from '../components/Form';
import { login } from '../utils/api';
import { useAuth } from '../context/authContext';
import '../styles/page_style/login.css';

const loginFields = [
  {
    name: 'email',
    label: 'Email',
    type: 'email',
    required: true,
    autoComplete: 'email',
  },
  {
    name: 'password',
    label: 'Password',
    type: 'password',
    required: true,
    autoComplete: 'current-password',
  },
  {
    name: 'rememberMe',
    label: 'Remember me',
    type: 'checkbox',
  },
];

const Login = () => {
  const { login: authLogin } = useAuth();
  const [values, setValues] = useState({
    username: '',
    email: '',
    password: '',
    rememberMe: false,
  });
  
  const [error, setError] = useState("");

  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setValues((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const postData = async () => {
    setError("");
    setLoading(true);

    const userData = {
      username: values.username,
      email: values.email,
      password: values.password,
    };

      try {
        const data = await login(userData);

        authLogin(data.access_token, data.refresh_token, data.user);

        navigate('/prices');

      } catch (error) {
        console.error('Login error:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await postData();
  };


    return (
        <div className="login-page">
            <h2>Login to Your Account</h2>
            {error && ( 
              <p className="error-message">
              {error}
            </p>
            )}
            <Form
            fields={loginFields}
            values={values}
            onChange={handleChange}
            onSubmit={handleSubmit}
            submitLabel={loading ? "Logging in..." : "Login"}
            />
            <p>
                Don't have an account? <Link to="/register">Register here</Link>.
            </p>
        </div>
    );
}

export default Login;
