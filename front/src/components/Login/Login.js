import React from 'react';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import LogoAi from '../../assets/LogoAi.jpeg';
import './Login.css';

function Login() {
    const navigate = useNavigate(); // Initialize navigate hook

    return (
        <Container fluid className="login-container">
            <Row className="login-row g-0">
                {/* Left (White) Column */}
                <Col md={8} className="login-form-col">
                    <div className="login-form-wrapper">
                        {/* Logo */}
                        <div className="logo-container">
                            <img src={LogoAi} alt="Logo" className="logo" />
                        </div>

                        {/* Title & Subtitle */}
                        <h1 className="login-title">Login to Your Account</h1>
                        <p className="login-subtitle">Enter your username and password</p>

                        {/* Form */}
                        <Form>
                            <Form.Group controlId="formBasicUsername">
                                <Form.Control
                                    type="text"
                                    placeholder="Username"
                                    className="rounded-input"
                                />
                            </Form.Group>

                            <Form.Group controlId="formBasicPassword" className="mt-3">
                                <Form.Control
                                    type="password"
                                    placeholder="Password"
                                    className="rounded-input"
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
