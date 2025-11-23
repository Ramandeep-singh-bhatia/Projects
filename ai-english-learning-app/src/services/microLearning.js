/**
 * Micro-Learning Service
 * Manages 3-minute power lessons, quick practice, and bite-sized learning
 */

class MicroLearningService {
  constructor() {
    this.lessonTemplates = this.initializeLessonTemplates();
  }

  /**
   * Initialize lesson templates
   */
  initializeLessonTemplates() {
    return {
      vocabulary: [
        {
          type: 'word_of_the_day',
          title: 'Word of the Day',
          duration: 3,
          template: {
            word: '',
            definition: '',
            examples: [],
            quiz: [],
          },
        },
        {
          type: 'synonym_challenge',
          title: 'Synonym Challenge',
          duration: 2,
          template: {
            baseWord: '',
            synonyms: [],
            quiz: 'match_synonyms',
          },
        },
        {
          type: 'collocation_practice',
          title: 'Common Phrases',
          duration: 3,
          template: {
            verb: '',
            collocations: [],
            fillInBlanks: [],
          },
        },
      ],
      grammar: [
        {
          type: 'grammar_quick_fix',
          title: 'Quick Grammar Fix',
          duration: 3,
          template: {
            rule: '',
            examples: [],
            mistakes: [],
          },
        },
        {
          type: 'article_practice',
          title: 'Article Practice (a/an/the)',
          duration: 2,
          template: {
            sentences: [],
          },
        },
        {
          type: 'preposition_drill',
          title: 'Preposition Drill',
          duration: 2,
          template: {
            sentences: [],
          },
        },
      ],
      speaking: [
        {
          type: 'pronunciation_drill',
          title: 'Pronunciation Practice',
          duration: 2,
          template: {
            sounds: [],
            words: [],
            sentences: [],
          },
        },
        {
          type: 'quick_response',
          title: 'Quick Response Challenge',
          duration: 3,
          template: {
            question: '',
            timeLimit: 30,
          },
        },
      ],
      writing: [
        {
          type: 'sentence_builder',
          title: 'Sentence Builder',
          duration: 3,
          template: {
            prompt: '',
            targetWords: [],
          },
        },
        {
          type: 'paragraph_review',
          title: 'Find the Mistakes',
          duration: 3,
          template: {
            paragraph: '',
            mistakeCount: 0,
          },
        },
      ],
    };
  }

  /**
   * Generate a random micro-lesson
   */
  async generateMicroLesson(focusSkill = null, difficulty = 'intermediate', aiService = null) {
    const skillTypes = focusSkill ? [focusSkill] : Object.keys(this.lessonTemplates);
    const randomSkill = skillTypes[Math.floor(Math.random() * skillTypes.length)];
    const templates = this.lessonTemplates[randomSkill];
    const template = templates[Math.floor(Math.random() * templates.length)];

    // Generate content based on template type
    const lesson = {
      id: Date.now(),
      skill: randomSkill,
      type: template.type,
      title: template.title,
      duration: template.duration,
      difficulty: difficulty,
      content: null,
      createdAt: new Date().toISOString(),
    };

    // Generate specific content based on type
    if (aiService) {
      lesson.content = await this.generateLessonContent(template, difficulty, aiService);
    } else {
      lesson.content = this.getDefaultLessonContent(template.type, difficulty);
    }

    return lesson;
  }

