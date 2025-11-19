/**
 * Contextual Memory Service
 * Manages personal contexts, context cards, and vocabulary relationships
 */

class ContextualMemoryService {
  constructor() {
    this.defaultContexts = [
      { name: 'Work & Professional', category: 'professional', color: '#3b82f6', icon: 'Briefcase' },
      { name: 'Daily Life & Routine', category: 'daily', color: '#10b981', icon: 'Home' },
      { name: 'Social & Friends', category: 'social', color: '#f59e0b', icon: 'Users' },
      { name: 'Family & Personal', category: 'personal', color: '#ec4899', icon: 'Heart' },
      { name: 'Hobbies & Interests', category: 'hobbies', color: '#8b5cf6', icon: 'Star' },
    ];
  }

  /**
   * Get all personal contexts
   */
  getPersonalContexts() {
    const stored = localStorage.getItem('personal_contexts');
    if (stored) {
      return JSON.parse(stored);
    }
    // Return default contexts
    const contexts = this.defaultContexts.map((ctx, index) => ({
      id: index + 1,
      user_id: 1,
      context_name: ctx.name,
      context_category: ctx.category,
      description: `Vocabulary and phrases related to ${ctx.name.toLowerCase()}`,
      color_code: ctx.color,
      icon_name: ctx.icon,
      created_at: new Date().toISOString(),
    }));
    localStorage.setItem('personal_contexts', JSON.stringify(contexts));
    return contexts;
  }

  /**
   * Create a new personal context
   */
  createContext(name, category, description, color, icon) {
    const contexts = this.getPersonalContexts();
    const newContext = {
      id: Date.now(),
      user_id: 1,
      context_name: name,
      context_category: category,
      description: description || '',
      color_code: color || '#6366f1',
      icon_name: icon || 'Tag',
      created_at: new Date().toISOString(),
    };
    contexts.push(newContext);
    localStorage.setItem('personal_contexts', JSON.stringify(contexts));
    return newContext;
  }

  /**
   * Update a personal context
   */
  updateContext(contextId, updates) {
    const contexts = this.getPersonalContexts();
    const index = contexts.findIndex(c => c.id === contextId);
    if (index >= 0) {
      contexts[index] = { ...contexts[index], ...updates };
      localStorage.setItem('personal_contexts', JSON.stringify(contexts));
      return contexts[index];
    }
    return null;
  }

  /**
   * Delete a personal context
   */
  deleteContext(contextId) {
    const contexts = this.getPersonalContexts();
    const filtered = contexts.filter(c => c.id !== contextId);
    localStorage.setItem('personal_contexts', JSON.stringify(filtered));

    // Also remove associations
    const associations = this.getVocabularyContextAssociations();
    const filteredAssoc = associations.filter(a => a.context_id !== contextId);
    localStorage.setItem('vocabulary_contexts', JSON.stringify(filteredAssoc));

    return true;
  }

  /**
   * Associate vocabulary with contexts
   */
  associateVocabularyWithContext(vocabularyId, contextId, relevance = 5) {
    const associations = this.getVocabularyContextAssociations();

    // Check if association already exists
    const existing = associations.find(
      a => a.vocabulary_id === vocabularyId && a.context_id === contextId
    );

    if (existing) {
      existing.relevance_score = relevance;
    } else {
      associations.push({
        id: Date.now(),
        vocabulary_id: vocabularyId,
        context_id: contextId,
        relevance_score: relevance,
      });
    }

    localStorage.setItem('vocabulary_contexts', JSON.stringify(associations));
    return true;
  }

  /**
   * Get vocabulary context associations
   */
  getVocabularyContextAssociations() {
    const stored = localStorage.getItem('vocabulary_contexts');
    return stored ? JSON.parse(stored) : [];
  }

  /**
   * Get vocabularies by context
   */
  getVocabulariesByContext(contextId) {
    const associations = this.getVocabularyContextAssociations();
    const contextAssociations = associations.filter(a => a.context_id === contextId);

    // Get vocabulary details
    const allVocabulary = JSON.parse(localStorage.getItem('vocabulary') || '[]');
    const userVocabulary = JSON.parse(localStorage.getItem('user_vocabulary') || '[]');

    return contextAssociations.map(assoc => {
      const vocab = allVocabulary.find(v => v.id === assoc.vocabulary_id);
      const userVocab = userVocabulary.find(uv => uv.vocabulary_id === assoc.vocabulary_id);

      return {
        ...vocab,
        ...userVocab,
        relevance: assoc.relevance_score,
      };
    }).filter(v => v);
  }

