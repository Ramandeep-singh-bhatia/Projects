/**
 * Motivation Tracker Service
 * Manages daily wins, milestones, achievements, and flexible streaks
 */

class MotivationTrackerService {
  constructor() {
    this.achievementDefinitions = this.initializeAchievements();
    this.milestoneDefinitions = this.initializeMilestones();
  }

  /**
   * Initialize achievement definitions
   */
  initializeAchievements() {
    return [
      {
        id: 'first_exercise',
        name: 'Getting Started',
        description: 'Complete your first exercise',
        icon: 'Rocket',
        type: 'milestone',
        condition: (data) => data.exercisesCompleted >= 1,
      },
      {
        id: 'streak_7',
        name: '7-Day Warrior',
        description: 'Maintain a 7-day learning streak',
        icon: 'Flame',
        type: 'streak',
        condition: (data) => data.currentStreak >= 7,
      },
      {
        id: 'streak_30',
        name: '30-Day Champion',
        description: 'Maintain a 30-day learning streak',
        icon: 'Trophy',
        type: 'streak',
        condition: (data) => data.currentStreak >= 30,
      },
      {
        id: 'vocab_100',
        name: 'Vocabulary Master',
        description: 'Master 100 vocabulary words',
        icon: 'BookOpen',
        type: 'vocabulary',
        condition: (data) => data.masteredWords >= 100,
      },
      {
        id: 'vocab_500',
        name: 'Word Wizard',
        description: 'Master 500 vocabulary words',
        icon: 'Sparkles',
        type: 'vocabulary',
        condition: (data) => data.masteredWords >= 500,
      },
      {
        id: 'perfect_score',
        name: 'Perfect Score',
        description: 'Get 100% on any exercise',
        icon: 'Star',
        type: 'performance',
        condition: (data) => data.hasPerf ectScore,
      },
      {
        id: 'exercises_100',
        name: 'Centurion',
        description: 'Complete 100 exercises',
        icon: 'Award',
        type: 'milestone',
        condition: (data) => data.exercisesCompleted >= 100,
      },
      {
        id: 'exercises_500',
        name: 'Dedicated Learner',
        description: 'Complete 500 exercises',
        icon: 'Medal',
        type: 'milestone',
        condition: (data) => data.exercisesCompleted >= 500,
      },
      {
        id: 'proficiency_60',
        name: 'Intermediate Achieved',
        description: 'Reach intermediate proficiency (60+)',
        icon: 'TrendingUp',
        type: 'level',
        condition: (data) => data.proficiencyScore >= 60,
      },
      {
        id: 'proficiency_80',
        name: 'Advanced Learner',
        description: 'Reach advanced proficiency (80+)',
        icon: 'Crown',
        type: 'level',
        condition: (data) => data.proficiencyScore >= 80,
      },
      {
        id: 'early_bird',
        name: 'Early Bird',
        description: 'Practice before 8 AM five times',
        icon: 'Sunrise',
        type: 'habit',
        condition: (data) => data.earlyMorningPractices >= 5,
      },
      {
        id: 'night_owl',
        name: 'Night Owl',
        description: 'Practice after 10 PM five times',
        icon: 'Moon',
        type: 'habit',
        condition: (data) => data.lateNightPractices >= 5,
      },
      {
        id: 'comeback',
        name: 'Comeback Kid',
        description: 'Return after a 7-day break',
        icon: 'RotateCcw',
        type: 'perseverance',
        condition: (data) => data.returnedAfterBreak,
      },
    ];
  }

  /**
   * Initialize milestone definitions
   */
  initializeMilestones() {
    return [
      {
        id: 'vocab_100',
        type: 'vocabulary',
        name: 'First 100 Words',
        description: 'Master your first 100 vocabulary words',
        target: 100,
        icon: 'BookOpen',
      },
      {
        id: 'vocab_500',
        type: 'vocabulary',
        name: '500 Words Mastered',
        description: 'Build a strong vocabulary foundation',
        target: 500,
        icon: 'Book',
      },
      {
        id: 'streak_7',
        type: 'streak',
        name: '7-Day Streak',
        description: 'Practice for 7 days in a row',
        target: 7,
        icon: 'Flame',
      },
      {
        id: 'streak_30',
        type: 'streak',
        name: '30-Day Streak',
        description: 'A full month of consistent practice',
        target: 30,
        icon: 'Calendar',
      },
      {
        id: 'exercises_100',
        type: 'exercises',
        name: '100 Exercises',
        description: 'Complete 100 practice exercises',
        target: 100,
        icon: 'Target',
      },
      {
        id: 'proficiency_intermediate',
        type: 'proficiency',
        name: 'Intermediate Level',
        description: 'Reach intermediate proficiency',
        target: 60,
        icon: 'TrendingUp',
      },
      {
        id: 'proficiency_advanced',
        type: 'proficiency',
        name: 'Advanced Level',
        description: 'Reach advanced proficiency',
        target: 80,
        icon: 'Award',
      },
    ];
  }

