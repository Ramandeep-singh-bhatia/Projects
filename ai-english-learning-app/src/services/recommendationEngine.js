/**
 * Recommendation Engine
 * Provides intelligent, personalized learning recommendations based on user data
 */

import patternRecognition from './patternRecognition.js';

class RecommendationEngine {
  constructor() {
    this.recommendationTypes = {
      PRACTICE_FOCUS: 'practice_focus',
      DIFFICULTY_ADJUSTMENT: 'difficulty_adjustment',
      SKILL_BALANCE: 'skill_balance',
      REVIEW_REMINDER: 'review_reminder',
      VOCABULARY_USE: 'vocabulary_use',
      ERROR_PATTERN: 'error_pattern',
      TIME_OPTIMIZATION: 'time_optimization',
      ENERGY_BASED: 'energy_based',
      MILESTONE_PROGRESS: 'milestone_progress',
      RECOVERY: 'recovery',
    };

    this.priorityLevels = {
      CRITICAL: 5,
      HIGH: 4,
      MEDIUM: 3,
      LOW: 2,
      INFO: 1,
    };
  }

  /**
   * Generate comprehensive recommendations based on user data
   */
  async generateRecommendations(userData) {
    const recommendations = [];

    const {
      learningProgress,
      exerciseHistory,
      mistakes,
      vocabularyMastery,
      streak,
      userProfile,
      sessionPerformance,
    } = userData;

    // 1. Skill balance recommendations
    const balanceRec = this.checkSkillBalance(learningProgress);
    if (balanceRec) recommendations.push(balanceRec);

    // 2. Practice frequency recommendations
    const frequencyRec = this.checkPracticeFrequency(exerciseHistory, streak);
    if (frequencyRec) recommendations.push(frequencyRec);

    // 3. Difficulty adjustment recommendations
    const difficultyRec = this.checkDifficultyLevel(exerciseHistory, userProfile);
    if (difficultyRec) recommendations.push(difficultyRec);

    // 4. Error pattern recommendations
    const errorRecs = this.generateErrorPatternRecommendations(mistakes);
    recommendations.push(...errorRecs);

    // 5. Vocabulary review recommendations
    const vocabRecs = this.generateVocabularyRecommendations(vocabularyMastery, exerciseHistory);
    recommendations.push(...vocabRecs);

    // 6. Time optimization recommendations
    const timeRec = this.generateTimeRecommendations(sessionPerformance);
    if (timeRec) recommendations.push(timeRec);

    // 7. Recovery mode detection
    const recoveryRec = this.checkForRecoveryMode(exerciseHistory);
    if (recoveryRec) recommendations.push(recoveryRec);

    // 8. Milestone progress recommendations
    const milestoneRecs = this.generateMilestoneRecommendations(userData);
    recommendations.push(...milestoneRecs);

    // Sort by priority and return top recommendations
    return recommendations
      .sort((a, b) => b.priority - a.priority)
      .slice(0, 10); // Return top 10 recommendations
  }

  /**
   * Check if skills are balanced
   */
  checkSkillBalance(learningProgress) {
    if (!learningProgress || learningProgress.length === 0) return null;

    const scores = learningProgress.map(p => p.score);
    const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
    const maxScore = Math.max(...scores);
    const minScore = Math.min(...scores);

    const imbalance = maxScore - minScore;

    if (imbalance > 30) {
      const weakestSkill = learningProgress.find(p => p.score === minScore);
      const strongestSkill = learningProgress.find(p => p.score === maxScore);

      return {
        type: this.recommendationTypes.SKILL_BALANCE,
        priority: this.priorityLevels.HIGH,
        title: 'Balance Your Skills',
        message: `Your ${strongestSkill.skill_type.replace('_', ' ')} (${strongestSkill.score}) is much stronger than ${weakestSkill.skill_type.replace('_', ' ')} (${weakestSkill.score}). Let's work on balancing your skills.`,
        action: {
          type: 'practice',
          focus: weakestSkill.skill_type,
          difficulty: 'beginner',
        },
        reason: `Skill imbalance detected: ${imbalance} points difference`,
      };
    }

    return null;
  }

