/**
 * Pattern Recognition Service
 * Analyzes user mistakes, identifies patterns, and provides intelligent insights
 */

class PatternRecognitionService {
  constructor() {
    this.errorCategories = {
      articles: ['a', 'an', 'the'],
      prepositions: ['in', 'on', 'at', 'to', 'for', 'with', 'from'],
      tenses: ['past', 'present', 'future', 'perfect', 'continuous'],
      word_order: ['subject', 'verb', 'object', 'placement'],
      vocabulary: ['word_choice', 'inappropriate', 'awkward'],
      grammar: ['agreement', 'structure', 'form'],
    };

    this.severityLevels = {
      critical: 'Changes meaning significantly',
      important: 'Sounds very unnatural',
      moderate: 'Noticeable but understandable',
      minor: 'Slightly off but acceptable',
    };
  }

  /**
   * Analyze a mistake and categorize it
   */
  analyzeMistake(originalText, correctedText, explanation) {
    const category = this.detectMistakeCategory(originalText, correctedText, explanation);
    const severity = this.assessSeverity(originalText, correctedText);
    const pattern = this.extractPattern(originalText, correctedText, category);

    return {
      category,
      severity,
      pattern,
      isRecurring: false, // Will be determined by checking history
    };
  }

  /**
   * Detect the category of a mistake
   */
  detectMistakeCategory(original, corrected, explanation) {
    const lowerExplanation = (explanation || '').toLowerCase();
    const lowerOriginal = original.toLowerCase();
    const lowerCorrected = corrected.toLowerCase();

    // Article detection
    if (this.hasArticleIssue(lowerOriginal, lowerCorrected) ||
        lowerExplanation.includes('article') ||
        lowerExplanation.includes('a/an/the')) {
      return 'articles';
    }

    // Preposition detection
    if (this.hasPrepositionIssue(lowerOriginal, lowerCorrected) ||
        lowerExplanation.includes('preposition')) {
      return 'prepositions';
    }

    // Tense detection
    if (lowerExplanation.includes('tense') ||
        lowerExplanation.includes('past') ||
        lowerExplanation.includes('present') ||
        lowerExplanation.includes('future')) {
      return 'tenses';
    }

    // Word order
    if (lowerExplanation.includes('word order') ||
        lowerExplanation.includes('placement') ||
        this.hasDifferentWordOrder(original, corrected)) {
      return 'word_order';
    }

    // Vocabulary choice
    if (lowerExplanation.includes('word choice') ||
        lowerExplanation.includes('vocabulary') ||
        lowerExplanation.includes('better word')) {
      return 'vocabulary';
    }

    // Default to grammar
    return 'grammar';
  }

  /**
   * Check if there's an article issue
   */
  hasArticleIssue(original, corrected) {
    const articles = ['a ', 'an ', 'the '];
    const origArticles = articles.filter(a => original.includes(a)).length;
    const corrArticles = articles.filter(a => corrected.includes(a)).length;
    return origArticles !== corrArticles;
  }

  /**
   * Check if there's a preposition issue
   */
  hasPrepositionIssue(original, corrected) {
    const preps = this.errorCategories.prepositions;
    for (const prep of preps) {
      const origHas = original.includes(` ${prep} `);
      const corrHas = corrected.includes(` ${prep} `);
      if (origHas !== corrHas) return true;
    }
    return false;
  }

  /**
   * Check if word order is different
   */
  hasDifferentWordOrder(original, corrected) {
    const origWords = original.toLowerCase().split(/\s+/).filter(w => w.length > 2);
    const corrWords = corrected.toLowerCase().split(/\s+/).filter(w => w.length > 2);

    if (origWords.length !== corrWords.length) return true;

    // Check if words are in different positions
    const origSorted = [...origWords].sort().join(' ');
    const corrSorted = [...corrWords].sort().join(' ');
    const sameWords = origSorted === corrSorted;
    const sameOrder = origWords.join(' ') === corrWords.join(' ');

    return sameWords && !sameOrder;
  }

  /**
   * Assess the severity of a mistake
   */
  assessSeverity(original, corrected) {
    const originalWords = original.split(/\s+/);
    const correctedWords = corrected.split(/\s+/);

    // Length difference suggests structural change
    const lengthDiff = Math.abs(originalWords.length - correctedWords.length);

    // Word-level differences
    const differences = this.countWordDifferences(originalWords, correctedWords);
    const differenceRatio = differences / Math.max(originalWords.length, correctedWords.length);

    if (differenceRatio > 0.5 || lengthDiff > 3) {
      return 'critical';
    } else if (differenceRatio > 0.3 || lengthDiff > 1) {
      return 'important';
    } else if (differenceRatio > 0.1) {
      return 'moderate';
    } else {
      return 'minor';
    }
  }

