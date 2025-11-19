/**
 * Active Listening & Shadowing Service
 * Manages pronunciation practice, speech comparison, pacing training, and accent reduction
 */

class ActiveListeningService {
  constructor() {
    this.difficultSounds = this.initializeDifficultSounds();
    this.speechPatterns = this.initializeSpeechPatterns();
  }

  /**
   * Initialize difficult sounds by language background
   */
  initializeDifficultSounds() {
    return {
      general: [
        { sound: 'th', words: ['think', 'this', 'thread', 'mother', 'weather'], type: 'consonant' },
        { sound: 'r/l', words: ['right', 'light', 'road', 'load', 'rice', 'lice'], type: 'consonant' },
        { sound: 'v/w', words: ['vest', 'west', 'vine', 'wine', 'vote', 'woke'], type: 'consonant' },
        { sound: 'p/b', words: ['pat', 'bat', 'pig', 'big', 'peace', 'beast'], type: 'consonant' },
        { sound: 'æ/ɛ', words: ['bad', 'bed', 'cat', 'get', 'pan', 'pen'], type: 'vowel' },
        { sound: 'i/ɪ', words: ['sheep', 'ship', 'beat', 'bit', 'seat', 'sit'], type: 'vowel' },
      ],
      spanish: [
        { sound: 'h', words: ['hat', 'house', 'hello', 'happy'], type: 'consonant' },
        { sound: 'sh/ch', words: ['ship', 'chip', 'shop', 'chop'], type: 'consonant' },
      ],
      chinese: [
        { sound: 'r/l', words: ['right', 'light', 'road', 'load'], type: 'consonant' },
        { sound: 'th', words: ['think', 'sink', 'thick', 'sick'], type: 'consonant' },
      ],
      japanese: [
        { sound: 'r/l', words: ['right', 'light', 'rally', 'lally'], type: 'consonant' },
        { sound: 'f/h', words: ['fan', 'hand', 'fast', 'haste'], type: 'consonant' },
      ],
    };
  }

  /**
   * Initialize speech patterns for pacing training
   */
  initializeSpeechPatterns() {
    return {
      thought_groups: [
        {
          sentence: "I went to the store / to buy some milk / and bread.",
          groups: ["I went to the store", "to buy some milk", "and bread"],
          pauses: [1, 1, 0],
        },
        {
          sentence: "When I was younger / I used to play soccer / every weekend.",
          groups: ["When I was younger", "I used to play soccer", "every weekend"],
          pauses: [1, 1, 0],
        },
      ],
      stress_patterns: [
        {
          sentence: "I DIDN'T say he STOLE the money.",
          emphasis: [1, 4],
          meaning: "Someone else said it",
        },
        {
          sentence: "I didn't SAY he stole the money.",
          emphasis: [2],
          meaning: "I implied it",
        },
        {
          sentence: "I didn't say HE stole the money.",
          emphasis: [3],
          meaning: "Someone else stole it",
        },
      ],
      linking: [
        {
          phrase: "an apple",
          linked: "a-napple",
          rule: "Consonant to vowel linking",
        },
        {
          phrase: "go out",
          linked: "go-wout",
          rule: "W linking with 'o' sound",
        },
        {
          phrase: "see it",
          linked: "see-yit",
          rule: "Y linking with 'ee' sound",
        },
      ],
    };
  }

