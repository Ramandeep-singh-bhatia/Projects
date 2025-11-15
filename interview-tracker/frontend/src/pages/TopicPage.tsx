import { useState, useEffect } from 'react';
import { topicService, sessionService, fileService } from '../services/api';
import { Topic, TopicCategory, PracticeSession, SessionType, DifficultyLevel } from '../types';

interface TopicPageProps {
  category: TopicCategory;
}

const TopicPage = ({ category }: TopicPageProps) => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTopic, setEditingTopic] = useState<Topic | null>(null);
  const [showSessionModal, setShowSessionModal] = useState(false);
  const [selectedTopicId, setSelectedTopicId] = useState<number | null>(null);

  const loadTopics = async () => {
    try {
      const response = await topicService.getAll(category.toLowerCase());
      setTopics(response.data);
    } catch (error) {
      console.error('Error loading topics:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTopics();
  }, [category]);

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this topic?')) {
      try {
        await topicService.delete(category.toLowerCase(), id);
        loadTopics();
      } catch (error) {
        console.error('Error deleting topic:', error);
      }
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 8) return 'bg-green-500';
    if (confidence >= 5) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">{category} Topics</h1>
        <button
          onClick={() => { setEditingTopic(null); setShowModal(true); }}
          className="btn btn-primary"
        >
          + Add New Topic
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8">Loading...</div>
      ) : topics.length === 0 ? (
        <div className="card text-center py-8 text-gray-500">
          No topics yet. Create your first topic to get started!
        </div>
      ) : (
        <div className="grid gap-4">
          {topics.map((topic) => (
            <div key={topic.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold">{topic.topic}</h3>
                    {topic.subtopic && (
                      <span className="text-sm text-gray-500">({topic.subtopic})</span>
                    )}
                    <div className="flex items-center gap-2">
                      <div className={`w-24 h-2 rounded-full ${getConfidenceColor(topic.confidence)}`}></div>
                      <span className="text-sm font-medium">{topic.confidence}/10</span>
                    </div>
                  </div>
                  <div className="flex gap-4 text-sm text-gray-600 dark:text-gray-400">
                    <span>⏱️ {topic.totalTimeSpent || 0} mins</span>
                    <span>📝 {topic.sessionCount || 0} sessions</span>
                    <span>🕒 {formatDate(topic.lastStudiedDate)}</span>
                    {(topic as any).difficulty && (
                      <span className={`px-2 py-1 rounded ${
                        (topic as any).difficulty === 'EASY' ? 'bg-green-100 text-green-800' :
                        (topic as any).difficulty === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {(topic as any).difficulty}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => { setSelectedTopicId(topic.id!); setShowSessionModal(true); }}
                    className="btn btn-primary text-sm"
                  >
                    Practice
                  </button>
                  <button
                    onClick={() => { setEditingTopic(topic); setShowModal(true); }}
                    className="btn btn-secondary text-sm"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(topic.id!)}
                    className="btn btn-danger text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <TopicModal
          category={category}
          topic={editingTopic}
          onClose={() => setShowModal(false)}
          onSave={() => { setShowModal(false); loadTopics(); }}
        />
      )}

      {showSessionModal && selectedTopicId && (
        <SessionModal
          topicId={selectedTopicId}
          onClose={() => setShowSessionModal(false)}
          onSave={() => { setShowSessionModal(false); loadTopics(); }}
        />
      )}
    </div>
  );
};

// Topic Modal Component
const TopicModal = ({ category, topic, onClose, onSave }: any) => {
  const [formData, setFormData] = useState({
    topic: topic?.topic || '',
    subtopic: topic?.subtopic || '',
    confidence: topic?.confidence || 5,
    sourceUrl: topic?.sourceUrl || '',
    notes: topic?.notes || '',
    thingsToRemember: topic?.thingsToRemember || '',
    difficulty: (topic as any)?.difficulty || 'MEDIUM',
    pagesRead: (topic as any)?.pagesRead || 0,
    questionCategory: (topic as any)?.questionCategory || '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: any = {
        ...formData,
        category,
      };

      if (topic?.id) {
        await topicService.update(category.toLowerCase(), topic.id, payload);
      } else {
        await topicService.create(category.toLowerCase(), payload);
      }
      onSave();
    } catch (error) {
      console.error('Error saving topic:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">{topic ? 'Edit' : 'Add'} Topic</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">{category === 'BEHAVIORAL' ? 'Question' : 'Topic'} *</label>
            <input
              className="input"
              value={formData.topic}
              onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="label">Subtopic</label>
            <input
              className="input"
              value={formData.subtopic}
              onChange={(e) => setFormData({ ...formData, subtopic: e.target.value })}
            />
          </div>
          <div>
            <label className="label">Confidence (1-10) *</label>
            <input
              type="number"
              min="1"
              max="10"
              className="input"
              value={formData.confidence}
              onChange={(e) => setFormData({ ...formData, confidence: parseInt(e.target.value) })}
              required
            />
          </div>
          {category === 'DSA' && (
            <div>
              <label className="label">Difficulty *</label>
              <select
                className="input"
                value={formData.difficulty}
                onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                required
              >
                <option value="EASY">Easy</option>
                <option value="MEDIUM">Medium</option>
                <option value="HARD">Hard</option>
              </select>
            </div>
          )}
          {category === 'HLD' && (
            <div>
              <label className="label">Pages Read</label>
              <input
                type="number"
                min="0"
                className="input"
                value={formData.pagesRead}
                onChange={(e) => setFormData({ ...formData, pagesRead: parseInt(e.target.value) })}
              />
            </div>
          )}
          {category === 'BEHAVIORAL' && (
            <div>
              <label className="label">Question Category *</label>
              <input
                className="input"
                value={formData.questionCategory}
                onChange={(e) => setFormData({ ...formData, questionCategory: e.target.value })}
                placeholder="e.g., Leadership, Conflict Resolution, Teamwork"
                required
              />
            </div>
          )}
          <div>
            <label className="label">Source URL</label>
            <input
              type="url"
              className="input"
              value={formData.sourceUrl}
              onChange={(e) => setFormData({ ...formData, sourceUrl: e.target.value })}
            />
          </div>
          <div>
            <label className="label">Notes</label>
            <textarea
              className="input"
              rows={3}
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            />
          </div>
          <div>
            <label className="label">Things to Remember</label>
            <textarea
              className="input"
              rows={3}
              value={formData.thingsToRemember}
              onChange={(e) => setFormData({ ...formData, thingsToRemember: e.target.value })}
            />
          </div>
          <div className="flex gap-2 justify-end">
            <button type="button" onClick={onClose} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">Save</button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Session Modal Component
const SessionModal = ({ topicId, onClose, onSave }: any) => {
  const [formData, setFormData] = useState({
    duration: 30,
    performanceRating: 5,
    whatWentWell: '',
    mistakesMade: '',
    sessionNotes: '',
    sessionType: 'REVISION' as SessionType,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await sessionService.create(topicId, formData);
      onSave();
    } catch (error) {
      console.error('Error saving session:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">Log Practice Session</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Duration (minutes) *</label>
            <input
              type="number"
              min="1"
              className="input"
              value={formData.duration}
              onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) })}
              required
            />
          </div>
          <div>
            <label className="label">Performance Rating (1-10) *</label>
            <input
              type="number"
              min="1"
              max="10"
              className="input"
              value={formData.performanceRating}
              onChange={(e) => setFormData({ ...formData, performanceRating: parseInt(e.target.value) })}
              required
            />
          </div>
          <div>
            <label className="label">Session Type *</label>
            <select
              className="input"
              value={formData.sessionType}
              onChange={(e) => setFormData({ ...formData, sessionType: e.target.value as SessionType })}
              required
            >
              <option value="FIRST_LEARNING">First Learning</option>
              <option value="REVISION">Revision</option>
              <option value="MOCK_INTERVIEW">Mock Interview</option>
              <option value="QUICK_REVIEW">Quick Review</option>
            </select>
          </div>
          <div>
            <label className="label">What Went Well</label>
            <textarea
              className="input"
              rows={2}
              value={formData.whatWentWell}
              onChange={(e) => setFormData({ ...formData, whatWentWell: e.target.value })}
            />
          </div>
          <div>
            <label className="label">Mistakes Made / Areas to Improve</label>
            <textarea
              className="input"
              rows={2}
              value={formData.mistakesMade}
              onChange={(e) => setFormData({ ...formData, mistakesMade: e.target.value })}
            />
          </div>
          <div>
            <label className="label">Session Notes</label>
            <textarea
              className="input"
              rows={2}
              value={formData.sessionNotes}
              onChange={(e) => setFormData({ ...formData, sessionNotes: e.target.value })}
            />
          </div>
          <div className="flex gap-2 justify-end">
            <button type="button" onClick={onClose} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">Save Session</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TopicPage;
