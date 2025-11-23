/**
 * Immersion Simulation Service
 * Daily life scenarios, multi-turn conversations, stress testing, think-in-English exercises
 */

class ImmersionSimulationService {
  constructor() {
    this.dailyLifeScenarios = this.initializeDailyLifeScenarios();
    this.environmentTypes = this.initializeEnvironmentTypes();
    this.stressScenarios = this.initializeStressScenarios();
  }

  /**
   * Initialize daily life scenarios
   */
  initializeDailyLifeScenarios() {
    return {
      morning_routine: {
        name: 'Morning Routine',
        difficulty: 'beginner',
        vocabulary: ['alarm clock', 'shower', 'breakfast', 'commute', 'traffic'],
        situations: [
          {
            trigger: 'Your alarm doesn\'t go off',
            response_options: [
              'Call work to let them know you\'ll be late',
              'Rush to get ready',
              'Check alternative transportation',
            ],
          },
          {
            trigger: 'The coffee shop is out of your usual order',
            response_options: [
              'Ask for recommendations',
              'Try something new',
              'Go to a different shop',
            ],
          },
        ],
      },
      grocery_shopping: {
        name: 'Grocery Shopping',
        difficulty: 'beginner',
        vocabulary: ['aisle', 'checkout', 'receipt', 'produce', 'cart', 'dairy'],
        situations: [
          {
            trigger: 'You can\'t find an item',
            dialogue: [
              { speaker: 'you', text: 'Excuse me, could you help me find [item]?' },
              { speaker: 'staff', text: 'Sure! It\'s in aisle 5, near the bread.' },
              { speaker: 'you', text: 'Thank you so much!' },
            ],
          },
          {
            trigger: 'The cashier asks if you have a loyalty card',
            dialogue: [
              { speaker: 'cashier', text: 'Do you have a rewards card?' },
              { speaker: 'you', options: ['Yes, here it is', 'No, but can I sign up?', 'No, thank you'] },
            ],
          },
        ],
      },
      doctor_appointment: {
        name: 'Doctor\'s Appointment',
        difficulty: 'intermediate',
        vocabulary: ['symptoms', 'prescription', 'insurance', 'appointment', 'medical history'],
        situations: [
          {
            trigger: 'Describing symptoms to the doctor',
            dialogue: [
              { speaker: 'doctor', text: 'What brings you in today?' },
              { speaker: 'you', text: 'I\'ve been having [symptom] for [duration]' },
              { speaker: 'doctor', text: 'I see. Any other symptoms?' },
              { speaker: 'you', text: '[Describe additional symptoms]' },
            ],
          },
          {
            trigger: 'Understanding prescription instructions',
            dialogue: [
              { speaker: 'doctor', text: 'Take this medication twice a day with food.' },
              { speaker: 'you', text: 'Should I take it at specific times?' },
              { speaker: 'doctor', text: 'Morning and evening, about 12 hours apart.' },
            ],
          },
        ],
      },
      job_first_day: {
        name: 'First Day at New Job',
        difficulty: 'intermediate',
        vocabulary: ['onboarding', 'colleagues', 'supervisor', 'orientation', 'workspace'],
        situations: [
          {
            trigger: 'Meeting new colleagues',
            dialogue: [
              { speaker: 'colleague', text: 'Hi! You must be the new [position]. Welcome!' },
              { speaker: 'you', text: 'Yes, I\'m [name]. Nice to meet you!' },
              { speaker: 'colleague', text: 'Let me show you around. Have you done the orientation yet?' },
              { speaker: 'you', text: 'Not yet. I\'m starting that this afternoon.' },
            ],
          },
          {
            trigger: 'Setting up your workspace',
            challenges: ['Ask IT for computer access', 'Request office supplies', 'Learn building security'],
          },
        ],
      },
      moving_apartment: {
        name: 'Moving to New Apartment',
        difficulty: 'advanced',
        vocabulary: ['lease', 'deposit', 'utilities', 'landlord', 'inspection', 'amenities'],
        situations: [
          {
            trigger: 'Apartment viewing',
            dialogue: [
              { speaker: 'agent', text: 'This unit has been recently renovated. Would you like to see it?' },
              { speaker: 'you', text: 'Yes, please. What are the monthly costs?' },
              { speaker: 'agent', text: 'Rent is $1500, plus utilities. There\'s a one-month security deposit.' },
              { speaker: 'you', text: 'Are pets allowed? And what about parking?' },
            ],
          },
          {
            trigger: 'Signing lease',
            challenges: [
              'Understand lease terms',
              'Negotiate move-in date',
              'Ask about maintenance responsibilities',
              'Clarify notice period for ending lease',
            ],
          },
        ],
      },
      emergency_situations: {
        name: 'Emergency Situations',
        difficulty: 'advanced',
        vocabulary: ['emergency', 'urgent', 'help', 'police', 'ambulance', 'fire'],
        situations: [
          {
            trigger: 'Calling emergency services',
            dialogue: [
              { speaker: 'operator', text: '911, what\'s your emergency?' },
              { speaker: 'you', text: '[Clearly state emergency]' },
              { speaker: 'operator', text: 'What is your location?' },
              { speaker: 'you', text: '[Provide exact address]' },
              { speaker: 'operator', text: 'Help is on the way. Stay on the line.' },
            ],
          },
          {
            trigger: 'Car breakdown',
            challenges: [
              'Call roadside assistance',
              'Explain the problem',
              'Provide location',
              'Estimate arrival time',
            ],
          },
        ],
      },
    };
  }

