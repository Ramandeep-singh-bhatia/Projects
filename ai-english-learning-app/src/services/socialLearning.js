/**
 * Social Learning & Simulation Service
 * Debate mode, interview simulator, emotion/tone training, cultural context
 */

class SocialLearningService {
  constructor() {
    this.debateTopics = this.initializeDebateTopics();
    this.interviewTypes = this.initializeInterviewTypes();
    this.emotionScenarios = this.initializeEmotionScenarios();
    this.culturalContexts = this.initializeCulturalContexts();
  }

  /**
   * Initialize debate topics
   */
  initializeDebateTopics() {
    return [
      {
        category: 'technology',
        topic: 'Social media does more harm than good',
        difficulty: 'intermediate',
        forArguments: [
          'Increases anxiety and mental health issues',
          'Spreads misinformation',
          'Reduces face-to-face interaction',
          'Privacy concerns',
        ],
        againstArguments: [
          'Connects people globally',
          'Platform for free speech',
          'Business and marketing opportunities',
          'Access to information',
        ],
      },
      {
        category: 'education',
        topic: 'Online learning is better than traditional classroom education',
        difficulty: 'intermediate',
        forArguments: [
          'Flexible schedule',
          'Access from anywhere',
          'Cost-effective',
          'Self-paced learning',
        ],
        againstArguments: [
          'Lack of social interaction',
          'Requires high self-discipline',
          'Technical difficulties',
          'Less hands-on experience',
        ],
      },
      {
        category: 'environment',
        topic: 'Individual actions can meaningfully combat climate change',
        difficulty: 'advanced',
        forArguments: [
          'Collective individual actions create significant impact',
          'Drives demand for sustainable products',
          'Sets example for others',
          'Reduces personal carbon footprint',
        ],
        againstArguments: [
          'Corporate emissions are the main problem',
          'Systemic change is needed',
          'Individual impact is negligible',
          'Focuses blame on wrong actors',
        ],
      },
      {
        category: 'work',
        topic: 'Remote work should be the default option for all office jobs',
        difficulty: 'intermediate',
        forArguments: [
          'Better work-life balance',
          'Reduced commute time and costs',
          'Increased productivity for many',
          'Access to global talent pool',
        ],
        againstArguments: [
          'Collaboration suffers',
          'Work-home boundary issues',
          'Not suitable for all job types',
          'Social isolation',
        ],
      },
      {
        category: 'society',
        topic: 'Success is more about hard work than talent',
        difficulty: 'advanced',
        forArguments: [
          'Many successful people overcame lack of initial talent',
          'Consistent effort builds skills',
          'Talent without work doesn\'t succeed',
          'Mindset and perseverance matter most',
        ],
        againstArguments: [
          'Natural ability provides huge advantages',
          'Some fields require innate talent',
          'Privilege and circumstances matter',
          'Survivorship bias in success stories',
        ],
      },
    ];
  }

