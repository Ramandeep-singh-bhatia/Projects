/**
 * Practical Application Tools Service
 * Quick lookup, phrase builders, anti-translation trainer, context suggestions
 */

class PracticalToolsService {
  constructor() {
    this.commonSituations = this.initializeCommonSituations();
    this.phraseTemplates = this.initializePhraseTemplates();
    this.contextualPhrases = this.initializeContextualPhrases();
  }

  /**
   * Initialize common real-world situations
   */
  initializeCommonSituations() {
    return {
      restaurant: {
        scenarios: [
          'Making a reservation',
          'Ordering food',
          'Asking about ingredients',
          'Requesting the bill',
          'Complaining politely',
        ],
        vocabulary: ['reservation', 'menu', 'appetizer', 'main course', 'bill', 'tip'],
      },
      shopping: {
        scenarios: [
          'Asking for sizes',
          'Trying things on',
          'Asking for discounts',
          'Returning items',
          'Comparing products',
        ],
        vocabulary: ['size', 'fitting room', 'receipt', 'refund', 'discount', 'exchange'],
      },
      workplace: {
        scenarios: [
          'Scheduling meetings',
          'Giving presentations',
          'Asking for clarification',
          'Providing updates',
          'Requesting time off',
        ],
        vocabulary: ['deadline', 'agenda', 'follow-up', 'deliverable', 'stakeholder'],
      },
      healthcare: {
        scenarios: [
          'Describing symptoms',
          'Making appointments',
          'Understanding prescriptions',
          'Asking about side effects',
        ],
        vocabulary: ['symptoms', 'prescription', 'appointment', 'medication', 'allergy'],
      },
      travel: {
        scenarios: [
          'Checking in at hotel',
          'Asking for directions',
          'Booking transportation',
          'Reporting lost items',
        ],
        vocabulary: ['itinerary', 'boarding pass', 'reservation', 'luggage', 'destination'],
      },
    };
  }

  /**
   * Initialize phrase templates
   */
  initializePhraseTemplates() {
    return {
      making_requests: {
        veryDirect: 'Give me [item]',
        direct: 'Can I have [item]?',
        polite: 'Could I please have [item]?',
        veryPolite: 'I was wondering if I might have [item]?',
        formal: 'Would it be possible to have [item]?',
      },
      disagreeing: {
        casual: 'I don\'t think so',
        polite: 'I see your point, but...',
        diplomatic: 'That\'s one way to look at it. However...',
        formal: 'I respectfully disagree because...',
        academic: 'While that perspective has merit, alternative evidence suggests...',
      },
      asking_permission: {
        informal: 'Can I...?',
        neutral: 'May I...?',
        polite: 'Would it be okay if I...?',
        formal: 'Would you mind if I...?',
        veryFormal: 'I would like to request permission to...',
      },
      giving_opinions: {
        casual: 'I think...',
        confident: 'In my opinion...',
        tentative: 'It seems to me that...',
        balanced: 'From my perspective...',
        formal: 'I would argue that...',
      },
      apologizing: {
        simple: 'Sorry',
        sincere: 'I\'m really sorry',
        formal: 'I apologize',
        taking_responsibility: 'I apologize for my mistake',
        professional: 'Please accept my sincerest apologies',
      },
    };
  }

  /**
   * Initialize contextual phrases
   */
  initializeContextualPhrases() {
    return {
      email_writing: {
        opening_formal: [
          'Dear [Name],',
          'I hope this email finds you well.',
          'Thank you for your email regarding...',
        ],
        opening_casual: [
          'Hi [Name],',
          'Hope you\'re doing well!',
          'Thanks for reaching out!',
        ],
        closing_formal: [
          'Best regards,',
          'Sincerely,',
          'Kind regards,',
        ],
        closing_casual: [
          'Best,',
          'Cheers,',
          'Talk soon,',
        ],
      },
      phone_calls: {
        answering: [
          'Hello, this is [name] speaking.',
          '[Name] speaking, how can I help you?',
          'Good morning/afternoon, [name] here.',
        ],
        asking_for_someone: [
          'May I speak with [name], please?',
          'Is [name] available?',
          'Could you connect me to [name]?',
        ],
        leaving_message: [
          'Could you take a message?',
          'Please let them know I called.',
          'Could you ask them to call me back?',
        ],
      },
      presentations: {
        opening: [
          'Good morning everyone. Today I\'ll be talking about...',
          'Thank you for being here. Let\'s dive into...',
          'I\'m excited to share with you...',
        ],
        transitions: [
          'Moving on to the next point...',
          'Now let\'s look at...',
          'This brings us to...',
        ],
        closing: [
          'To sum up...',
          'In conclusion...',
          'Let me wrap up by saying...',
        ],
      },
    };
  }