  /**
   * Initialize environment types
   */
  initializeEnvironmentTypes() {
    return {
      airport: {
        name: 'Airport',
        key_areas: ['check-in', 'security', 'gate', 'customs', 'baggage_claim'],
        common_interactions: [
          {
            area: 'check-in',
            dialogues: [
              { staff: 'Passport and ticket, please', you: '[Hand over documents]' },
              { staff: 'Any bags to check?', you: 'Yes, just this one' },
              { staff: 'Window or aisle?', you: 'Aisle, please' },
            ],
          },
          {
            area: 'security',
            instructions: [
              'Remove laptops and liquids',
              'Take off shoes and belt',
              'Place items in bins',
              'Walk through metal detector',
            ],
          },
          {
            area: 'gate',
            scenarios: [
              'Flight delayed - ask for information',
              'Boarding announcement - listen for your zone',
              'Overhead bin full - ask for help',
            ],
          },
        ],
        emergency_phrases: [
          'Excuse me, I think I missed my flight',
          'My luggage didn\'t arrive',
          'I need to change my ticket',
        ],
      },
      hotel: {
        name: 'Hotel',
        key_areas: ['reception', 'room', 'restaurant', 'concierge'],
        common_interactions: [
          {
            area: 'check-in',
            dialogue: [
              { staff: 'Welcome to [Hotel]. Do you have a reservation?', you: 'Yes, under the name [name]' },
              { staff: 'Can I see your ID and credit card?', you: '[Provide documents]' },
              { staff: 'You\'re in room 305. Breakfast is from 7-10 AM', you: 'Thank you. Where are the elevators?' },
            ],
          },
          {
            area: 'room_service',
            dialogue: [
              { you: 'Hello, I\'d like to order room service', staff: 'Certainly. What would you like?' },
              { you: '[Order items]', staff: 'That will be about 30 minutes. Room number?' },
              { you: '305', staff: 'Perfect. We\'ll bring that right up.' },
            ],
          },
        ],
        problem_solving: [
          'Room is too cold/hot',
          'Wifi not working',
          'Noisy neighbors',
          'Missing amenities',
        ],
      },
      office: {
        name: 'Office Environment',
        key_areas: ['meeting_room', 'break_room', 'workspace', 'reception'],
        common_interactions: [
          {
            situation: 'Coffee break conversation',
            dialogue: [
              { colleague: 'How\'s your day going?', you: 'Busy! Working on the quarterly report' },
              { colleague: 'Oh, when\'s that due?', you: 'End of the week. How about you?' },
              { colleague: 'Same. Want to grab lunch later?', you: 'Sure! Around noon?' },
            ],
          },
          {
            situation: 'Printer trouble',
            dialogue: [
              { you: 'Excuse me, the printer isn\'t working', colleague: 'Did you check if it has paper?' },
              { you: 'Yes, it seems to be jammed', colleague: 'Let me help you with that' },
            ],
          },
        ],
      },
      restaurant_full: {
        name: 'Full Restaurant Experience',
        stages: ['arrival', 'ordering', 'during_meal', 'payment'],
        interactions: [
          {
            stage: 'arrival',
            dialogue: [
              { host: 'Good evening! Do you have a reservation?', you: 'Yes, for two under [name]' },
              { host: 'Right this way. Your server will be with you shortly', you: 'Thank you' },
            ],
          },
          {
            stage: 'ordering',
            dialogue: [
              { server: 'Can I start you off with drinks?', you: 'I\'ll have a water with lemon, please' },
              { server: 'Are you ready to order, or do you need more time?', you: 'I have a question about the salmon...' },
              { server: 'It\'s grilled with herbs and comes with vegetables', you: 'Perfect, I\'ll have that' },
            ],
          },
          {
            stage: 'during_meal',
            scenarios: [
              { issue: 'Food is cold', response: 'Excuse me, could you warm this up?' },
              { issue: 'Wrong order', response: 'I\'m sorry, I ordered the chicken, not the fish' },
              { issue: 'Need condiments', response: 'Could I get some salt and pepper?' },
            ],
          },
          {
            stage: 'payment',
            dialogue: [
              { server: 'How was everything?', you: 'Delicious, thank you!' },
              { server: 'Can I get you anything else?', you: 'Just the check, please' },
              { server: 'Together or separate?', you: 'Together is fine' },
            ],
          },
        ],
      },
    };
  }