  /**
   * Initialize interview types
   */
  initializeInterviewTypes() {
    return {
      job_interview: {
        roles: ['Software Engineer', 'Marketing Manager', 'Sales Representative', 'Teacher', 'Designer'],
        commonQuestions: [
          {
            question: 'Tell me about yourself',
            type: 'introduction',
            tips: [
              'Keep it professional and relevant',
              'Follow present-past-future structure',
              'Highlight relevant experience',
              'Keep it under 2 minutes',
            ],
            goodExample: 'I\'m currently a marketing specialist with 3 years of experience in digital campaigns. Previously, I worked in social media management where I increased engagement by 40%. I\'m excited about this role because it combines my skills with new challenges in your industry.',
          },
          {
            question: 'What are your strengths?',
            type: 'strengths',
            tips: [
              'Choose 2-3 relevant strengths',
              'Provide specific examples',
              'Connect to the job requirements',
              'Be genuine, not boastful',
            ],
            goodExample: 'One of my key strengths is problem-solving. For example, when our team faced declining user engagement, I analyzed the data and implemented a new content strategy that increased retention by 25%.',
          },
          {
            question: 'What are your weaknesses?',
            type: 'weaknesses',
            tips: [
              'Choose a real but not critical weakness',
              'Show self-awareness',
              'Explain how you\'re working on it',
              'Don\'t use clichés like "I\'m a perfectionist"',
            ],
            goodExample: 'I sometimes struggle with public speaking. I\'ve been working on this by volunteering to present at team meetings and taking a presentation skills course. I\'ve already seen improvement in my confidence.',
          },
          {
            question: 'Why do you want this job?',
            type: 'motivation',
            tips: [
              'Research the company beforehand',
              'Connect your goals to the role',
              'Show enthusiasm',
              'Be specific',
            ],
            goodExample: 'I\'m impressed by your company\'s commitment to innovation. This role combines my passion for data analysis with the opportunity to work on cutting-edge projects. I particularly admire your recent work on [specific project].',
          },
          {
            question: 'Where do you see yourself in 5 years?',
            type: 'future_goals',
            tips: [
              'Show ambition but be realistic',
              'Align with company growth',
              'Focus on skill development',
              'Don\'t mention leaving',
            ],
            goodExample: 'In 5 years, I hope to have grown into a senior role where I can lead projects and mentor junior team members. I want to develop expertise in [relevant area] and contribute to the company\'s strategic initiatives.',
          },
        ],
      },
      university_interview: {
        commonQuestions: [
          {
            question: 'Why do you want to study at our university?',
            type: 'motivation',
            tips: [
              'Mention specific programs or professors',
              'Show you\'ve researched the university',
              'Connect to your goals',
              'Be enthusiastic',
            ],
          },
          {
            question: 'What will you contribute to our university community?',
            type: 'contribution',
            tips: [
              'Mention extracurricular interests',
              'Highlight leadership experience',
              'Show diverse interests',
              'Be specific about activities',
            ],
          },
        ],
      },
      media_interview: {
        commonQuestions: [
          {
            question: 'Can you explain [complex topic] in simple terms?',
            type: 'explanation',
            tips: [
              'Use analogies',
              'Avoid jargon',
              'Be concise',
              'Check if they understand',
            ],
          },
        ],
      },
    };
  }

  /**
   * Initialize emotion scenarios
   */
  initializeEmotionScenarios() {
    return {
      expressing_empathy: {
        situations: [
          {
            scenario: 'A friend tells you they didn\'t get the job they applied for',
            appropriateResponses: [
              'I\'m so sorry to hear that. I know how much you wanted it.',
              'That must be really disappointing. How are you feeling?',
              'I know this is tough. Is there anything I can do to help?',
            ],
            inappropriateResponses: [
              'Well, maybe you weren\'t qualified enough.',
              'There are plenty of other jobs.',
              'At least you tried.',
            ],
            tone: 'sympathetic, supportive',
          },
          {
            scenario: 'A colleague is stressed about a deadline',
            appropriateResponses: [
              'I can see you\'re under a lot of pressure. Can I help with anything?',
              'That sounds really stressful. Let\'s break it down together.',
              'I understand. I\'ve been there. You\'ve got this.',
            ],
            inappropriateResponses: [
              'You should have started earlier.',
              'It\'s not that hard.',
              'Everyone has deadlines.',
            ],
            tone: 'understanding, helpful',
          },
        ],
      },
      showing_enthusiasm: {
        situations: [
          {
            scenario: 'Someone shares good news with you',
            appropriateResponses: [
              'That\'s amazing! I\'m so happy for you!',
              'Congratulations! You absolutely deserve this!',
              'Wow! That\'s fantastic news! Tell me more!',
            ],
            flatResponses: [
              'That\'s nice.',
              'Good for you.',
              'Okay.',
            ],
            tone: 'excited, genuine',
          },
        ],
      },
      expressing_disagreement: {
        levels: [
          {
            level: 'soft',
            phrases: [
              'I see what you\'re saying, but have you considered...?',
              'That\'s one perspective. Another way to look at it might be...',
              'Interesting point. I tend to see it differently because...',
            ],
          },
          {
            level: 'moderate',
            phrases: [
              'I understand your point, but I disagree because...',
              'I\'m afraid I don\'t agree with that',
              'I have a different opinion on this',
            ],
          },
          {
            level: 'strong',
            phrases: [
              'I completely disagree',
              'I must respectfully disagree',
              'That\'s not accurate in my view',
            ],
          },
        ],
      },
      giving_bad_news: {
        frameworks: [
          {
            name: 'Professional Setting',
            steps: [
              '1. Prepare them: "I need to discuss something with you"',
              '2. Be direct but kind: State the news clearly',
              '3. Show empathy: "I know this is difficult"',
              '4. Offer support: "Let\'s discuss next steps"',
            ],
          },
          {
            name: 'Personal Setting',
            steps: [
              '1. Choose the right time and place',
              '2. Be gentle but honest',
              '3. Allow time for reaction',
              '4. Offer comfort and support',
            ],
          },
        ],
      },
    };
  }

