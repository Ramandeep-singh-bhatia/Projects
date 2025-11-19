/**
 * Enhanced Vocabulary Building Service
 * Word relationship maps, frequency-based learning, collocations, register awareness
 */

class EnhancedVocabularyService {
  constructor() {
    this.frequencyRanks = this.initializeFrequencyRanks();
    this.commonCollocations = this.initializeCollocations();
    this.registerLevels = ['very_informal', 'informal', 'neutral', 'formal', 'very_formal'];
  }

  /**
   * Initialize frequency rank categories
   */
  initializeFrequencyRanks() {
    return {
      essential: { min: 1, max: 1000, color: '#ef4444', label: 'Essential (Top 1000)' },
      high: { min: 1001, max: 2000, color: '#f59e0b', label: 'High Frequency (1001-2000)' },
      medium: { min: 2001, max: 3000, color: '#10b981', label: 'Medium Frequency (2001-3000)' },
      low: { min: 3001, max: 5000, color: '#3b82f6', label: 'Lower Frequency (3001-5000)' },
      rare: { min: 5001, max: Infinity, color: '#8b5cf6', label: 'Rare (5000+)' },
    };
  }

  /**
   * Initialize common collocations
   */
  initializeCollocations() {
    return {
      // Verb + Noun
      make: ['a decision', 'a mistake', 'progress', 'an effort', 'a difference', 'sense', 'money', 'a plan'],
      take: ['a break', 'a chance', 'action', 'time', 'notes', 'care', 'responsibility', 'turns'],
      do: ['homework', 'business', 'research', 'work', 'your best', 'damage', 'good', 'harm'],
      have: ['a question', 'an idea', 'experience', 'fun', 'time', 'trouble', 'difficulty'],
      get: ['started', 'better', 'worse', 'ready', 'involved', 'married', 'divorced'],
      give: ['advice', 'permission', 'a speech', 'a presentation', 'feedback', 'support'],
      pay: ['attention', 'a visit', 'respect', 'tribute', 'dividends', 'a compliment'],
      keep: ['in touch', 'track', 'quiet', 'calm', 'going', 'a secret', 'a promise'],
      catch: ['a cold', 'fire', 'attention', 'up', 'a bus', 'someone\'s eye'],
      break: ['the news', 'a record', 'the ice', 'even', 'a promise', 'the law'],

      // Adjective + Noun
      strong: ['coffee', 'wind', 'smell', 'accent', 'personality', 'evidence'],
      heavy: ['rain', 'traffic', 'workload', 'drinker', 'smoker', 'sleeper'],
      light: ['meal', 'rain', 'traffic', 'sleeper', 'reading'],
      high: ['quality', 'price', 'temperature', 'hopes', 'standards'],
      low: ['price', 'quality', 'temperature', 'voice', 'self-esteem'],

      // Adverb + Adjective
      completely: ['different', 'wrong', 'satisfied', 'exhausted', 'unacceptable'],
      highly: ['recommend', 'qualified', 'unlikely', 'effective', 'competitive'],
      deeply: ['concerned', 'moved', 'rooted', 'grateful', 'disappointed'],
      bitterly: ['disappointed', 'cold', 'opposed', 'complain'],
      vastly: ['different', 'superior', 'improved', 'underestimated'],
    };
  }

  /**
   * Build comprehensive word relationship map
   */
  buildWordRelationshipMap(word, aiService = null) {
    const map = {
      centerWord: word,
      synonyms: [],
      antonyms: [],
      related: [],
      wordFamily: [],
      collocations: [],
      register: [],
      frequencyRank: null,
      usageNotes: [],
    };

    // Get word family (morphological variations)
    map.wordFamily = this.generateWordFamily(word);

    // Get collocations
    map.collocations = this.getCollocationsForWord(word);

    // Get register variants
    map.register = this.getRegisterVariants(word);

    // Frequency rank (would come from database in production)
    map.frequencyRank = this.estimateFrequencyRank(word);

    // If AI service available, get AI-generated relationships
    if (aiService) {
      return this.enhanceMapWithAI(map, aiService);
    }

    // Otherwise, use built-in relationships
    map.synonyms = this.getBuiltInSynonyms(word);
    map.antonyms = this.getBuiltInAntonyms(word);
    map.related = this.getRelatedWords(word);

    return map;
  }