  /**
   * Generate shadowing exercise
   */
  generateShadowingExercise(difficulty = 'intermediate', duration = 30) {
    const exercises = {
      beginner: [
        {
          text: "Hello, how are you today? I'm doing very well, thank you.",
          duration: 10,
          focus: 'Clear pronunciation and natural rhythm',
          speaker: 'Native speaker - slow pace',
        },
        {
          text: "I like to read books in my free time. It helps me relax and learn new things.",
          duration: 15,
          focus: 'Sentence rhythm and word stress',
          speaker: 'Native speaker - slow pace',
        },
      ],
      intermediate: [
        {
          text: "Although I've been studying English for several years, I still find it challenging to speak fluently in conversations.",
          duration: 20,
          focus: 'Complex sentence structure and natural pauses',
          speaker: 'Native speaker - normal pace',
        },
        {
          text: "The key to improving your English is consistent practice and exposure to native content like podcasts and movies.",
          duration: 20,
          focus: 'Thought groups and natural linking',
          speaker: 'Native speaker - normal pace',
        },
      ],
      advanced: [
        {
          text: "Nevertheless, the implications of this research extend far beyond the immediate application, potentially revolutionizing the way we approach the problem.",
          duration: 30,
          focus: 'Academic vocabulary and formal register',
          speaker: 'Native speaker - natural pace',
        },
        {
          text: "What's particularly fascinating about this phenomenon is not merely its frequency, but rather the nuanced ways in which it manifests across different contexts.",
          duration: 30,
          focus: 'Complex structures and natural intonation',
          speaker: 'Native speaker - natural pace',
        },
      ],
    };

    const levelExercises = exercises[difficulty] || exercises.intermediate;
    const exercise = levelExercises[Math.floor(Math.random() * levelExercises.length)];

    return {
      id: Date.now(),
      ...exercise,
      difficulty,
      instructions: [
        "1. Listen to the audio carefully",
        "2. Pause and immediately repeat",
        "3. Record yourself saying it",
        "4. Compare your version with the original",
        "5. Focus on intonation, rhythm, and stress patterns",
      ],
      evaluationCriteria: [
        'Pronunciation clarity',
        'Natural rhythm and pacing',
        'Word stress accuracy',
        'Intonation patterns',
        'Sound linking',
      ],
    };
  }

  /**
   * Analyze speech comparison (simulated - would use actual audio analysis in production)
   */
  analyzeSpeechComparison(userTranscript, targetTranscript, audioDuration) {
    const analysis = {
      overallScore: 0,
      pace: { score: 0, feedback: '', ideal: 0, actual: 0 },
      clarity: { score: 0, feedback: '', issues: [] },
      rhythm: { score: 0, feedback: '', patterns: [] },
      pronunciation: { score: 0, feedback: '', problems: [] },
      recommendations: [],
    };

    // Pace analysis
    const targetWordsPerMinute = (targetTranscript.split(' ').length / audioDuration) * 60;
    const userWordsPerMinute = (userTranscript.split(' ').length / audioDuration) * 60;
    const paceDifference = Math.abs(targetWordsPerMinute - userWordsPerMinute);

    analysis.pace.ideal = Math.round(targetWordsPerMinute);
    analysis.pace.actual = Math.round(userWordsPerMinute);

    if (paceDifference < 20) {
      analysis.pace.score = 90;
      analysis.pace.feedback = 'Excellent pacing! Very close to native speed.';
    } else if (paceDifference < 40) {
      analysis.pace.score = 70;
      if (userWordsPerMinute < targetWordsPerMinute) {
        analysis.pace.feedback = 'Speaking a bit slowly. Try to match the natural pace.';
        analysis.recommendations.push('Practice speaking slightly faster while maintaining clarity');
      } else {
        analysis.pace.feedback = 'Speaking a bit fast. Slow down for better clarity.';
        analysis.recommendations.push('Focus on clear pronunciation even if it means slowing down');
      }
    } else {
      analysis.pace.score = 50;
      analysis.pace.feedback = 'Significant pace difference. Practice matching the speed.';
      analysis.recommendations.push('Use a metronome or count syllables to match the rhythm');
    }

    // Word-level analysis
    const targetWords = targetTranscript.toLowerCase().split(' ');
    const userWords = userTranscript.toLowerCase().split(' ');

    let matchingWords = 0;
    for (let i = 0; i < Math.min(targetWords.length, userWords.length); i++) {
      if (targetWords[i] === userWords[i]) {
        matchingWords++;
      } else {
        analysis.pronunciation.problems.push({
          expected: targetWords[i],
          said: userWords[i] || '[missing]',
          position: i,
        });
      }
    }

    analysis.clarity.score = Math.round((matchingWords / targetWords.length) * 100);

    if (analysis.clarity.score >= 90) {
      analysis.clarity.feedback = 'Excellent clarity! Words are very clear.';
    } else if (analysis.clarity.score >= 70) {
      analysis.clarity.feedback = 'Good clarity, but some words need work.';
      analysis.recommendations.push('Practice difficult words individually before full sentences');
    } else {
      analysis.clarity.feedback = 'Work on pronunciation clarity for individual words.';
      analysis.recommendations.push('Start with slower pace to ensure each word is clear');
    }

    // Overall score
    analysis.overallScore = Math.round((analysis.pace.score + analysis.clarity.score) / 2);
    analysis.rhythm.score = Math.max(50, analysis.overallScore - 10);
    analysis.pronunciation.score = analysis.clarity.score;

    return analysis;
  }