  /**
   * Initialize cultural contexts
   */
  initializeCulturalContexts() {
    return {
      greetings: {
        american: {
          casual: 'Hey! How are you?',
          formal: 'Good morning/afternoon. How do you do?',
          notes: [
            '"How are you?" is often rhetorical - brief answer expected',
            'Firm handshake is standard in business',
            'Direct eye contact shows confidence',
          ],
        },
        british: {
          casual: 'Hello! How are you doing?',
          formal: 'Good morning/afternoon. Pleased to meet you.',
          notes: [
            'More reserved than American style',
            'Small talk about weather is common',
            'Politeness and understatement valued',
          ],
        },
        australian: {
          casual: 'G\'day! How\'s it going?',
          formal: 'Hello. Nice to meet you.',
          notes: [
            'Generally informal and friendly',
            'Humor is important in interactions',
            'Tall poppy syndrome - avoid excessive boasting',
          ],
        },
      },
      business_culture: {
        directness: {
          high_context: [
            'Consider Japanese, Chinese communication',
            'Indirect refusals',
            'Reading between the lines important',
            'Silence can mean disagreement',
          ],
          low_context: [
            'American, German communication',
            'Direct and explicit',
            'Say what you mean',
            'Silence can be uncomfortable',
          ],
        },
        time: {
          monochronic: [
            'Punctuality is crucial',
            'One thing at a time',
            'Schedules are fixed',
            'Examples: Germany, USA, Japan',
          ],
          polychronic: [
            'Flexible time',
            'Multiple things at once',
            'Relationships over schedules',
            'Examples: Latin America, Middle East',
          ],
        },
      },
      taboo_topics: {
        generally_avoid: [
          'Politics (unless in appropriate context)',
          'Religion',
          'Money/salary (especially in initial conversations)',
          'Age (particularly with women)',
          'Weight or appearance',
        ],
        cultural_variations: [
          {
            culture: 'American',
            additional: ['Personal questions too early in relationship'],
          },
          {
            culture: 'British',
            additional: ['Excessive bragging', 'Very personal questions'],
          },
        ],
      },
      politeness_strategies: {
        making_requests: {
          direct: 'Give me the report',
          polite: 'Could you please send me the report?',
          very_polite: 'Would you mind sending me the report when you have a chance?',
          notes: 'Use more polite forms with strangers, superiors, or in formal contexts',
        },
        refusing: {
          direct: 'No, I can\'t',
          polite: 'I\'m afraid I can\'t because...',
          very_polite: 'I would love to, but unfortunately I have a prior commitment',
          notes: 'Softening refusals is common in English-speaking cultures',
        },
      },
    };
  }

  /**
   * Generate debate exercise
   */
  generateDebateExercise(category = null, difficulty = 'intermediate') {
    let topics = this.debateTopics;

    if (category) {
      topics = topics.filter(t => t.category === category);
    }

    topics = topics.filter(t => t.difficulty === difficulty);

    if (topics.length === 0) {
      topics = this.debateTopics.filter(t => t.difficulty === difficulty);
    }

    const topic = topics[Math.floor(Math.random() * topics.length)];
    const side = Math.random() > 0.5 ? 'for' : 'against';

    return {
      id: Date.now(),
      type: 'debate',
      topic: topic.topic,
      category: topic.category,
      difficulty: topic.difficulty,
      yourSide: side,
      yourArguments: side === 'for' ? topic.forArguments : topic.againstArguments,
      opponentArguments: side === 'for' ? topic.againstArguments : topic.forArguments,
      structure: {
        opening: 'State your position (1-2 minutes)',
        arguments: 'Present 3 main arguments with evidence',
        rebuttal: 'Respond to opponent arguments',
        closing: 'Summarize your position',
      },
      usefulPhrases: this.getDebatePhrases(),
      evaluationCriteria: [
        'Clear argument structure',
        'Use of evidence and examples',
        'Addressing counterarguments',
        'Persuasive language',
        'Logical flow',
      ],
    };
  }

