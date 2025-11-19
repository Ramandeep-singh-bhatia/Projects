/**
 * Advanced Analytics & Insights Service
 * Provides deep learning insights, velocity tracking, retention analysis, and projections
 */

class AdvancedAnalyticsService {
  constructor() {
    this.cefr_levels = {
      A1: { min: 0, max: 20, description: 'Beginner' },
      A2: { min: 20, max: 40, description: 'Elementary' },
      B1: { min: 40, max: 60, description: 'Intermediate' },
      B2: { min: 60, max: 75, description: 'Upper Intermediate' },
      C1: { min: 75, max: 90, description: 'Advanced' },
      C2: { min: 90, max: 100, description: 'Proficient' },
    };

    this.skill_categories = ['vocabulary', 'grammar', 'speaking', 'writing', 'listening', 'reading'];
  }

  /**
   * Calculate learning velocity (rate of improvement over time)
   */
  calculateLearningVelocity(exerciseHistory, timeframe = 30) {
    if (!exerciseHistory || exerciseHistory.length < 2) {
      return {
        velocity: 0,
        trend: 'insufficient_data',
        pointsPerWeek: 0,
        acceleration: 0,
      };
    }

    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - timeframe);

    const recentExercises = exerciseHistory
      .filter(e => new Date(e.completed_at) >= cutoffDate)
      .sort((a, b) => new Date(a.completed_at) - new Date(b.completed_at));

    if (recentExercises.length < 2) {
      return { velocity: 0, trend: 'insufficient_data', pointsPerWeek: 0, acceleration: 0 };
    }

    // Calculate velocity as improvement rate
    const firstHalf = recentExercises.slice(0, Math.floor(recentExercises.length / 2));
    const secondHalf = recentExercises.slice(Math.floor(recentExercises.length / 2));

    const firstAvg = firstHalf.reduce((sum, e) => sum + (e.score || 0), 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((sum, e) => sum + (e.score || 0), 0) / secondHalf.length;

    const improvement = secondAvg - firstAvg;
    const days = timeframe;
    const pointsPerWeek = (improvement / days) * 7;

    // Calculate acceleration (comparing velocity to previous period)
    const previousCutoff = new Date(cutoffDate);
    previousCutoff.setDate(previousCutoff.getDate() - timeframe);

    const previousExercises = exerciseHistory
      .filter(e => {
        const date = new Date(e.completed_at);
        return date >= previousCutoff && date < cutoffDate;
      });

    let acceleration = 0;
    if (previousExercises.length >= 2) {
      const prevAvg = previousExercises.reduce((sum, e) => sum + (e.score || 0), 0) / previousExercises.length;
      const prevImprovement = firstAvg - prevAvg;
      acceleration = improvement - prevImprovement;
    }

    return {
      velocity: Math.round(pointsPerWeek * 10) / 10,
      trend: pointsPerWeek > 0 ? 'improving' : pointsPerWeek < 0 ? 'declining' : 'stable',
      pointsPerWeek: Math.round(pointsPerWeek * 10) / 10,
      acceleration: Math.round(acceleration * 10) / 10,
      currentPeriodAvg: Math.round(secondAvg),
      previousPeriodAvg: Math.round(firstAvg),
      interpretation: this.interpretVelocity(pointsPerWeek, acceleration),
    };
  }

  /**
   * Interpret velocity metrics
   */
  interpretVelocity(pointsPerWeek, acceleration) {
    if (pointsPerWeek > 2 && acceleration > 0) {
      return 'Excellent! Your learning is accelerating rapidly.';
    } else if (pointsPerWeek > 1) {
      return 'Great progress! You\'re improving steadily.';
    } else if (pointsPerWeek > 0) {
      return 'Slow but steady progress. Keep going!';
    } else if (pointsPerWeek === 0) {
      return 'Your performance is stable. Consider trying new challenge levels.';
    } else {
      return 'Recent scores have dipped. This is normal - take a break or review basics.';
    }
  }

