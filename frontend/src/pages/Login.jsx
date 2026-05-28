import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import Form from '../components/Form';
import '../styles/page_style/login.css';

const loginFields = [
  {
    name: 'username',
    label: 'Username',
    type: 'text',
    required: true,
    autoComplete: 'username',
  },
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

  const[values, setValues] = useState({
    username: '',
    email: '',
    password: '',
    rememberMe: false,
  });
  
  const [showPassword, setShowPassword] = useState(false);

  const toggleShowPassword = () => {
    setShowPassword((prev) => !prev);
    setValues((prev) => ({ ...prev, showPassword: !prev.showPassword }));
  };

  const navigate = useNavigate();
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setValues((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const postData = async () => {
    const userData = {
      username: values.username,
      email: values.email,
      password: values.password,
    };

      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(userData),
        });
        const data = await response.json();
        navigate('/prices');

      } catch (error) {
        console.error('Login error:', error);
      }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await postData();
  };


    return (
        <div className="login-page">
            <h2>Login to Your Account</h2>
            <Form
                fields={loginFields}
                values={values}
                onChange={handleChange}
                onSubmit={handleSubmit}
                submitLabel="Login"
            />
            <p>
                Don't have an account? <Link to="/register">Register here</Link>.
            </p>
        </div>
    );
}

export default Login;
