/**
 * Meta-Learning Skills Service
 * Learning how to learn, study habits, reflection, self-assessment, learning strategies
 */

class MetaLearningService {
  constructor() {
    this.learningStrategies = this.initializeLearningStrategies();
    this.memoryTechniques = this.initializeMemoryTechniques();
    this.reflectionPrompts = this.initializeReflectionPrompts();
    this.studyHabits = this.initializeStudyHabits();
  }

  /**
   * Initialize learning strategies
   */
  initializeLearningStrategies() {
    return {
      spaced_repetition: {
        name: 'Spaced Repetition',
        description: 'Review material at increasing intervals',
        howToUse: [
          'Review new content within 24 hours',
          'Review again after 3 days',
          'Review after 1 week',
          'Review after 1 month',
          'Continue at longer intervals',
        ],
        benefits: [
          'Better long-term retention',
          'More efficient than cramming',
          'Strengthens memory connections',
        ],
        application: 'Use for vocabulary, grammar rules, common phrases',
        difficulty: 'easy',
      },
      active_recall: {
        name: 'Active Recall',
        description: 'Test yourself instead of passive review',
        howToUse: [
          'After learning, close your notes',
          'Try to remember what you learned',
          'Write it down or say it out loud',
          'Check and correct mistakes',
          'Focus on what you forgot',
        ],
        benefits: [
          'Strengthens memory retrieval',
          'Identifies weak areas',
          'More effective than rereading',
        ],
        application: 'After each study session, quiz yourself',
        difficulty: 'medium',
      },
      interleaving: {
        name: 'Interleaving Practice',
        description: 'Mix different topics instead of blocking',
        howToUse: [
          'Don\'t practice one skill for too long',
          'Switch between grammar, vocabulary, speaking',
          'Mix difficulty levels',
          'Practice variety in one session',
        ],
        benefits: [
          'Improves discrimination between concepts',
          'Better transfer of skills',
          'More engaging',
        ],
        application: 'In a 1-hour session, do 20 min each of 3 different skills',
        difficulty: 'medium',
      },
      elaboration: {
        name: 'Elaborative Interrogation',
        description: 'Ask yourself "why" and "how"',
        howToUse: [
          'Learn a new word or rule',
          'Ask: Why does this work this way?',
          'Ask: How is this similar to what I know?',
          'Connect to personal examples',
          'Explain it to yourself in your own words',
        ],
        benefits: [
          'Deeper understanding',
          'Better connections to existing knowledge',
          'Improves retention',
        ],
        application: 'For every new concept, ask "why" and "how"',
        difficulty: 'medium',
      },
      dual_coding: {
        name: 'Dual Coding',
        description: 'Combine words with visual representations',
        howToUse: [
          'Draw pictures for new vocabulary',
          'Use mind maps for concepts',
          'Create visual associations',
          'Use diagrams for grammar',
        ],
        benefits: [
          'Engages multiple memory systems',
          'Easier recall',
          'Works well for visual learners',
        ],
        application: 'Draw images for 10 new words each week',
        difficulty: 'easy',
      },
      pomodoro_technique: {
        name: 'Pomodoro Technique',
        description: 'Focused work in time blocks',
        howToUse: [
          'Set timer for 25 minutes',
          'Focus completely on learning',
          'No distractions allowed',
          'Take 5-minute break',
          'After 4 pomodoros, take 15-30 min break',
        ],
        benefits: [
          'Maintains focus',
          'Prevents burnout',
          'Clear work/rest boundaries',
        ],
        application: 'Use for intensive study sessions',
        difficulty: 'easy',
      },
    };
  }

