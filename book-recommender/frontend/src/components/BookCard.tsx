/**
 * Book card component for displaying book information.
 */
import React from 'react';
import { Recommendation, LibraryAvailability } from '../services/api';

interface BookCardProps {
  book: Recommendation;
  onStartReading?: (bookId: number) => void;
  onAddToList?: (bookId: number) => void;
}

const BookCard: React.FC<BookCardProps> = ({ book, onStartReading, onAddToList }) => {
  const { title, author, reason, cover_url, library_availability, book_id } = book;

  return (
    <div className="book-card">
      <div className="book-card-image">
        {cover_url ? (
          <img src={cover_url} alt={title} />
        ) : (
          <div className="book-placeholder">No Cover</div>
        )}
      </div>

      <div className="book-card-content">
        <h3 className="book-title">{title}</h3>
        <p className="book-author">by {author}</p>

        <p className="book-reason">{reason}</p>

        {library_availability && (
          <div className="library-info">
            {library_availability.available ? (
              <>
                <span className="availability-badge available">
                  ✓ Available at {library_availability.library_system}
                </span>
                <div className="formats">
                  {library_availability.formats.map((format, idx) => (
                    <span key={idx} className="format-badge">{format}</span>
                  ))}
                </div>
                {library_availability.catalog_url && (
                  <a
                    href={library_availability.catalog_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="catalog-link"
                  >
                    View in Catalog →
                  </a>
                )}
              </>
            ) : (
              <span className="availability-badge unavailable">
                Not available at library
              </span>
            )}
          </div>
        )}

        <div className="book-actions">
          {book_id && onStartReading && (
            <button onClick={() => onStartReading(book_id)} className="btn btn-primary">
              Start Reading
            </button>
          )}
          {book_id && onAddToList && (
            <button onClick={() => onAddToList(book_id)} className="btn btn-secondary">
              Add to List
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default BookCard;