  /**
   * Generate word family (morphological variations)
   */
  generateWordFamily(word) {
    const family = [word];

    // Common suffixes for word families
    const suffixes = {
      noun: ['tion', 'ment', 'ness', 'ity', 'er', 'or', 'ist'],
      verb: ['ize', 'ify', 'ate', 'en'],
      adjective: ['able', 'ible', 'ful', 'less', 'ive', 'ous', 'al'],
      adverb: ['ly'],
    };

    // This is simplified - in production, use a morphological database
    const base = word.replace(/s$|ed$|ing$|ly$|ness$|ment$|tion$/, '');

    if (word !== base) family.push(base);

    // Add common variations
    const variations = [
      base + 'tion',
      base + 'ment',
      base + 'ness',
      base + 'ly',
      base + 'er',
      base + 'ing',
      base + 'ed',
    ];

    return [...new Set([...family, ...variations])];
  }

  /**
   * Get collocations for a word
   */
  getCollocationsForWord(word) {
    const collocations = [];

    // Check if word is in our collocation database
    if (this.commonCollocations[word.toLowerCase()]) {
      collocations.push(...this.commonCollocations[word.toLowerCase()].map(c => ({
        phrase: `${word} ${c}`,
        type: 'verb + noun',
        frequency: 'high',
      })));
    }

    // Check if word appears in other collocations
    for (const [key, values] of Object.entries(this.commonCollocations)) {
      for (const value of values) {
        if (value.toLowerCase().includes(word.toLowerCase())) {
          collocations.push({
            phrase: `${key} ${value}`,
            type: this.detectCollocationType(key, value),
            frequency: 'high',
          });
        }
      }
    }

    return collocations.slice(0, 10); // Return top 10
  }

  /**
   * Detect collocation type
   */
  detectCollocationType(word1, word2) {
    const verbs = ['make', 'take', 'do', 'have', 'get', 'give', 'pay', 'keep', 'catch', 'break'];
    const adjectives = ['strong', 'heavy', 'light', 'high', 'low'];
    const adverbs = ['completely', 'highly', 'deeply', 'bitterly', 'vastly'];

    if (verbs.includes(word1.toLowerCase())) return 'verb + noun';
    if (adjectives.includes(word1.toLowerCase())) return 'adjective + noun';
    if (adverbs.includes(word1.toLowerCase())) return 'adverb + adjective';

    return 'collocation';
  }

  /**
   * Get register variants for a word
   */
  getRegisterVariants(word) {
    const registerMap = {
      // Kids → Children → Youngsters
      kids: [
        { word: 'kids', level: 'very_informal', context: 'Casual speech' },
        { word: 'children', level: 'neutral', context: 'General use' },
        { word: 'youngsters', level: 'formal', context: 'Formal writing' },
        { word: 'juveniles', level: 'very_formal', context: 'Legal/academic' },
      ],
      // Buy → Purchase → Acquire
      buy: [
        { word: 'get', level: 'very_informal', context: 'Casual speech' },
        { word: 'buy', level: 'neutral', context: 'General use' },
        { word: 'purchase', level: 'formal', context: 'Business/formal' },
        { word: 'acquire', level: 'very_formal', context: 'Academic/legal' },
      ],
      // Home → Residence → Dwelling
      home: [
        { word: 'place', level: 'very_informal', context: 'Casual speech' },
        { word: 'home', level: 'neutral', context: 'General use' },
        { word: 'residence', level: 'formal', context: 'Formal/business' },
        { word: 'dwelling', level: 'very_formal', context: 'Legal/technical' },
      ],
      // Start → Begin → Commence
      start: [
        { word: 'start', level: 'neutral', context: 'General use' },
        { word: 'begin', level: 'formal', context: 'Formal speech/writing' },
        { word: 'commence', level: 'very_formal', context: 'Very formal/legal' },
        { word: 'initiate', level: 'very_formal', context: 'Technical/academic' },
      ],
      // Talk → Discuss → Converse
      talk: [
        { word: 'chat', level: 'very_informal', context: 'Casual' },
        { word: 'talk', level: 'neutral', context: 'General use' },
        { word: 'discuss', level: 'formal', context: 'Formal/professional' },
        { word: 'converse', level: 'very_formal', context: 'Very formal' },
      ],
      // Ask → Inquire → Request
      ask: [
        { word: 'ask', level: 'neutral', context: 'General use' },
        { word: 'inquire', level: 'formal', context: 'Formal/professional' },
        { word: 'request', level: 'formal', context: 'Formal/business' },
      ],
      // Help → Assist → Aid
      help: [
        { word: 'help', level: 'neutral', context: 'General use' },
        { word: 'assist', level: 'formal', context: 'Formal/professional' },
        { word: 'aid', level: 'formal', context: 'Formal writing' },
      ],
      // Show → Demonstrate → Exhibit
      show: [
        { word: 'show', level: 'neutral', context: 'General use' },
        { word: 'demonstrate', level: 'formal', context: 'Professional/academic' },
        { word: 'exhibit', level: 'very_formal', context: 'Academic/technical' },
        { word: 'display', level: 'formal', context: 'Formal use' },
      ],
    };

    return registerMap[word.toLowerCase()] || [
      { word: word, level: 'neutral', context: 'General use' }
    ];
  }

