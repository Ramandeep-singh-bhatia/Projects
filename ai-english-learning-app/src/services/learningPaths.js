/**
 * Personalized Learning Paths Service
 * Goal-based tracks, industry-specific modules, custom roadmaps, adaptive paths
 */

class LearningPathsService {
  constructor() {
    this.goalBasedTracks = this.initializeGoalBasedTracks();
    this.industryModules = this.initializeIndustryModules();
    this.skillLevels = ['beginner', 'elementary', 'intermediate', 'upper_intermediate', 'advanced'];
  }

  /**
   * Initialize goal-based learning tracks
   */
  initializeGoalBasedTracks() {
    return {
      job_interview_prep: {
        name: 'Job Interview Preparation',
        duration: '4-6 weeks',
        difficulty: 'intermediate',
        modules: [
          {
            week: 1,
            focus: 'Interview Basics',
            topics: [
              'Common interview questions',
              'STAR method storytelling',
              'Professional vocabulary',
              'Confidence building',
            ],
            exercises: ['Mock interviews', 'Question practice', 'Pronunciation drills'],
          },
          {
            week: 2,
            focus: 'Behavioral Questions',
            topics: [
              'Describing achievements',
              'Discussing weaknesses positively',
              'Team collaboration examples',
              'Problem-solving stories',
            ],
            exercises: ['Story preparation', 'Recording practice', 'Peer review'],
          },
          {
            week: 3,
            focus: 'Technical & Industry-Specific',
            topics: [
              'Industry terminology',
              'Technical explanations',
              'Project discussions',
              'Skills demonstration',
            ],
            exercises: ['Technical vocabulary', 'Explaining complex topics simply'],
          },
          {
            week: 4,
            focus: 'Advanced Techniques',
            topics: [
              'Salary negotiation',
              'Asking smart questions',
              'Following up',
              'Handling difficult questions',
            ],
            exercises: ['Negotiation role-play', 'Question formulation', 'Email writing'],
          },
        ],
        milestones: [
          { week: 2, goal: 'Master 10 common interview questions' },
          { week: 4, goal: 'Complete full mock interview' },
          { week: 6, goal: 'Confident in salary negotiation' },
        ],
      },
      ielts_toefl_prep: {
        name: 'IELTS/TOEFL Preparation',
        duration: '8-12 weeks',
        difficulty: 'intermediate',
        modules: [
          {
            section: 'Speaking',
            weeks: '1-3',
            focus: [
              'Part 1: Personal questions',
              'Part 2: Long turn (2-minute speech)',
              'Part 3: Discussion',
              'Pronunciation & fluency',
            ],
            strategies: [
              'Expanding answers beyond yes/no',
              'Using discourse markers',
              'Time management for Part 2',
              'Expressing opinions clearly',
            ],
          },
          {
            section: 'Writing',
            weeks: '4-6',
            focus: [
              'Task 1: Describing graphs/charts/diagrams',
              'Task 2: Essay writing',
              'Academic vocabulary',
              'Grammar accuracy',
            ],
            strategies: [
              'Essay structures',
              'Paraphrasing techniques',
              'Time management',
              'Coherence and cohesion',
            ],
          },
          {
            section: 'Reading',
            weeks: '7-9',
            focus: [
              'Skimming and scanning',
              'Question types',
              'Academic texts',
              'Time management',
            ],
            strategies: [
              'Identifying key information',
              'Dealing with unknown vocabulary',
              'Question strategies for each type',
            ],
          },
          {
            section: 'Listening',
            weeks: '10-12',
            focus: [
              'Note-taking',
              'Different accents',
              'Multiple speakers',
              'Academic lectures',
            ],
            strategies: [
              'Predicting content',
              'Identifying signpost language',
              'Dealing with distractors',
            ],
          },
        ],
        scoringGoals: {
          beginner: 'Band 5.0-5.5',
          intermediate: 'Band 6.0-7.0',
          advanced: 'Band 7.5+',
        },
      },
      business_english: {
        name: 'Business English Mastery',
        duration: '6-8 weeks',
        difficulty: 'intermediate',
        modules: [
          {
            week: 1,
            focus: 'Email Communication',
            topics: [
              'Professional email structure',
              'Formal vs semi-formal tone',
              'Common phrases and templates',
              'Responding to emails',
            ],
            vocabulary: ['regarding', 'attached', 'further to', 'kindly', 'as per'],
          },
          {
            week: 2,
            focus: 'Meetings',
            topics: [
              'Starting and ending meetings',
              'Agreeing and disagreeing professionally',
              'Making suggestions',
              'Action items and follow-up',
            ],
            vocabulary: ['agenda', 'minutes', 'to table (a topic)', 'to adjourn', 'consensus'],
          },
          {
            week: 3,
            focus: 'Presentations',
            topics: [
              'Opening and closing',
              'Signposting',
              'Handling questions',
              'Visual aids language',
            ],
            vocabulary: ['to outline', 'to elaborate', 'to summarize', 'moving on to', 'in conclusion'],
          },
          {
            week: 4,
            focus: 'Negotiations',
            topics: [
              'Making offers',
              'Counter-offers',
              'Reaching agreement',
              'Diplomatic language',
            ],
            vocabulary: ['leverage', 'win-win', 'compromise', 'terms', 'deal-breaker'],
          },
          {
            week: 5,
            focus: 'Phone Skills',
            topics: [
              'Making and receiving calls',
              'Taking messages',
              'Conference calls',
              'Dealing with problems',
            ],
            vocabulary: ['to put through', 'hold the line', 'can I take a message', 'the line is busy'],
          },
          {
            week: 6,
            focus: 'Networking',
            topics: [
              'Small talk',
              'Self-introduction',
              'Building rapport',
              'Following up',
            ],
            vocabulary: ['What brings you here?', 'What line of work are you in?', 'Let\'s stay in touch'],
          },
        ],
      },
      travel_english: {
        name: 'Travel English Essentials',
        duration: '3-4 weeks',
        difficulty: 'beginner',
        modules: [
          {
            week: 1,
            focus: 'Airport & Transportation',
            situations: [
              'Check-in and boarding',
              'Security and customs',
              'Asking for directions',
              'Public transportation',
              'Taxi/Uber',
            ],
            essentialPhrases: [
              'Where is gate...?',
              'How do I get to...?',
              'How much is the fare?',
              'Can you take me to...?',
            ],
          },
          {
            week: 2,
            focus: 'Accommodation',
            situations: [
              'Hotel check-in/out',
              'Making complaints',
              'Requesting services',
              'Asking about amenities',
            ],
            essentialPhrases: [
              'I have a reservation under...',
              'The air conditioning isn\'t working',
              'What time is breakfast?',
              'Can I get a wake-up call?',
            ],
          },
          {
            week: 3,
            focus: 'Dining Out',
            situations: [
              'Making reservations',
              'Ordering food',
              'Dietary restrictions',
              'Paying the bill',
            ],
            essentialPhrases: [
              'Table for two, please',
              'I\'m allergic to...',
              'What do you recommend?',
              'Can I have the check?',
            ],
          },
          {
            week: 4,
            focus: 'Shopping & Emergencies',
            situations: [
              'Asking for prices',
              'Trying things on',
              'Returning items',
              'Medical emergencies',
              'Lost items',
            ],
            essentialPhrases: [
              'How much is this?',
              'Do you have this in...?',
              'I need to see a doctor',
              'I\'ve lost my passport',
            ],
          },
        ],
      },
      academic_english: {
        name: 'Academic English',
        duration: '8-10 weeks',
        difficulty: 'advanced',
        modules: [
          {
            phase: 'Foundation',
            weeks: '1-3',
            focus: [
              'Academic vocabulary',
              'Formal writing style',
              'Citation and referencing',
              'Critical reading',
            ],
          },
          {
            phase: 'Development',
            weeks: '4-6',
            focus: [
              'Essay structure',
              'Argumentation',
              'Research skills',
              'Note-taking from lectures',
            ],
          },
          {
            phase: 'Advanced',
            weeks: '7-10',
            focus: [
              'Research paper writing',
              'Literature reviews',
              'Academic presentations',
              'Thesis statements',
            ],
          },
        ],
      },
      casual_conversation: {
        name: 'Casual Conversation Fluency',
        duration: '4-6 weeks',
        difficulty: 'beginner',
        modules: [
          {
            week: 1,
            focus: 'Small Talk Basics',
            topics: [
              'Greetings and introductions',
              'Weather talk',
              'Weekend plans',
              'Hobbies and interests',
            ],
          },
          {
            week: 2,
            focus: 'Keeping Conversation Going',
            topics: [
              'Follow-up questions',
              'Showing interest',
              'Sharing experiences',
              'Topic transitions',
            ],
          },
          {
            week: 3,
            focus: 'Expressing Opinions',
            topics: [
              'Agreeing and disagreeing',
              'Giving reasons',
              'Asking for opinions',
              'Discussing current events',
            ],
          },
          {
            week: 4,
            focus: 'Social Situations',
            topics: [
              'Making plans',
              'Declining politely',
              'Showing empathy',
              'Humor and idioms',
            ],
          },
        ],
      },
    };
  }