  /**
   * Get or create daily wins list
   */
  getDailyWins() {
    const stored = localStorage.getItem('daily_wins');
    return stored ? JSON.parse(stored) : [];
  }

  /**
   * Add a daily win
   */
  addDailyWin(description, category = 'general', emotionalValue = 5) {
    const wins = this.getDailyWins();

    const newWin = {
      id: Date.now(),
      user_id: 1,
      win_description: description,
      win_category: category,
      emotional_value: emotionalValue,
      created_at: new Date().toISOString(),
    };

    wins.unshift(newWin);
    localStorage.setItem('daily_wins', JSON.stringify(wins.slice(0, 200))); // Keep last 200

    return newWin;
  }

  /**
   * Get today's wins
   */
  getTodaysWins() {
    const wins = this.getDailyWins();
    const today = new Date().toDateString();

    return wins.filter(win => {
      const winDate = new Date(win.created_at).toDateString();
      return winDate === today;
    });
  }

  /**
   * Get wins by date range
   */
  getWinsByDateRange(startDate, endDate) {
    const wins = this.getDailyWins();
    const start = new Date(startDate);
    const end = new Date(endDate);

    return wins.filter(win => {
      const winDate = new Date(win.created_at);
      return winDate >= start && winDate <= end;
    });
  }

  /**
   * Update flexible streak
   */
  updateFlexibleStreak(userId = 1) {
    const streakData = this.getStreakData();
    const today = new Date().toDateString();

    // If already practiced today, don't update
    if (streakData.last_activity_date === today) {
      return streakData;
    }

    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayStr = yesterday.toDateString();

    // Check if continuing streak
    if (streakData.last_activity_date === yesterdayStr) {
      // Continue streak
      streakData.streak_count += 1;
      streakData.total_practice_days += 1;
    } else {
      // Check if can use freeze day
      const daysSinceLastActivity = this.daysBetween(
        new Date(streakData.last_activity_date),
        new Date()
      );

      if (daysSinceLastActivity === 2 && streakData.freeze_days_available > 0) {
        // Use one freeze day
        streakData.freeze_days_used += 1;
        streakData.freeze_days_available -= 1;
        streakData.streak_count += 1; // Maintain streak
        streakData.total_practice_days += 1;
      } else if (daysSinceLastActivity > 2) {
        // Streak broken
        streakData.streak_count = 1;
        streakData.total_practice_days += 1;
      }
    }

    streakData.last_activity_date = today;
    streakData.longest_streak = Math.max(streakData.longest_streak, streakData.streak_count);

    // Reset freeze days monthly
    this.resetFreezeДaysIfNeeded(streakData);

    this.saveStreakData(streakData);
    return streakData;
  }

  /**
   * Get current streak data
   */
  getStreakData() {
    const stored = localStorage.getItem('flexible_streak');
    if (stored) {
      return JSON.parse(stored);
    }

    // Default streak data
    return {
      user_id: 1,
      streak_count: 0,
      last_activity_date: null,
      longest_streak: 0,
      freeze_days_available: 2,
      freeze_days_used: 0,
      last_freeze_reset: new Date().toISOString().split('T')[0].substring(0, 7), // YYYY-MM
      total_practice_days: 0,
    };
  }

  /**
   * Save streak data
   */
  saveStreakData(streakData) {
    localStorage.setItem('flexible_streak', JSON.stringify(streakData));
  }

  /**
   * Reset freeze days if new month
   */
  resetFreezeDaysIfNeeded(streakData) {
    const currentMonth = new Date().toISOString().split('T')[0].substring(0, 7);

    if (streakData.last_freeze_reset !== currentMonth) {
      streakData.freeze_days_available = 2;
      streakData.freeze_days_used = 0;
      streakData.last_freeze_reset = currentMonth;
    }
  }

  /**
   * Check and unlock achievements
   */
  checkAchievements(userData) {
    const existingAchievements = this.getAchievements();
    const existingIds = new Set(existingAchievements.map(a => a.achievement_id));
    const newAchievements = [];

    // Prepare data for conditions
    const conditionData = {
      exercisesCompleted: userData.exerciseHistory?.length || 0,
      currentStreak: userData.streak?.current || 0,
      masteredWords: (userData.vocabularyMastery || []).filter(v => v.mastery_level >= 80).length,
      hasPerfectScore: (userData.exerciseHistory || []).some(e => e.score >= 100),
      proficiencyScore: userData.userProfile?.proficiency_score || 0,
      earlyMorningPractices: this.countEarlyMorningPractices(userData.sessionPerformance),
      lateNightPractices: this.countLateNightPractices(userData.sessionPerformance),
      returnedAfterBreak: this.checkReturnedAfterBreak(userData.exerciseHistory),
    };

    // Check each achievement
    for (const achievement of this.achievementDefinitions) {
      if (!existingIds.has(achievement.id) && achievement.condition(conditionData)) {
        const newAchievement = {
          id: Date.now() + Math.random(),
          user_id: 1,
          achievement_id: achievement.id,
          achievement_type: achievement.type,
          achievement_name: achievement.name,
          achievement_description: achievement.description,
          icon_name: achievement.icon,
          achieved_at: new Date().toISOString(),
        };

        existingAchievements.push(newAchievement);
        newAchievements.push(newAchievement);
      }
    }

    if (newAchievements.length > 0) {
      this.saveAchievements(existingAchievements);
    }

    return newAchievements;
  }

