import React, { useState } from 'react';
import { Container, Row, Col, Form, Button, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import LogoAi from '../../assets/Logo_Negro_Cloud.png';
import './Login.css';
import api from '../../api';

function Login() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({ username: '', password: '' });
    const [error, setError] = useState('');

    // Handle form input changes
    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault();

        // Basic validation for missing values
        if (!formData.username || !formData.password) {
            setError('Please enter both username and password.');
            return;
        }

        try {
            // Make the login request. Adjust the URL if your blueprint is mounted with a prefix.
            const response = await api.post('/auth/login', formData);
            const { access_token, refresh_token, usuario } = response.data;

            // Save tokens (and user data if needed) in localStorage
            localStorage.setItem('token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
            localStorage.setItem('userId', usuario);

            // Clear error and navigate to dashboard
            setError('');
            navigate('/dashboard');
        } catch (err) {
            // Handle error response from backend
            if (err.response && err.response.data && err.response.data.mensaje) {
                setError(err.response.data.mensaje);
            } else {
                setError('An error occurred. Please try again.');
            }
        }
    };

    return (
        <Container fluid className="login-container">
            <Row className="login-row g-0">
                <Col md={8} className="login-form-col">
                    <div className="login-form-wrapper">
                        {/* Logo */}
                        <div className="logo-container">
                            <img src={LogoAi} alt="Logo" className="logo" />
                        </div>
                        <h1 className="login-title">Login to Your Account</h1>
                        <p className="login-subtitle">Enter your username and password</p>
                        {error && <Alert variant="danger">{error}</Alert>}
                        {/* Login Form */}
                        <Form onSubmit={handleSubmit}>
                            <Form.Group controlId="formBasicUsername">
                                <Form.Control
                                    type="text"
                                    placeholder="Username"
                                    className="rounded-input"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleChange}
                                />
                            </Form.Group>

                            <Form.Group controlId="formBasicPassword" className="mt-3">
                                <Form.Control
                                    type="password"
                                    placeholder="Password"
                                    className="rounded-input"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                />
                            </Form.Group>

                            <Button
                                variant="primary"
                                type="submit"
                                className="mt-4 rounded-button login-button"
                            >
                                Sign In
                            </Button>
                        </Form>
                    </div>
                </Col>

                <Col md={4} className="signup-col">
                    <div className="signup-wrapper">
                        <h2>New Here?</h2>
                        <p>Sign up and analize all the text you want!</p>
                        <Button
                            variant="outline-light"
                            className="mt-4 rounded-button signup-button"
                            onClick={() => navigate('/signup')}
                        >
                            Sign Up
                        </Button>
                    </div>
                </Col>
            </Row>
        </Container>
    );
}

export default Login;