  /**
   * Initialize industry-specific modules
   */
  initializeIndustryModules() {
    return {
      technology: {
        name: 'Technology & IT',
        vocabulary: [
          { word: 'deploy', definition: 'Release software to production', usage: 'We deployed the new feature yesterday' },
          { word: 'scalability', definition: 'Ability to handle growth', usage: 'This solution offers great scalability' },
          { word: 'agile', definition: 'Iterative development methodology', usage: 'We use agile methodology for our projects' },
          { word: 'API', definition: 'Application Programming Interface', usage: 'The API allows different systems to communicate' },
          { word: 'debugging', definition: 'Finding and fixing errors', usage: 'I spent the morning debugging the code' },
        ],
        commonPhrases: [
          'Let\'s circle back on that',
          'We\'re looking to scale this',
          'This is a blocker for...',
          'Let\'s sync up later',
          'We need to optimize...',
        ],
        scenarios: [
          'Stand-up meeting',
          'Code review',
          'Client demo',
          'Sprint planning',
        ],
      },
      healthcare: {
        name: 'Healthcare & Medical',
        vocabulary: [
          { word: 'diagnosis', definition: 'Identification of illness', usage: 'The doctor gave her a diagnosis' },
          { word: 'prognosis', definition: 'Expected outcome', usage: 'The prognosis is positive' },
          { word: 'symptoms', definition: 'Signs of illness', usage: 'What symptoms are you experiencing?' },
          { word: 'prescription', definition: 'Doctor\'s order for medication', usage: 'Here\'s your prescription' },
          { word: 'procedure', definition: 'Medical operation or process', usage: 'The procedure will take an hour' },
        ],
        commonPhrases: [
          'What brings you in today?',
          'How long have you had these symptoms?',
          'Take this medication twice daily',
          'Let\'s schedule a follow-up',
          'Any allergies I should know about?',
        ],
        scenarios: [
          'Patient consultation',
          'Explaining treatment',
          'Taking medical history',
          'Hospital rounds',
        ],
      },
      finance: {
        name: 'Finance & Banking',
        vocabulary: [
          { word: 'liquidity', definition: 'Available cash or assets', usage: 'The company has good liquidity' },
          { word: 'portfolio', definition: 'Collection of investments', usage: 'Let\'s review your investment portfolio' },
          { word: 'ROI', definition: 'Return on Investment', usage: 'What\'s the expected ROI?' },
          { word: 'assets', definition: 'Valuable possessions', usage: 'The company\'s assets have grown' },
          { word: 'fiscal', definition: 'Related to government revenue', usage: 'The fiscal year ends in December' },
        ],
        commonPhrases: [
          'Let\'s look at the bottom line',
          'What\'s the cash flow situation?',
          'We need to diversify',
          'Let\'s run the numbers',
          'What\'s the projected growth?',
        ],
        scenarios: [
          'Client consultation',
          'Quarterly review',
          'Investment presentation',
          'Budget meeting',
        ],
      },
      marketing: {
        name: 'Marketing & Sales',
        vocabulary: [
          { word: 'engagement', definition: 'Audience interaction', usage: 'Our engagement rate has increased' },
          { word: 'conversion', definition: 'Turning prospects to customers', usage: 'We improved our conversion rate' },
          { word: 'segmentation', definition: 'Dividing market into groups', usage: 'We use demographic segmentation' },
          { word: 'ROI', definition: 'Return on Investment', usage: 'What\'s the ROI on this campaign?' },
          { word: 'brand awareness', definition: 'Public recognition of brand', usage: 'We\'re building brand awareness' },
        ],
        commonPhrases: [
          'Let\'s target this demographic',
          'What\'s our unique selling point?',
          'We need to increase visibility',
          'Let\'s A/B test this',
          'What\'s the customer journey?',
        ],
        scenarios: [
          'Campaign planning',
          'Client pitch',
          'Market analysis',
          'Brand strategy meeting',
        ],
      },
      education: {
        name: 'Education & Teaching',
        vocabulary: [
          { word: 'pedagogy', definition: 'Teaching methods', usage: 'We focus on student-centered pedagogy' },
          { word: 'curriculum', definition: 'Course content and structure', usage: 'The curriculum covers all required topics' },
          { word: 'assessment', definition: 'Evaluation of learning', usage: 'We use formative assessment' },
          { word: 'differentiation', definition: 'Adapting to different learners', usage: 'Differentiation is key in our classroom' },
          { word: 'engagement', definition: 'Student participation', usage: 'Student engagement has improved' },
        ],
        commonPhrases: [
          'Let\'s scaffold this lesson',
          'We need to check for understanding',
          'Let\'s differentiate instruction',
          'What\'s the learning objective?',
          'Let\'s use formative assessment',
        ],
        scenarios: [
          'Lesson planning',
          'Parent-teacher conference',
          'Faculty meeting',
          'Student feedback',
        ],
      },
    };
  }