  /**
   * Quick phrase lookup
   */
  quickLookup(situation, intent) {
    const situationData = this.commonSituations[situation];

    if (!situationData) {
      return {
        found: false,
        message: 'Situation not found. Try: restaurant, shopping, workplace, healthcare, travel',
      };
    }

    // Get relevant phrases for the situation
    const phrases = this.generatePhrasesForSituation(situation, intent);

    return {
      found: true,
      situation,
      intent,
      phrases,
      vocabulary: situationData.vocabulary,
      examples: this.getExamplesForSituation(situation, intent),
    };
  }

  /**
   * Generate phrases for a situation
   */
  generatePhrasesForSituation(situation, intent) {
    const situationPhrases = {
      restaurant: {
        ordering: [
          'I\'d like to order the [dish], please.',
          'Could I have the [dish]?',
          'I\'ll have the [dish], thank you.',
        ],
        asking: [
          'What do you recommend?',
          'Does this contain [ingredient]?',
          'How spicy is this dish?',
        ],
        complaining: [
          'I\'m sorry, but this isn\'t what I ordered.',
          'Excuse me, there seems to be a problem with...',
          'Would it be possible to get this replaced?',
        ],
      },
      shopping: {
        asking: [
          'Do you have this in a different size/color?',
          'Where can I find [item]?',
          'How much does this cost?',
        ],
        trying: [
          'Can I try this on?',
          'Where are the fitting rooms?',
          'Do you have a mirror?',
        ],
        purchasing: [
          'I\'ll take this.',
          'Do you accept credit cards?',
          'Can I get a receipt?',
        ],
      },
      workplace: {
        requesting: [
          'Could you send me the report by [date]?',
          'I\'d like to schedule a meeting to discuss...',
          'Would it be possible to get an extension on...?',
        ],
        updating: [
          'Just wanted to update you on...',
          'Here\'s the progress so far...',
          'I\'ve completed the first phase of...',
        ],
        clarifying: [
          'Could you clarify what you mean by...?',
          'Just to make sure I understand...',
          'So you\'re saying that...?',
        ],
      },
    };

    return situationPhrases[situation]?.[intent] || [
      'No specific phrases found for this combination.',
    ];
  }

  /**
   * Get examples for situation
   */
  getExamplesForSituation(situation, intent) {
    const examples = {
      restaurant_ordering: [
        {
          you: 'I\'d like to order the grilled salmon, please.',
          them: 'Certainly! Would you like that with vegetables or salad?',
          you: 'Vegetables, please.',
        },
      ],
      shopping_asking: [
        {
          you: 'Excuse me, do you have this shirt in medium?',
          them: 'Let me check for you. Yes, we have it in stock.',
          you: 'Great! Can I try it on?',
        },
      ],
      workplace_requesting: [
        {
          you: 'Hi Sarah, could you send me the Q3 report when you have a moment?',
          them: 'Sure! I\'ll send it over by end of day.',
          you: 'Perfect, thank you!',
        },
      ],
    };

    const key = `${situation}_${intent}`;
    return examples[key] || [];
  }

