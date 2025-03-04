import React, { useEffect, useState, useRef } from 'react';
import api from '../../api';
import io from 'socket.io-client';
import './DocumentDetail.css';

// Import the send icon and loading GIF
import SendIcon from '../../assets/send-icon.png';
import LoadingCat from '../../assets/loading_cat.gif';

function DocumentDetail({ docId }) {
    const [doc, setDoc] = useState(null);
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);
    // Use a ref to track the last task type ("question" or "summary")
    const lastTaskTypeRef = useRef(null);

    const textareaRef = useRef(null);

    // Create socket connection to your AI backend
    const socket = io("http://localhost:5000");

    useEffect(() => {
        if (!docId) return;
        fetchDocDetail(docId);
    }, [docId]);

    // Listen for AI answers via "task_update"
    useEffect(() => {
        socket.on("task_update", (data) => {
            if (data && data.message) {
                if (lastTaskTypeRef.current === "summary") {
                    // Update the summary in the doc object
                    setDoc((prevDoc) => ({
                        ...prevDoc,
                        summary: data.message,
                    }));
                } else if (lastTaskTypeRef.current === "question") {
                    // Update the answer box
                    setAnswer(data.message);
                }
                setLoading(false);
            }
        });
        return () => {
            socket.off("task_update");
        };
    }, [socket]);

    // Fetch the document details from the backend
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

    // Auto-resize the textarea as the user types
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

    // Send a normal question and update the Answer section
    const handleAskQuestion = async () => {
        if (!question.trim()) return;
        setLoading(true);
        lastTaskTypeRef.current = "question"; // Set last task type as question
        try {
            const token = localStorage.getItem('token');
            await api.post(
                `/ai/documents/${docId}/ask`,
                { question },
                {
                    headers: { Authorization: `Bearer ${token}` },
                }
            );
            setAnswer("Waiting for answer...");
        } catch (error) {
            console.error('Error asking question:', error);
            setAnswer("Error generating an answer. Please try again.");
            setLoading(false);
        }
        setQuestion('');
    };

    // Send a summary prompt and update the Summary section (doc.summary)
    const handleGenerateSummary = async () => {
        setLoading(true);
        lastTaskTypeRef.current = "summary"; // Set last task type as summary
        try {
            const token = localStorage.getItem('token');
            await api.post(
                `/ai/documents/${docId}/ask`,
                { question: "Please summarize the entire document" },
                {
                    headers: { Authorization: `Bearer ${token}` },
                }
            );
            // Update the doc summary placeholder instead of updating the Answer box
            setDoc((prevDoc) => ({
                ...prevDoc,
                summary: "Waiting for summary..."
            }));
        } catch (error) {
            console.error('Error generating summary:', error);
            setAnswer("Error generating summary. Please try again.");
            setLoading(false);
        }
    };

    // Send question on Enter (without Shift)
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
        <>
            {loading && (
                <div className="loading-overlay">
                    <img src={LoadingCat} alt="Loading..." className="loading-cat" />
                </div>
            )}
            <div className="doc-detail-wrapper-unique-id">
                <div className="doc-detail-container-unique-id">
                    <h2 className="doc-detail-title-unique-id">{doc.original_filename}</h2>

                    {/* Summary Section */}
                    <div className="doc-detail-section-unique-id summary-section-unique-id">
                        <h3>Summary:</h3>
                        <p>{doc.summary || 'No summary available.'}</p>
                        {/* Button to generate summary */}
                        <button onClick={handleGenerateSummary}>
                            Generate Summary
                        </button>
                    </div>

                    {/* Answer Section */}
                    <div className="doc-detail-section-unique-id answer-section-unique-id">
                        <h3>Answer:</h3>
                        <p>{answer || 'Ask me something...'}</p>
                    </div>
                </div>

                {/* Ask Bar at the bottom */}
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
        </>
    );
}

export default DocumentDetail;
