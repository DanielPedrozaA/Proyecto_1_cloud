// src/components/Signup/Signup.js
import React, { useState } from 'react';
import { Container, Form, Button, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import LogoAi from '../../assets/Logo_Negro_Cloud.png';
import './Signup.css';
import api from '../../api';

function Signup() {
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Basic client-side validation
        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }
        setError("");

        try {
            // Call the register endpoint; adjust if your blueprint prefix changes
            const response = await api.post('/auth/register', { username, email, password });
            if (response.status === 201) {
                setSuccess("Usuario creado exitosamente. Redirigiendo al login...");
                // Redirect after a short delay so the user can see the success message
                setTimeout(() => {
                    navigate('/login');
                }, 2000);
            }
        } catch (err) {
            if (err.response && err.response.data && err.response.data.mensaje) {
                setError(err.response.data.mensaje);
            } else {
                setError("An error occurred. Please try again.");
            }
        }
    };

    return (
        <Container fluid className="signup-container">
            <div className="signup-card">
                <div className="text-center mb-4">
                    <img src={LogoAi} alt="Logo" className="mb-3 signup-logo" />
                    <h1 className="signup-title">Create an Account</h1>
                </div>
                {error && <Alert variant="danger">{error}</Alert>}
                {success && <Alert variant="success">{success}</Alert>}
                <Form onSubmit={handleSubmit}>
                    <Form.Group controlId="formUsername" className="mb-3">
                        <Form.Control
                            type="text"
                            placeholder="Username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="rounded-input"
                            required
                        />
                    </Form.Group>
                    <Form.Group controlId="formEmail" className="mb-3">
                        <Form.Control
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="rounded-input"
                            required
                        />
                    </Form.Group>
                    <Form.Group controlId="formPassword" className="mb-3">
                        <Form.Control
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="rounded-input"
                            required
                        />
                    </Form.Group>
                    <Form.Group controlId="formConfirmPassword" className="mb-3">
                        <Form.Control
                            type="password"
                            placeholder="Confirm Password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            className="rounded-input"
                            required
                        />
                    </Form.Group>
                    <Button variant="primary" type="submit" className="w-100 rounded-button signup-button mb-3">
                        Sign Up
                    </Button>
                </Form>
                <Button variant="link" onClick={() => navigate('/login')}>
                    Back to Login
                </Button>
            </div>
        </Container>
    );
}

export default Signup;