  /**
   * Phrase builder - express the same idea multiple ways
   */
  buildPhraseVariations(baseIdea, context = 'neutral', aiService = null) {
    const variations = {
      variations: [],
      context,
      registers: ['very_informal', 'informal', 'neutral', 'formal', 'very_formal'],
    };

    // Common phrase patterns
    const patterns = this.getPatternForIdea(baseIdea, context);

    if (patterns.length > 0) {
      variations.variations = patterns;
    } else {
      // Default variations
      variations.variations = [
        { register: 'very_informal', phrase: baseIdea, explanation: 'Casual conversation with friends' },
        { register: 'informal', phrase: this.makeInformal(baseIdea), explanation: 'Relaxed but clear' },
        { register: 'neutral', phrase: baseIdea, explanation: 'Standard, all-purpose' },
        { register: 'formal', phrase: this.makeFormal(baseIdea), explanation: 'Business or professional' },
        { register: 'very_formal', phrase: this.makeVeryFormal(baseIdea), explanation: 'Official or academic' },
      ];
    }

    return variations;
  }

  /**
   * Get pattern variations for common ideas
   */
  getPatternForIdea(idea, context) {
    const lowerIdea = idea.toLowerCase();

    // Disagreement patterns
    if (lowerIdea.includes('disagree') || lowerIdea.includes('don\'t think')) {
      return [
        { register: 'very_informal', phrase: 'Nah, I don\'t think so', explanation: 'Very casual' },
        { register: 'informal', phrase: 'I don\'t really agree', explanation: 'Friendly disagreement' },
        { register: 'neutral', phrase: 'I have a different opinion', explanation: 'Neutral stance' },
        { register: 'formal', phrase: 'I\'m afraid I must disagree', explanation: 'Polite disagreement' },
        { register: 'very_formal', phrase: 'I respectfully hold a contrary view', explanation: 'Diplomatic' },
      ];
    }

    // Request patterns
    if (lowerIdea.includes('can you') || lowerIdea.includes('help')) {
      return [
        { register: 'very_informal', phrase: 'Can you help me?', explanation: 'Direct request' },
        { register: 'informal', phrase: 'Could you help me out?', explanation: 'Friendly request' },
        { register: 'neutral', phrase: 'Could you please help me?', explanation: 'Polite request' },
        { register: 'formal', phrase: 'Would you be able to assist me?', explanation: 'Professional' },
        { register: 'very_formal', phrase: 'I would greatly appreciate your assistance', explanation: 'Very polite' },
      ];
    }

    return [];
  }

  /**
   * Make phrase more informal
   */
  makeInformal(phrase) {
    return phrase
      .replace(/could you/gi, 'can you')
      .replace(/would you/gi, 'will you')
      .replace(/I would/gi, 'I\'d')
      .replace(/purchase/gi, 'buy')
      .replace(/assist/gi, 'help');
  }

  /**
   * Make phrase more formal
   */
  makeFormal(phrase) {
    return phrase
      .replace(/can you/gi, 'could you')
      .replace(/want to/gi, 'would like to')
      .replace(/buy/gi, 'purchase')
      .replace(/help/gi, 'assist')
      .replace(/get/gi, 'obtain');
  }

  /**
   * Make phrase very formal
   */
  makeVeryFormal(phrase) {
    return this.makeFormal(phrase)
      .replace(/could you/gi, 'would it be possible for you to')
      .replace(/I would like/gi, 'I would be grateful if I could')
      .replace(/sorry/gi, 'I apologize');
  }