  /**
   * Generate personalized learning path
   */
  generatePersonalizedPath(userGoal, currentLevel, timeCommitment, industryFocus = null) {
    const track = this.goalBasedTracks[userGoal];

    if (!track) {
      return {
        error: 'Goal not found',
        available: Object.keys(this.goalBasedTracks),
      };
    }

    // Adjust based on level
    const adjustedDuration = this.adjustDurationForLevel(track.duration, currentLevel, track.difficulty);

    // Create weekly plan
    const weeklyPlan = this.createWeeklyPlan(track, currentLevel, timeCommitment);

    // Add industry-specific content if relevant
    if (industryFocus && this.industryModules[industryFocus]) {
      weeklyPlan.industryModule = this.industryModules[industryFocus];
    }

    return {
      id: Date.now(),
      goal: userGoal,
      trackName: track.name,
      currentLevel,
      estimatedDuration: adjustedDuration,
      timeCommitmentPerWeek: timeCommitment,
      weeklyPlan,
      milestones: track.milestones || this.generateMilestones(weeklyPlan),
      nextSteps: this.getNextSteps(weeklyPlan, 0),
      progressTracking: {
        currentWeek: 1,
        completedModules: 0,
        totalModules: weeklyPlan.length,
        estimatedCompletion: this.calculateCompletionDate(adjustedDuration),
      },
    };
  }

