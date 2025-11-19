/**
 * Speaking Confidence Builders Service
 * Filler word alternatives, conversation starters, question formation, thinking time phrases
 */

class SpeakingConfidenceService {
  constructor() {
    this.fillerAlternatives = this.initializeFillerAlternatives();
    this.conversationStarters = this.initializeConversationStarters();
    this.thinkingPhrases = this.initializeThinkingPhrases();
  }

  /**
   * Initialize filler word alternatives
   */
  initializeFillerAlternatives() {
    return {
      fillers_to_avoid: ['um', 'uh', 'like', 'you know', 'basically', 'actually', 'literally'],
      better_alternatives: {
        buying_time: [
          "Let me think about that...",
          "That's an interesting question...",
          "Good question...",
          "Hmm, let me see...",
          "If I understand correctly...",
        ],
        pausing: [
          "Well...",
          "So...",
          "Now...",
          "Actually...",
          "In fact...",
        ],
        professional: [
          "Let me consider that for a moment...",
          "That's a great point...",
          "I'd like to think about that...",
          "From my perspective...",
          "Based on my experience...",
        ],
        casual: [
          "You know what?",
          "The thing is...",
          "Here's the thing...",
          "I mean...",
          "To be honest...",
        ],
      },
      silent_pause_tips: [
        "It's okay to pause silently - it shows you're thinking",
        "Count to 2 in your head instead of saying 'um'",
        "Take a breath during the pause",
        "A short silence is better than filler words",
      ],
    };
  }

  /**
   * Initialize conversation starters by context
   */
  initializeConversationStarters() {
    return {
      networking: {
        openers: [
          "Hi, I don't think we've met. I'm [name].",
          "Hello! How are you finding the event?",
          "Interesting presentation, wasn't it?",
          "Have you been to one of these before?",
        ],
        followups: [
          "What brings you here today?",
          "What do you do?",
          "How do you know [person/organization]?",
          "Are you working on anything exciting?",
        ],
        tips: [
          "Smile and make eye contact",
          "Ask open-ended questions",
          "Show genuine interest",
          "Remember their name",
        ],
      },
      social: {
        openers: [
          "Nice weather today, isn't it?",
          "Have you been here before?",
          "I love your [item] - where did you get it?",
          "Enjoying your day so far?",
        ],
        followups: [
          "What do you like to do for fun?",
          "Have any plans for the weekend?",
          "Where are you from originally?",
          "Have you seen/read [popular topic]?",
        ],
        tips: [
          "Keep it light and positive",
          "Find common ground",
          "Be friendly and approachable",
          "Share something about yourself too",
        ],
      },
      professional: {
        openers: [
          "Thank you for taking the time to meet.",
          "I've been looking forward to this discussion.",
          "I appreciate the opportunity to speak with you.",
          "Great to finally connect in person.",
        ],
        followups: [
          "Could you tell me more about your role?",
          "What are your team's current priorities?",
          "How did you get started in this field?",
          "What's the biggest challenge you're facing?",
        ],
        tips: [
          "Be professional yet personable",
          "Do your homework beforehand",
          "Listen more than you talk",
          "Follow up on their points",
        ],
      },
      casual_meeting: {
        openers: [
          "Hey! How's it going?",
          "Long time no see! How have you been?",
          "Great to see you again!",
          "What a coincidence running into you!",
        ],
        followups: [
          "What have you been up to lately?",
          "How's work/school going?",
          "Have you done anything fun recently?",
          "Still living in [place]?",
        ],
        tips: [
          "Be enthusiastic",
          "Reference shared experiences",
          "Show you remember them",
          "Keep the energy positive",
        ],
      },
    };
  }

  /**
   * Initialize thinking time phrases
   */
  initializeThinkingPhrases() {
    return {
      professional: [
        "That's a great question. Let me consider that...",
        "I'd like to think about that for a moment...",
        "Let me gather my thoughts on that...",
        "I need a moment to formulate my response...",
        "If you don't mind, I'd like to reflect on that briefly...",
      ],
      casual: [
        "Hmm, let me think...",
        "Good question! Give me a sec...",
        "That's interesting... let me see...",
        "Oh, I haven't thought about that before...",
        "Let me think how to put this...",
      ],
      clarifying: [
        "Just to make sure I understand correctly...",
        "Could you clarify what you mean by...?",
        "Let me rephrase that to make sure...",
        "So what you're asking is...",
        "If I understand the question...",
      ],
      redirecting: [
        "That's an important point. Related to that...",
        "Before I answer that, I should mention...",
        "That reminds me of...",
        "Building on that idea...",
        "To put it another way...",
      ],
    };
  }