  /**
   * Get contexts for a vocabulary word
   */
  getContextsForVocabulary(vocabularyId) {
    const associations = this.getVocabularyContextAssociations();
    const vocabAssociations = associations.filter(a => a.vocabulary_id === vocabularyId);

    const contexts = this.getPersonalContexts();

    return vocabAssociations.map(assoc => {
      const context = contexts.find(c => c.id === assoc.context_id);
      return {
        ...context,
        relevance: assoc.relevance_score,
      };
    }).filter(c => c);
  }

  /**
   * Create a context card for a vocabulary word
   */
  createContextCard(vocabularyId, personalExample, usageContexts, commonMistakes, relatedWords) {
    const cards = this.getContextCards();

    const newCard = {
      id: Date.now(),
      user_id: 1,
      vocabulary_id: vocabularyId,
      personal_example: personalExample,
      usage_contexts: JSON.stringify(usageContexts || []),
      common_mistakes: JSON.stringify(commonMistakes || []),
      related_words: JSON.stringify(relatedWords || []),
      last_reviewed: new Date().toISOString(),
      review_count: 0,
      created_at: new Date().toISOString(),
    };

    cards.push(newCard);
    localStorage.setItem('context_cards', JSON.stringify(cards));
    return newCard;
  }

  /**
   * Get all context cards
   */
  getContextCards() {
    const stored = localStorage.getItem('context_cards');
    return stored ? JSON.parse(stored) : [];
  }

  /**
   * Get context card for a specific vocabulary
   */
  getContextCard(vocabularyId) {
    const cards = this.getContextCards();
    const card = cards.find(c => c.vocabulary_id === vocabularyId);

    if (card) {
      return {
        ...card,
        usage_contexts: JSON.parse(card.usage_contexts || '[]'),
        common_mistakes: JSON.parse(card.common_mistakes || '[]'),
        related_words: JSON.parse(card.related_words || '[]'),
      };
    }

    return null;
  }

  /**
   * Update a context card
   */
  updateContextCard(cardId, updates) {
    const cards = this.getContextCards();
    const index = cards.findIndex(c => c.id === cardId);

    if (index >= 0) {
      // Stringify array fields if they're being updated
      const processedUpdates = { ...updates };
      if (updates.usage_contexts) {
        processedUpdates.usage_contexts = JSON.stringify(updates.usage_contexts);
      }
      if (updates.common_mistakes) {
        processedUpdates.common_mistakes = JSON.stringify(updates.common_mistakes);
      }
      if (updates.related_words) {
        processedUpdates.related_words = JSON.stringify(updates.related_words);
      }

      cards[index] = { ...cards[index], ...processedUpdates };
      localStorage.setItem('context_cards', JSON.stringify(cards));

      return this.getContextCard(cards[index].vocabulary_id);
    }

    return null;
  }

  /**
   * Review a context card (update review stats)
   */
  reviewContextCard(cardId) {
    const cards = this.getContextCards();
    const index = cards.findIndex(c => c.id === cardId);

    if (index >= 0) {
      cards[index].last_reviewed = new Date().toISOString();
      cards[index].review_count = (cards[index].review_count || 0) + 1;
      localStorage.setItem('context_cards', JSON.stringify(cards));
      return true;
    }

    return false;
  }

  /**
   * Get cards due for review
   */
  getCardsDueForReview() {
    const cards = this.getContextCards();
    const now = new Date();

    return cards.filter(card => {
      if (!card.last_reviewed) return true;

      const lastReview = new Date(card.last_reviewed);
      const daysSinceReview = (now - lastReview) / (1000 * 60 * 60 * 24);

      // Review interval based on review count (spaced repetition)
      const reviewIntervals = [1, 3, 7, 14, 30]; // days
      const interval = reviewIntervals[Math.min(card.review_count || 0, reviewIntervals.length - 1)];

      return daysSinceReview >= interval;
    });
  }