  /**
   * Initialize memory techniques
   */
  initializeMemoryTechniques() {
    return {
      mnemonics: {
        name: 'Mnemonics',
        techniques: [
          {
            type: 'Acronyms',
            description: 'Create words from first letters',
            example: 'FANBOYS (coordinating conjunctions: For, And, Nor, But, Or, Yet, So)',
          },
          {
            type: 'Acrostics',
            description: 'Sentences where each word starts with the letter you need',
            example: 'Every Good Boy Does Fine (musical notes E, G, B, D, F)',
          },
          {
            type: 'Rhymes',
            description: 'Create rhyming phrases',
            example: 'I before E except after C (spelling rule)',
          },
        ],
      },
      memory_palace: {
        name: 'Memory Palace (Method of Loci)',
        description: 'Associate information with physical locations',
        howToUse: [
          'Choose a familiar place (your home)',
          'Create a mental route through it',
          'Place new vocabulary at different locations',
          'Mentally walk the route to recall',
        ],
        example: 'Put "exhausted" on your couch (imagine being too tired to get up)',
      },
      chunking: {
        name: 'Chunking',
        description: 'Group information into meaningful chunks',
        howToUse: [
          'Instead of learning 10 random words',
          'Group them by category (emotions, food, actions)',
          'Learn 3 words per category',
          'Easier to remember and recall',
        ],
        example: 'Instead of random words, learn all kitchen vocabulary together',
      },
      association: {
        name: 'Association',
        description: 'Link new information to what you know',
        techniques: [
          {
            type: 'Personal Connection',
            example: 'Learn "gregarious" by thinking of your outgoing friend Greg',
          },
          {
            type: 'Sound Association',
            example: 'Learn "bizarre" by associating with "bazaar" (unusual market)',
          },
          {
            type: 'Visual Association',
            example: 'Picture a word\'s meaning when learning it',
          },
        ],
      },
      storytelling: {
        name: 'Story Method',
        description: 'Create stories with the words you need to remember',
        howToUse: [
          'Take 5-10 new words',
          'Create a silly or memorable story using all of them',
          'The more vivid and unusual, the better',
          'Tell the story to remember the words',
        ],
        example: 'To remember "benevolent, gregarious, meticulous": "The benevolent king was so gregarious he threw parties, but so meticulous he color-coded the guests"',
      },
    };
  }

  /**
   * Initialize reflection prompts
   */
  initializeReflectionPrompts() {
    return {
      daily: [
        {
          prompt: 'What did I learn today?',
          purpose: 'Consolidate learning',
        },
        {
          prompt: 'What was challenging today?',
          purpose: 'Identify obstacles',
        },
        {
          prompt: 'What strategy worked well?',
          purpose: 'Recognize effective methods',
        },
        {
          prompt: 'What will I do differently tomorrow?',
          purpose: 'Plan improvement',
        },
      ],
      weekly: [
        {
          prompt: 'What progress did I make this week?',
          purpose: 'Acknowledge achievements',
        },
        {
          prompt: 'What patterns do I notice in my mistakes?',
          purpose: 'Identify recurring issues',
        },
        {
          prompt: 'How consistent was I with practice?',
          purpose: 'Evaluate habits',
        },
        {
          prompt: 'What\'s my focus for next week?',
          purpose: 'Set direction',
        },
        {
          prompt: 'Am I enjoying the learning process?',
          purpose: 'Check motivation',
        },
        {
          prompt: 'What learning strategy should I try next?',
          purpose: 'Promote experimentation',
        },
      ],
      monthly: [
        {
          prompt: 'How has my English improved this month?',
          purpose: 'Measure progress',
        },
        {
          prompt: 'What am I most proud of?',
          purpose: 'Celebrate success',
        },
        {
          prompt: 'What obstacles did I overcome?',
          purpose: 'Recognize resilience',
        },
        {
          prompt: 'What surprised me about my learning?',
          purpose: 'Gain insights',
        },
        {
          prompt: 'Are my goals still relevant?',
          purpose: 'Align with objectives',
        },
        {
          prompt: 'What do I need to focus on next month?',
          purpose: 'Strategic planning',
        },
      ],
    };
  }

