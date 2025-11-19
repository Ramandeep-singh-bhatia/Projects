/**
 * Advanced Conversation Skills Service
 * Interruption recovery, storytelling, active listening, negotiation, turn-taking
 */

class AdvancedConversationService {
  constructor() {
    this.storytellingFrameworks = this.initializeStorytellingFrameworks();
    this.negotiationStrategies = this.initializeNegotiationStrategies();
    this.conversationRepair = this.initializeConversationRepair();
    this.turnTakingPatterns = this.initializeTurnTakingPatterns();
  }

  /**
   * Initialize storytelling frameworks
   */
  initializeStorytellingFrameworks() {
    return {
      situation_complication_resolution: {
        name: 'SCR Framework',
        description: 'Situation, Complication, Resolution - classic story structure',
        template: {
          situation: 'Set the scene - where, when, who',
          complication: 'What went wrong or what was the challenge',
          resolution: 'How it was resolved and what happened',
        },
        example: {
          situation: 'Last summer, I was traveling in Japan and needed to catch a train.',
          complication: 'But I couldn\'t read the schedule and missed my original train.',
          resolution: 'A kind stranger helped me find the next train and I made it just in time.',
        },
        tips: [
          'Start with context',
          'Build tension with the complication',
          'End with a satisfying resolution',
          'Keep it concise - 2-3 minutes max',
        ],
      },
      star_method: {
        name: 'STAR Method',
        description: 'Situation, Task, Action, Result - ideal for professional stories',
        template: {
          situation: 'Describe the context',
          task: 'Explain your responsibility',
          action: 'Detail what you did',
          result: 'Share the outcome',
        },
        example: {
          situation: 'Our team was behind on a major project deadline.',
          task: 'As lead, I needed to get us back on track.',
          action: 'I reorganized the workflow and delegated tasks based on strengths.',
          result: 'We delivered on time and received praise from the client.',
        },
        useCases: ['Job interviews', 'Performance reviews', 'Professional networking'],
      },
      hero_journey: {
        name: 'Hero\'s Journey (Simplified)',
        description: 'Personal growth story framework',
        template: {
          ordinary_world: 'Your situation before the change',
          challenge: 'What pushed you out of comfort zone',
          struggle: 'The difficulties you faced',
          transformation: 'How you changed or what you learned',
        },
        example: {
          ordinary_world: 'I was afraid of public speaking my whole life.',
          challenge: 'My job required me to present to clients.',
          struggle: 'My first presentations were terrifying and awkward.',
          transformation: 'Now I actually enjoy presenting and it\'s one of my strengths.',
        },
      },
      punchline_first: {
        name: 'Punchline First',
        description: 'Start with the interesting part, then explain',
        template: {
          hook: 'The most interesting/surprising part',
          backstory: 'How you got there',
          details: 'Fill in the interesting details',
        },
        example: {
          hook: 'I ended up having dinner with a movie star!',
          backstory: 'I was just at a random restaurant in LA...',
          details: '[Fill in the story]',
        },
        tips: [
          'Grab attention immediately',
          'Good for casual conversations',
          'Make sure the hook is genuinely interesting',
        ],
      },
    };
  }

