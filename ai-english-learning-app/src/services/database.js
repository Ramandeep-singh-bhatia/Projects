import Database from 'better-sqlite3';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// For browser environment, we'll use localStorage as fallback
const isBrowser = typeof window !== 'undefined';

class DatabaseService {
  constructor() {
    if (!isBrowser) {
      this.db = new Database(join(__dirname, '../../database/english-learning.db'));
      this.db.pragma('foreign_keys = ON');
    }
  }

  // User Profile Methods
  getUserProfile(userId = 1) {
    if (isBrowser) {
      const profile = localStorage.getItem('user_profile');
      return profile ? JSON.parse(profile) : this._getDefaultProfile();
    }
    return this.db.prepare('SELECT * FROM user_profile WHERE id = ?').get(userId);
  }

  updateUserProfile(userId, data) {
    if (isBrowser) {
      const profile = this.getUserProfile(userId);
      const updated = { ...profile, ...data, last_active: new Date().toISOString() };
      localStorage.setItem('user_profile', JSON.stringify(updated));
      return updated;
    }
    const fields = Object.keys(data).map(key => `${key} = ?`).join(', ');
    const values = [...Object.values(data), userId];
    this.db.prepare(`UPDATE user_profile SET ${fields}, last_active = CURRENT_TIMESTAMP WHERE id = ?`).run(...values);
    return this.getUserProfile(userId);
  }

  // Learning Progress Methods
  getLearningProgress(userId = 1) {
    if (isBrowser) {
      const progress = localStorage.getItem('learning_progress');
      return progress ? JSON.parse(progress) : this._getDefaultProgress();
    }
    return this.db.prepare('SELECT * FROM learning_progress WHERE user_id = ?').all(userId);
  }

  updateLearningProgress(userId, skillType, score, timeSpent) {
    if (isBrowser) {
      const progress = this.getLearningProgress(userId);
      const skillIndex = progress.findIndex(p => p.skill_type === skillType);
      if (skillIndex >= 0) {
        progress[skillIndex].score = score;
        progress[skillIndex].exercises_completed += 1;
        progress[skillIndex].total_time_minutes += Math.floor(timeSpent / 60);
        progress[skillIndex].last_practiced = new Date().toISOString();
      }
      localStorage.setItem('learning_progress', JSON.stringify(progress));
      return progress;
    }

    this.db.prepare(`
      UPDATE learning_progress
      SET score = ?,
          exercises_completed = exercises_completed + 1,
          total_time_minutes = total_time_minutes + ?,
          last_practiced = CURRENT_TIMESTAMP
      WHERE user_id = ? AND skill_type = ?
    `).run(score, Math.floor(timeSpent / 60), userId, skillType);

    return this.getLearningProgress(userId);
  }

  // Exercise History Methods
  saveExerciseHistory(userId, exerciseType, exerciseData, userResponse, aiFeedback, score, duration) {
    const data = {
      user_id: userId,
      exercise_type: exerciseType,
      exercise_data: JSON.stringify(exerciseData),
      user_response: userResponse,
      ai_feedback: aiFeedback,
      score: score,
      duration_seconds: duration,
      completed_at: new Date().toISOString()
    };

    if (isBrowser) {
      const history = this.getExerciseHistory(userId);
      history.unshift({ id: Date.now(), ...data });
      localStorage.setItem('exercise_history', JSON.stringify(history.slice(0, 100))); // Keep last 100
      return data;
    }

    this.db.prepare(`
      INSERT INTO exercise_history
      (user_id, exercise_type, exercise_data, user_response, ai_feedback, score, duration_seconds)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `).run(userId, exerciseType, JSON.stringify(exerciseData), userResponse, aiFeedback, score, duration);

    return data;
  }

  getExerciseHistory(userId = 1, limit = 50) {
    if (isBrowser) {
      const history = localStorage.getItem('exercise_history');
      return history ? JSON.parse(history).slice(0, limit) : [];
    }
    return this.db.prepare(`
      SELECT * FROM exercise_history
      WHERE user_id = ?
      ORDER BY completed_at DESC
      LIMIT ?
    `).all(userId, limit);
  }

