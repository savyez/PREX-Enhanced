import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import Form from '../components/Form';

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
    return (
        <div className="login-page">
            <h2>Login to Your Account</h2>
            <Form
                fields={loginFields}
                values={{ username: '', email: '', password: '', rememberMe: false }}
                onChange={() => {}}
                onSubmit={() => {}}
                submitLabel="Login"
            />
            <p>
                Don't have an account? <Link to="/register">Register here</Link>.
            </p>
        </div>
    );
}

export default Login;