  /**
   * Count word-level differences
   */
  countWordDifferences(words1, words2) {
    const maxLength = Math.max(words1.length, words2.length);
    let differences = 0;

    for (let i = 0; i < maxLength; i++) {
      if (words1[i]?.toLowerCase() !== words2[i]?.toLowerCase()) {
        differences++;
      }
    }

    return differences;
  }

  /**
   * Extract the specific pattern from the mistake
   */
  extractPattern(original, corrected, category) {
    switch (category) {
      case 'articles':
        return this.extractArticlePattern(original, corrected);
      case 'prepositions':
        return this.extractPrepositionPattern(original, corrected);
      case 'tenses':
        return this.extractTensePattern(original, corrected);
      default:
        return `${category}_error`;
    }
  }

  /**
   * Extract article-specific pattern
   */
  extractArticlePattern(original, corrected) {
    const articles = ['a', 'an', 'the'];
    let pattern = 'article_';

    for (const article of articles) {
      if (original.includes(` ${article} `) && !corrected.includes(` ${article} `)) {
        pattern += `removed_${article}`;
      } else if (!original.includes(` ${article} `) && corrected.includes(` ${article} `)) {
        pattern += `added_${article}`;
      }
    }

    return pattern || 'article_general';
  }

  /**
   * Extract preposition-specific pattern
   */
  extractPrepositionPattern(original, corrected) {
    const preps = this.errorCategories.prepositions;

    for (const prep of preps) {
      const origMatch = original.match(new RegExp(`\\s${prep}\\s`, 'i'));
      const corrMatch = corrected.match(new RegExp(`\\s${prep}\\s`, 'i'));

      if (origMatch && !corrMatch) {
        return `preposition_removed_${prep}`;
      } else if (!origMatch && corrMatch) {
        return `preposition_added_${prep}`;
      }
    }

    return 'preposition_substitution';
  }

  /**
   * Extract tense-specific pattern
   */
  extractTensePattern(original, corrected) {
    // Simple heuristic based on common tense markers
    if (corrected.includes('have') || corrected.includes('has') || corrected.includes('had')) {
      return 'tense_perfect';
    } else if (corrected.includes('will') || corrected.includes('would')) {
      return 'tense_future';
    } else if (corrected.includes('ing')) {
      return 'tense_continuous';
    } else if (corrected.includes('ed')) {
      return 'tense_past';
    }

    return 'tense_general';
  }

  /**
   * Aggregate error patterns from history
   */
  aggregatePatterns(mistakes) {
    const patterns = {};
    const categories = {};
    const severities = {};

    for (const mistake of mistakes) {
      // Count by category
      const category = mistake.mistake_category || 'general';
      categories[category] = (categories[category] || 0) + 1;

      // Count by severity
      const severity = mistake.severity || 'moderate';
      severities[severity] = (severities[severity] || 0) + 1;

      // Extract and count specific patterns
      const analysis = this.analyzeMistake(
        mistake.original_text || '',
        mistake.corrected_text || '',
        mistake.explanation || ''
      );

      const patternKey = analysis.pattern;
      if (!patterns[patternKey]) {
        patterns[patternKey] = {
          pattern: patternKey,
          category: analysis.category,
          count: 0,
          examples: [],
        };
      }

      patterns[patternKey].count++;
      if (patterns[patternKey].examples.length < 3) {
        patterns[patternKey].examples.push({
          original: mistake.original_text,
          corrected: mistake.corrected_text,
          date: mistake.occurred_at,
        });
      }
    }

    return {
      patterns: Object.values(patterns).sort((a, b) => b.count - a.count),
      categories,
      severities,
      totalMistakes: mistakes.length,
    };
  }

  /**
   * Identify recurring patterns
   */
  identifyRecurringPatterns(patterns, threshold = 3) {
    return patterns.filter(p => p.count >= threshold);
  }