  /**
   * Initialize study habits
   */
  initializeStudyHabits() {
    return {
      optimal_habits: [
        {
          habit: 'Consistent Schedule',
          description: 'Study at the same time each day',
          why: 'Builds routine and reduces decision fatigue',
          howTo: 'Block 30-60 minutes daily at your peak energy time',
        },
        {
          habit: 'Dedicated Space',
          description: 'Have a specific study location',
          why: 'Environmental cues trigger learning mode',
          howTo: 'Choose a quiet, comfortable spot with minimal distractions',
        },
        {
          habit: 'Start Small',
          description: 'Begin with manageable goals',
          why: 'Prevents overwhelm and builds momentum',
          howTo: 'Start with 10 minutes daily, gradually increase',
        },
        {
          habit: 'Active Learning',
          description: 'Engage actively, not passively',
          why: 'Active practice is more effective than passive reading',
          howTo: 'Speak out loud, write, test yourself',
        },
        {
          habit: 'Regular Breaks',
          description: 'Take breaks to maintain focus',
          why: 'Prevents mental fatigue and consolidates memory',
          howTo: 'Use Pomodoro: 25 min work, 5 min break',
        },
        {
          habit: 'Review Regularly',
          description: 'Schedule review sessions',
          why: 'Spaced repetition strengthens long-term memory',
          howTo: 'Review yesterday\'s lesson before starting new content',
        },
        {
          habit: 'Track Progress',
          description: 'Record what you\'ve learned',
          why: 'Provides motivation and identifies gaps',
          howTo: 'Keep a learning journal or use app tracking',
        },
        {
          habit: 'Use English Daily',
          description: 'Practice outside study sessions',
          why: 'Real-world application reinforces learning',
          howTo: 'Think in English, label objects, talk to yourself',
        },
      ],
      habits_to_avoid: [
        {
          habit: 'Cramming',
          why_avoid: 'Poor long-term retention',
          alternative: 'Space out learning over time',
        },
        {
          habit: 'Passive Reading',
          why_avoid: 'Creates illusion of knowledge without retention',
          alternative: 'Test yourself, summarize, explain to others',
        },
        {
          habit: 'Multitasking',
          why_avoid: 'Reduces focus and effectiveness',
          alternative: 'Single-task with full attention',
        },
        {
          habit: 'Perfectionism',
          why_avoid: 'Causes anxiety and prevents practice',
          alternative: 'Embrace mistakes as learning opportunities',
        },
        {
          habit: 'Comparing to Others',
          why_avoid: 'Demotivating and irrelevant to your journey',
          alternative: 'Compare to your past self',
        },
      ],
    };
  }

  /**
   * Generate personalized learning how-to-learn guide
   */
  generateLearningGuide(userProfile, learningHistory) {
    const guide = {
      introduction: 'Learning a language is a skill itself. Here\'s how to optimize YOUR learning process.',
      yourLearningStyle: this.identifyLearningStyle(learningHistory),
      recommendedStrategies: [],
      customizedPlan: {},
      resources: [],
    };

    // Recommend strategies based on user data
    const performance = this.analyzePerformance(learningHistory);

    if (performance.consistency < 50) {
      guide.recommendedStrategies.push({
        strategy: this.learningStrategies.pomodoro_technique,
        priority: 'high',
        reason: 'Will help build consistent study habit',
      });
    }

    if (performance.retention < 60) {
      guide.recommendedStrategies.push({
        strategy: this.learningStrategies.spaced_repetition,
        priority: 'high',
        reason: 'Improve long-term retention',
      });

      guide.recommendedStrategies.push({
        strategy: this.learningStrategies.active_recall,
        priority: 'medium',
        reason: 'Strengthen memory retrieval',
      });
    }

    // Add general good strategies
    guide.recommendedStrategies.push({
      strategy: this.learningStrategies.interleaving,
      priority: 'medium',
      reason: 'Keep learning engaging and effective',
    });

    // Create customized plan
    guide.customizedPlan = this.createCustomPlan(userProfile, performance);

    return guide;
  }

  /**
   * Identify learning style
   */
  identifyLearningStyle(learningHistory) {
    // Simplified - in reality would analyze actual behavior
    return {
      primary: 'Visual',
      secondary: 'Kinesthetic',
      recommendations: [
        'Use diagrams and visual aids',
        'Create mind maps',
        'Practice speaking and writing (kinesthetic)',
      ],
    };
  }

  /**
   * Analyze performance
   */
  analyzePerformance(learningHistory) {
    if (!learningHistory || learningHistory.length === 0) {
      return {
        consistency: 0,
        retention: 0,
        engagement: 0,
      };
    }

    // Simplified analysis
    return {
      consistency: 70,
      retention: 65,
      engagement: 80,
    };
  }

  /**
   * Create custom learning plan
   */
  createCustomPlan(userProfile, performance) {
    return {
      dailyRoutine: {
        morning: [
          '5 min: Review yesterday\'s vocabulary',
          '15 min: New content (grammar or vocabulary)',
          '5 min: Speaking practice (describe your day)',
        ],
        evening: [
          '10 min: Active recall quiz',
          '10 min: Conversation or writing practice',
          '5 min: Reflection - what did I learn today?',
        ],
      },
      weeklyGoals: [
        'Learn 20-30 new words',
        'Complete 3-4 grammar exercises',
        'Have 2 conversations in English',
        'Write 1-2 short paragraphs',
      ],
      monthlyReview: [
        'Self-assessment test',
        'Review all vocabulary learned',
        'Identify weak areas',
        'Adjust learning plan',
      ],
    };
  }