  /**
   * Generate lesson content using AI
   */
  async generateLessonContent(template, difficulty, aiService) {
    const prompts = {
      word_of_the_day: `Generate a "Word of the Day" micro-lesson for ${difficulty} level. Include:
1. An interesting English word
2. Clear definition
3. 3 example sentences
4. 2 quiz questions (multiple choice)

Format as JSON:
{
  "word": "...",
  "definition": "...",
  "examples": ["...", "...", "..."],
  "quiz": [{"question": "...", "options": ["...", "...", "...", "..."], "correct": 0}]
}`,

      grammar_quick_fix: `Create a quick grammar lesson (3 minutes) for ${difficulty} level focusing on a common mistake. Include:
1. The grammar rule
2. 3 correct examples
3. 3 incorrect examples with corrections

Format as JSON.`,

      synonym_challenge: `Create a synonym matching challenge for ${difficulty} level. Include:
1. A base word
2. 5 synonyms with subtle meaning differences
3. Usage context for each

Format as JSON.`,

      quick_response: `Generate a conversational quick-response challenge for ${difficulty} level. Include:
1. An interesting question or scenario
2. Expected response type
3. Evaluation criteria

Format as JSON.`,
    };

    const prompt = prompts[template.type] || prompts.word_of_the_day;

    try {
      const response = await aiService.chat(prompt, {
        exerciseType: 'micro_lesson',
        userLevel: difficulty,
      });

      // Extract JSON from response
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (error) {
      console.error('Error generating micro-lesson:', error);
    }

    return this.getDefaultLessonContent(template.type, difficulty);
  }

  /**
   * Get default lesson content (fallback)
   */
  getDefaultLessonContent(type, difficulty) {
    const defaultContent = {
      word_of_the_day: {
        word: 'serendipity',
        definition: 'Finding something good without looking for it; a happy accident',
        examples: [
          'Meeting my best friend was pure serendipity.',
          'The discovery was a result of serendipity in the lab.',
          'Life is full of serendipitous moments.',
        ],
        quiz: [
          {
            question: 'Which sentence uses "serendipity" correctly?',
            options: [
              'I planned the serendipity carefully.',
              'It was serendipity that I found this café.',
              'The serendipity was very difficult.',
              'She studied serendipity for hours.',
            ],
            correct: 1,
          },
        ],
      },

      grammar_quick_fix: {
        rule: 'Present Perfect: Use "have/has + past participle" for actions that started in the past and continue to the present or have present relevance.',
        examples: [
          'I have lived here for five years.',
          'She has visited Paris three times.',
          'They have been friends since childhood.',
        ],
        mistakes: [
          {
            wrong: 'I am living here for five years.',
            correct: 'I have been living here for five years.',
            explanation: 'Use present perfect for duration starting in the past.',
          },
          {
            wrong: 'She has went to Paris.',
            correct: 'She has gone to Paris.',
            explanation: 'Use past participle "gone", not simple past "went".',
          },
        ],
      },

      synonym_challenge: {
        baseWord: 'happy',
        synonyms: [
          { word: 'joyful', context: 'Deep, spiritual happiness' },
          { word: 'content', context: 'Satisfied, peaceful happiness' },
          { word: 'delighted', context: 'Pleasantly surprised happiness' },
          { word: 'cheerful', context: 'Outwardly showing happiness' },
          { word: 'ecstatic', context: 'Extremely intense happiness' },
        ],
      },

      quick_response: {
        question: 'Someone asks: "What do you do for fun?" You have 30 seconds to respond naturally.',
        timeLimit: 30,
        tips: [
          'Be specific (mention actual hobbies)',
          'Show enthusiasm',
          'Ask a follow-up question',
        ],
      },
    };

    return defaultContent[type] || defaultContent.word_of_the_day;
  }

  /**
   * Get quick practice exercises (2-5 minutes)
   */
  getQuickPracticeExercises() {
    return [
      {
        id: 'vocab_flashcards',
        title: 'Vocabulary Flashcards',
        duration: 3,
        type: 'vocabulary',
        description: 'Review 10 vocabulary words',
        icon: 'BookOpen',
      },
      {
        id: 'grammar_quiz',
        title: 'Grammar Quick Quiz',
        duration: 2,
        type: 'grammar',
        description: '5 quick grammar questions',
        icon: 'CheckSquare',
      },
      {
        id: 'fill_blanks',
        title: 'Fill in the Blanks',
        duration: 3,
        type: 'mixed',
        description: 'Complete 10 sentences',
        icon: 'Edit3',
      },
      {
        id: 'pronunciation',
        title: 'Pronunciation Practice',
        duration: 2,
        type: 'speaking',
        description: 'Practice 5 challenging sounds',
        icon: 'Mic',
      },
      {
        id: 'sentence_correct',
        title: 'Spot the Mistake',
        duration: 3,
        type: 'grammar',
        description: 'Find and correct errors',
        icon: 'AlertCircle',
      },
    ];
  }

  /**
   * Generate a screenshot description exercise
   */
  generateScreenshotExercise() {
    return {
      id: Date.now(),
      title: 'Describe What You See',
      type: 'speaking',
      duration: 3,
      instructions: [
        'Look at an object or scene around you',
        'Describe it in detail for 1-2 minutes',
        'Use descriptive adjectives and specific vocabulary',
        'Practice using present continuous tense',
      ],
      prompts: [
        'What colors do you see?',
        'Describe the shapes and sizes',
        'What is the purpose of this object/scene?',
        'How does it make you feel?',
      ],
      evaluationCriteria: [
        'Variety of vocabulary',
        'Use of descriptive language',
        'Grammatical accuracy',
        'Natural flow',
      ],
    };
  }

  /**
   * Generate voice journal prompt
   */
  generateVoiceJournalPrompt() {
    const prompts = [
      'Talk about your day today. What did you do? How did you feel?',
      'Describe a recent challenge you faced and how you dealt with it.',
      'What are you looking forward to this week?',
      'Tell a story about something interesting that happened to you recently.',
      'Describe your current mood and what caused it.',
      'What did you learn today? Explain it as if teaching someone else.',
      'Talk about a hobby or interest of yours. Why do you enjoy it?',
      'Describe your ideal weekend. What would you do?',
    ];

    return {
      id: Date.now(),
      prompt: prompts[Math.floor(Math.random() * prompts.length)],
      duration: 2,
      type: 'voice_journal',
      tips: [
        'Speak naturally, don\'t overthink',
        'Use transition words (first, then, also, finally)',
        'Describe feelings and details',
        'Practice speaking for the full time',
      ],
    };
  }

  /**
   * Generate waiting room practice (super quick)
   */
  generateWaitingRoomPractice() {
    const exercises = [
      {
        title: 'Mental Translation Practice',
        duration: 2,
        instructions: 'Think of 5 things you see around you and name them in English without translating from your native language.',
      },
      {
        title: 'Quick Verb Conjugation',
        duration: 1,
        instructions: 'Pick a verb (e.g., "eat") and quickly say all its forms: eat, eats, eating, ate, eaten.',
      },
      {
        title: 'Synonyms Sprint',
        duration: 2,
        instructions: 'Think of the word "good". How many synonyms can you think of in 2 minutes? (great, excellent, wonderful...)',
      },
      {
        title: 'Describe Your Surroundings',
        duration: 3,
        instructions: 'Describe where you are right now using as many adjectives as possible.',
      },
      {
        title: 'Question Formation',
        duration: 2,
        instructions: 'Create 5 different questions about what you\'re currently doing or where you are.',
      },
    ];

    return exercises[Math.floor(Math.random() * exercises.length)];
  }

  /**
   * Save completed micro-lesson
   */
  saveCompletedLesson(lesson, score, timeSpent) {
    const completed = this.getCompletedLessons();
    completed.unshift({
      ...lesson,
      score,
      timeSpent,
      completedAt: new Date().toISOString(),
    });

    // Keep last 100
    localStorage.setItem('completed_micro_lessons', JSON.stringify(completed.slice(0, 100)));
  }

  /**
   * Get completed lessons
   */
  getCompletedLessons() {
    const stored = localStorage.getItem('completed_micro_lessons');
    return stored ? JSON.parse(stored) : [];
  }

  /**
   * Get micro-learning statistics
   */
  getStatistics() {
    const completed = this.getCompletedLessons();

    const stats = {
      totalCompleted: completed.length,
      totalTimeSpent: completed.reduce((sum, l) => sum + (l.timeSpent || 0), 0),
      averageScore: completed.length > 0
        ? completed.reduce((sum, l) => sum + (l.score || 0), 0) / completed.length
        : 0,
      bySkill: {},
      thisWeek: 0,
      thisMonth: 0,
    };

    const now = new Date();
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

    completed.forEach(lesson => {
      const skill = lesson.skill || 'general';
      if (!stats.bySkill[skill]) {
        stats.bySkill[skill] = { count: 0, totalScore: 0 };
      }
      stats.bySkill[skill].count++;
      stats.bySkill[skill].totalScore += (lesson.score || 0);

      const completedDate = new Date(lesson.completedAt);
      if (completedDate >= weekAgo) stats.thisWeek++;
      if (completedDate >= monthAgo) stats.thisMonth++;
    });

    return stats;
  }
}

export default new MicroLearningService();