  /**
   * Generate correction strategy for a pattern
   */
  generateCorrectionStrategy(pattern) {
    const strategies = {
      articles: 'Practice with noun countability exercises. Remember: "a/an" for singular countable, "the" for specific items, no article for general plurals/uncountable.',
      prepositions: 'Learn common collocation pairs (e.g., "arrive at", "depend on"). Context and usage are more important than rules.',
      tenses: 'Focus on time markers. Use timelines to visualize when actions occur. Practice with context-rich scenarios.',
      word_order: 'English follows Subject-Verb-Object. Adjectives before nouns, adverbs are flexible but typically after verbs.',
      vocabulary: 'Build vocabulary in context. Learn word families and collocations. Practice using new words in your own sentences.',
      grammar: 'Review the specific grammar rule. Practice with targeted exercises. Use it in writing and speaking.',
    };

    const category = pattern.category || 'grammar';
    return strategies[category] || strategies.grammar;
  }

  /**
   * Calculate improvement rate for a pattern
   */
  calculateImprovementRate(pattern, recentMistakes, historicalMistakes) {
    if (historicalMistakes.length === 0) return 0;

    const recentCount = recentMistakes.filter(m =>
      m.mistake_category === pattern.category
    ).length;

    const historicalCount = historicalMistakes.filter(m =>
      m.mistake_category === pattern.category
    ).length;

    const recentRate = recentCount / Math.max(1, recentMistakes.length);
    const historicalRate = historicalCount / historicalMistakes.length;

    // Positive number means improvement (fewer errors)
    const improvement = ((historicalRate - recentRate) / historicalRate) * 100;
    return Math.round(improvement);
  }

  /**
   * Detect avoided words (words student consistently doesn't use)
   */
  detectAvoidedWords(exerciseHistory, vocabularyLearned) {
    const wordsUsed = new Set();

    // Extract words from responses
    for (const exercise of exerciseHistory) {
      if (exercise.user_response) {
        const words = exercise.user_response.toLowerCase().match(/\b\w+\b/g) || [];
        words.forEach(word => wordsUsed.add(word));
      }
    }

    // Find learned words not used
    const avoidedWords = [];
    for (const vocab of vocabularyLearned) {
      if (vocab.word && !wordsUsed.has(vocab.word.toLowerCase())) {
        const daysSinceLearned = this.daysSince(vocab.last_reviewed || vocab.created_at);
        if (daysSinceLearned >= 7) { // Learned more than a week ago but never used
          avoidedWords.push({
            word: vocab.word,
            learnedDate: vocab.last_reviewed || vocab.created_at,
            daysSinceLearned,
          });
        }
      }
    }

    return avoidedWords.sort((a, b) => b.daysSinceLearned - a.daysSinceLearned);
  }

  /**
   * Detect overused words/phrases
   */
  detectOverusedWords(exerciseHistory, threshold = 10) {
    const wordCounts = {};
    const phraseCounts = {};

    for (const exercise of exerciseHistory) {
      if (exercise.user_response) {
        const text = exercise.user_response.toLowerCase();

        // Count individual words
        const words = text.match(/\b\w+\b/g) || [];
        for (const word of words) {
          if (word.length > 3) { // Ignore very short words
            wordCounts[word] = (wordCounts[word] || 0) + 1;
          }
        }

        // Count common phrases (2-3 words)
        const sentences = text.split(/[.!?]+/);
        for (const sentence of sentences) {
          const sentenceWords = sentence.trim().split(/\s+/);
          for (let i = 0; i < sentenceWords.length - 1; i++) {
            const phrase = `${sentenceWords[i]} ${sentenceWords[i+1]}`;
            if (phrase.length > 6) {
              phraseCounts[phrase] = (phraseCounts[phrase] || 0) + 1;
            }
          }
        }
      }
    }

    const overusedWords = Object.entries(wordCounts)
      .filter(([word, count]) => count >= threshold)
      .map(([word, count]) => ({ word, count, type: 'word' }))
      .sort((a, b) => b.count - a.count);

    const overusedPhrases = Object.entries(phraseCounts)
      .filter(([phrase, count]) => count >= Math.floor(threshold / 2))
      .map(([phrase, count]) => ({ phrase, count, type: 'phrase' }))
      .sort((a, b) => b.count - a.count);

    return {
      words: overusedWords.slice(0, 10),
      phrases: overusedPhrases.slice(0, 10),
    };
  }

  /**
   * Helper: Calculate days since a date
   */
  daysSince(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  }
}

export default new PatternRecognitionService();