  /**
   * Anti-translation trainer
   * Helps users think in English, not translate from native language
   */
  generateAntiTranslationExercise(nativeLanguage = 'general') {
    const exercises = {
      general: [
        {
          concept: 'Age',
          wrongThinking: 'I have 25 years',
          correctThinking: 'I am 25 years old',
          explanation: 'English uses "to be" for age, not "to have"',
        },
        {
          concept: 'Weather',
          wrongThinking: 'It has rain',
          correctThinking: 'It is raining / It\'s rainy',
          explanation: 'Weather uses "to be" + adjective or present continuous',
        },
        {
          concept: 'Hunger',
          wrongThinking: 'I have hungry',
          correctThinking: 'I am hungry',
          explanation: 'Feelings use "to be" + adjective in English',
        },
      ],
      spanish: [
        {
          concept: 'Liking things',
          wrongThinking: 'I like very much pizza',
          correctThinking: 'I really like pizza / I like pizza a lot',
          explanation: '"Very much" comes after the object, or use "really"',
        },
        {
          concept: 'Making things',
          wrongThinking: 'I make sport',
          correctThinking: 'I play sports / I do exercise',
          explanation: 'Use "play" for sports, "do" for exercise, "make" for creating things',
        },
      ],
      chinese: [
        {
          concept: 'Possession',
          wrongThinking: 'I have seen that movie already',
          correctThinking: 'I have already seen that movie',
          explanation: '"Already" usually comes before the past participle',
        },
        {
          concept: 'Questions',
          wrongThinking: 'You want go where?',
          correctThinking: 'Where do you want to go?',
          explanation: 'English questions need auxiliary verbs and specific word order',
        },
      ],
    };

    const exerciseSet = exercises[nativeLanguage] || exercises.general;
    const randomExercise = exerciseSet[Math.floor(Math.random() * exerciseSet.length)];

    return {
      id: Date.now(),
      type: 'anti_translation',
      nativeLanguage,
      exercise: randomExercise,
      challenge: 'Think about why the correct version is different. Try to think directly in English patterns.',
      practice: {
        instruction: 'Create 3 similar sentences using the correct English pattern',
        targetPattern: randomExercise.correctThinking,
      },
    };
  }

  /**
   * Context-appropriate suggestions
   */
  getSituationAppropriateLanguage(situation, formality = 'neutral') {
    const suggestions = {
      job_interview: {
        formal: {
          greetings: ['Good morning/afternoon', 'Pleased to meet you', 'Thank you for inviting me'],
          avoid: ['Hey', 'What\'s up', 'Yeah', 'Nope'],
          body_language: ['Maintain eye contact', 'Firm handshake', 'Sit up straight'],
          closing: ['Thank you for your time', 'I look forward to hearing from you'],
        },
      },
      casual_conversation: {
        informal: {
          greetings: ['Hey!', 'How\'s it going?', 'What\'s up?'],
          phrases: ['That\'s cool', 'No worries', 'Sounds good'],
          avoid: ['To whom it may concern', 'I hereby...', 'Notwithstanding'],
        },
      },
      email_professional: {
        formal: {
          opening: ['Dear [Name]', 'I hope this email finds you well'],
          body: ['I am writing to...', 'I would like to...', 'Please find attached...'],
          closing: ['Best regards', 'Sincerely', 'Kind regards'],
          avoid: ['Hey!', 'LOL', 'ASAP (spell it out)', 'Emoji'],
        },
      },
      presentation: {
        formal: {
          opening: ['Good morning everyone', 'Thank you for being here', 'Today I\'ll be discussing...'],
          transitions: ['Moving on to...', 'This leads us to...', 'Let\'s now consider...'],
          engaging: ['As you can see...', 'Consider this example...', 'This is particularly important because...'],
          closing: ['To summarize...', 'In conclusion...', 'Thank you for your attention'],
        },
      },
    };

    const situationData = suggestions[situation];

    if (!situationData) {
      return {
        error: 'Situation not found',
        available: Object.keys(suggestions),
      };
    }

    const formalityLevel = situationData[formality] || situationData.formal || situationData.informal;

    return {
      situation,
      formality,
      suggestions: formalityLevel,
      tips: this.getTipsForSituation(situation),
    };
  }

  /**
   * Get tips for situation
   */
  getTipsForSituation(situation) {
    const tips = {
      job_interview: [
        'Speak clearly and at a moderate pace',
        'Use complete sentences',
        'Avoid slang and overly casual language',
        'Show enthusiasm through your tone',
      ],
      casual_conversation: [
        'Be natural and relaxed',
        'It\'s okay to use contractions (I\'m, you\'re)',
        'Ask follow-up questions',
        'Show interest in what others say',
      ],
      email_professional: [
        'Keep it concise',
        'Proofread before sending',
        'Use proper punctuation',
        'Maintain professional tone throughout',
      ],
      presentation: [
        'Practice beforehand',
        'Use visual aids',
        'Engage your audience with questions',
        'Speak to the audience, not the slides',
      ],
    };

    return tips[situation] || [];
  }