  /**
   * Get debate phrases
   */
  getDebatePhrases() {
    return {
      opening: [
        'I strongly believe that...',
        'Today I will argue that...',
        'The evidence clearly shows that...',
      ],
      presenting_arguments: [
        'First of all / Firstly...',
        'Moreover / Furthermore...',
        'Most importantly...',
        'Consider the fact that...',
      ],
      providing_evidence: [
        'According to research...',
        'Studies have shown that...',
        'For example...',
        'The data suggests that...',
      ],
      countering: [
        'While it\'s true that..., we must also consider...',
        'Some may argue that..., however...',
        'On the contrary...',
        'That argument fails to account for...',
      ],
      concluding: [
        'In conclusion...',
        'To summarize my position...',
        'The evidence clearly demonstrates that...',
        'Therefore, I maintain that...',
      ],
    };
  }

  /**
   * Generate interview simulation
   */
  generateInterviewSimulation(interviewType = 'job_interview', role = null) {
    const interview = this.interviewTypes[interviewType];

    if (!interview) {
      return {
        error: 'Interview type not found',
        available: Object.keys(this.interviewTypes),
      };
    }

    // Select random questions
    const questionCount = 5;
    const selectedQuestions = [];
    const availableQuestions = [...interview.commonQuestions];

    for (let i = 0; i < Math.min(questionCount, availableQuestions.length); i++) {
      const index = Math.floor(Math.random() * availableQuestions.length);
      selectedQuestions.push(availableQuestions.splice(index, 1)[0]);
    }

    return {
      id: Date.now(),
      type: interviewType,
      role: role || (interview.roles ? interview.roles[Math.floor(Math.random() * interview.roles.length)] : 'General'),
      questions: selectedQuestions,
      preparation: {
        before: [
          'Research the company/institution',
          'Prepare examples from your experience',
          'Practice answering out loud',
          'Prepare questions to ask them',
        ],
        during: [
          'Listen carefully to the full question',
          'Take a moment to think before answering',
          'Be specific and give examples',
          'Show enthusiasm',
          'Ask for clarification if needed',
        ],
        after: [
          'Send a thank-you email',
          'Reflect on what went well',
          'Note areas for improvement',
        ],
      },
      commonMistakes: [
        'Rambling answers - keep responses focused',
        'Negative talk about previous employers',
        'Not preparing questions to ask',
        'Poor body language',
        'Not researching the organization',
      ],
    };
  }

  /**
   * Generate emotion/tone training exercise
   */
  generateEmotionTrainingExercise(emotion = null) {
    const emotions = ['empathy', 'enthusiasm', 'disagreement', 'bad_news'];
    const selectedEmotion = emotion || emotions[Math.floor(Math.random() * emotions.length)];

    const emotionMap = {
      empathy: this.emotionScenarios.expressing_empathy,
      enthusiasm: this.emotionScenarios.showing_enthusiasm,
      disagreement: this.emotionScenarios.expressing_disagreement,
      bad_news: this.emotionScenarios.giving_bad_news,
    };

    const scenarioData = emotionMap[selectedEmotion];

    return {
      id: Date.now(),
      emotion: selectedEmotion,
      instruction: `Practice expressing ${selectedEmotion} appropriately`,
      scenarios: scenarioData.situations || scenarioData.levels || scenarioData.frameworks,
      tips: this.getEmotionTips(selectedEmotion),
      practice: {
        record: 'Record yourself responding to these scenarios',
        listen: 'Listen to your tone - does it match the intended emotion?',
        adjust: 'Try different variations to find what feels natural',
      },
    };
  }

  /**
   * Get emotion-specific tips
   */
  getEmotionTips(emotion) {
    const tips = {
      empathy: [
        'Use a gentle, caring tone',
        'Validate their feelings first',
        'Avoid minimizing their experience',
        'Offer support, not solutions (unless asked)',
      ],
      enthusiasm: [
        'Vary your pitch and volume',
        'Use exclamatory words genuinely',
        'Mirror their energy',
        'Show it in your facial expressions too',
      ],
      disagreement: [
        'Stay calm and respectful',
        'Acknowledge their perspective first',
        'Use "I" statements',
        'Focus on ideas, not the person',
      ],
      bad_news: [
        'Be direct but compassionate',
        'Choose the right time and place',
        'Allow time for processing',
        'Offer support and next steps',
      ],
    };

    return tips[emotion] || [];
  }