  /**
   * Initialize negotiation strategies
   */
  initializeNegotiationStrategies() {
    return {
      salary_negotiation: {
        framework: [
          {
            stage: 'Research',
            actions: [
              'Know market rates for your role',
              'Document your achievements',
              'Understand company\'s position',
            ],
          },
          {
            stage: 'Opening',
            phrases: [
              'Based on my research and experience, I was hoping for...',
              'I\'ve looked at comparable positions and...',
              'Given my contributions to [specific achievement]...',
            ],
          },
          {
            stage: 'Handling_Objections',
            responses: [
              {
                objection: 'That\'s above our budget',
                response: 'I understand budget constraints. Could we discuss other forms of compensation like [benefits, equity, etc.]?',
              },
              {
                objection: 'You don\'t have enough experience',
                response: 'I see your point. However, I have demonstrated [specific skills/results]. Can we revisit this in [timeframe]?',
              },
            ],
          },
          {
            stage: 'Closing',
            phrases: [
              'I\'m excited about this role. Can we find a number that works for both of us?',
              'I\'d like to accept if we can agree on [X]',
            ],
          },
        ],
        tips: [
          'Always negotiate in person or by phone, not email',
          'Show enthusiasm for the role',
          'Have a minimum acceptable number in mind',
          'Be prepared to walk away',
        ],
      },
      conflict_resolution: {
        framework: [
          {
            step: 'Listen First',
            technique: 'Let the other person fully express their view',
            phrases: [
              'I want to understand your perspective',
              'Help me see this from your point of view',
              'Tell me more about why this concerns you',
            ],
          },
          {
            step: 'Acknowledge',
            technique: 'Show you heard and understood',
            phrases: [
              'I hear that you\'re frustrated because...',
              'So what you\'re saying is...',
              'I can see why that would be upsetting',
            ],
          },
          {
            step: 'Share Your View',
            technique: 'Use "I" statements, not "you" accusations',
            phrases: [
              'From my perspective...',
              'I feel... when...',
              'My concern is...',
            ],
          },
          {
            step: 'Find Common Ground',
            technique: 'Identify shared goals or values',
            phrases: [
              'We both want...',
              'I think we can agree that...',
              'Our shared goal is...',
            ],
          },
          {
            step: 'Propose Solutions',
            technique: 'Collaborative problem-solving',
            phrases: [
              'What if we tried...',
              'Would you be open to...',
              'How about we...',
            ],
          },
        ],
      },
      persuasion: {
        techniques: [
          {
            name: 'Reciprocity',
            description: 'Give something first',
            example: 'I helped with your project last week. Could you review my proposal?',
          },
          {
            name: 'Social Proof',
            description: 'Show others are doing it',
            example: 'Several other departments have already adopted this approach successfully.',
          },
          {
            name: 'Authority',
            description: 'Reference credible sources',
            example: 'According to industry experts / research shows...',
          },
          {
            name: 'Scarcity',
            description: 'Highlight limited availability',
            example: 'This opportunity is only available for a limited time.',
          },
          {
            name: 'Consistency',
            description: 'Remind of previous commitments',
            example: 'You mentioned that quality was your priority. This aligns with that.',
          },
        ],
        structure: {
          opening: 'Start with common ground or shared goal',
          body: 'Present benefits using 2-3 techniques above',
          objections: 'Anticipate and address concerns',
          close: 'Clear call to action',
        },
      },
    };
  }

  /**
   * Initialize conversation repair strategies
   */
  initializeConversationRepair() {
    return {
      clarification_requests: {
        polite: [
          'I\'m sorry, I didn\'t quite catch that. Could you repeat it?',
          'Could you say that again, please?',
          'I\'m not sure I understood. Did you mean...?',
        ],
        specific: [
          'When you say [word], what exactly do you mean?',
          'Could you clarify what you meant by [phrase]?',
          'I\'m not familiar with that term. Could you explain?',
        ],
        checking_understanding: [
          'So what you\'re saying is... Is that right?',
          'Let me make sure I understand...',
          'Just to confirm...',
        ],
      },
      topic_transitions: {
        subtle: [
          'That reminds me of...',
          'Speaking of [topic]...',
          'On a related note...',
        ],
        direct: [
          'Can I change the subject for a moment?',
          'I\'d like to talk about something else if that\'s okay',
          'Before we move on, there\'s something I wanted to mention...',
        ],
        returning: [
          'Going back to what you said earlier...',
          'You mentioned [topic] before...',
          'To return to your question...',
        ],
      },
      interruption_recovery: {
        when_interrupted: {
          polite: [
            'If I could just finish this thought...',
            'Let me complete this point, then I\'d love to hear your input',
            'Hold that thought - I want to finish this idea first',
          ],
          assertive: [
            'Please let me finish',
            'I\'m not done speaking',
            'One moment, let me complete this',
          ],
        },
        when_you_interrupt: {
          apologize: [
            'Oh sorry, please continue',
            'I apologize for interrupting. Go ahead',
            'My apologies - what were you saying?',
          ],
          acknowledge: [
            'Sorry, I got excited. Please finish your thought',
            'Excuse me for cutting you off',
          ],
        },
        recovering_after_interruption: {
          phrases: [
            'So as I was saying...',
            'Where was I? Oh yes...',
            'Anyway, my point was...',
          ],
        },
      },
      misunderstandings: {
        realizing_error: [
          'Actually, I think I misunderstood. Let me rephrase...',
          'I\'m sorry, I realize I wasn\'t clear',
          'Let me explain that better...',
        ],
        correcting_politely: [
          'I think there might be a small misunderstanding...',
          'Just to clarify...',
          'Actually, what I meant was...',
        ],
        when_corrected: [
          'Oh, thank you for clarifying',
          'I see, I misunderstood',
          'That makes more sense, thanks',
        ],
      },
    };
  }