  /**
   * Generate retention heatmap data
   */
  generateRetentionHeatmap(vocabularyMastery, exerciseHistory, daysBack = 90) {
    const heatmapData = [];
    const today = new Date();

    // Create array of last N days
    for (let i = daysBack - 1; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];

      // Check if practiced that day
      const dayExercises = exerciseHistory.filter(e =>
        e.completed_at.startsWith(dateStr)
      );

      // Calculate retention score for that day
      let retentionScore = 0;
      if (dayExercises.length > 0) {
        // Base retention on average score
        retentionScore = dayExercises.reduce((sum, e) => sum + (e.score || 0), 0) / dayExercises.length;
      } else {
        // No practice = retention decay
        retentionScore = 0;
      }

      heatmapData.push({
        date: dateStr,
        dayOfWeek: date.getDay(),
        weekOfYear: this.getWeekNumber(date),
        exerciseCount: dayExercises.length,
        retentionScore: Math.round(retentionScore),
        intensity: this.calculateIntensity(dayExercises.length, retentionScore),
      });
    }

    return {
      heatmap: heatmapData,
      summary: this.summarizeHeatmap(heatmapData),
    };
  }

  /**
   * Calculate practice intensity
   */
  calculateIntensity(exerciseCount, retentionScore) {
    if (exerciseCount === 0) return 0;
    if (exerciseCount >= 10 && retentionScore >= 80) return 5; // Very high
    if (exerciseCount >= 7 && retentionScore >= 70) return 4; // High
    if (exerciseCount >= 4 && retentionScore >= 60) return 3; // Medium
    if (exerciseCount >= 2 && retentionScore >= 50) return 2; // Low
    return 1; // Very low
  }

  /**
   * Summarize heatmap patterns
   */
  summarizeHeatmap(heatmapData) {
    const practiceDays = heatmapData.filter(d => d.exerciseCount > 0);
    const totalDays = heatmapData.length;
    const consistency = (practiceDays.length / totalDays) * 100;

    // Find best day of week
    const dayStats = {};
    heatmapData.forEach(d => {
      if (!dayStats[d.dayOfWeek]) {
        dayStats[d.dayOfWeek] = { count: 0, totalScore: 0 };
      }
      if (d.exerciseCount > 0) {
        dayStats[d.dayOfWeek].count++;
        dayStats[d.dayOfWeek].totalScore += d.retentionScore;
      }
    });

    let bestDay = null;
    let bestDayScore = 0;
    const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

    Object.entries(dayStats).forEach(([day, stats]) => {
      if (stats.count > 0) {
        const avgScore = stats.totalScore / stats.count;
        if (avgScore > bestDayScore) {
          bestDayScore = avgScore;
          bestDay = dayNames[parseInt(day)];
        }
      }
    });

    // Find longest streak
    let currentStreak = 0;
    let longestStreak = 0;

    heatmapData.forEach(d => {
      if (d.exerciseCount > 0) {
        currentStreak++;
        longestStreak = Math.max(longestStreak, currentStreak);
      } else {
        currentStreak = 0;
      }
    });

    return {
      totalDays,
      practiceDays: practiceDays.length,
      consistency: Math.round(consistency),
      bestDay: bestDay || 'N/A',
      longestStreak,
      averageIntensity: practiceDays.length > 0
        ? Math.round((practiceDays.reduce((sum, d) => sum + d.intensity, 0) / practiceDays.length) * 10) / 10
        : 0,
    };
  }

  /**
   * Identify optimal learning times
   */
  identifyOptimalLearningTimes(sessionPerformance) {
    if (!sessionPerformance || sessionPerformance.length < 5) {
      return {
        optimalTime: null,
        recommendation: 'Not enough data yet. Practice at different times to find your peak performance window.',
      };
    }

    // Group by time of day
    const timeGroups = {
      early_morning: { scores: [], focus: [], count: 0 }, // 5-8 AM
      morning: { scores: [], focus: [], count: 0 },       // 8-12 PM
      afternoon: { scores: [], focus: [], count: 0 },     // 12-5 PM
      evening: { scores: [], focus: [], count: 0 },       // 5-9 PM
      night: { scores: [], focus: [], count: 0 },         // 9 PM - 12 AM
    };

    sessionPerformance.forEach(session => {
      const time = session.time_of_day || 'unknown';
      if (timeGroups[time]) {
        timeGroups[time].scores.push(session.average_score || 0);
        timeGroups[time].focus.push(session.focus_quality || 0);
        timeGroups[time].count++;
      }
    });

    // Calculate averages and find optimal time
    const results = [];

    Object.entries(timeGroups).forEach(([time, data]) => {
      if (data.count >= 2) {
        const avgScore = data.scores.reduce((a, b) => a + b, 0) / data.count;
        const avgFocus = data.focus.reduce((a, b) => a + b, 0) / data.count;
        const combinedScore = (avgScore + avgFocus) / 2;

        results.push({
          time,
          avgScore: Math.round(avgScore),
          avgFocus: Math.round(avgFocus),
          combinedScore: Math.round(combinedScore),
          sessionCount: data.count,
        });
      }
    });

    results.sort((a, b) => b.combinedScore - a.combinedScore);

    if (results.length === 0) {
      return {
        optimalTime: null,
        recommendation: 'Practice at different times to identify your peak learning window.',
      };
    }

    const best = results[0];
    const timeLabels = {
      early_morning: '5-8 AM',
      morning: '8 AM-12 PM',
      afternoon: '12-5 PM',
      evening: '5-9 PM',
      night: '9 PM-12 AM',
    };

    return {
      optimalTime: best.time,
      optimalTimeLabel: timeLabels[best.time],
      performanceScore: best.combinedScore,
      allTimes: results,
      recommendation: `You perform best during ${timeLabels[best.time]} (score: ${best.combinedScore}). Try to schedule important practice sessions during this window.`,
    };
  }

  /**
   * Generate skill radar chart data
   */
  generateSkillRadar(learningProgress, exerciseHistory) {
    const skills = {};

    // Initialize from learning progress
    if (learningProgress) {
      learningProgress.forEach(progress => {
        skills[progress.skill_type] = progress.score || 0;
      });
    }

    // Enhance with exercise history analysis
    if (exerciseHistory) {
      this.skill_categories.forEach(skill => {
        const skillExercises = exerciseHistory.filter(e =>
          e.exercise_type && e.exercise_type.toLowerCase().includes(skill)
        );

        if (skillExercises.length > 0) {
          const avgScore = skillExercises.reduce((sum, e) => sum + (e.score || 0), 0) / skillExercises.length;
          skills[skill] = Math.round(avgScore);
        } else if (!skills[skill]) {
          skills[skill] = 0;
        }
      });
    }

    // Ensure all skill categories are present
    this.skill_categories.forEach(skill => {
      if (!skills[skill]) {
        skills[skill] = 0;
      }
    });

    // Calculate balance score (how balanced are skills)
    const values = Object.values(skills);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const variance = values.reduce((sum, val) => sum + Math.pow(val - avg, 2), 0) / values.length;
    const balanceScore = Math.max(0, 100 - Math.sqrt(variance));

    return {
      skills,
      averageScore: Math.round(avg),
      balanceScore: Math.round(balanceScore),
      strongest: this.findStrongest(skills),
      weakest: this.findWeakest(skills),
      recommendation: this.generateSkillRecommendation(skills, balanceScore),
    };
  }

  /**
   * Compare to CEFR levels
   */
  compareToCEFR(proficiencyScore, skillBreakdown) {
    let currentLevel = 'A1';

    // Determine current CEFR level
    for (const [level, range] of Object.entries(this.cefr_levels)) {
      if (proficiencyScore >= range.min && proficiencyScore < range.max) {
        currentLevel = level;
        break;
      }
    }

    // Determine next level
    const levelOrder = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
    const currentIndex = levelOrder.indexOf(currentLevel);
    const nextLevel = currentIndex < levelOrder.length - 1 ? levelOrder[currentIndex + 1] : null;

    const currentRange = this.cefr_levels[currentLevel];
    const progressInLevel = currentRange.max > currentRange.min
      ? ((proficiencyScore - currentRange.min) / (currentRange.max - currentRange.min)) * 100
      : 0;

    let pointsToNext = 0;
    if (nextLevel) {
      pointsToNext = this.cefr_levels[nextLevel].min - proficiencyScore;
    }

    return {
      currentLevel,
      currentLevelName: currentRange.description,
      nextLevel,
      nextLevelName: nextLevel ? this.cefr_levels[nextLevel].description : 'Mastery Achieved',
      progressInLevel: Math.round(progressInLevel),
      pointsToNext: Math.max(0, pointsToNext),
      proficiencyScore,
      skillAlignment: this.checkSkillAlignment(skillBreakdown, currentLevel),
      strengths: this.identifyLevelStrengths(skillBreakdown, proficiencyScore),
    };
  }

  /**
   * Check if skills align with CEFR level
   */
  checkSkillAlignment(skillBreakdown, cefrLevel) {
    if (!skillBreakdown) return { aligned: true, outliers: [] };

    const expectedRange = this.cefr_levels[cefrLevel];
    const outliers = [];

    Object.entries(skillBreakdown).forEach(([skill, score]) => {
      if (score < expectedRange.min - 10) {
        outliers.push({ skill, score, status: 'below_level' });
      } else if (score > expectedRange.max + 10) {
        outliers.push({ skill, score, status: 'above_level' });
      }
    });

    return {
      aligned: outliers.length === 0,
      outliers,
      recommendation: outliers.length > 0
        ? `Focus on improving ${outliers.filter(o => o.status === 'below_level').map(o => o.skill).join(', ')} to match your overall level.`
        : 'All skills are well-aligned with your CEFR level.',
    };
  }

  /**
   * Identify level-specific strengths
   */
  identifyLevelStrengths(skillBreakdown, proficiencyScore) {
    const strengths = [];

    if (proficiencyScore >= 60) strengths.push('Can handle complex conversations');
    if (proficiencyScore >= 70) strengths.push('Can express ideas fluently');
    if (proficiencyScore >= 80) strengths.push('Can use language flexibly');
    if (proficiencyScore >= 90) strengths.push('Near-native proficiency');

    return strengths;
  }

  /**
   * Project learning timeline
   */
  projectLearningTimeline(currentScore, targetScore, learningVelocity, consistency) {
    if (currentScore >= targetScore) {
      return {
        achieved: true,
        message: 'Target already achieved!',
      };
    }

    if (learningVelocity.pointsPerWeek <= 0) {
      return {
        achievable: false,
        message: 'Current progress trend is not positive. Adjust your learning strategy.',
        recommendation: 'Consider increasing practice frequency or trying different exercise types.',
      };
    }

    const pointsNeeded = targetScore - currentScore;
    const weeksNeeded = pointsNeeded / learningVelocity.pointsPerWeek;

    // Adjust for consistency
    const consistencyFactor = consistency / 100;
    const adjustedWeeks = weeksNeeded / Math.max(consistencyFactor, 0.3); // Minimum 30% consistency

    const estimatedDate = new Date();
    estimatedDate.setDate(estimatedDate.getDate() + adjustedWeeks * 7);

    // Calculate confidence level
    const confidence = this.calculateProjectionConfidence(learningVelocity, consistency);

    return {
      achievable: true,
      pointsNeeded,
      estimatedWeeks: Math.ceil(adjustedWeeks),
      estimatedDate: estimatedDate.toISOString().split('T')[0],
      confidence,
      recommendation: this.generateTimelineRecommendation(adjustedWeeks, confidence, consistency),
      milestones: this.generateMilestones(currentScore, targetScore, adjustedWeeks),
    };
  }

  /**
   * Calculate projection confidence
   */
  calculateProjectionConfidence(learningVelocity, consistency) {
    let confidence = 50; // Base confidence

    // Velocity trend
    if (learningVelocity.trend === 'improving') confidence += 20;
    if (learningVelocity.acceleration > 0) confidence += 10;

    // Consistency
    if (consistency >= 80) confidence += 20;
    else if (consistency >= 60) confidence += 10;
    else if (consistency < 40) confidence -= 20;

    return Math.max(10, Math.min(95, confidence));
  }

  /**
   * Generate timeline recommendation
   */
  generateTimelineRecommendation(weeks, confidence, consistency) {
    if (confidence >= 70 && consistency >= 70) {
      return `You're on track! Maintain your current pace and you'll reach your goal in about ${Math.ceil(weeks)} weeks.`;
    } else if (confidence >= 50) {
      return `You can reach your goal in ${Math.ceil(weeks)} weeks if you improve consistency to 80%+.`;
    } else {
      return `To reach your goal faster, increase practice frequency and focus on weak areas. Current timeline: ${Math.ceil(weeks)} weeks.`;
    }
  }

  /**
   * Generate milestone markers
   */
  generateMilestones(currentScore, targetScore, totalWeeks) {
    const milestones = [];
    const pointsDiff = targetScore - currentScore;
    const milestoneCount = 4;

    for (let i = 1; i <= milestoneCount; i++) {
      const percentage = i / milestoneCount;
      const score = Math.round(currentScore + (pointsDiff * percentage));
      const week = Math.round(totalWeeks * percentage);

      milestones.push({
        score,
        week,
        description: this.getMilestoneDescription(score),
      });
    }

    return milestones;
  }

  /**
   * Get milestone description
   */
  getMilestoneDescription(score) {
    if (score >= 90) return 'Near-native proficiency';
    if (score >= 80) return 'Advanced level';
    if (score >= 70) return 'Upper intermediate';
    if (score >= 60) return 'Intermediate level';
    if (score >= 40) return 'Elementary level';
    return 'Basic level';
  }

  /**
   * Analyze strengths and weaknesses in detail
   */
  analyzeStrengthsWeaknesses(learningProgress, exerciseHistory, mistakes) {
    const analysis = {
      strengths: [],
      weaknesses: [],
      opportunities: [],
      recommendations: [],
    };

    // Analyze by skill
    if (learningProgress) {
      learningProgress.forEach(progress => {
        if (progress.score >= 75) {
          analysis.strengths.push({
            area: progress.skill_type,
            score: progress.score,
            reason: `Strong performance in ${progress.skill_type}`,
          });
        } else if (progress.score < 50) {
          analysis.weaknesses.push({
            area: progress.skill_type,
            score: progress.score,
            reason: `Needs improvement in ${progress.skill_type}`,
          });
        }
      });
    }

    // Analyze mistake patterns
    if (mistakes && mistakes.length > 0) {
      const mistakeCategories = {};
      mistakes.forEach(m => {
        const category = m.mistake_category || 'general';
        mistakeCategories[category] = (mistakeCategories[category] || 0) + 1;
      });

      Object.entries(mistakeCategories)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
        .forEach(([category, count]) => {
          analysis.weaknesses.push({
            area: category,
            count,
            reason: `Frequent ${category} errors (${count} times)`,
          });
        });
    }

    // Identify opportunities
    const skillScores = learningProgress ? learningProgress.map(p => p.score) : [];
    const avgScore = skillScores.length > 0
      ? skillScores.reduce((a, b) => a + b, 0) / skillScores.length
      : 0;

    if (avgScore >= 60 && avgScore < 75) {
      analysis.opportunities.push({
        type: 'advancement',
        description: 'Ready to advance to upper intermediate level',
      });
    }

    // Generate recommendations
    analysis.weaknesses.slice(0, 3).forEach(weakness => {
      analysis.recommendations.push({
        focus: weakness.area,
        action: `Practice ${weakness.area} exercises for 15 minutes daily`,
        priority: 'high',
      });
    });

    return analysis;
  }

  /**
   * Helper methods
   */
  getWeekNumber(date) {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = d.getUTCDay() || 7;
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
  }

  findStrongest(skills) {
    let max = -1;
    let strongest = null;
    Object.entries(skills).forEach(([skill, score]) => {
      if (score > max) {
        max = score;
        strongest = skill;
      }
    });
    return { skill: strongest, score: max };
  }

  findWeakest(skills) {
    let min = 101;
    let weakest = null;
    Object.entries(skills).forEach(([skill, score]) => {
      if (score < min) {
        min = score;
        weakest = skill;
      }
    });
    return { skill: weakest, score: min };
  }

  generateSkillRecommendation(skills, balanceScore) {
    if (balanceScore >= 80) {
      return 'Your skills are well-balanced! Continue practicing all areas equally.';
    } else if (balanceScore >= 60) {
      const weakest = this.findWeakest(skills);
      return `Focus more on ${weakest.skill} to improve skill balance.`;
    } else {
      const weakest = this.findWeakest(skills);
      return `Your ${weakest.skill} (${weakest.score}) needs significant attention to balance your skills.`;
    }
  }
}

export default new AdvancedAnalyticsService();