  /**
   * Generate quick reference card
   */
  generateQuickReferenceCard(topic) {
    const cards = {
      phone_calls: {
        title: 'Phone Calls Quick Reference',
        sections: [
          {
            heading: 'Answering',
            phrases: [
              'Hello, this is [name] speaking',
              '[Company name], how can I help you?',
            ],
          },
          {
            heading: 'Asking for someone',
            phrases: [
              'May I speak with [name]?',
              'Is [name] available?',
              'Could you transfer me to [name]?',
            ],
          },
          {
            heading: 'Taking a message',
            phrases: [
              'Can I take a message?',
              'Would you like to leave a message?',
              'I\'ll let them know you called',
            ],
          },
          {
            heading: 'Clarifying',
            phrases: [
              'Could you repeat that, please?',
              'I\'m sorry, could you speak more slowly?',
              'Let me make sure I have this correct...',
            ],
          },
        ],
      },
      meetings: {
        title: 'Meetings Quick Reference',
        sections: [
          {
            heading: 'Starting',
            phrases: [
              'Let\'s get started',
              'Thanks everyone for joining',
              'Let\'s go over the agenda',
            ],
          },
          {
            heading: 'Contributing',
            phrases: [
              'I\'d like to add that...',
              'From my perspective...',
              'Building on that point...',
            ],
          },
          {
            heading: 'Disagreeing politely',
            phrases: [
              'I see it differently...',
              'Have we considered...?',
              'Another perspective might be...',
            ],
          },
        ],
      },
    };

    return cards[topic] || {
      error: 'Topic not found',
      available: Object.keys(cards),
    };
  }

  /**
   * Real-world scenario practice generator
   */
  generateScenarioPractice(category, difficulty = 'intermediate') {
    const scenarios = {
      restaurant: {
        beginner: {
          scenario: 'You want to order a vegetarian meal but don\'t see options on the menu.',
          yourGoal: 'Ask if they have vegetarian options',
          usefulPhrases: [
            'Do you have any vegetarian dishes?',
            'I don\'t eat meat. What would you recommend?',
          ],
        },
        intermediate: {
          scenario: 'Your food arrived cold and you want it reheated.',
          yourGoal: 'Politely ask them to reheat your food',
          usefulPhrases: [
            'Excuse me, my food is a bit cold. Could you warm it up?',
            'I\'m sorry, but would it be possible to reheat this?',
          ],
        },
        advanced: {
          scenario: 'You were charged for items you didn\'t order. Resolve this diplomatically.',
          yourGoal: 'Explain the error and get the bill corrected',
          usefulPhrases: [
            'I think there might be a mistake on the bill',
            'We didn\'t order these items. Could we review the charges?',
          ],
        },
      },
      workplace: {
        beginner: {
          scenario: 'You need to tell your manager you\'ll be late tomorrow.',
          yourGoal: 'Inform them professionally',
          usefulPhrases: [
            'I wanted to let you know I\'ll be about 30 minutes late tomorrow',
            'I have an appointment tomorrow morning. I\'ll be in by 10 AM',
          ],
        },
        intermediate: {
          scenario: 'A colleague keeps interrupting you in meetings.',
          yourGoal: 'Address this professionally',
          usefulPhrases: [
            'If I could just finish my point...',
            'I appreciate your input. Let me complete this thought first.',
          ],
        },
        advanced: {
          scenario: 'You need to give constructive criticism to a team member.',
          yourGoal: 'Provide feedback diplomatically',
          usefulPhrases: [
            'I\'ve noticed... and I wanted to discuss how we can improve this',
            'You\'re doing well with X. Let\'s work on strengthening Y',
          ],
        },
      },
    };

    const categoryScenarios = scenarios[category];
    if (!categoryScenarios) {
      return { error: 'Category not found', available: Object.keys(scenarios) };
    }

    const scenarioData = categoryScenarios[difficulty];
    return {
      category,
      difficulty,
      ...scenarioData,
      evaluation: {
        checkpoints: [
          'Did you use appropriate formality?',
          'Were you clear and direct?',
          'Did you remain polite?',
          'Did you achieve your goal?',
        ],
      },
    };
  }
}

export default new PracticalToolsService();
