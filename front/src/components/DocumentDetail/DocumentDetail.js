import React, { useEffect, useState, useRef } from 'react';
import api from '../../api';
import io from 'socket.io-client';
import './DocumentDetail.css';

// Import the send icon
import SendIcon from '../../assets/send-icon.png';

function DocumentDetail({ docId }) {
    const [doc, setDoc] = useState(null);
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const textareaRef = useRef(null);
    const socket = io("http://localhost:5000");

    useEffect(() => {
        if (!docId) return;
        fetchDocDetail(docId);
    }, [docId]);

    useEffect(() => {
        // Listen for task_update event and update the answer state
        socket.on("task_update", (data) => {
            if (data && data.message) {
                setAnswer(data.message);
            }
        });

        // Clean up on unmount
        return () => {
            socket.off("task_update");
        };
    }, [socket]);

    const fetchDocDetail = async (id) => {
        try {
            const token = localStorage.getItem('token');
            const response = await api.get(`/documents/${id}`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            setDoc(response.data);
        } catch (error) {
            console.error('Error fetching document details:', error);
        }
    };

    const autoResize = (elem) => {
        elem.style.height = 'auto';
        elem.style.height = `${elem.scrollHeight}px`;
    };

    const handleQuestionChange = (e) => {
        setQuestion(e.target.value);
        if (textareaRef.current) {
            autoResize(textareaRef.current);
        }
    };

    const handleAskQuestion = async () => {
        if (!question.trim()) return;
        try {
            const token = localStorage.getItem('token');
            const response = await api.post(
                `/ai/documents/${docId}/ask`,
                { question },
                {
                    headers: { Authorization: `Bearer ${token}` },
                }
            );
            const taskId = response.data.task_id;
            setAnswer(`Task sent. Task ID: ${taskId}. Waiting for answer...`);
        } catch (error) {
            console.error('Error asking question:', error);
            setAnswer('Error generating an answer. Please try again.');
        }
        setQuestion('');
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleAskQuestion();
        }
    };

    if (!doc) {
        return <div className="doc-detail-container-unique-id">Loading...</div>;
    }

    return (
        <div className="doc-detail-wrapper-unique-id">
            <div className="doc-detail-container-unique-id">
                <h2 className="doc-detail-title-unique-id">{doc.original_filename}</h2>
                <div className="doc-detail-section-unique-id summary-section-unique-id">
                    <h3>Summary:</h3>
                    <p>{doc.summary || 'No summary available.'}</p>
                </div>
                <div className="doc-detail-section-unique-id answer-section-unique-id">
                    <h3>Answer:</h3>
                    <p>{answer || 'Ask me something...'}</p>
                </div>
            </div>
            <div className="doc-detail-askbar-unique-id">
                <div className="doc-detail-askbar-inner-unique-id">
                    <textarea
                        ref={textareaRef}
                        className="doc-detail-textarea-unique-id"
                        value={question}
                        onChange={handleQuestionChange}
                        onKeyDown={handleKeyDown}
                        placeholder="Type your question here..."
                    />
                    <button className="doc-detail-ask-button-unique-id" onClick={handleAskQuestion}>
                        <img src={SendIcon} alt="Send" className="doc-detail-send-icon-unique-id" />
                    </button>
                </div>
            </div>
        </div>
    );
}

export default DocumentDetail;
