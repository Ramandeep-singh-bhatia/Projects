/**
 * Add/Evaluate Book Modal - Unified interface for adding books and evaluation
 */
import React, { useState } from 'react';
import axios from 'axios';

interface AddBookModalProps {
  isOpen: boolean;
  onClose: () => void;
  onBookAdded?: (bookId: number) => void;
}

type AddMode = 'search' | 'isbn' | 'manual';

const AddBookModal: React.FC<AddBookModalProps> = ({ isOpen, onClose, onBookAdded }) => {
  const [mode, setMode] = useState<AddMode>('search');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form fields
  const [searchQuery, setSearchQuery] = useState('');
  const [isbn, setIsbn] = useState('');
  const [manualData, setManualData] = useState({
    title: '',
    author: '',
    genre: '',
    isbn: '',
    page_count: '',
    description: ''
  });

  // Metadata
  const [source, setSource] = useState('manual');
  const [recommenderName, setRecommenderName] = useState('');
  const [whyRead, setWhyRead] = useState('');
  const [evaluateAfterAdd, setEvaluateAfterAdd] = useState(true);

  const resetForm = () => {
    setSearchQuery('');
    setIsbn('');
    setManualData({
      title: '',
      author: '',
      genre: '',
      isbn: '',
      page_count: '',
      description: ''
    });
    setRecommenderName('');
    setWhyRead('');
    setError(null);
    setSuccess(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleQuickAddBySearch = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/manual/quick-add/search`,
        null,
        {
          params: {
            query: searchQuery,
            source,
            recommender_name: recommenderName || undefined,
            why_read: whyRead || undefined
          }
        }
      );

      const bookId = response.data.book_id;
      setSuccess(`Book added successfully: ${response.data.book_data.title}`);

      if (evaluateAfterAdd) {
        await handleEvaluateBook(bookId);
      }

      if (onBookAdded) {
        onBookAdded(bookId);
      }

      setTimeout(handleClose, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add book');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAddByISBN = async () => {
    if (!isbn.trim()) {
      setError('Please enter an ISBN');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/manual/quick-add/isbn/${isbn}`,
        null,
        {
          params: {
            source,
            recommender_name: recommenderName || undefined,
            why_read: whyRead || undefined
          }
        }
      );

      const bookId = response.data.book_id;
      setSuccess(`Book added successfully: ${response.data.book_data.title}`);

      if (evaluateAfterAdd) {
        await handleEvaluateBook(bookId);
      }

      if (onBookAdded) {
        onBookAdded(bookId);
      }

      setTimeout(handleClose, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add book');
    } finally {
      setIsLoading(false);
    }
  };

  const handleManualAdd = async () => {
    if (!manualData.title.trim() || !manualData.author.trim()) {
      setError('Title and author are required');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/manual/add-book`,
        {
          book_data: {
            title: manualData.title,
            author: manualData.author,
            genre: manualData.genre || 'Unknown',
            isbn: manualData.isbn || null,
            page_count: manualData.page_count ? parseInt(manualData.page_count) : null,
            description: manualData.description || null
          },
          source,
          recommender_name: recommenderName || null,
          why_read: whyRead || null,
          auto_analyze: true
        }
      );

      const bookId = response.data.book_id;
      setSuccess('Book added successfully!');

      if (evaluateAfterAdd) {
        await handleEvaluateBook(bookId);
      }

      if (onBookAdded) {
        onBookAdded(bookId);
      }

      setTimeout(handleClose, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add book');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEvaluateBook = async (bookId: number) => {
    try {
      const evalResponse = await axios.post(
        `${process.env.REACT_APP_API_URL}/manual/evaluate/${bookId}`
      );

      const evaluation = evalResponse.data.evaluation;

      // If not ready, show option to add to future reads
      if (evaluation.recommendation_type !== 'read_now') {
        const addToFuture = window.confirm(
          `Readiness Score: ${evaluation.readiness_score}/100\n\n` +
          `${evaluation.detailed_reasoning}\n\n` +
          'Add to Future Reads for later?'
        );

        if (addToFuture) {
          await axios.post(`${process.env.REACT_APP_API_URL}/manual/future-reads/add`, {
            book_id: bookId,
            user_notes: whyRead
          }, {
            params: { evaluation_data: evaluation }
          });

          setSuccess('Added to Future Reads! You\'ll be notified when ready.');
        }
      } else {
        alert(`🎉 You're ready to read this book!\n\nReadiness Score: ${evaluation.readiness_score}/100\n\n${evaluation.detailed_reasoning}`);
      }
    } catch (err) {
      console.error('Evaluation failed:', err);
    }
  };

  const handleSubmit = () => {
    switch (mode) {
      case 'search':
        handleQuickAddBySearch();
        break;
      case 'isbn':
        handleQuickAddByISBN();
        break;
      case 'manual':
        handleManualAdd();
        break;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content add-book-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Add a Book</h2>
          <button className="modal-close" onClick={handleClose}>&times;</button>
        </div>

        {/* Mode Selector */}
        <div className="add-mode-selector">
          <button
            className={`mode-btn ${mode === 'search' ? 'active' : ''}`}
            onClick={() => setMode('search')}
          >
            Search
          </button>
          <button
            className={`mode-btn ${mode === 'isbn' ? 'active' : ''}`}
            onClick={() => setMode('isbn')}
          >
            ISBN/Barcode
          </button>
          <button
            className={`mode-btn ${mode === 'manual' ? 'active' : ''}`}
            onClick={() => setMode('manual')}
          >
            Manual Entry
          </button>
        </div>

        <div className="modal-body">
          {/* Search Mode */}
          {mode === 'search' && (
            <div className="form-group">
              <label>Search by Title or Author</label>
              <input
                type="text"
                className="form-control"
                placeholder="Enter book title or author..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                disabled={isLoading}
              />
            </div>
          )}

          {/* ISBN Mode */}
          {mode === 'isbn' && (
            <div className="form-group">
              <label>ISBN or Barcode</label>
              <input
                type="text"
                className="form-control"
                placeholder="Enter ISBN..."
                value={isbn}
                onChange={e => setIsbn(e.target.value)}
                disabled={isLoading}
              />
            </div>
          )}

          {/* Manual Mode */}
          {mode === 'manual' && (
            <>
              <div className="form-group">
                <label>Title *</label>
                <input
                  type="text"
                  className="form-control"
                  value={manualData.title}
                  onChange={e => setManualData({ ...manualData, title: e.target.value })}
                  disabled={isLoading}
                />
              </div>
              <div className="form-group">
                <label>Author *</label>
                <input
                  type="text"
                  className="form-control"
                  value={manualData.author}
                  onChange={e => setManualData({ ...manualData, author: e.target.value })}
                  disabled={isLoading}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Genre</label>
                  <input
                    type="text"
                    className="form-control"
                    value={manualData.genre}
                    onChange={e => setManualData({ ...manualData, genre: e.target.value })}
                    disabled={isLoading}
                  />
                </div>
                <div className="form-group">
                  <label>Page Count</label>
                  <input
                    type="number"
                    className="form-control"
                    value={manualData.page_count}
                    onChange={e => setManualData({ ...manualData, page_count: e.target.value })}
                    disabled={isLoading}
                  />
                </div>
              </div>
            </>
          )}

          {/* Metadata Section */}
          <div className="metadata-section">
            <h4>Additional Info (Optional)</h4>

            <div className="form-group">
              <label>How did you find this book?</label>
              <select
                className="form-control"
                value={source}
                onChange={e => setSource(e.target.value)}
                disabled={isLoading}
              >
                <option value="manual">Just browsing</option>
                <option value="friend">Friend recommendation</option>
                <option value="online">Found online</option>
                <option value="bookstore">Saw in bookstore</option>
                <option value="other">Other</option>
              </select>
            </div>

            {(source === 'friend' || source === 'online') && (
              <div className="form-group">
                <label>Who recommended it?</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Person or source name..."
                  value={recommenderName}
                  onChange={e => setRecommenderName(e.target.value)}
                  disabled={isLoading}
                />
              </div>
            )}

            <div className="form-group">
              <label>Why do you want to read this?</label>
              <textarea
                className="form-control"
                placeholder="Optional notes..."
                value={whyRead}
                onChange={e => setWhyRead(e.target.value)}
                rows={2}
                disabled={isLoading}
              />
            </div>

            <div className="form-check">
              <input
                type="checkbox"
                id="evaluate-checkbox"
                checked={evaluateAfterAdd}
                onChange={e => setEvaluateAfterAdd(e.target.checked)}
                disabled={isLoading}
              />
              <label htmlFor="evaluate-checkbox">
                Evaluate if I'm ready to read this now
              </label>
            </div>
          </div>

          {error && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={handleClose} disabled={isLoading}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={isLoading}>
            {isLoading ? 'Adding...' : 'Add Book'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddBookModal;
