import { useState, useEffect } from 'react';
import { studyPlanService } from '../services/api';
import { StudyPlan, StudyPlanItem } from '../types';

const StudyPlanPage = () => {
  const [activePlan, setActivePlan] = useState<StudyPlan | null>(null);
  const [showGenerator, setShowGenerator] = useState(false);
  const [loading, setLoading] = useState(true);

  const [formData, setFormData] = useState({
    interviewDate: '',
    daysAvailable: 30,
    hoursPerDay: 4,
    priorityFocus: 'BALANCED',
    topicSelection: 'WEAK',
  });

  useEffect(() => {
    loadActivePlan();
  }, []);

  const loadActivePlan = async () => {
    try {
      const response = await studyPlanService.getActive();
      setActivePlan(response.data);
    } catch (error) {
      console.error('Error loading plan:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    try {
      const response = await studyPlanService.generate(formData);
      setActivePlan(response.data);
      setShowGenerator(false);
      alert('Study plan generated successfully!');
    } catch (error) {
      console.error('Error generating plan:', error);
      alert('Failed to generate plan');
    }
  };

  const markComplete = async (itemId: number) => {
    const minutes = prompt('How many minutes did you spend?');
    if (minutes) {
      try {
        await studyPlanService.markItemComplete(itemId, parseInt(minutes));
        loadActivePlan();
      } catch (error) {
        console.error('Error marking complete:', error);
      }
    }
  };

  const groupItemsByDate = (items: StudyPlanItem[]) => {
    const grouped: Record<string, StudyPlanItem[]> = {};
    items?.forEach(item => {
      if (!grouped[item.scheduledDate]) {
        grouped[item.scheduledDate] = [];
      }
      grouped[item.scheduledDate].push(item);
    });
    return grouped;
  };

  const getItemTypeColor = (type: string) => {
    switch (type) {
      case 'NEW_TOPIC': return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200';
      case 'REVISION': return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200';
      case 'REST': return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
      case 'CONSOLIDATION': return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200';
      default: return 'bg-gray-100';
    }
  };

  if (loading) return <div className="text-center py-8">Loading...</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Study Plan</h1>
        <button onClick={() => setShowGenerator(!showGenerator)} className="btn btn-primary">
          {showGenerator ? 'Cancel' : '+ Generate New Plan'}
        </button>
      </div>

      {showGenerator && (
        <div className="card mb-6">
          <h2 className="text-2xl font-semibold mb-4">Generate Study Plan</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Interview Date *</label>
              <input
                type="date"
                className="input"
                value={formData.interviewDate}
                onChange={(e) => setFormData({ ...formData, interviewDate: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="label">Days Available</label>
              <input
                type="number"
                min="1"
                className="input"
                value={formData.daysAvailable}
                onChange={(e) => setFormData({ ...formData, daysAvailable: parseInt(e.target.value) })}
              />
            </div>
            <div>
              <label className="label">Hours Per Day</label>
              <input
                type="number"
                min="1"
                max="12"
                className="input"
                value={formData.hoursPerDay}
                onChange={(e) => setFormData({ ...formData, hoursPerDay: parseInt(e.target.value) })}
              />
            </div>
            <div>
              <label className="label">Priority Focus</label>
              <select
                className="input"
                value={formData.priorityFocus}
                onChange={(e) => setFormData({ ...formData, priorityFocus: e.target.value })}
              >
                <option value="BALANCED">Balanced</option>
                <option value="DSA_HEAVY">DSA Heavy (70%)</option>
                <option value="SYSTEM_DESIGN_HEAVY">System Design Heavy</option>
              </select>
            </div>
            <div>
              <label className="label">Topics to Include</label>
              <select
                className="input"
                value={formData.topicSelection}
                onChange={(e) => setFormData({ ...formData, topicSelection: e.target.value })}
              >
                <option value="ALL">All Topics</option>
                <option value="WEAK">Weak Areas Only (Confidence &lt; 6)</option>
              </select>
            </div>
          </div>
          <button onClick={handleGenerate} className="btn btn-primary mt-4">
            Generate Plan
          </button>
        </div>
      )}

      {activePlan ? (
        <div>
          <div className="card mb-6">
            <h2 className="text-xl font-semibold mb-2">{activePlan.name}</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-600 dark:text-gray-400">Interview Date:</span>
                <div className="font-medium">{new Date(activePlan.interviewDate).toLocaleDateString()}</div>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Total Topics:</span>
                <div className="font-medium">{activePlan.totalTopics || 0}</div>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Completed:</span>
                <div className="font-medium">{activePlan.completedTopics || 0}</div>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Progress:</span>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-1">
                  <div
                    className="bg-primary-600 h-2 rounded-full"
                    style={{ width: `${((activePlan.completedTopics || 0) / Math.max(activePlan.totalTopics || 1, 1)) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-2xl font-semibold mb-4">Calendar View</h2>
            <div className="space-y-6">
              {Object.entries(groupItemsByDate(activePlan.items || [])).map(([date, items]) => (
                <div key={date} className="border-l-4 border-primary-500 pl-4">
                  <h3 className="font-semibold text-lg mb-2">
                    {new Date(date).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
                  </h3>
                  <div className="space-y-2">
                    {items.map((item) => (
                      <div
                        key={item.id}
                        className={`p-3 rounded-lg ${item.completed ? 'opacity-50' : ''} ${getItemTypeColor(item.itemType)}`}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-medium">
                                {item.topic?.topic || item.itemType}
                              </span>
                              <span className="text-xs px-2 py-1 rounded bg-white dark:bg-gray-800">
                                {item.estimatedMinutes} min
                              </span>
                              {item.completed && <span className="text-xs">✓ Completed</span>}
                            </div>
                            {item.topic?.category && (
                              <div className="text-sm mt-1">{item.topic.category}</div>
                            )}
                          </div>
                          {!item.completed && item.itemType !== 'REST' && (
                            <button
                              onClick={() => markComplete(item.id!)}
                              className="btn btn-primary btn-sm"
                            >
                              Mark Complete
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="card text-center py-12">
          <h3 className="text-xl font-semibold mb-2">No Active Study Plan</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Generate a smart study plan to organize your preparation
          </p>
          <button onClick={() => setShowGenerator(true)} className="btn btn-primary">
            Generate Study Plan
          </button>
        </div>
      )}
    </div>
  );
};

export default StudyPlanPage;