  /**
   * Initialize turn-taking patterns
   */
  initializeTurnTakingPatterns() {
    return {
      yielding_turn: {
        description: 'Signaling you\'re done speaking',
        verbal_cues: [
          'So that\'s my take on it',
          'Anyway...',
          'But what do you think?',
          'Does that make sense?',
        ],
        nonverbal: [
          'Decrease in volume at end',
          'Final falling intonation',
          'Longer pause',
          'Eye contact invitation',
        ],
      },
      taking_turn: {
        description: 'Entering the conversation',
        smooth_entry: [
          'That\'s interesting because...',
          'Building on that...',
          'I have a similar experience...',
        ],
        requesting_turn: [
          'May I add something?',
          'Can I jump in here?',
          'If I could add to that...',
        ],
        timing: [
          'Wait for natural pause',
          'Don\'t interrupt mid-sentence',
          'Use transition phrases',
        ],
      },
      holding_turn: {
        description: 'Keeping the floor when you have more to say',
        fillers: [
          'And...',
          'So...',
          'Um... (use sparingly)',
        ],
        signals: [
          'Raised hand gesture',
          'Maintained eye contact away from listener',
          'Continuous speaking without long pauses',
        ],
      },
      back_channeling: {
        description: 'Showing you\'re listening without taking turn',
        minimal_responses: [
          'Mm-hmm',
          'I see',
          'Right',
          'Uh-huh',
          'Oh really?',
        ],
        encouragement: [
          'That\'s interesting',
          'Tell me more',
          'And then what happened?',
          'How did that make you feel?',
        ],
      },
    };
  }

  /**
   * Generate interruption recovery exercise
   */
  generateInterruptionRecoveryExercise() {
    const scenarios = [
      {
        situation: 'You\'re presenting an idea in a meeting and a colleague interrupts',
        yourAction: 'Politely reclaim your turn',
        practice: 'Practice saying: "If I could just finish this thought..." then complete your idea',
        evaluation: ['Remained polite', 'Asserted yourself', 'Completed your point'],
      },
      {
        situation: 'You accidentally interrupted someone',
        yourAction: 'Apologize and let them continue',
        practice: 'Practice saying: "Oh sorry, please continue" with genuine tone',
        evaluation: ['Quick apology', 'Gave back the floor', 'Seemed genuine'],
      },
      {
        situation: 'Someone keeps interrupting you in conversation',
        yourAction: 'Address it directly but kindly',
        practice: 'Practice saying: "I\'d like to finish what I\'m saying, then I\'d love to hear your thoughts"',
        evaluation: ['Direct but polite', 'Set boundary', 'Offered turn after'],
      },
    ];

    const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];

