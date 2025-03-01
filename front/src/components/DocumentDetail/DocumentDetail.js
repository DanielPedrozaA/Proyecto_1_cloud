import React, { useEffect, useState, useRef } from 'react';
import api from '../../api';
import './DocumentDetail.css';

// Import the send icon
import SendIcon from '../../assets/send-icon.png';

function DocumentDetail({ docId }) {
    const [doc, setDoc] = useState(null);

    // We'll store the user’s question and the AI-generated answer here
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');

    // Ref for the auto-resizing text area
    const textareaRef = useRef(null);

    useEffect(() => {
        if (!docId) return;
        fetchDocDetail(docId);
    }, [docId]);

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

    // Auto-resize the text area as the user types
    const autoResize = (elem) => {
        elem.style.height = 'auto'; // reset
        elem.style.height = `${elem.scrollHeight}px`; // grow to fit content
    };

    const handleQuestionChange = (e) => {
        setQuestion(e.target.value);
        if (textareaRef.current) {
            autoResize(textareaRef.current);
        }
    };

    // Send the question to the backend
    const handleAskQuestion = async () => {
        if (!question.trim()) return;

        try {
            const token = localStorage.getItem('token');
            // Example: POST /documents/<docId>/ask
            const response = await api.post(
                `/documents/${docId}/ask`,
                { question },
                {
                    headers: { Authorization: `Bearer ${token}` },
                }
            );
            // Suppose the response includes { answer: "..." }
            setAnswer(response.data.answer || 'No answer received.');
        } catch (error) {
            console.error('Error asking question:', error);
            setAnswer('Error generating an answer. Please try again.');
        }
        // Clear the question and reset textarea height
        setQuestion('');
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }
    };

    // Send on Enter (without Shift)
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
            {/* Main content (Summary & Answer) */}
            <div className="doc-detail-container-unique-id">
                <h2 className="doc-detail-title-unique-id">{doc.original_filename}</h2>

                {/* Summary Section */}
                <div className="doc-detail-section-unique-id summary-section-unique-id">
                    <h3>Summary:</h3>
                    <p>{doc.summary || 'No summary available.'}</p>
                </div>

                {/* Answer Section displays the AI-generated answer */}
                <div className="doc-detail-section-unique-id answer-section-unique-id">
                    <h3>Answer:</h3>
                    <p>{answer || 'Placeholder for the answer (not provided by backend yet).'}</p>
                </div>
            </div>

            {/* Pinned "ask bar" at the bottom of the screen */}
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