  /**
   * Generate self-assessment questionnaire
   */
  generateSelfAssessment(skillType = 'overall') {
    const assessments = {
      overall: {
        title: 'Overall English Proficiency Self-Assessment',
        questions: [
          {
            question: 'I can understand main ideas in complex text',
            scale: '1 (Never) to 5 (Always)',
            skill: 'reading',
          },
          {
            question: 'I can express myself fluently and spontaneously',
            scale: '1 (Never) to 5 (Always)',
            skill: 'speaking',
          },
          {
            question: 'I can write clear, detailed text on complex subjects',
            scale: '1 (Never) to 5 (Always)',
            skill: 'writing',
          },
          {
            question: 'I can follow extended speech and complex lines of argument',
            scale: '1 (Never) to 5 (Always)',
            skill: 'listening',
          },
          {
            question: 'I can use language flexibly for social, academic, or professional purposes',
            scale: '1 (Never) to 5 (Always)',
            skill: 'general',
          },
        ],
        interpretation: {
          '20-25': 'Advanced (C1-C2)',
          '15-19': 'Upper Intermediate (B2)',
          '10-14': 'Intermediate (B1)',
          '5-9': 'Elementary (A2)',
          '0-4': 'Beginner (A1)',
        },
      },
      learning_habits: {
        title: 'Learning Habits Assessment',
        questions: [
          {
            question: 'I practice English every day',
            purpose: 'Consistency check',
          },
          {
            question: 'I actively try to use new words I learn',
            purpose: 'Active learning check',
          },
          {
            question: 'I reflect on my mistakes and learn from them',
            purpose: 'Growth mindset check',
          },
          {
            question: 'I set specific goals for my learning',
            purpose: 'Goal-orientation check',
          },
          {
            question: 'I use multiple resources and methods to learn',
            purpose: 'Variety check',
          },
        ],
      },
      confidence: {
        title: 'Confidence Assessment',
        questions: [
          {
            situation: 'Ordering food in a restaurant',
            confidence: '1 (Very uncomfortable) to 5 (Very confident)',
          },
          {
            situation: 'Job interview in English',
            confidence: '1 (Very uncomfortable) to 5 (Very confident)',
          },
          {
            situation: 'Casual conversation with native speakers',
            confidence: '1 (Very uncomfortable) to 5 (Very confident)',
          },
          {
            situation: 'Writing a professional email',
            confidence: '1 (Very uncomfortable) to 5 (Very confident)',
          },
          {
            situation: 'Giving a presentation',
            confidence: '1 (Very uncomfortable) to 5 (Very confident)',
          },
        ],
      },
    };

    return assessments[skillType] || assessments.overall;
  }

  /**
   * Generate weekly reflection
   */
  generateWeeklyReflection() {
    return {
      id: Date.now(),
      week: this.getCurrentWeekNumber(),
      prompts: this.reflectionPrompts.weekly,
      sections: {
        wins: {
          title: 'This Week\'s Wins',
          prompts: [
            'What went well this week?',
            'What are you proud of?',
            'What progress did you make?',
          ],
        },
        challenges: {
          title: 'Challenges Faced',
          prompts: [
            'What was difficult?',
            'What frustrated you?',
            'Where did you struggle?',
          ],
        },
        insights: {
          title: 'Learning Insights',
          prompts: [
            'What did you learn about the language?',
            'What did you learn about your learning process?',
            'What patterns do you notice?',
          ],
        },
        actionPlan: {
          title: 'Next Week\'s Plan',
          prompts: [
            'What will you focus on?',
            'What will you do differently?',
            'What\'s your main goal?',
          ],
        },
      },
      tips: [
        'Be honest with yourself',
        'Celebrate small wins',
        'Don\'t be too harsh on mistakes',
        'Focus on progress, not perfection',
      ],
    };
  }

