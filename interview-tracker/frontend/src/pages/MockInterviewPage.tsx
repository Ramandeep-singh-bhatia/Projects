import { useState, useEffect } from 'react';
import { mockInterviewService } from '../services/api';
import { MockInterview } from '../types';

const MockInterviewPage = () => {
  const [interviews, setInterviews] = useState<MockInterview[]>([]);
  const [activeInterview, setActiveInterview] = useState<any>(null);
  const [showConfig, setShowConfig] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [scratchpad, setScratchpad] = useState('');
  const [assessments, setAssessments] = useState<any[]>([]);

  const [config, setConfig] = useState({
    categories: ['DSA', 'HLD'],
    difficulty: 'MIXED',
    duration: 60,
    focusArea: 'ALL',
  });

  useEffect(() => {
    loadInterviews();
  }, []);

  useEffect(() => {
    if (activeInterview && timeRemaining > 0) {
      const timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            handleTimeUp();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [activeInterview, timeRemaining]);

  const loadInterviews = async () => {
    try {
      const response = await mockInterviewService.getAll();
      setInterviews(response.data);
    } catch (error) {
      console.error('Error loading interviews:', error);
    }
  };

  const startInterview = async () => {
    try {
      const response = await mockInterviewService.start(config);
      setActiveInterview(response.data);
      setTimeRemaining(config.duration * 60);
      setCurrentQuestion(0);
      setAssessments(new Array(response.data.questionCount).fill(null).map(() => ({
        performanceRating: 5,
        whatWentWell: '',
        whatNeedsImprovement: '',
        couldSolveInRealInterview: null,
        timeSpent: 0,
        scratchpadContent: '',
      })));
      setShowConfig(false);
    } catch (error) {
      console.error('Error starting interview:', error);
      alert('Failed to start interview');
    }
  };

  const handleTimeUp = () => {
    alert('Time is up! Please complete your assessment.');
  };

  const nextQuestion = () => {
    if (currentQuestion < activeInterview.questions.length - 1) {
      // Save scratchpad for current question
      const updated = [...assessments];
      updated[currentQuestion].scratchpadContent = scratchpad;
      setAssessments(updated);
      setScratchpad('');
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const completeInterview = async () => {
    const overallPerformance = parseInt(prompt('Overall Performance (1-10):') || '5');
    const overallConfidence = parseInt(prompt('Overall Confidence (1-10):') || '5');
    const pressureLevel = parseInt(prompt('Pressure Level (1-5):') || '3');
    const generalNotes = prompt('General Notes:') || '';

    try {
      await mockInterviewService.complete(activeInterview.mockInterviewId, {
        overallPerformance,
        overallConfidence,
        generalNotes,
        pressureLevel,
        questionAssessments: assessments.map((a, idx) => ({
          ...a,
          questionId: activeInterview.questions[idx].topicId,
          timeSpent: Math.floor((config.duration * 60) / activeInterview.questionCount),
        })),
      });
      alert('Mock interview completed successfully!');
      setActiveInterview(null);
      loadInterviews();
    } catch (error) {
      console.error('Error completing interview:', error);
      alert('Failed to complete interview');
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (activeInterview) {
    const question = activeInterview.questions[currentQuestion];
    const progressPercent = ((currentQuestion + 1) / activeInterview.questionCount) * 100;

    return (
      <div className="fixed inset-0 bg-gray-900 text-white z-50 p-8">
        <div className="max-w-6xl mx-auto h-full flex flex-col">
          {/* Header */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-4">
              <h1 className="text-3xl font-bold">Mock Interview</h1>
              <div className={`text-4xl font-mono ${timeRemaining < 60 ? 'text-red-500' : timeRemaining < 300 ? 'text-yellow-500' : ''}`}>
                {formatTime(timeRemaining)}
              </div>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div className="bg-primary-500 h-2 rounded-full transition-all" style={{ width: `${progressPercent}%` }}></div>
            </div>
            <div className="text-sm mt-2">Question {currentQuestion + 1} of {activeInterview.questionCount}</div>
          </div>

          {/* Question */}
          <div className="flex-1 grid grid-cols-2 gap-6 overflow-hidden">
            <div className="flex flex-col">
              <div className="card bg-gray-800 mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-1 rounded bg-primary-600 text-xs">{question.category}</span>
                  {question.difficulty && (
                    <span className="px-2 py-1 rounded bg-yellow-600 text-xs">{question.difficulty}</span>
                  )}
                </div>
                <h2 className="text-2xl font-bold mb-2">{question.topic}</h2>
                {question.subtopic && <p className="text-gray-400">{question.subtopic}</p>}
              </div>

              <div className="card bg-gray-800 flex-1 flex flex-col">
                <h3 className="font-semibold mb-2">Assessment</h3>
                <div className="space-y-2 flex-1 overflow-y-auto">
                  <div>
                    <label className="text-sm">Performance (1-10)</label>
                    <input
                      type="range"
                      min="1"
                      max="10"
                      className="w-full"
                      value={assessments[currentQuestion]?.performanceRating || 5}
                      onChange={(e) => {
                        const updated = [...assessments];
                        updated[currentQuestion].performanceRating = parseInt(e.target.value);
                        setAssessments(updated);
                      }}
                    />
                    <div className="text-center font-bold">{assessments[currentQuestion]?.performanceRating || 5}/10</div>
                  </div>
                  <div>
                    <label className="text-sm">What went well?</label>
                    <textarea
                      className="w-full bg-gray-700 text-white p-2 rounded"
                      rows={2}
                      value={assessments[currentQuestion]?.whatWentWell || ''}
                      onChange={(e) => {
                        const updated = [...assessments];
                        updated[currentQuestion].whatWentWell = e.target.value;
                        setAssessments(updated);
                      }}
                    />
                  </div>
                  <div>
                    <label className="text-sm">What needs improvement?</label>
                    <textarea
                      className="w-full bg-gray-700 text-white p-2 rounded"
                      rows={2}
                      value={assessments[currentQuestion]?.whatNeedsImprovement || ''}
                      onChange={(e) => {
                        const updated = [...assessments];
                        updated[currentQuestion].whatNeedsImprovement = e.target.value;
                        setAssessments(updated);
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Scratchpad */}
            <div className="flex flex-col">
              <div className="card bg-gray-800 flex-1 flex flex-col">
                <h3 className="font-semibold mb-2">Scratchpad</h3>
                <textarea
                  className="flex-1 w-full bg-gray-900 text-white p-4 rounded font-mono text-sm"
                  value={scratchpad}
                  onChange={(e) => setScratchpad(e.target.value)}
                  placeholder="Write your solution here..."
                />
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-6 flex justify-between">
            <button
              onClick={() => { if (window.confirm('End interview early?')) setActiveInterview(null); }}
              className="btn btn-danger"
            >
              End Early
            </button>
            <div className="space-x-2">
              {currentQuestion < activeInterview.questionCount - 1 ? (
                <button onClick={nextQuestion} className="btn btn-primary">
                  Next Question →
                </button>
              ) : (
                <button onClick={completeInterview} className="btn btn-primary">
                  Complete Interview
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Mock Interview</h1>
        <button onClick={() => setShowConfig(true)} className="btn btn-primary">
          Start Mock Interview
        </button>
      </div>

      {showConfig && (
        <div className="card mb-6">
          <h2 className="text-2xl font-semibold mb-4">Configure Interview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Duration</label>
              <select className="input" value={config.duration} onChange={(e) => setConfig({ ...config, duration: parseInt(e.target.value) })}>
                <option value="30">Quick (30 min)</option>
                <option value="45">Standard (45 min)</option>
                <option value="60">Full (60 min)</option>
                <option value="90">Extended (90 min)</option>
              </select>
            </div>
            <div>
              <label className="label">Focus Area</label>
              <select className="input" value={config.focusArea} onChange={(e) => setConfig({ ...config, focusArea: e.target.value })}>
                <option value="ALL">All Topics</option>
                <option value="WEAK">Weak Areas Only</option>
              </select>
            </div>
          </div>
          <div className="flex gap-2 mt-4">
            <button onClick={startInterview} className="btn btn-primary">Start Interview</button>
            <button onClick={() => setShowConfig(false)} className="btn btn-secondary">Cancel</button>
          </div>
        </div>
      )}

      <div className="card">
        <h2 className="text-2xl font-semibold mb-4">Past Interviews</h2>
        {interviews.length === 0 ? (
          <p className="text-center text-gray-500 py-8">No past interviews</p>
        ) : (
          <div className="space-y-4">
            {interviews.map((interview) => (
              <div key={interview.id} className="border dark:border-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-semibold">{new Date(interview.startTime).toLocaleDateString()}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {interview.questionCount} questions • {interview.actualDuration} minutes
                    </div>
                    {interview.overallPerformance && (
                      <div className="text-sm mt-1">
                        Performance: {interview.overallPerformance}/10
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MockInterviewPage;