  /**
   * Get all achievements
   */
  getAchievements() {
    const stored = localStorage.getItem('achievements');
    return stored ? JSON.parse(stored) : [];
  }

  /**
   * Save achievements
   */
  saveAchievements(achievements) {
    localStorage.setItem('achievements', JSON.stringify(achievements));
  }

  /**
   * Get milestone progress
   */
  getMilestoneProgress(userData) {
    const progress = [];

    for (const milestone of this.milestoneDefinitions) {
      let currentValue = 0;

      switch (milestone.type) {
        case 'vocabulary':
          currentValue = (userData.vocabularyMastery || []).filter(v => v.mastery_level >= 80).length;
          break;
        case 'streak':
          currentValue = userData.streak?.current || 0;
          break;
        case 'exercises':
          currentValue = userData.exerciseHistory?.length || 0;
          break;
        case 'proficiency':
          currentValue = userData.userProfile?.proficiency_score || 0;
          break;
      }

      const percentage = Math.min(100, Math.round((currentValue / milestone.target) * 100));
      const completed = currentValue >= milestone.target;

      progress.push({
        ...milestone,
        currentValue,
        percentage,
        completed,
        remaining: Math.max(0, milestone.target - currentValue),
      });
    }

    return progress.sort((a, b) => b.percentage - a.percentage);
  }

  /**
   * Generate progress story
   */
  generateProgressStory(userData, daysAgo = 30) {
    const story = {
      periodDays: daysAgo,
      startDate: new Date(Date.now() - daysAgo * 24 * 60 * 60 * 1000).toISOString(),
      endDate: new Date().toISOString(),
      improvements: [],
      newSkills: [],
      consistency: {},
      highlights: [],
    };

    // Analyze exercise history for the period
    const periodExercises = (userData.exerciseHistory || []).filter(e => {
      const exerciseDate = new Date(e.completed_at);
      const startDate = new Date(story.startDate);
      return exerciseDate >= startDate;
    });

    const olderExercises = (userData.exerciseHistory || []).filter(e => {
      const exerciseDate = new Date(e.completed_at);
      const startDate = new Date(story.startDate);
      return exerciseDate < startDate;
    });

    // Calculate improvements
    if (periodExercises.length > 0 && olderExercises.length > 0) {
      const recentAvg = periodExercises.reduce((sum, e) => sum + (e.score || 0), 0) / periodExercises.length;
      const olderAvg = olderExercises.reduce((sum, e) => sum + (e.score || 0), 0) / olderExercises.length;

      if (recentAvg > olderAvg) {
        story.improvements.push({
          metric: 'Average Score',
          before: Math.round(olderAvg),
          after: Math.round(recentAvg),
          change: Math.round(recentAvg - olderAvg),
        });
      }
    }

    // Check consistency
    const practiceDays = new Set(periodExercises.map(e =>
      new Date(e.completed_at).toDateString()
    )).size;

    story.consistency = {
      daysActive: practiceDays,
      totalDays: daysAgo,
      percentage: Math.round((practiceDays / daysAgo) * 100),
    };

    // Highlights
    const perfectScores = periodExercises.filter(e => e.score >= 100).length;
    if (perfectScores > 0) {
      story.highlights.push(`Achieved ${perfectScores} perfect score${perfectScores > 1 ? 's' : ''}!`);
    }

    const wins = this.getWinsByDateRange(story.startDate, story.endDate);
    if (wins.length > 0) {
      story.highlights.push(`Celebrated ${wins.length} learning wins`);
    }

    return story;
  }

  /**
   * Helper methods
   */
  daysBetween(date1, date2) {
    const diffTime = Math.abs(date2 - date1);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  }

  countEarlyMorningPractices(sessions) {
    if (!sessions) return 0;
    return sessions.filter(s => s.time_of_day === 'morning').length;
  }

  countLateNightPractices(sessions) {
    if (!sessions) return 0;
    return sessions.filter(s => s.time_of_day === 'night').length;
  }

  checkReturnedAfterBreak(exerciseHistory) {
    if (!exerciseHistory || exerciseHistory.length < 2) return false;

    for (let i = 0; i < exerciseHistory.length - 1; i++) {
      const current = new Date(exerciseHistory[i].completed_at);
      const previous = new Date(exerciseHistory[i + 1].completed_at);
      const daysDiff = this.daysBetween(current, previous);

      if (daysDiff >= 7) return true;
    }

    return false;
  }
}

export default new MotivationTrackerService();