  /**
   * Initialize stress test scenarios
   */
  initializeStressScenarios() {
    return [
      {
        name: 'Rapid Fire Questions',
        description: 'Answer questions quickly without preparation time',
        difficulty: 'intermediate',
        questions: [
          'What did you do last weekend?',
          'What\'s your favorite food?',
          'If you could travel anywhere, where would you go?',
          'What was the last book you read?',
          'Describe your perfect day',
        ],
        timeLimit: 15, // seconds per question
        evaluation: ['Speed', 'Coherence', 'Completeness'],
      },
      {
        name: 'Unexpected Problem',
        description: 'Handle unexpected situations and find solutions',
        difficulty: 'advanced',
        scenarios: [
          {
            situation: 'Your presentation file won\'t open before an important meeting',
            tasks: [
              'Explain the problem to your manager',
              'Propose alternatives',
              'Stay calm and professional',
            ],
          },
          {
            situation: 'A customer is angry about a product issue',
            tasks: [
              'Listen to their complaint',
              'Apologize appropriately',
              'Offer a solution',
              'Follow up',
            ],
          },
        ],
      },
      {
        name: 'Multi-tasking Conversation',
        description: 'Handle multiple conversation threads simultaneously',
        difficulty: 'advanced',
        scenario: 'You\'re at a networking event talking to someone when another person joins',
        tasks: [
          'Introduce the two people',
          'Continue previous conversation',
          'Engage new person',
          'Balance attention',
        ],
      },
      {
        name: 'Accent Challenge',
        description: 'Understand different English accents',
        difficulty: 'advanced',
        accents: ['British', 'Australian', 'American South', 'Indian', 'Scottish'],
        task: 'Listen and comprehend various accents in quick succession',
      },
    ];
  }

  /**
   * Generate daily life scenario
   */
  generateDailyLifeScenario(scenarioType = null, difficulty = 'intermediate') {
    let scenarios = Object.entries(this.dailyLifeScenarios);

    if (difficulty) {
      scenarios = scenarios.filter(([_, data]) => data.difficulty === difficulty);
    }

    if (scenarioType && this.dailyLifeScenarios[scenarioType]) {
      scenarios = [[scenarioType, this.dailyLifeScenarios[scenarioType]]];
    }

    if (scenarios.length === 0) {
      scenarios = Object.entries(this.dailyLifeScenarios);
    }

    const [type, data] = scenarios[Math.floor(Math.random() * scenarios.length)];

    return {
      id: Date.now(),
      type,
      name: data.name,
      difficulty: data.difficulty,
      vocabulary: data.vocabulary,
      situation: data.situations[Math.floor(Math.random() * data.situations.length)],
      tips: this.getTipsForScenario(type),
      success_criteria: [
        'Clear communication',
        'Appropriate vocabulary usage',
        'Natural flow',
        'Problem resolution',
      ],
    };
  }

  /**
   * Generate multi-turn conversation
   */
  generateMultiTurnConversation(environment, complexity = 'medium') {
    const env = this.environmentTypes[environment];

    if (!env) {
      return {
        error: 'Environment not found',
        available: Object.keys(this.environmentTypes),
      };
    }

    const turns = complexity === 'simple' ? 3 : complexity === 'medium' ? 5 : 8;

    return {
      id: Date.now(),
      environment: env.name,
      turns: turns,
      interactions: env.common_interactions || [],
      challenges: this.generateChallenges(environment, complexity),
      vocabulary: this.getEnvironmentVocabulary(environment),
      completion_criteria: {
        turnsCompleted: turns,
        objectivesAchieved: true,
        naturalLanguageUsed: true,
      },
    };
  }