  /**
   * Get cultural context lesson
   */
  getCulturalContextLesson(topic) {
    const lessons = {
      greetings: {
        title: 'Cultural Differences in Greetings',
        content: this.culturalContexts.greetings,
        keyTakeaways: [
          'Adapt your greeting style to the cultural context',
          'Observe and mirror the formality level',
          'When in doubt, start more formal',
          'Physical contact varies greatly by culture',
        ],
      },
      business: {
        title: 'Business Communication Styles',
        content: this.culturalContexts.business_culture,
        keyTakeaways: [
          'Direct vs. indirect communication varies by culture',
          'Time perception affects business interactions',
          'Build awareness of high-context vs. low-context cultures',
          'Adapt your style when working internationally',
        ],
      },
      taboos: {
        title: 'Topics to Avoid in Conversation',
        content: this.culturalContexts.taboo_topics,
        keyTakeaways: [
          'Some topics are universally sensitive',
          'What\'s acceptable varies by culture and relationship',
          'Start with safer topics like weather, hobbies, food',
          'Let the other person bring up personal topics first',
        ],
      },
      politeness: {
        title: 'Politeness Strategies in English',
        content: this.culturalContexts.politeness_strategies,
        keyTakeaways: [
          'Indirect language is often more polite',
          'Use modal verbs (could, would, might) for politeness',
          'Soften requests and refusals',
          'Consider power distance and familiarity',
        ],
      },
    };

    return lessons[topic] || {
      error: 'Topic not found',
      available: Object.keys(lessons),
    };
  }

  /**
   * Generate role-playing scenario
   */
  generateRolePlayScenario(context = 'professional') {
    const scenarios = {
      professional: [
        {
          situation: 'Difficult Client Meeting',
          yourRole: 'Account Manager',
          otherRole: 'Unhappy Client',
          objective: 'Address concerns and maintain the relationship',
          challenges: ['Client is frustrated', 'Project is behind schedule', 'Budget concerns'],
          usefulPhrases: [
            'I understand your frustration',
            'Let me explain what happened',
            'Here\'s what we can do to fix this',
          ],
        },
        {
          situation: 'Performance Review',
          yourRole: 'Employee',
          otherRole: 'Manager',
          objective: 'Discuss achievements and request a raise',
          challenges: ['Need to advocate for yourself', 'Justify the raise', 'Handle objections'],
          usefulPhrases: [
            'I\'d like to discuss my performance and compensation',
            'I\'ve achieved the following results...',
            'Based on this, I believe a salary adjustment is warranted',
          ],
        },
      ],
      social: [
        {
          situation: 'Networking Event',
          yourRole: 'Professional looking to expand network',
          otherRole: 'Potential contact',
          objective: 'Make a good impression and exchange contact information',
          challenges: ['Start conversation with stranger', 'Find common ground', 'End gracefully'],
          usefulPhrases: [
            'Hi, I\'m [name]. What brings you here?',
            'That\'s interesting! Tell me more about that',
            'It was great meeting you. Can we connect on LinkedIn?',
          ],
        },
      ],
      service: [
        {
          situation: 'Restaurant Complaint',
          yourRole: 'Customer',
          otherRole: 'Restaurant Manager',
          objective: 'Resolve an issue with your order',
          challenges: ['Stay polite but firm', 'Explain the problem clearly', 'Get satisfactory resolution'],
          usefulPhrases: [
            'I\'m sorry to bring this up, but...',
            'This isn\'t what I ordered',
            'How can we resolve this?',
          ],
        },
      ],
    };

    const contextScenarios = scenarios[context] || scenarios.professional;
    const scenario = contextScenarios[Math.floor(Math.random() * contextScenarios.length)];

    return {
      id: Date.now(),
      context,
      ...scenario,
      evaluationPoints: [
        'Appropriate language for the situation',
        'Clear communication of objectives',
        'Handling of challenges',
        'Tone and politeness',
        'Achievement of goal',
      ],
    };
  }
}

export default new SocialLearningService();