  /**
   * Check practice frequency and suggest optimal patterns
   */
  checkPracticeFrequency(exerciseHistory, streak) {
    if (!exerciseHistory || exerciseHistory.length === 0) return null;

    const recent = exerciseHistory.slice(0, 7); // Last 7 exercises
    const daysSinceLastPractice = this.daysSince(exerciseHistory[0]?.completed_at);

    // Haven't practiced in 2+ days
    if (daysSinceLastPractice >= 2) {
      return {
        type: this.recommendationTypes.PRACTICE_FOCUS,
        priority: this.priorityLevels.HIGH,
        title: "You've Been Missed!",
        message: `It's been ${daysSinceLastPractice} days since your last practice. Let's get back on track with a quick 5-minute session.`,
        action: {
          type: 'quick_practice',
          duration: 5,
        },
        reason: 'Practice gap detected',
      };
    }

    // Practicing too much in one day (burnout risk)
    const today = new Date().toDateString();
    const todaysPractice = exerciseHistory.filter(e =>
      new Date(e.completed_at).toDateString() === today
    );

    if (todaysPractice.length > 10) {
      return {
        type: this.recommendationTypes.ENERGY_BASED,
        priority: this.priorityLevels.MEDIUM,
        title: 'Take a Break',
        message: `You've completed ${todaysPractice.length} exercises today! Great work! Consider taking a break - quality over quantity.`,
        action: {
          type: 'rest',
        },
        reason: 'Preventing burnout',
      };
    }

    // Suggest consistent practice pattern
    if (streak && streak.current < 3 && exerciseHistory.length > 10) {
      return {
        type: this.recommendationTypes.PRACTICE_FOCUS,
        priority: this.priorityLevels.MEDIUM,
        title: 'Build Consistency',
        message: 'Consistent daily practice (even 10 minutes) is more effective than long irregular sessions. Can you commit to 10 minutes tomorrow?',
        action: {
          type: 'schedule_reminder',
          frequency: 'daily',
          duration: 10,
        },
        reason: 'Building habit consistency',
      };
    }

    return null;
  }

  /**
   * Check if difficulty level needs adjustment
   */
  checkDifficultyLevel(exerciseHistory, userProfile) {
    if (!exerciseHistory || exerciseHistory.length < 5) return null;

    const recent = exerciseHistory.slice(0, 10);
    const avgScore = recent.reduce((sum, e) => sum + (e.score || 0), 0) / recent.length;

    // Too easy (consistently scoring 90+)
    if (avgScore >= 90) {
      return {
        type: this.recommendationTypes.DIFFICULTY_ADJUSTMENT,
        priority: this.priorityLevels.HIGH,
        title: 'Ready for a Challenge?',
        message: `You're averaging ${Math.round(avgScore)}% on recent exercises. You're ready for more advanced content!`,
        action: {
          type: 'increase_difficulty',
          currentLevel: userProfile.current_level,
        },
        reason: 'Consistently high scores indicate readiness for advancement',
      };
    }

    // Too hard (struggling with <50%)
    if (avgScore < 50) {
      return {
        type: this.recommendationTypes.DIFFICULTY_ADJUSTMENT,
        priority: this.priorityLevels.HIGH,
        title: 'Let\'s Adjust Difficulty',
        message: `You're averaging ${Math.round(avgScore)}%. Let's practice with slightly easier content to build confidence.`,
        action: {
          type: 'decrease_difficulty',
          currentLevel: userProfile.current_level,
        },
        reason: 'Low scores suggest content is too challenging',
      };
    }

    return null;
  }

  /**
   * Generate recommendations based on error patterns
   */
  generateErrorPatternRecommendations(mistakes) {
    if (!mistakes || mistakes.length === 0) return [];

    const recentMistakes = mistakes.slice(0, 20);
    const analysis = patternRecognition.aggregatePatterns(recentMistakes);
    const recurringPatterns = patternRecognition.identifyRecurringPatterns(analysis.patterns, 3);

    const recommendations = [];

    for (const pattern of recurringPatterns.slice(0, 3)) { // Top 3 patterns
      const strategy = patternRecognition.generateCorrectionStrategy(pattern);

      recommendations.push({
        type: this.recommendationTypes.ERROR_PATTERN,
        priority: this.priorityLevels.HIGH,
        title: `Focus on ${pattern.category.replace('_', ' ').toUpperCase()}`,
        message: `You've made ${pattern.count} ${pattern.category} errors recently. ${strategy}`,
        action: {
          type: 'targeted_practice',
          focus: pattern.category,
          exerciseCount: 5,
        },
        reason: `Recurring error pattern: ${pattern.pattern}`,
        examples: pattern.examples.slice(0, 2),
      });
    }

    return recommendations;
  }

  /**
   * Generate vocabulary-related recommendations
   */
  generateVocabularyRecommendations(vocabularyMastery, exerciseHistory) {
    if (!vocabularyMastery || vocabularyMastery.length === 0) return [];

    const recommendations = [];

    // Find words due for review
    const dueForReview = vocabularyMastery.filter(v => {
      if (!v.next_review) return true;
      return new Date(v.next_review) <= new Date();
    });

    if (dueForReview.length > 0) {
      recommendations.push({
        type: this.recommendationTypes.REVIEW_REMINDER,
        priority: this.priorityLevels.MEDIUM,
        title: 'Vocabulary Review Time',
        message: `You have ${dueForReview.length} words ready for review. A quick 5-minute session will strengthen your memory!`,
        action: {
          type: 'vocabulary_review',
          wordCount: dueForReview.length,
        },
        reason: 'Spaced repetition schedule',
      });
    }

    // Find avoided words
    const avoidedWords = patternRecognition.detectAvoidedWords(
      exerciseHistory || [],
      vocabularyMastery
    );

    if (avoidedWords.length > 0) {
      const topAvoided = avoidedWords.slice(0, 3);
      recommendations.push({
        type: this.recommendationTypes.VOCABULARY_USE,
        priority: this.priorityLevels.MEDIUM,
        title: 'Use Your Vocabulary',
        message: `You learned "${topAvoided.map(w => w.word).join('", "')}" but haven't used them yet. Let's practice!`,
        action: {
          type: 'vocabulary_practice',
          words: topAvoided.map(w => w.word),
        },
        reason: 'Inactive vocabulary detected',
      });
    }

    return recommendations;
  }