  /**
   * Adjust duration based on level
   */
  adjustDurationForLevel(baseDuration, userLevel, trackDifficulty) {
    const levelIndex = this.skillLevels.indexOf(userLevel);
    const difficultyIndex = this.skillLevels.indexOf(trackDifficulty);

    const gap = difficultyIndex - levelIndex;

    // Parse duration (e.g., "4-6 weeks")
    const weeks = parseInt(baseDuration.match(/\d+/)[0]);

    if (gap > 1) {
      // User below track level - add time
      return `${weeks + 2}-${weeks + 4} weeks`;
    } else if (gap < -1) {
      // User above track level - reduce time
      return `${Math.max(2, weeks - 2)}-${Math.max(3, weeks - 1)} weeks`;
    }

    return baseDuration;
  }

  /**
   * Create weekly plan
   */
  createWeeklyPlan(track, level, timeCommitment) {
    const plan = [];

    // Convert track modules to weekly plan
    if (track.modules) {
      track.modules.forEach((module, index) => {
        plan.push({
          week: index + 1,
          focus: module.focus || module.section,
          topics: module.topics || module.focus,
          exercises: module.exercises || this.generateExercisesForTopics(module.topics),
          estimatedTime: this.calculateModuleTime(module, timeCommitment),
          checkpoints: this.generateCheckpoints(module),
        });
      });
    }

    return plan;
  }