  /**
   * Generate challenges for environment
   */
  generateChallenges(environment, complexity) {
    const challenges = {
      airport: {
        simple: ['Check in for your flight', 'Find your gate'],
        medium: ['Check in', 'Handle delayed flight', 'Ask about luggage'],
        complex: ['Check in late', 'Handle cancellation', 'Rebook flight', 'File complaint'],
      },
      hotel: {
        simple: ['Check in', 'Ask about breakfast'],
        medium: ['Check in', 'Request room change', 'Use concierge service'],
        complex: ['Late check-in', 'Room problem', 'Special request', 'Early checkout'],
      },
      office: {
        simple: ['Greet colleagues', 'Find meeting room'],
        medium: ['Schedule meeting', 'Present idea', 'Handle disagreement'],
        complex: ['Lead meeting', 'Resolve conflict', 'Negotiate deadline', 'Give feedback'],
      },
    };

    return challenges[environment]?.[complexity] || [];
  }

  /**
   * Get environment vocabulary
   */
  getEnvironmentVocabulary(environment) {
    const vocab = {
      airport: ['boarding pass', 'departure', 'arrival', 'gate', 'terminal', 'baggage claim', 'customs', 'security'],
      hotel: ['reservation', 'check-in', 'check-out', 'amenities', 'concierge', 'housekeeping', 'room service'],
      office: ['meeting', 'deadline', 'agenda', 'colleague', 'supervisor', 'presentation', 'conference room'],
      restaurant_full: ['reservation', 'menu', 'appetizer', 'entree', 'dessert', 'bill', 'tip', 'to-go'],
    };

    return vocab[environment] || [];
  }

  /**
   * Generate stress test exercise
   */
  generateStressTest(testType = null) {
    const tests = testType
      ? this.stressScenarios.filter(t => t.name.toLowerCase().includes(testType.toLowerCase()))
      : this.stressScenarios;

    if (tests.length === 0) {
      return {
        error: 'Test type not found',
        available: this.stressScenarios.map(t => t.name),
      };
    }

    const test = tests[Math.floor(Math.random() * tests.length)];

    return {
      id: Date.now(),
      ...test,
      instructions: this.getStressTestInstructions(test.name),
      preparation: {
        mental: 'Take a deep breath. You\'ve got this!',
        strategy: 'Focus on communicating your message, not perfection',
        reminder: 'It\'s okay to pause and think',
      },
    };
  }

  /**
   * Get stress test instructions
   */
  getStressTestInstructions(testName) {
    const instructions = {
      'Rapid Fire Questions': [
        'You will be asked 5 questions',
        'You have 15 seconds to answer each',
        'Answer as completely as possible',
        'Don\'t worry about perfection - focus on communication',
      ],
      'Unexpected Problem': [
        'Read the scenario carefully',
        'Think about how you would respond',
        'Practice speaking your response',
        'Focus on clarity and calmness',
      ],
      'Multi-tasking Conversation': [
        'Try to balance attention between both people',
        'Use transitional phrases',
        'Don\'t lose track of either conversation',
        'Practice active listening',
      ],
      'Accent Challenge': [
        'Listen carefully to each speaker',
        'Focus on content, not accent',
        'Ask for repetition if needed (in real life)',
        'Practice makes it easier over time',
      ],
    };

    return instructions[testName] || [];
  }

  /**
   * Generate think-in-English exercise
   */
  generateThinkInEnglishExercise() {
    const exercises = [
      {
        type: 'describe_surroundings',
        instruction: 'Look around you. Describe everything you see in English (in your head or out loud)',
        duration: 2,
        prompts: [
          'What colors do you see?',
          'What objects are nearby?',
          'What are people doing?',
          'What sounds do you hear?',
        ],
      },
      {
        type: 'plan_your_day',
        instruction: 'Think through your plans for today, entirely in English',
        duration: 3,
        prompts: [
          'What do you need to do today?',
          'What time will you do each thing?',
          'Who will you talk to?',
          'What might go wrong and how will you handle it?',
        ],
      },
      {
        type: 'reflect_on_conversation',
        instruction: 'Think about a recent conversation. Replay it in English in your mind',
        duration: 3,
        prompts: [
          'What did you talk about?',
          'What did you say?',
          'What did the other person say?',
          'How could you have expressed it differently?',
        ],
      },
      {
        type: 'problem_solving',
        instruction: 'Think through how to solve a problem, entirely in English',
        duration: 5,
        scenarios: [
          'You need to plan a birthday party',
          'You want to learn a new skill',
          'You need to convince someone of your idea',
          'You have to organize a trip',
        ],
      },
      {
        type: 'mental_narration',
        instruction: 'Narrate your actions in your mind as you do them, like a sports commentator',
        duration: 5,
        examples: [
          '"Now I\'m opening the fridge..."',
          '"I\'m reaching for the milk..."',
          '"I\'m pouring it into my coffee..."',
          '"Now I\'m taking a sip..."',
        ],
      },
    ];

    const exercise = exercises[Math.floor(Math.random() * exercises.length)];

    return {
      id: Date.now(),
      ...exercise,
      benefits: [
        'Reduces translation time',
        'Builds English thinking patterns',
        'Improves fluency',
        'Makes speaking more natural',
      ],
      tips: [
        'Don\'t worry if it feels slow at first',
        'Use simple words when starting',
        'Gradually increase complexity',
        'Practice daily for best results',
      ],
    };
  }