  /**
   * Generate time-based recommendations
   */
  generateTimeRecommendations(sessionPerformance) {
    if (!sessionPerformance || sessionPerformance.length < 5) return null;

    // Analyze performance by time of day
    const timeAnalysis = {};

    for (const session of sessionPerformance) {
      const time = session.time_of_day || 'unknown';
      if (!timeAnalysis[time]) {
        timeAnalysis[time] = {
          count: 0,
          totalScore: 0,
          totalFocus: 0,
        };
      }

      timeAnalysis[time].count++;
      timeAnalysis[time].totalScore += session.average_score || 0;
      timeAnalysis[time].totalFocus += session.focus_quality || 0;
    }

    // Find best time
    let bestTime = null;
    let bestScore = 0;

    for (const [time, data] of Object.entries(timeAnalysis)) {
      if (data.count >= 2) { // Need at least 2 sessions to be significant
        const avgScore = data.totalScore / data.count;
        if (avgScore > bestScore) {
          bestScore = avgScore;
          bestTime = time;
        }
      }
    }

    if (bestTime && bestScore > 0) {
      return {
        type: this.recommendationTypes.TIME_OPTIMIZATION,
        priority: this.priorityLevels.LOW,
        title: 'Optimize Your Practice Time',
        message: `Your performance is best during ${bestTime} (avg: ${Math.round(bestScore)}%). Consider practicing at this time regularly!`,
        action: {
          type: 'schedule_reminder',
          preferredTime: bestTime,
        },
        reason: 'Performance analysis by time of day',
      };
    }

    return null;
  }

  /**
   * Check if user needs recovery mode (struggling)
   */
  checkForRecoveryMode(exerciseHistory) {
    if (!exerciseHistory || exerciseHistory.length < 3) return null;

    const recent = exerciseHistory.slice(0, 5);
    const failures = recent.filter(e => (e.score || 0) < 40);

    if (failures.length >= 3) {
      return {
        type: this.recommendationTypes.RECOVERY,
        priority: this.priorityLevels.CRITICAL,
        title: 'Let\'s Take a Step Back',
        message: 'You seem to be struggling with recent exercises. No worries! Let\'s review the basics to rebuild your confidence.',
        action: {
          type: 'recovery_mode',
          reviewTopics: true,
          easierDifficulty: true,
        },
        reason: 'Multiple consecutive low scores detected',
      };
    }

    return null;
  }

  /**
   * Generate milestone progress recommendations
   */
  generateMilestoneRecommendations(userData) {
    const recommendations = [];

    // Check vocabulary milestone
    const vocabMastered = (userData.vocabularyMastery || []).filter(v => v.mastery_level >= 80).length;
    if (vocabMastered >= 90 && vocabMastered < 100) {
      recommendations.push({
        type: this.recommendationTypes.MILESTONE_PROGRESS,
        priority: this.priorityLevels.MEDIUM,
        title: 'Almost There!',
        message: `You're ${100 - vocabMastered} words away from mastering your first 100 words! Keep going!`,
        action: {
          type: 'vocabulary_practice',
          remaining: 100 - vocabMastered,
        },
        reason: 'Approaching milestone',
      });
    }

    // Check streak milestone
    if (userData.streak && userData.streak.current >= 6 && userData.streak.current < 7) {
      recommendations.push({
        type: this.recommendationTypes.MILESTONE_PROGRESS,
        priority: this.priorityLevels.HIGH,
        title: 'One Day to 7-Day Streak!',
        message: 'You\'re one day away from a 7-day streak! Don\'t break it now!',
        action: {
          type: 'practice_reminder',
          urgency: 'high',
        },
        reason: 'Streak milestone approaching',
      });
    }

    return recommendations;
  }

  /**
   * Filter recommendations based on user preferences and history
   */
  filterRecommendations(recommendations, dismissedRecommendations = []) {
    // Remove recently dismissed recommendations
    const dismissedTypes = new Set(
      dismissedRecommendations
        .filter(d => this.daysSince(d.created_at) < 7)
        .map(d => d.recommendation_type)
    );

    return recommendations.filter(rec => !dismissedTypes.has(rec.type));
  }

  /**
   * Get priority recommendation for "What to practice now?"
   */
  getPriorityRecommendation(recommendations) {
    if (!recommendations || recommendations.length === 0) {
      return {
        type: 'general',
        priority: this.priorityLevels.MEDIUM,
        title: 'Choose Your Practice',
        message: 'All skills look good! Pick any module you\'d like to practice today.',
        action: {
          type: 'free_choice',
        },
      };
    }

    return recommendations[0]; // Highest priority after sorting
  }

  /**
   * Helper: Calculate days since a date
   */
  daysSince(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  }
}

export default new RecommendationEngine();
