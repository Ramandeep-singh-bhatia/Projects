import { useState, useEffect } from 'react';
import { voiceNoteService } from '../services/api';
import { VoiceNote, VoiceNoteStats } from '../types';

const VoiceNotesPage = () => {
  const [voiceNotes, setVoiceNotes] = useState<VoiceNote[]>([]);
  const [stats, setStats] = useState<VoiceNoteStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedNote, setSelectedNote] = useState<VoiceNote | null>(null);
  const [showRecordModal, setShowRecordModal] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  useEffect(() => {
    loadVoiceNotes();
    loadStats();
  }, []);

  const loadVoiceNotes = async () => {
    try {
      const response = await voiceNoteService.getAll();
      setVoiceNotes(response.data);
    } catch (error) {
      console.error('Error loading voice notes:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await voiceNoteService.getAnalytics();
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      loadVoiceNotes();
      return;
    }

    try {
      const response = await voiceNoteService.search(searchTerm);
      setVoiceNotes(response.data);
    } catch (error) {
      console.error('Error searching:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this voice note?')) return;

    try {
      await voiceNoteService.delete(id);
      loadVoiceNotes();
      loadStats();
    } catch (error) {
      console.error('Error deleting voice note:', error);
    }
  };

  const handleDownload = async (id: number) => {
    try {
      const response = await voiceNoteService.downloadAudio(id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `voice-note-${id}.mp3`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading audio:', error);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div className="max-w-7xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Voice Notes</h1>
        <button
          onClick={() => setShowRecordModal(true)}
          className="btn btn-primary"
        >
          🎤 Record Voice Note
        </button>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="card">
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Notes</div>
            <div className="text-2xl font-bold">{stats.totalVoiceNotes}</div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Duration</div>
            <div className="text-2xl font-bold">{formatDuration(stats.totalDuration)}</div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-600 dark:text-gray-400">Storage Used</div>
            <div className="text-2xl font-bold">{formatFileSize(stats.totalFileSize)}</div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-600 dark:text-gray-400">Avg Duration</div>
            <div className="text-2xl font-bold">{formatDuration(stats.averageDuration)}</div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-600 dark:text-gray-400">Transcribed</div>
            <div className="text-2xl font-bold text-green-600">{stats.transcribedCount}</div>
          </div>
        </div>
      )}

      {/* Search */}
      <div className="card mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            className="input flex-1"
            placeholder="Search transcriptions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch} className="btn btn-primary">Search</button>
        </div>
      </div>

      {/* Voice Notes List */}
      <div className="space-y-4">
        {voiceNotes.map(note => (
          <div key={note.id} className="card hover:shadow-lg transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold mb-1">
                  {note.title || `Voice Note - ${new Date(note.recordedDate!).toLocaleDateString()}`}
                </h3>
                <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  <div>Recorded: {new Date(note.recordedDate!).toLocaleString()}</div>
                  <div>Duration: {formatDuration(note.duration || 0)} • Size: {formatFileSize(note.fileSize || 0)}</div>
                  {note.tags && note.tags.length > 0 && (
                    <div className="flex gap-2 mt-2">
                      {note.tags.map((tag, idx) => (
                        <span key={idx} className="text-xs px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 rounded">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                {note.transcribed && (
                  <span className="text-xs px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900 rounded">
                    Transcribed
                  </span>
                )}
              </div>
            </div>

            {note.transcription && (
              <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded">
                <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-1">Transcription:</div>
                <div className="text-sm line-clamp-3">{note.transcription}</div>
              </div>
            )}

            {note.summary && (
              <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900 rounded">
                <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-1">Summary:</div>
                <div className="text-sm">{note.summary}</div>
              </div>
            )}

            <div className="flex gap-2">
              <button
                onClick={() => setSelectedNote(note)}
                className="btn btn-primary text-sm"
              >
                View Details
              </button>
              <button
                onClick={() => handleDownload(note.id!)}
                className="btn btn-secondary text-sm"
              >
                Download Audio
              </button>
              {note.topic && (
                <span className="text-sm px-3 py-2 bg-gray-100 dark:bg-gray-700 rounded">
                  Linked to topic
                </span>
              )}
              <button
                onClick={() => handleDelete(note.id!)}
                className="btn btn-danger text-sm ml-auto"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {voiceNotes.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No voice notes yet. Record your first voice note to get started!
        </div>
      )}

      {/* Record Modal */}
      {showRecordModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold mb-4">Record Voice Note</h2>

            <div className="text-center py-8">
              {!isRecording ? (
                <>
                  <div className="text-6xl mb-4">🎤</div>
                  <p className="text-gray-600 dark:text-gray-400 mb-6">
                    Note: Voice recording with Web Speech API requires browser support.
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                    Full implementation would integrate with browser's MediaRecorder API
                    and Web Speech API for real-time transcription.
                  </p>
                  <button
                    onClick={() => {
                      alert('This is a demo. Full voice recording would be implemented with MediaRecorder API.');
                      setShowRecordModal(false);
                    }}
                    className="btn btn-primary"
                  >
                    Start Recording (Demo)
                  </button>
                </>
              ) : (
                <>
                  <div className="text-6xl mb-4 animate-pulse">🔴</div>
                  <p className="text-xl font-semibold mb-2">Recording...</p>
                  <p className="text-gray-600 dark:text-gray-400 mb-6">0:00</p>
                  <button
                    onClick={() => setIsRecording(false)}
                    className="btn btn-danger"
                  >
                    Stop Recording
                  </button>
                </>
              )}
            </div>

            <button
              onClick={() => setShowRecordModal(false)}
              className="btn btn-secondary w-full mt-4"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* View Details Modal */}
      {selectedNote && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-2xl font-bold">Voice Note Details</h2>
              <button
                onClick={() => setSelectedNote(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <div className="text-sm font-semibold text-gray-600 dark:text-gray-400">Title</div>
                <div>{selectedNote.title || `Voice Note - ${new Date(selectedNote.recordedDate!).toLocaleDateString()}`}</div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-400">Duration</div>
                  <div>{formatDuration(selectedNote.duration || 0)}</div>
                </div>
                <div>
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-400">File Size</div>
                  <div>{formatFileSize(selectedNote.fileSize || 0)}</div>
                </div>
                <div>
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-400">Recorded</div>
                  <div>{new Date(selectedNote.recordedDate!).toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-400">Transcribed</div>
                  <div>{selectedNote.transcribed ? 'Yes' : 'No'}</div>
                </div>
              </div>

              {selectedNote.transcription && (
                <div>
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Transcription</div>
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded">{selectedNote.transcription}</div>
                </div>
              )}

              {selectedNote.summary && (
                <div>
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Summary</div>
                  <div className="p-4 bg-blue-50 dark:bg-blue-900 rounded">{selectedNote.summary}</div>
                </div>
              )}

              {selectedNote.tags && selectedNote.tags.length > 0 && (
                <div>
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Tags</div>
                  <div className="flex gap-2 flex-wrap">
                    {selectedNote.tags.map((tag, idx) => (
                      <span key={idx} className="text-sm px-3 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex gap-2 pt-4">
                <button
                  onClick={() => handleDownload(selectedNote.id!)}
                  className="btn btn-primary flex-1"
                >
                  Download Audio
                </button>
                <button
                  onClick={() => setSelectedNote(null)}
                  className="btn btn-secondary flex-1"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceNotesPage;