  /**
   * Get scenario tips
   */
  getTipsForScenario(scenarioType) {
    const tips = {
      morning_routine: [
        'Use time expressions naturally',
        'Practice describing routine actions',
        'Learn transport vocabulary',
      ],
      grocery_shopping: [
        'Memorize common grocery items',
        'Practice asking for help politely',
        'Learn location vocabulary (aisle, section, etc.)',
      ],
      doctor_appointment: [
        'Prepare to describe symptoms accurately',
        'Learn body part vocabulary',
        'Practice understanding medical instructions',
      ],
      job_first_day: [
        'Be professional but friendly',
        'Ask questions when unclear',
        'Take notes on important information',
      ],
      moving_apartment: [
        'Understand legal terms in lease',
        'Ask about all costs upfront',
        'Document condition of apartment',
      ],
      emergency_situations: [
        'Stay calm and speak clearly',
        'Know your address and phone number',
        'Practice emergency phrases beforehand',
      ],
    };

    return tips[scenarioType] || [];
  }

  /**
   * Track immersion progress
   */
  trackImmersionProgress(scenarioId, environment, completed, score, duration) {
    const history = this.getImmersionHistory();

    history.unshift({
      scenarioId,
      environment,
      completed,
      score,
      duration,
      completedAt: new Date().toISOString(),
    });

    localStorage.setItem('immersion_history', JSON.stringify(history.slice(0, 100)));

    return this.calculateImmersionStats(history);
  }

  /**
   * Get immersion history
   */
  getImmersionHistory() {
    const stored = localStorage.getItem('immersion_history');
    return stored ? JSON.parse(stored) : [];
  }

  /**
   * Calculate immersion statistics
   */
  calculateImmersionStats(history) {
    if (history.length === 0) {
      return {
        totalScenarios: 0,
        averageScore: 0,
        environmentsExplored: 0,
      };
    }

    const totalScore = history.reduce((sum, h) => sum + (h.score || 0), 0);
    const environments = new Set(history.map(h => h.environment));

    return {
      totalScenarios: history.length,
      averageScore: Math.round(totalScore / history.length),
      environmentsExplored: environments.size,
      mostPracticed: this.findMostPracticed(history),
      recentPerformance: this.analyzeRecentPerformance(history),
    };
  }

  /**
   * Find most practiced environment
   */
  findMostPracticed(history) {
    const counts = {};
    history.forEach(h => {
      counts[h.environment] = (counts[h.environment] || 0) + 1;
    });

    let max = 0;
    let mostPracticed = null;

    Object.entries(counts).forEach(([env, count]) => {
      if (count > max) {
        max = count;
        mostPracticed = env;
      }
    });

    return { environment: mostPracticed, count: max };
  }

  /**
   * Analyze recent performance
   */
  analyzeRecentPerformance(history) {
    const recent = history.slice(0, 5);
    if (recent.length === 0) return { trend: 'no_data' };

    const avgScore = recent.reduce((sum, h) => sum + (h.score || 0), 0) / recent.length;
    const older = history.slice(5, 10);

    if (older.length === 0) return { trend: 'insufficient_data', currentAvg: Math.round(avgScore) };

    const olderAvg = older.reduce((sum, h) => sum + (h.score || 0), 0) / older.length;

    return {
      trend: avgScore > olderAvg ? 'improving' : avgScore < olderAvg ? 'declining' : 'stable',
      currentAvg: Math.round(avgScore),
      previousAvg: Math.round(olderAvg),
      change: Math.round(avgScore - olderAvg),
    };
  }
}

export default new ImmersionSimulationService();
