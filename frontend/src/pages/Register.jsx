import Form from '../components/Form';
import '../styles/page_style/register.css';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { register } from '../utils/api';

const Register = () => {
    const navigate = useNavigate();

const registerFields = [
    {
        name: 'username',
        label: 'Username',
        type: 'text',
        required: true,
        autoComplete: 'username',
    },
    {
        name: 'date_of_birth',
        label: 'Date of Birth',
        type: 'date',
        required: true,
        autoComplete: 'bday',
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
        autoComplete: 'new-password',
    },
];
    const[values, setValues] = useState({
        username: '',
        date_of_birth: '',
        email: '',
        password: '',
    });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setValues((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const postData = async () => {
        setLoading(true);
        setError("");
        
        const userData = {
        username: values.username,
        dob: values.date_of_birth,
        email: values.email,
        password: values.password,
    };

      try {
        await register(userData);
        navigate('/login');

        } catch (error) {
            setError(error.message);
            console.error('Registration error:', error);
        } finally {
            setLoading(false);
        }

        };

        const handleSubmit = async (e) => {
                e.preventDefault();
                await postData();
        };

        return (
        <div className='register'>
            <h1 className='register-title'>Create an account</h1>
            {error && <p className="error-message">{error}</p>}
            <Form 
                type='register'
                fields={registerFields}
                values={values}
                onChange={handleChange}
                onSubmit={handleSubmit}
                submitLabel={loading ? 'Registering...' : 'Register'}
            />
            <p>Already have an account? <a href='/login'>Login</a></p>
        </div>
    );
};

export default Register;