  // Vocabulary Methods
  addVocabulary(word, definition, difficultyLevel, contextExamples) {
    if (isBrowser) {
      const vocab = this.getAllVocabulary();
      const exists = vocab.find(v => v.word.toLowerCase() === word.toLowerCase());
      if (!exists) {
        vocab.push({
          id: Date.now(),
          word,
          definition,
          difficulty_level: difficultyLevel,
          context_examples: JSON.stringify(contextExamples),
          created_at: new Date().toISOString()
        });
        localStorage.setItem('vocabulary', JSON.stringify(vocab));
      }
      return exists || vocab[vocab.length - 1];
    }

    try {
      this.db.prepare(`
        INSERT INTO vocabulary (word, definition, difficulty_level, context_examples)
        VALUES (?, ?, ?, ?)
      `).run(word, definition, difficultyLevel, JSON.stringify(contextExamples));
      return this.db.prepare('SELECT * FROM vocabulary WHERE word = ?').get(word);
    } catch (error) {
      return this.db.prepare('SELECT * FROM vocabulary WHERE word = ?').get(word);
    }
  }

  getAllVocabulary() {
    if (isBrowser) {
      const vocab = localStorage.getItem('vocabulary');
      return vocab ? JSON.parse(vocab) : [];
    }
    return this.db.prepare('SELECT * FROM vocabulary').all();
  }

  getUserVocabularyMastery(userId = 1) {
    if (isBrowser) {
      const mastery = localStorage.getItem('user_vocabulary');
      return mastery ? JSON.parse(mastery) : [];
    }
    return this.db.prepare(`
      SELECT uv.*, v.word, v.definition
      FROM user_vocabulary uv
      JOIN vocabulary v ON uv.vocabulary_id = v.id
      WHERE uv.user_id = ?
      ORDER BY uv.last_reviewed DESC
    `).all(userId);
  }

  updateVocabularyMastery(userId, vocabularyId, correct) {
    if (isBrowser) {
      const mastery = this.getUserVocabularyMastery(userId);
      let entry = mastery.find(m => m.vocabulary_id === vocabularyId);

      if (!entry) {
        entry = {
          id: Date.now(),
          user_id: userId,
          vocabulary_id: vocabularyId,
          mastery_level: 0,
          times_seen: 0,
          times_correct: 0,
          last_reviewed: new Date().toISOString(),
          next_review: this._calculateNextReview(0)
        };
        mastery.push(entry);
      }

      entry.times_seen += 1;
      if (correct) {
        entry.times_correct += 1;
        entry.mastery_level = Math.min(100, entry.mastery_level + 10);
      } else {
        entry.mastery_level = Math.max(0, entry.mastery_level - 5);
      }
      entry.last_reviewed = new Date().toISOString();
      entry.next_review = this._calculateNextReview(entry.mastery_level);

      localStorage.setItem('user_vocabulary', JSON.stringify(mastery));
      return entry;
    }

    const existing = this.db.prepare(`
      SELECT * FROM user_vocabulary WHERE user_id = ? AND vocabulary_id = ?
    `).get(userId, vocabularyId);

    if (existing) {
      const newMastery = correct
        ? Math.min(100, existing.mastery_level + 10)
        : Math.max(0, existing.mastery_level - 5);

      this.db.prepare(`
        UPDATE user_vocabulary
        SET mastery_level = ?,
            times_seen = times_seen + 1,
            times_correct = times_correct + ?,
            last_reviewed = CURRENT_TIMESTAMP,
            next_review = DATETIME('now', '+' || ? || ' days')
        WHERE user_id = ? AND vocabulary_id = ?
      `).run(newMastery, correct ? 1 : 0, this._getReviewInterval(newMastery), userId, vocabularyId);
    } else {
      this.db.prepare(`
        INSERT INTO user_vocabulary
        (user_id, vocabulary_id, mastery_level, times_seen, times_correct, next_review)
        VALUES (?, ?, ?, 1, ?, DATETIME('now', '+1 day'))
      `).run(userId, vocabularyId, correct ? 10 : 0, correct ? 1 : 0);
    }
  }