  /**
   * Generate pronunciation drill
   */
  generatePronunciationDrill(targetSounds = [], difficulty = 'intermediate') {
    const sounds = targetSounds.length > 0
      ? this.difficultSounds.general.filter(s => targetSounds.includes(s.sound))
      : this.difficultSounds.general.slice(0, 3);

    return {
      id: Date.now(),
      title: 'Pronunciation Drill',
      difficulty,
      sounds: sounds.map(sound => ({
        sound: sound.sound,
        type: sound.type,
        minimalPairs: sound.words,
        practice: {
          isolation: `Say the ${sound.sound} sound by itself`,
          words: `Practice these words: ${sound.words.join(', ')}`,
          sentences: this.generateSentencesForSound(sound.sound, sound.words),
        },
        tips: this.getTipsForSound(sound.sound),
      })),
      duration: 5,
      instructions: [
        'Listen to the target sound',
        'Practice the sound in isolation',
        'Say words with the sound',
        'Use the sound in sentences',
        'Record yourself and compare',
      ],
    };
  }

  /**
   * Generate sentences for specific sounds
   */
  generateSentencesForSound(sound, words) {
    const sentences = {
      'th': [
        "I think this is the best thing ever.",
        "My mother and father are together.",
        "The weather is getting better every day.",
      ],
      'r/l': [
        "The light is on the right side.",
        "I need to read and lead the team.",
        "Rice and lice are very different things.",
      ],
      'v/w': [
        "We value the vest more than the west.",
        "The vine and wine are both very good.",
        "Vote for what you want.",
      ],
    };

    return sentences[sound] || words.map(w => `This is a ${w}.`);
  }

  /**
   * Get pronunciation tips for specific sounds
   */
  getTipsForSound(sound) {
    const tips = {
      'th': [
        'Put your tongue between your teeth',
        'Breathe out gently',
        'Don\'t use \'s\' or \'t\' sounds',
      ],
      'r/l': [
        'For R: Curl your tongue slightly back',
        'For L: Touch tongue to roof of mouth',
        'Practice switching between them',
      ],
      'v/w': [
        'For V: Touch bottom lip with top teeth',
        'For W: Round your lips',
        'V is voiced, W is not',
      ],
    };

    return tips[sound] || ['Listen carefully', 'Repeat slowly', 'Record and compare'];
  }