  /**
   * Generate exercises for topics
   */
  generateExercisesForTopics(topics) {
    if (!topics) return [];

    return topics.slice(0, 3).map(topic => ({
      type: 'practice',
      topic: topic,
      duration: 15,
    }));
  }

  /**
   * Calculate module time
   */
  calculateModuleTime(module, weeklyCommitment) {
    const hoursPerWeek = parseInt(weeklyCommitment) || 5;
    const topicCount = module.topics?.length || module.focus?.length || 3;

    return {
      total: `${hoursPerWeek} hours/week`,
      perTopic: `${Math.round((hoursPerWeek / topicCount) * 10) / 10} hours/topic`,
    };
  }

  /**
   * Generate checkpoints
   */
  generateCheckpoints(module) {
    return [
      `Complete all ${module.topics?.length || 3} topic exercises`,
      'Score 70%+ on module quiz',
      'Practice speaking exercises',
    ];
  }

  /**
   * Generate milestones
   */
  generateMilestones(weeklyPlan) {
    const milestones = [];
    const quarterPoints = [
      Math.floor(weeklyPlan.length * 0.25),
      Math.floor(weeklyPlan.length * 0.5),
      Math.floor(weeklyPlan.length * 0.75),
      weeklyPlan.length,
    ];

    const descriptions = [
      'Foundation completed',
      'Halfway there - skills developing',
      'Advanced concepts mastered',
      'Goal achieved!',
    ];

    quarterPoints.forEach((week, index) => {
      milestones.push({
        week,
        goal: descriptions[index],
      });
    });

    return milestones;
  }

  /**
   * Get next steps
   */
  getNextSteps(weeklyPlan, currentWeek) {
    if (currentWeek >= weeklyPlan.length) {
      return ['Congratulations! Path completed', 'Review and practice', 'Consider next goal'];
    }

    const current = weeklyPlan[currentWeek];
    return [
      `Focus on: ${current.focus}`,
      `Complete ${current.topics?.length || 0} topic areas`,
      `Practice: ${current.exercises?.[0]?.topic || 'exercises'}`,
    ];
  }

  /**
   * Calculate completion date
   */
  calculateCompletionDate(duration) {
    const weeks = parseInt(duration.match(/\d+/)?.[0]) || 4;
    const date = new Date();
    date.setDate(date.getDate() + weeks * 7);

    return date.toISOString().split('T')[0];
  }

  /**
   * Get industry-specific module
   */
  getIndustryModule(industry) {
    const module = this.industryModules[industry];

    if (!module) {
      return {
        error: 'Industry not found',
        available: Object.keys(this.industryModules),
      };
    }

    return {
      ...module,
      studyPlan: {
        week1: 'Master essential vocabulary (15 words)',
        week2: 'Practice common phrases in context',
        week3: 'Role-play industry scenarios',
        week4: 'Real-world application and assessment',
      },
      assessment: this.generateIndustryAssessment(industry),
    };
  }

  /**
   * Generate industry assessment
   */
  generateIndustryAssessment(industry) {
    const module = this.industryModules[industry];

    return {
      vocabularyTest: `Define and use ${module.vocabulary.length} key terms`,
      scenarioTest: `Complete role-play in ${module.scenarios[0]}`,
      writingTask: `Write a professional email using industry terminology`,
      speakingTask: `Present a 2-minute overview of a ${industry} topic`,
    };
  }

  /**
   * Track path progress
   */
  trackPathProgress(pathId, weekCompleted, score, timeSpent) {
    const progress = this.getPathProgress();

    const existing = progress.find(p => p.pathId === pathId);

    if (existing) {
      existing.weeksCompleted.push(weekCompleted);
      existing.scores.push(score);
      existing.totalTimeSpent += timeSpent;
      existing.lastUpdated = new Date().toISOString();
    } else {
      progress.push({
        pathId,
        weeksCompleted: [weekCompleted],
        scores: [score],
        totalTimeSpent: timeSpent,
        startedAt: new Date().toISOString(),
        lastUpdated: new Date().toISOString(),
      });
    }

    localStorage.setItem('learning_path_progress', JSON.stringify(progress));

    return this.calculatePathStats(pathId);
  }