  // Mistakes Journal Methods
  addMistake(userId, mistakeType, originalText, correctedText, explanation) {
    const data = {
      user_id: userId,
      mistake_type: mistakeType,
      original_text: originalText,
      corrected_text: correctedText,
      explanation: explanation,
      occurred_at: new Date().toISOString()
    };

    if (isBrowser) {
      const mistakes = this.getMistakes(userId);
      mistakes.unshift({ id: Date.now(), ...data });
      localStorage.setItem('mistakes_journal', JSON.stringify(mistakes.slice(0, 100)));
      return data;
    }

    this.db.prepare(`
      INSERT INTO mistakes_journal
      (user_id, mistake_type, original_text, corrected_text, explanation)
      VALUES (?, ?, ?, ?, ?)
    `).run(userId, mistakeType, originalText, correctedText, explanation);

    return data;
  }

  getMistakes(userId = 1, limit = 50) {
    if (isBrowser) {
      const mistakes = localStorage.getItem('mistakes_journal');
      return mistakes ? JSON.parse(mistakes).slice(0, limit) : [];
    }
    return this.db.prepare(`
      SELECT * FROM mistakes_journal
      WHERE user_id = ?
      ORDER BY occurred_at DESC
      LIMIT ?
    `).all(userId, limit);
  }

  // Daily Streak Methods
  updateDailyStreak(userId = 1) {
    const today = new Date().toISOString().split('T')[0];

    if (isBrowser) {
      let streak = localStorage.getItem('daily_streak');
      streak = streak ? JSON.parse(streak) : { streak_count: 0, last_activity_date: null, longest_streak: 0 };

      if (streak.last_activity_date !== today) {
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        const yesterdayStr = yesterday.toISOString().split('T')[0];

        if (streak.last_activity_date === yesterdayStr) {
          streak.streak_count += 1;
        } else {
          streak.streak_count = 1;
        }

        streak.longest_streak = Math.max(streak.longest_streak, streak.streak_count);
        streak.last_activity_date = today;
        localStorage.setItem('daily_streak', JSON.stringify(streak));
      }

      return streak;
    }

    const current = this.db.prepare('SELECT * FROM daily_streaks WHERE user_id = ?').get(userId);

    if (current && current.last_activity_date !== today) {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      const yesterdayStr = yesterday.toISOString().split('T')[0];

      let newStreak = current.last_activity_date === yesterdayStr ? current.streak_count + 1 : 1;
      let longestStreak = Math.max(current.longest_streak, newStreak);

      this.db.prepare(`
        UPDATE daily_streaks
        SET streak_count = ?, last_activity_date = DATE('now'), longest_streak = ?
        WHERE user_id = ?
      `).run(newStreak, longestStreak, userId);
    }

    return this.db.prepare('SELECT * FROM daily_streaks WHERE user_id = ?').get(userId);
  }

  getDailyStreak(userId = 1) {
    if (isBrowser) {
      const streak = localStorage.getItem('daily_streak');
      return streak ? JSON.parse(streak) : { streak_count: 0, last_activity_date: null, longest_streak: 0 };
    }
    return this.db.prepare('SELECT * FROM daily_streaks WHERE user_id = ?').get(userId);
  }

  // Helper methods
  _calculateNextReview(masteryLevel) {
    const days = Math.ceil(masteryLevel / 20); // 0-20: 1 day, 21-40: 2 days, etc.
    const nextReview = new Date();
    nextReview.setDate(nextReview.getDate() + Math.max(1, days));
    return nextReview.toISOString();
  }

  _getReviewInterval(masteryLevel) {
    return Math.max(1, Math.ceil(masteryLevel / 20));
  }

  _getDefaultProfile() {
    return {
      id: 1,
      username: 'default_user',
      current_level: 'beginner',
      proficiency_score: 0,
      created_at: new Date().toISOString(),
      last_active: new Date().toISOString()
    };
  }

  _getDefaultProgress() {
    const skills = ['vocabulary', 'grammar', 'fluency', 'context_usage', 'writing_quality'];
    return skills.map((skill, index) => ({
      id: index + 1,
      user_id: 1,
      skill_type: skill,
      score: 0,
      exercises_completed: 0,
      total_time_minutes: 0,
      last_practiced: new Date().toISOString()
    }));
  }

  close() {
    if (!isBrowser && this.db) {
      this.db.close();
    }
  }
}

export default new DatabaseService();