    return {
      id: Date.now(),
      type: 'interruption_recovery',
      ...scenario,
      tips: this.conversationRepair.interruption_recovery,
      advice: [
        'Stay calm and confident',
        'Don\'t get defensive',
        'Use appropriate tone',
        'Body language matters',
      ],
    };
  }

  /**
   * Generate storytelling exercise
   */
  generateStorytellingExercise(framework = null, topic = null) {
    const frameworks = Object.keys(this.storytellingFrameworks);
    const selectedFramework = framework || frameworks[Math.floor(Math.random() * frameworks.length)];
    const frameworkData = this.storytellingFrameworks[selectedFramework];

    const topics = [
      'A challenge you overcame',
      'An unexpected adventure',
      'A time you learned something important',
      'A funny mistake you made',
      'Your proudest achievement',
      'A time you helped someone',
      'An embarrassing moment',
      'Your first day at a new job/school',
    ];

    const selectedTopic = topic || topics[Math.floor(Math.random() * topics.length)];

    return {
      id: Date.now(),
      type: 'storytelling',
      framework: selectedFramework,
      frameworkName: frameworkData.name,
      description: frameworkData.description,
      template: frameworkData.template,
      example: frameworkData.example,
      topic: selectedTopic,
      timeLimit: 180, // 3 minutes
      evaluation: {
        structure: 'Did you follow the framework?',
        engagement: 'Was it interesting?',
        clarity: 'Was it easy to follow?',
        delivery: 'Good pace and intonation?',
        completion: 'Did you finish within time?',
      },
      tips: frameworkData.tips || [
        'Practice beforehand',
        'Use vivid details',
        'Show, don\'t just tell',
        'End strong',
      ],
    };
  }

  /**
   * Generate active listening simulation
   */
  generateActiveListeningExercise() {
    const scenarios = [
      {
        speaker_role: 'Friend telling you about a problem',
        story: 'Your friend is stressed about an upcoming exam they feel unprepared for',
        poor_listening: [
          'Immediately give advice',
          'Change subject to your own exam stress',
          'Minimize their concern ("It\'s not that bad")',
        ],
        good_listening: [
          'Make eye contact',
          'Use back-channeling ("Mm-hmm", "I see")',
          'Paraphrase: "So you\'re worried about the exam because you haven\'t had time to study?"',
          'Show empathy: "That sounds really stressful"',
          'Ask open questions: "What are you most concerned about?"',
        ],
      },
      {
        speaker_role: 'Colleague explaining a complex problem',
        story: 'Your colleague is describing a technical issue they\'re facing',
        poor_listening: [
          'Interrupt with solutions before they finish',
          'Check your phone',
          'Assume you know what they\'ll say',
        ],
        good_listening: [
          'Let them finish explaining',
          'Take mental notes of key points',
          'Ask clarifying questions',
          'Summarize understanding: "So the main issue is...?"',
          'Offer to help after fully understanding',
        ],
      },
    ];

    const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];

    return {
      id: Date.now(),
      type: 'active_listening',
      ...scenario,
      activeListeningTechniques: {
        verbal: [
          'Paraphrasing: Repeat back in your own words',
          'Clarifying: Ask questions to understand better',
          'Summarizing: Recap main points',
          'Empathizing: Acknowledge feelings',
        ],
        nonverbal: [
          'Eye contact (culturally appropriate)',
          'Nodding',
          'Open body language',
          'Leaning slightly forward',
          'Facial expressions matching emotion',
        ],
        avoid: [
          'Planning your response while they talk',
          'Interrupting',
          'Judging',
          'Giving unsolicited advice',
        ],
      },
      practice: 'Try this with a real conversation today and note what worked',
    };
  }

  /**
   * Generate negotiation practice
   */
  generateNegotiationPractice(type = 'salary_negotiation') {
    const negotiation = this.negotiationStrategies[type];

    if (!negotiation) {
      return {
        error: 'Negotiation type not found',
        available: Object.keys(this.negotiationStrategies),
      };
    }

    return {
      id: Date.now(),
      type: type,
      framework: negotiation.framework || negotiation.techniques,
      scenario: this.getNegotiationScenario(type),
      tips: negotiation.tips || [],
      commonMistakes: this.getNegotiationMistakes(type),
      practice: {
        preparation: 'Write down your key points before starting',
        execution: 'Practice the dialogue out loud',
        reflection: 'What would you do differently?',
      },
    };
  }

  /**
   * Get negotiation scenario
   */
  getNegotiationScenario(type) {
    const scenarios = {
      salary_negotiation: {
        context: 'You\'ve been offered a job at $60,000 but market rate is $70,000',
        yourGoal: 'Negotiate to at least $68,000',
        theirPosition: 'Budget conscious but want to hire you',
      },
      conflict_resolution: {
        context: 'You and a colleague disagree on project approach',
        yourGoal: 'Find a solution that incorporates both perspectives',
        theirPosition: 'Convinced their way is better',
      },
      persuasion: {
        context: 'You want to convince your team to try a new process',
        yourGoal: 'Get agreement to pilot the new approach',
        theirPosition: 'Comfortable with current process, resistant to change',
      },
    };

    return scenarios[type] || {};
  }

  /**
   * Get common negotiation mistakes
   */
  getNegotiationMistakes(type) {
    const mistakes = {
      salary_negotiation: [
        'Accepting first offer without negotiating',
        'Focusing only on salary (not total compensation)',
        'Being aggressive or demanding',
        'Not knowing your market value',
      ],
      conflict_resolution: [
        'Getting emotional or defensive',
        'Not listening to other perspective',
        'Focusing on being right vs finding solution',
        'Bringing up past grievances',
      ],
      persuasion: [
        'Only presenting one option',
        'Not addressing concerns',
        'Being too pushy',
        'Not showing value/benefits',
      ],
    };

    return mistakes[type] || [];
  }

  /**
   * Generate conversation repair exercise
   */
  generateConversationRepairExercise() {
    const repairTypes = ['clarification', 'topic_transition', 'misunderstanding'];
    const type = repairTypes[Math.floor(Math.random() * repairTypes.length)];

    const exercises = {
      clarification: {
        scenario: 'Someone used a word or phrase you don\'t understand',
        practice: 'Ask for clarification politely without stopping flow',
        phrases: this.conversationRepair.clarification_requests,
        tips: [
          'Don\'t pretend to understand',
          'Ask sooner rather than later',
          'Be specific about what you didn\'t understand',
        ],
      },
      topic_transition: {
        scenario: 'The conversation has run its course and you want to change topics',
        practice: 'Smoothly transition to a new topic',
        phrases: this.conversationRepair.topic_transitions,
        tips: [
          'Find a natural connection',
          'Don\'t abruptly change',
          'Check if current topic is finished',
        ],
      },
      misunderstanding: {
        scenario: 'You realize there\'s been a misunderstanding',
        practice: 'Clarify without making it awkward',
        phrases: this.conversationRepair.misunderstandings,
        tips: [
          'Address it promptly',
          'Take responsibility if needed',
          'Don\'t blame',
          'Move forward once cleared up',
        ],
      },
    };

    return {
      id: Date.now(),
      type: 'conversation_repair',
      repairType: type,
      ...exercises[type],
    };
  }

  /**
   * Generate turn-taking exercise
   */
  generateTurnTakingExercise() {
    return {
      id: Date.now(),
      type: 'turn_taking',
      skills: [
        {
          skill: 'Yielding the floor',
          description: 'Signaling you\'re done speaking',
          techniques: this.turnTakingPatterns.yielding_turn,
          practice: 'End your statements with clear signals that invite response',
        },
        {
          skill: 'Taking your turn',
          description: 'Entering the conversation smoothly',
          techniques: this.turnTakingPatterns.taking_turn,
          practice: 'Wait for natural pause, then use transition phrase',
        },
        {
          skill: 'Holding the floor',
          description: 'Keeping your turn when you have more to say',
          techniques: this.turnTakingPatterns.holding_turn,
          practice: 'Use continuation signals when you\'re not done',
        },
        {
          skill: 'Back-channeling',
          description: 'Showing engagement without taking turn',
          techniques: this.turnTakingPatterns.back_channeling,
          practice: 'Use minimal responses to show you\'re listening',
        },
      ],
      scenario: {
        description: 'Group discussion about weekend plans',
        challenge: 'Practice all four turn-taking skills naturally',
        participants: 3,
        duration: 5,
      },
      evaluation: [
        'Did everyone get equal speaking time?',
        'Were transitions smooth?',
        'Did you show active listening?',
        'Did you contribute meaningfully?',
      ],
    };
  }

  /**
   * Comprehensive conversation analysis
   */
  analyzeConversationSkills(conversationTranscript) {
    const analysis = {
      turn_taking: this.analyzeTurnTaking(conversationTranscript),
      topic_management: this.analyzeTopicManagement(conversationTranscript),
      engagement: this.analyzeEngagement(conversationTranscript),
      clarity: this.analyzeClarity(conversationTranscript),
      recommendations: [],
    };

    // Generate recommendations
    if (analysis.turn_taking.interruptions > 3) {
      analysis.recommendations.push('Practice waiting for natural pauses before speaking');
    }

    if (analysis.engagement.backchanneling < 2) {
      analysis.recommendations.push('Use more listening signals like "mm-hmm", "I see"');
    }

    if (analysis.topic_management.abruptTransitions > 2) {
      analysis.recommendations.push('Use smoother topic transitions with connecting phrases');
    }

    return analysis;
  }

  /**
   * Analyze turn-taking in transcript
   */
  analyzeTurnTaking(transcript) {
    // Simplified analysis - in real implementation would use NLP
    return {
      speakingTurns: 0,
      interruptions: 0,
      smoothTransitions: 0,
      rating: 'good',
    };
  }

  /**
   * Analyze topic management
   */
  analyzeTopicManagement(transcript) {
    return {
      topicChanges: 0,
      smoothTransitions: 0,
      abruptTransitions: 0,
      rating: 'good',
    };
  }

  /**
   * Analyze engagement
   */
  analyzeEngagement(transcript) {
    return {
      backchanneling: 0,
      questions: 0,
      empathyStatements: 0,
      rating: 'good',
    };
  }

  /**
   * Analyze clarity
   */
  analyzeClarity(transcript) {
    return {
      clarificationRequests: 0,
      fillerWords: 0,
      completeThoughts: 0,
      rating: 'good',
    };
  }
}

export default new AdvancedConversationService();