  /**
   * Generate filler word reduction exercise
   */
  generateFillerReductionExercise() {
    const topics = [
      "Describe your perfect weekend",
      "Explain what you do for work/study",
      "Tell me about your hometown",
      "Describe your favorite hobby",
      "What's your opinion on working from home?",
    ];

    const topic = topics[Math.floor(Math.random() * topics.length)];

    return {
      id: Date.now(),
      type: 'filler_reduction',
      topic,
      duration: 120, // 2 minutes
      instructions: [
        `Speak about: "${topic}"`,
        "Aim for 2 minutes of speaking",
        "Try to avoid filler words (um, uh, like)",
        "Use silent pauses or better alternatives instead",
        "Record yourself to count filler words",
      ],
      targetFillers: ['um', 'uh', 'like', 'you know'],
      betterAlternatives: this.fillerAlternatives.better_alternatives.buying_time,
      scoringCriteria: {
        excellent: '0-2 filler words',
        good: '3-5 filler words',
        needs_work: '6+ filler words',
      },
      tips: this.fillerAlternatives.silent_pause_tips,
    };
  }

  /**
   * Generate conversation starter practice
   */
  generateConversationStarterPractice(context = 'social') {
    const contextData = this.conversationStarters[context] || this.conversationStarters.social;

    return {
      id: Date.now(),
      type: 'conversation_starters',
      context,
      scenarios: [
        {
          situation: this.getScenarioForContext(context),
          yourOpener: contextData.openers[0],
          possibleResponses: this.generatePossibleResponses(context),
          yourFollowup: contextData.followups[0],
        },
      ],
      practice: {
        openers: contextData.openers,
        followups: contextData.followups,
        tips: contextData.tips,
      },
      exercise: {
        instruction: "Practice starting conversations in this context",
        steps: [
          "1. Choose an opener from the list",
          "2. Imagine the other person's response",
          "3. Prepare your follow-up question",
          "4. Practice the whole exchange out loud",
          "5. Try variations with different openers",
        ],
      },
    };
  }

  /**
   * Get scenario description for context
   */
  getScenarioForContext(context) {
    const scenarios = {
      networking: "You're at a professional networking event and see someone standing alone by the refreshments.",
      social: "You're waiting in line at a coffee shop and someone next to you looks friendly.",
      professional: "You're meeting a potential client or partner for the first time in their office.",
      casual_meeting: "You bump into an old acquaintance at a shopping mall.",
    };

    return scenarios[context] || scenarios.social;
  }

  /**
   * Generate possible responses
   */
  generatePossibleResponses(context) {
    const responses = {
      networking: [
        "Hi! I'm enjoying it so far. Are you with any of the companies here?",
        "Hello! It's my first time at this event. How about you?",
        "Good, thanks! The keynote speaker was excellent.",
      ],
      social: [
        "Pretty good, thanks! Just grabbing my usual coffee.",
        "Can't complain! Nice day, isn't it?",
        "Going well! I love this place - their lattes are amazing.",
      ],
      professional: [
        "Thank you for having me. I've heard great things about your company.",
        "Likewise! I'm excited to discuss the opportunity.",
        "Thank you. I've been looking forward to learning more about your needs.",
      ],
      casual_meeting: [
        "I'm doing great! Wow, it's been ages!",
        "Good! I can't believe we ran into each other!",
        "I'm well, thanks! What are you up to these days?",
      ],
    };

    return responses[context] || responses.social;
  }

  /**
   * Generate question formation drill
   */
  generateQuestionFormationDrill() {
    const topics = ['work', 'hobbies', 'travel', 'food', 'technology'];
    const topic = topics[Math.floor(Math.random() * topics.length)];

    return {
      id: Date.now(),
      type: 'question_formation',
      topic,
      challenge: `Create 10 different questions about "${topic}" in 3 minutes`,
      questionTypes: [
        { type: 'Yes/No', example: 'Do you enjoy your work?' },
        { type: 'Open-ended', example: 'What do you like most about your work?' },
        { type: 'Clarifying', example: 'Could you explain what you mean by that?' },
        { type: 'Follow-up', example: 'How did that make you feel?' },
        { type: 'Opinion', example: 'What do you think about remote work?' },
      ],
      tips: [
        "Use question words: who, what, when, where, why, how",
        "Start with auxiliary verbs for yes/no questions: do, does, did, can, will",
        "Open-ended questions get more interesting answers",
        "Follow-up questions show you're listening",
      ],
      scoring: {
        target: 10,
        timeLimit: 180,
        bonus: "Extra points for variety in question types",
      },
    };
  }