  /**
   * Estimate frequency rank (simplified - would use actual frequency database)
   */
  estimateFrequencyRank(word) {
    // Very simplified estimation based on word length and common patterns
    // In production, this would come from a frequency database

    const commonWords = ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'I'];
    if (commonWords.includes(word.toLowerCase())) return 'essential';

    if (word.length <= 4) return 'high';
    if (word.length <= 6) return 'medium';
    if (word.length <= 8) return 'low';
    return 'rare';
  }

  /**
   * Get built-in synonyms
   */
  getBuiltInSynonyms(word) {
    const synonymMap = {
      happy: ['joyful', 'cheerful', 'delighted', 'pleased', 'content', 'glad'],
      sad: ['unhappy', 'miserable', 'sorrowful', 'dejected', 'melancholy'],
      big: ['large', 'huge', 'enormous', 'giant', 'massive', 'immense'],
      small: ['tiny', 'little', 'minute', 'petite', 'compact'],
      good: ['excellent', 'great', 'wonderful', 'superb', 'fine', 'splendid'],
      bad: ['poor', 'terrible', 'awful', 'dreadful', 'inferior'],
      important: ['significant', 'crucial', 'vital', 'essential', 'critical'],
      beautiful: ['pretty', 'lovely', 'gorgeous', 'attractive', 'stunning'],
      smart: ['intelligent', 'clever', 'bright', 'brilliant', 'wise'],
      fast: ['quick', 'rapid', 'swift', 'speedy', 'hasty'],
    };

    return synonymMap[word.toLowerCase()] || [];
  }

  /**
   * Get built-in antonyms
   */
  getBuiltInAntonyms(word) {
    const antonymMap = {
      happy: ['sad', 'unhappy', 'miserable'],
      big: ['small', 'tiny', 'little'],
      good: ['bad', 'poor', 'terrible'],
      hot: ['cold', 'cool', 'freezing'],
      fast: ['slow', 'sluggish', 'leisurely'],
      easy: ['difficult', 'hard', 'challenging'],
      light: ['dark', 'heavy'],
      new: ['old', 'ancient', 'outdated'],
      rich: ['poor', 'impoverished'],
      strong: ['weak', 'feeble', 'frail'],
    };

    return antonymMap[word.toLowerCase()] || [];
  }

  /**
   * Get related words
   */
  getRelatedWords(word) {
    // Simplified - in production, use semantic similarity models
    const related = {
      happy: ['smile', 'laugh', 'joy', 'celebration', 'pleasure'],
      sad: ['cry', 'tears', 'sorrow', 'grief', 'depression'],
      eat: ['food', 'meal', 'dinner', 'breakfast', 'lunch', 'restaurant'],
      work: ['job', 'career', 'office', 'boss', 'colleague', 'salary'],
      study: ['learn', 'education', 'school', 'university', 'teacher', 'exam'],
    };

    return related[word.toLowerCase()] || [];
  }

  /**
   * Enhance map with AI-generated content
   */
  async enhanceMapWithAI(map, aiService) {
    try {
      const prompt = `For the English word "${map.centerWord}", provide:
1. 5 synonyms with subtle meaning differences
2. 3 antonyms
3. 5 related words (same semantic field)
4. Usage notes and context

Format as JSON:
{
  "synonyms": [{"word": "...", "difference": "..."}],
  "antonyms": ["...", "..."],
  "related": ["...", "..."],
  "usageNotes": ["...", "..."]
}`;

      const response = await aiService.chat(prompt, { exerciseType: 'vocabulary' });
      const jsonMatch = response.match(/\{[\s\S]*\}/);

      if (jsonMatch) {
        const aiData = JSON.parse(jsonMatch[0]);
        map.synonyms = aiData.synonyms || map.synonyms;
        map.antonyms = aiData.antonyms || map.antonyms;
        map.related = aiData.related || map.related;
        map.usageNotes = aiData.usageNotes || [];
      }
    } catch (error) {
      console.error('Error enhancing word map with AI:', error);
    }

    return map;
  }

  /**
   * Get vocabulary by frequency priority
   */
  getVocabularyByFrequency(allVocabulary) {
    const categorized = {
      essential: [],
      high: [],
      medium: [],
      low: [],
      rare: [],
    };

    for (const vocab of allVocabulary) {
      const category = this.estimateFrequencyRank(vocab.word);
      if (categorized[category]) {
        categorized[category].push(vocab);
      }
    }

    return categorized;
  }

  /**
   * Generate frequency-based learning plan
   */
  generateFrequencyLearningPlan(userLevel = 'intermediate', masteredWords = []) {
    const masteredSet = new Set(masteredWords.map(w => w.toLowerCase()));

    const plan = {
      currentFocus: 'essential',
      progress: {
        essential: 0,
        high: 0,
        medium: 0,
        low: 0,
      },
      recommendations: [],
    };

    // Calculate progress
    const targets = { essential: 1000, high: 1000, medium: 1000, low: 2000 };

    for (const category of ['essential', 'high', 'medium', 'low']) {
      const masteredInCategory = Array.from(masteredSet).filter(w =>
        this.estimateFrequencyRank(w) === category
      ).length;

      plan.progress[category] = Math.round((masteredInCategory / targets[category]) * 100);
    }

    // Determine current focus
    if (plan.progress.essential < 80) {
      plan.currentFocus = 'essential';
      plan.recommendations.push('Focus on the most common 1000 words first - they make up 75% of everyday English!');
    } else if (plan.progress.high < 80) {
      plan.currentFocus = 'high';
      plan.recommendations.push('Great progress! Now master high-frequency words (1001-2000) for fluent conversation.');
    } else if (plan.progress.medium < 80) {
      plan.currentFocus = 'medium';
      plan.recommendations.push('Excellent! Medium-frequency words will help you express nuanced ideas.');
    } else {
      plan.currentFocus = 'low';
      plan.recommendations.push('Amazing progress! Focus on specialized vocabulary for your interests.');
    }

    return plan;
  }

  /**
   * Generate collocation trainer exercise
   */
  generateCollocationExercise(difficulty = 'intermediate') {
    const verbs = Object.keys(this.commonCollocations).filter(k =>
      ['make', 'take', 'do', 'have', 'get', 'give', 'pay', 'keep'].includes(k)
    );

    const targetVerb = verbs[Math.floor(Math.random() * verbs.length)];
    const collocations = this.commonCollocations[targetVerb];

    const exercise = {
      id: Date.now(),
      type: 'collocation_practice',
      verb: targetVerb,
      difficulty,
      questions: [],
    };

    // Generate fill-in-the-blank questions
    for (let i = 0; i < Math.min(5, collocations.length); i++) {
      const collocation = collocations[i];
      const sentence = this.generateSentenceForCollocation(targetVerb, collocation);

      exercise.questions.push({
        sentence: sentence.replace(targetVerb, '____'),
        options: this.generateCollocationOptions(targetVerb),
        correct: targetVerb,
        fullPhrase: `${targetVerb} ${collocation}`,
      });
    }

    return exercise;
  }

  /**
   * Generate sentence for collocation
   */
  generateSentenceForCollocation(verb, noun) {
    const templates = {
      make: [
        `I need to ${verb} ${noun} about this.`,
        `She always ${verb}s ${noun}.`,
        `We should ${verb} ${noun} on this matter.`,
      ],
      take: [
        `Let's ${verb} ${noun} now.`,
        `He ${verb}s ${noun} of his health.`,
        `It's important to ${verb} ${noun}.`,
      ],
      do: [
        `I have to ${verb} ${noun} tonight.`,
        `She ${verb}es ${noun} very well.`,
        `We ${verb} ${noun} together.`,
      ],
      have: [
        `I ${verb} ${noun} about that.`,
        `Do you ${verb} ${noun}?`,
        `She ${verb}s ${noun} in this field.`,
      ],
    };

    const verbTemplates = templates[verb] || [`I ${verb} ${noun}.`];
    return verbTemplates[Math.floor(Math.random() * verbTemplates.length)];
  }

  /**
   * Generate collocation options for multiple choice
   */
  generateCollocationOptions(correctVerb) {
    const verbs = ['make', 'do', 'take', 'have', 'get', 'give'];
    const options = [correctVerb];

    while (options.length < 4) {
      const verb = verbs[Math.floor(Math.random() * verbs.length)];
      if (!options.includes(verb)) {
        options.push(verb);
      }
    }

    // Shuffle options
    return options.sort(() => Math.random() - 0.5);
  }

  /**
   * Save word relationship exploration
   */
  saveWordExploration(word, map) {
    const explorations = this.getWordExplorations();

    explorations.unshift({
      word,
      map,
      exploredAt: new Date().toISOString(),
    });

    localStorage.setItem('word_explorations', JSON.stringify(explorations.slice(0, 100)));
  }

  /**
   * Get word explorations history
   */
  getWordExplorations() {
    const stored = localStorage.getItem('word_explorations');
    return stored ? JSON.parse(stored) : [];
  }
}

export default new EnhancedVocabularyService();