  /**
   * Get path progress
   */
  getPathProgress() {
    const stored = localStorage.getItem('learning_path_progress');
    return stored ? JSON.parse(stored) : [];
  }

  /**
   * Calculate path statistics
   */
  calculatePathStats(pathId) {
    const progress = this.getPathProgress();
    const pathProgress = progress.find(p => p.pathId === pathId);

    if (!pathProgress) {
      return {
        weeksCompleted: 0,
        averageScore: 0,
        totalTime: 0,
      };
    }

    const avgScore = pathProgress.scores.reduce((a, b) => a + b, 0) / pathProgress.scores.length;

    return {
      weeksCompleted: pathProgress.weeksCompleted.length,
      averageScore: Math.round(avgScore),
      totalTime: pathProgress.totalTimeSpent,
      consistency: this.calculateConsistency(pathProgress),
      estimatedCompletion: this.estimateCompletion(pathProgress),
    };
  }

  /**
   * Calculate consistency
   */
  calculateConsistency(pathProgress) {
    const weeks = pathProgress.weeksCompleted;
    if (weeks.length < 2) return 100;

    // Check if weeks are consecutive
    const sorted = weeks.sort((a, b) => a - b);
    let gaps = 0;

    for (let i = 1; i < sorted.length; i++) {
      if (sorted[i] - sorted[i - 1] > 1) {
        gaps++;
      }
    }

    const consistency = Math.max(0, 100 - (gaps * 20));
    return consistency;
  }

  /**
   * Estimate completion
   */
  estimateCompletion(pathProgress) {
    const weeksPerUpdate = 1; // Assuming 1 week per update
    const totalWeeks = 8; // Average path length
    const completed = pathProgress.weeksCompleted.length;
    const remaining = totalWeeks - completed;

    const date = new Date();
    date.setDate(date.getDate() + remaining * 7);

    return date.toISOString().split('T')[0];
  }

  /**
   * Get recommended path based on user data
   */
  recommendPath(userData) {
    const { userProfile, learningProgress, exerciseHistory } = userData;

    // Analyze user's current situation and goals
    const proficiency = userProfile?.proficiency_score || 0;
    const level = this.determineLevel(proficiency);

    // Find weakest skill
    const weakestSkill = learningProgress
      ?.sort((a, b) => a.score - b.score)[0];

    const recommendations = [];

    // Recommend based on proficiency
    if (proficiency < 40) {
      recommendations.push({
        path: 'casual_conversation',
        reason: 'Build foundation with everyday conversation',
        priority: 'high',
      });
    } else if (proficiency < 60) {
      recommendations.push({
        path: 'business_english',
        reason: 'Advance to professional communication',
        priority: 'high',
      });
    }

    // Recommend based on goals (if available)
    if (userProfile?.goals?.includes('job')) {
      recommendations.push({
        path: 'job_interview_prep',
        reason: 'Prepare for job interviews',
        priority: 'high',
      });
    }

    if (userProfile?.goals?.includes('travel')) {
      recommendations.push({
        path: 'travel_english',
        reason: 'Essential phrases for travel',
        priority: 'medium',
      });
    }

    // Default recommendation
    if (recommendations.length === 0) {
      recommendations.push({
        path: 'casual_conversation',
        reason: 'Start with conversational fluency',
        priority: 'medium',
      });
    }

    return {
      recommendations,
      currentLevel: level,
      suggestedCommitment: '5-7 hours/week',
    };
  }

  /**
   * Determine skill level from proficiency score
   */
  determineLevel(proficiency) {
    if (proficiency < 20) return 'beginner';
    if (proficiency < 40) return 'elementary';
    if (proficiency < 60) return 'intermediate';
    if (proficiency < 75) return 'upper_intermediate';
    return 'advanced';
  }
}

export default new LearningPathsService();