  /**
   * Generate thinking time practice
   */
  generateThinkingTimePractice(register = 'casual') {
    const phrases = this.thinkingPhrases[register] || this.thinkingPhrases.casual;

    return {
      id: Date.now(),
      type: 'thinking_time',
      register,
      scenarios: [
        {
          question: "Tell me about a difficult decision you made recently.",
          badResponse: "*long silence* Um... uh... I don't know...",
          goodResponse: `"That's a great question. Let me think about that for a moment... ${phrases[0]}`,
          explanation: "Using a thinking phrase shows you're engaged and considering your answer thoughtfully.",
        },
        {
          question: "What's your opinion on the current situation?",
          badResponse: "Like, um, well, you know, I think...",
          goodResponse: `"${phrases[1]} *brief pause* I believe that...",`,
          explanation: "A brief, confident phrase is better than multiple filler words.",
        },
      ],
      practice: {
        phrases: phrases,
        exercise: "When asked a question, practice using one of these phrases before answering",
        tips: [
          "It's okay to take a moment to think",
          "A confident pause is better than 'um'",
          "These phrases show professionalism",
          "Practice makes them feel natural",
        ],
      },
    };
  }

  /**
   * Track filler word usage over time
   */
  trackFillerUsage(exerciseId, fillerCount, duration, targetWords) {
    const tracking = this.getFillerTracking();

    tracking.unshift({
      exerciseId,
      fillerCount,
      duration,
      targetWords,
      fillerRate: (fillerCount / duration) * 60, // Fillers per minute
      completedAt: new Date().toISOString(),
    });

    localStorage.setItem('filler_tracking', JSON.stringify(tracking.slice(0, 50)));

    return this.calculateFillerProgress(tracking);
  }

  /**
   * Get filler tracking data
   */
  getFillerTracking() {
    const stored = localStorage.getItem('filler_tracking');
    return stored ? JSON.parse(stored) : [];
  }

  /**
   * Calculate filler word progress
   */
  calculateFillerProgress(tracking) {
    if (tracking.length < 2) {
      return {
        currentRate: tracking[0]?.fillerRate || 0,
        improvement: 0,
        trend: 'insufficient_data',
      };
    }

    const recent = tracking.slice(0, 5);
    const older = tracking.slice(5, 10);

    const recentRate = recent.reduce((sum, t) => sum + t.fillerRate, 0) / recent.length;
    const olderRate = older.length > 0
      ? older.reduce((sum, t) => sum + t.fillerRate, 0) / older.length
      : recentRate;

    return {
      currentRate: Math.round(recentRate * 10) / 10,
      previousRate: Math.round(olderRate * 10) / 10,
      improvement: Math.round((olderRate - recentRate) * 10) / 10,
      improvementPercent: olderRate > 0 ? Math.round(((olderRate - recentRate) / olderRate) * 100) : 0,
      trend: recentRate < olderRate ? 'improving' : recentRate > olderRate ? 'declining' : 'stable',
    };
  }

  /**
   * Get confidence-building tips
   */
  getConfidenceTips() {
    return {
      before_speaking: [
        "Take a deep breath",
        "Remember: it's okay to pause and think",
        "Focus on your message, not perfection",
        "Smile - it helps you relax and sound friendly",
      ],
      during_speaking: [
        "Speak at a comfortable pace",
        "Use hand gestures naturally",
        "Make eye contact",
        "If you make a mistake, just keep going",
      ],
      after_speaking: [
        "Reflect on what went well",
        "Don't dwell on mistakes",
        "Note one thing to improve next time",
        "Celebrate that you practiced!",
      ],
      general: [
        "Confidence comes with practice",
        "Everyone makes mistakes - native speakers too",
        "Your accent is part of who you are",
        "Clear communication matters more than perfect grammar",
      ],
    };
  }
}

export default new SpeakingConfidenceService();