  /**
   * Build word relationship map
   */
  buildWordRelationshipMap(word) {
    // This would ideally use a vocabulary database or API
    // For now, we'll return a structured format for the UI

    const relationships = {
      word: word,
      synonyms: [],
      antonyms: [],
      related: [],
      wordFamily: [],
    };

    // Get from context cards and vocabulary
    const cards = this.getContextCards();
    const allVocabulary = JSON.parse(localStorage.getItem('vocabulary') || '[]');

    // Find related words from context cards
    cards.forEach(card => {
      const relatedWords = JSON.parse(card.related_words || '[]');
      relatedWords.forEach(related => {
        if (related.type === 'synonym' && !relationships.synonyms.includes(related.word)) {
          relationships.synonyms.push(related.word);
        } else if (related.type === 'antonym' && !relationships.antonyms.includes(related.word)) {
          relationships.antonyms.push(related.word);
        } else if (related.type === 'related' && !relationships.related.includes(related.word)) {
          relationships.related.push(related.word);
        } else if (related.type === 'family' && !relationships.wordFamily.includes(related.word)) {
          relationships.wordFamily.push(related.word);
        }
      });
    });

    return relationships;
  }

  /**
   * Get vocabulary organized by frequency rank
   */
  getVocabularyByFrequency() {
    const allVocabulary = JSON.parse(localStorage.getItem('vocabulary') || '[]');

    // Categorize by frequency
    const categorized = {
      high: [], // Top 1000
      medium: [], // 1001-2000
      low: [], // 2001-3000
      rare: [], // 3000+
    };

    allVocabulary.forEach(vocab => {
      const rank = vocab.frequency_rank || 9999;

      if (rank <= 1000) {
        categorized.high.push(vocab);
      } else if (rank <= 2000) {
        categorized.medium.push(vocab);
      } else if (rank <= 3000) {
        categorized.low.push(vocab);
      } else {
        categorized.rare.push(vocab);
      }
    });

    return categorized;
  }

  /**
   * Suggest collocations for a word
   */
  suggestCollocations(word, partOfSpeech = 'verb') {
    // Common collocations database (simplified)
    const commonCollocations = {
      make: ['a decision', 'a mistake', 'progress', 'an effort', 'a difference', 'sense'],
      take: ['a break', 'a chance', 'action', 'time', 'notes', 'care'],
      do: ['homework', 'business', 'research', 'work', 'your best'],
      have: ['a question', 'an idea', 'experience', 'fun', 'time'],
      get: ['started', 'better', 'worse', 'ready', 'involved'],
      go: ['ahead', 'wrong', 'well', 'smoothly', 'according to plan'],
      pay: ['attention', 'a visit', 'respect', 'tribute', 'dividends'],
      catch: ['a cold', 'fire', 'attention', 'up'],
      break: ['the news', 'a record', 'the ice', 'even'],
      keep: ['in touch', 'track', 'quiet', 'calm', 'going'],
    };

    const lowerWord = word.toLowerCase();

    if (commonCollocations[lowerWord]) {
      return commonCollocations[lowerWord].map(collocation => ({
        phrase: `${word} ${collocation}`,
        type: 'verb-noun',
      }));
    }

    return [];
  }

  /**
   * Get learning register (formality level) for vocabulary
   */
  getRegisterVariants(word) {
    // Common register variants (simplified)
    const registerMap = {
      kids: [
        { word: 'kids', level: 'informal' },
        { word: 'children', level: 'neutral' },
        { word: 'youngsters', level: 'formal' },
      ],
      buy: [
        { word: 'get', level: 'informal' },
        { word: 'buy', level: 'neutral' },
        { word: 'purchase', level: 'formal' },
        { word: 'acquire', level: 'very formal' },
      ],
      home: [
        { word: 'place', level: 'informal' },
        { word: 'home', level: 'neutral' },
        { word: 'residence', level: 'formal' },
        { word: 'dwelling', level: 'very formal' },
      ],
      start: [
        { word: 'start', level: 'neutral' },
        { word: 'begin', level: 'formal' },
        { word: 'commence', level: 'very formal' },
        { word: 'initiate', level: 'very formal' },
      ],
    };

    return registerMap[word.toLowerCase()] || [
      { word: word, level: 'neutral' }
    ];
  }

  /**
   * Export context cards and associations
   */
  exportPersonalData() {
    return {
      contexts: this.getPersonalContexts(),
      contextCards: this.getContextCards(),
      associations: this.getVocabularyContextAssociations(),
      exportedAt: new Date().toISOString(),
    };
  }

  /**
   * Import context cards and associations
   */
  importPersonalData(data) {
    if (data.contexts) {
      localStorage.setItem('personal_contexts', JSON.stringify(data.contexts));
    }
    if (data.contextCards) {
      localStorage.setItem('context_cards', JSON.stringify(data.contextCards));
    }
    if (data.associations) {
      localStorage.setItem('vocabulary_contexts', JSON.stringify(data.associations));
    }
    return true;
  }
}

export default new ContextualMemoryService();