  /**
   * Generate pacing and rhythm training
   */
  generatePacingExercise() {
    const exercises = [
      {
        type: 'timed_speaking',
        challenge: 'Describe your morning routine in exactly 30 seconds',
        timeLimit: 30,
        wordTarget: '50-70 words',
        tips: [
          'Speak naturally, not too fast or slow',
          'Use complete sentences',
          'Practice maintaining steady pace',
        ],
      },
      {
        type: 'thought_groups',
        sentence: this.speechPatterns.thought_groups[0],
        instructions: 'Pause at the / marks. Don\'t pause elsewhere.',
        tips: [
          'Pauses help listeners understand',
          'Don\'t pause in the middle of phrases',
          'Breathe at natural breaks',
        ],
      },
      {
        type: 'stress_patterns',
        examples: this.speechPatterns.stress_patterns,
        instructions: 'Emphasize the CAPITALIZED words. Notice how meaning changes.',
        tips: [
          'Stress changes meaning',
          'Content words get stress (nouns, verbs)',
          'Function words are unstressed (the, a, to)',
        ],
      },
      {
        type: 'linking',
        examples: this.speechPatterns.linking,
        instructions: 'Practice linking sounds between words naturally.',
        tips: [
          'Native speakers link words together',
          'Don\'t pause between every word',
          'Sounds flow into each other',
        ],
      },
    ];

    return exercises[Math.floor(Math.random() * exercises.length)];
  }

  /**
   * Generate accent reduction exercise
   */
  generateAccentReductionExercise(nativeLanguage = 'general') {
    const targetSounds = this.difficultSounds[nativeLanguage] || this.difficultSounds.general;

    return {
      id: Date.now(),
      title: 'Accent Reduction Practice',
      nativeLanguage,
      targetSounds: targetSounds.slice(0, 2),
      exercises: [
        {
          type: 'minimal_pairs',
          description: 'Practice words that sound similar but different',
          pairs: targetSounds[0].words,
        },
        {
          type: 'sentence_practice',
          description: 'Use target sounds in full sentences',
          sentences: this.generateSentencesForSound(targetSounds[0].sound, targetSounds[0].words),
        },
        {
          type: 'listening_discrimination',
          description: 'Identify which word you hear',
          tests: this.generateListeningTests(targetSounds[0].words),
        },
      ],
      tips: [
        'Focus on mouth and tongue position',
        'Practice slowly at first',
        'Record yourself daily to track improvement',
        'Don\'t aim for perfect accent - aim for clarity',
      ],
      duration: 10,
    };
  }

  /**
   * Generate listening discrimination tests
   */
  generateListeningTests(words) {
    const tests = [];
    for (let i = 0; i < Math.min(5, words.length - 1); i += 2) {
      tests.push({
        question: `Which word do you hear?`,
        options: [words[i], words[i + 1]],
        correct: Math.random() > 0.5 ? 0 : 1,
      });
    }
    return tests;
  }

  /**
   * Save shadowing practice result
   */
  saveShadowingResult(exerciseId, userRecording, analysis, score) {
    const results = this.getShadowingResults();

    results.unshift({
      id: Date.now(),
      exerciseId,
      userRecording: userRecording || null, // Would store audio blob in production
      analysis,
      score,
      completedAt: new Date().toISOString(),
    });

    localStorage.setItem('shadowing_results', JSON.stringify(results.slice(0, 50)));
  }

  /**
   * Get shadowing results
   */
  getShadowingResults() {
    const stored = localStorage.getItem('shadowing_results');
    return stored ? JSON.parse(stored) : [];
  }

  /**
   * Get pronunciation progress
   */
  getPronunciationProgress() {
    const results = this.getShadowingResults();

    if (results.length === 0) {
      return {
        averageScore: 0,
        totalPractices: 0,
        improvement: 0,
        strongSounds: [],
        weakSounds: [],
      };
    }

    const recent = results.slice(0, 10);
    const older = results.slice(10, 20);

    const recentAvg = recent.reduce((sum, r) => sum + (r.score || 0), 0) / recent.length;
    const olderAvg = older.length > 0
      ? older.reduce((sum, r) => sum + (r.score || 0), 0) / older.length
      : recentAvg;

    return {
      averageScore: Math.round(recentAvg),
      totalPractices: results.length,
      improvement: Math.round(recentAvg - olderAvg),
      recentScores: recent.map(r => r.score),
      trend: recentAvg > olderAvg ? 'improving' : recentAvg < olderAvg ? 'declining' : 'stable',
    };
  }
}

export default new ActiveListeningService();
