import { useState, useEffect } from 'react';
import { pomodoroService } from '../../services/api';
import { Pomodoro, PomodoroPhase } from '../../types';

const PomodoroWidget = () => {
  const [pomodoro, setPomodoro] = useState<Pomodoro | null>(null);
  const [timeLeft, setTimeLeft] = useState(0);
  const [isMinimized, setIsMinimized] = useState(true);

  useEffect(() => {
    loadActivePomodoro();
    const interval = setInterval(loadActivePomodoro, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (pomodoro && !pomodoro.completed) {
      const timer = setInterval(() => {
        const elapsed = Math.floor((Date.now() - new Date(pomodoro.startTime).getTime()) / 1000);
        const remaining = (pomodoro.duration * 60) - elapsed;
        setTimeLeft(Math.max(0, remaining));

        if (remaining <= 0) {
          clearInterval(timer);
          handleComplete();
        }
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [pomodoro]);

  const loadActivePomodoro = async () => {
    try {
      const response = await pomodoroService.getActive();
      if (response.data) {
        setPomodoro(response.data);
      } else {
        setPomodoro(null);
      }
    } catch (error) {
      setPomodoro(null);
    }
  };

  const startPomodoro = async (phase: PomodoroPhase) => {
    try {
      const response = await pomodoroService.start({
        topicId: null,
        phase,
        pomodoroNumber: 1,
      });
      setPomodoro(response.data);
      setIsMinimized(false);
    } catch (error) {
      console.error('Error starting pomodoro:', error);
      alert('Failed to start Pomodoro');
    }
  };

  const handleComplete = async () => {
    if (!pomodoro) return;

    try {
      await pomodoroService.complete(pomodoro.id!);

      if (pomodoro.phase === 'WORK') {
        const rating = prompt('Performance Rating (1-10):');
        if (rating) {
          await pomodoroService.logSession(pomodoro.id!, {
            performanceRating: parseInt(rating),
            quickNotes: 'Pomodoro session',
          });
        }
      }

      loadActivePomodoro();

      if (pomodoro.phase === 'WORK') {
        alert('Work session complete! Time for a break.');
      } else {
        alert('Break complete! Ready to focus?');
      }
    } catch (error) {
      console.error('Error completing pomodoro:', error);
    }
  };

  const stopPomodoro = async () => {
    if (!pomodoro || !window.confirm('Stop this Pomodoro?')) return;

    try {
      await pomodoroService.stop(pomodoro.id!);
      setPomodoro(null);
    } catch (error) {
      console.error('Error stopping pomodoro:', error);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getPhaseColor = (phase: PomodoroPhase) => {
    switch (phase) {
      case 'WORK': return 'bg-red-500';
      case 'SHORT_BREAK': return 'bg-green-500';
      case 'LONG_BREAK': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getPhaseLabel = (phase: PomodoroPhase) => {
    switch (phase) {
      case 'WORK': return 'Work';
      case 'SHORT_BREAK': return 'Short Break';
      case 'LONG_BREAK': return 'Long Break';
      default: return '';
    }
  };

  if (!pomodoro) {
    return (
      <div className="fixed bottom-4 right-4 z-40">
        <button
          onClick={() => startPomodoro('WORK' as PomodoroPhase)}
          className="btn btn-primary rounded-full shadow-lg px-6 py-3"
        >
          🍅 Start Pomodoro
        </button>
      </div>
    );
  }

  if (isMinimized) {
    return (
      <div className="fixed bottom-4 right-4 z-40">
        <button
          onClick={() => setIsMinimized(false)}
          className={`${getPhaseColor(pomodoro.phase)} text-white rounded-full shadow-lg px-6 py-3 font-mono text-lg font-bold`}
        >
          🍅 {formatTime(timeLeft)}
        </button>
      </div>
    );
  }

  const progress = ((pomodoro.duration * 60 - timeLeft) / (pomodoro.duration * 60)) * 100;

  return (
    <div className="fixed bottom-4 right-4 z-40 bg-white dark:bg-gray-800 rounded-lg shadow-2xl p-6 w-80">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-bold text-lg">Pomodoro Timer</h3>
        <button onClick={() => setIsMinimized(true)} className="text-gray-500 hover:text-gray-700">
          −
        </button>
      </div>

      <div className="text-center mb-4">
        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
          {getPhaseLabel(pomodoro.phase)}
        </div>
        <div className="text-5xl font-mono font-bold mb-2">
          {formatTime(timeLeft)}
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${getPhaseColor(pomodoro.phase)}`}
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      <div className="flex gap-2">
        <button onClick={stopPomodoro} className="btn btn-secondary flex-1">
          Stop
        </button>
        <button onClick={handleComplete} className="btn btn-primary flex-1">
          Complete
        </button>
      </div>
    </div>
  );
};

export default PomodoroWidget;