  /**
   * Track study habits
   */
  trackStudyHabit(habitType, completed, notes = '') {
    const habits = this.getStudyHabits();

    habits.unshift({
      id: Date.now(),
      habitType,
      completed,
      notes,
      date: new Date().toISOString().split('T')[0],
    });

    localStorage.setItem('study_habits', JSON.stringify(habits.slice(0, 365))); // Keep 1 year

    return this.analyzeHabitStreak(habitType);
  }

  /**
   * Get study habits
   */
  getStudyHabits() {
    const stored = localStorage.getItem('study_habits');
    return stored ? JSON.parse(stored) : [];
  }

  /**
   * Analyze habit streak
   */
  analyzeHabitStreak(habitType) {
    const habits = this.getStudyHabits();
    const typeHabits = habits.filter(h => h.habitType === habitType);

    if (typeHabits.length === 0) {
      return {
        currentStreak: 0,
        longestStreak: 0,
        totalDays: 0,
      };
    }

    let currentStreak = 0;
    let longestStreak = 0;
    let tempStreak = 0;

    const sorted = typeHabits.sort((a, b) => new Date(b.date) - new Date(a.date));

    // Calculate current streak
    const today = new Date().toISOString().split('T')[0];
    if (sorted[0].date === today && sorted[0].completed) {
      currentStreak = 1;

      for (let i = 1; i < sorted.length; i++) {
        const prevDate = new Date(sorted[i - 1].date);
        const currDate = new Date(sorted[i].date);
        const diffDays = Math.floor((prevDate - currDate) / (1000 * 60 * 60 * 24));

        if (diffDays === 1 && sorted[i].completed) {
          currentStreak++;
        } else {
          break;
        }
      }
    }

    // Calculate longest streak
    tempStreak = 0;
    for (let i = 0; i < sorted.length; i++) {
      if (sorted[i].completed) {
        tempStreak++;
        longestStreak = Math.max(longestStreak, tempStreak);
      } else {
        tempStreak = 0;
      }
    }

    return {
      currentStreak,
      longestStreak,
      totalDays: typeHabits.filter(h => h.completed).length,
      consistency: Math.round((typeHabits.filter(h => h.completed).length / typeHabits.length) * 100),
    };
  }

  /**
   * Save reflection
   */
  saveReflection(reflectionType, responses) {
    const reflections = this.getReflections();

    reflections.unshift({
      id: Date.now(),
      type: reflectionType,
      responses,
      createdAt: new Date().toISOString(),
    });

    localStorage.setItem('reflections', JSON.stringify(reflections.slice(0, 100)));

    return {
      saved: true,
      insight: this.generateInsightFromReflection(responses),
    };
  }

  /**
   * Get reflections
   */
  getReflections() {
    const stored = localStorage.getItem('reflections');
    return stored ? JSON.parse(stored) : [];
  }

  /**
   * Generate insight from reflection
   */
  generateInsightFromReflection(responses) {
    // Simple insight generation
    const insights = [
      'Regular reflection helps you learn faster',
      'Noticing patterns in your learning is the first step to improvement',
      'Celebrating wins, even small ones, keeps you motivated',
      'Being aware of challenges helps you address them strategically',
    ];

    return insights[Math.floor(Math.random() * insights.length)];
  }

  /**
   * Get current week number
   */
  getCurrentWeekNumber() {
    const now = new Date();
    const start = new Date(now.getFullYear(), 0, 1);
    const diff = now - start;
    const oneWeek = 1000 * 60 * 60 * 24 * 7;
    return Math.ceil(diff / oneWeek);
  }

  /**
   * Get learning strategy recommendation
   */
  getStrategyRecommendation(userNeed) {
    const recommendations = {
      'improve_memory': [
        this.learningStrategies.spaced_repetition,
        this.learningStrategies.active_recall,
        this.memoryTechniques.chunking,
      ],
      'stay_motivated': [
        this.learningStrategies.pomodoro_technique,
        this.studyHabits.optimal_habits[0], // Consistent schedule
        this.studyHabits.optimal_habits[6], // Track progress
      ],
      'learn_faster': [
        this.learningStrategies.interleaving,
        this.learningStrategies.active_recall,
        this.learningStrategies.elaboration,
      ],
      'understand_deeper': [
        this.learningStrategies.elaboration,
        this.learningStrategies.dual_coding,
        this.studyHabits.optimal_habits[3], // Active learning
      ],
    };

    return recommendations[userNeed] || Object.values(this.learningStrategies).slice(0, 3);
  }
}

export default new MetaLearningService();
