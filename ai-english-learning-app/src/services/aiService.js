import Anthropic from '@anthropic-ai/sdk';

class AIService {
  constructor() {
    this.useLocalModel = false;
    this.ollamaBaseUrl = 'http://localhost:11434';
    this.anthropicClient = null;

    // Try to initialize Anthropic client if API key is available
    const apiKey = import.meta.env.VITE_ANTHROPIC_API_KEY || localStorage.getItem('anthropic_api_key');
    if (apiKey) {
      this.anthropicClient = new Anthropic({
        apiKey: apiKey,
        dangerouslyAllowBrowser: true
      });
    }
  }

  setApiKey(apiKey) {
    localStorage.setItem('anthropic_api_key', apiKey);
    this.anthropicClient = new Anthropic({
      apiKey: apiKey,
      dangerouslyAllowBrowser: true
    });
  }

  setUseLocalModel(useLocal) {
    this.useLocalModel = useLocal;
  }

  async chat(prompt, context = {}) {
    if (this.useLocalModel) {
      return await this.chatWithOllama(prompt, context);
    } else if (this.anthropicClient) {
      return await this.chatWithClaude(prompt, context);
    } else {
      throw new Error('No AI service configured. Please set up Claude API key or enable local model.');
    }
  }

  async chatWithClaude(prompt, context = {}) {
    try {
      const systemPrompt = this.buildSystemPrompt(context);

      const message = await this.anthropicClient.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 2000,
        temperature: 0.7,
        system: systemPrompt,
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ]
      });

      return message.content[0].text;
    } catch (error) {
      console.error('Claude API error:', error);
      throw new Error(`Claude API error: ${error.message}`);
    }
  }

  async chatWithOllama(prompt, context = {}) {
    try {
      const systemPrompt = this.buildSystemPrompt(context);

      const response = await fetch(`${this.ollamaBaseUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'llama3',
          prompt: `${systemPrompt}\n\nUser: ${prompt}\n\nAssistant:`,
          stream: false,
          options: {
            temperature: 0.7,
            top_p: 0.9
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`Ollama API error: ${response.statusText}`);
      }

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Ollama error:', error);
      throw new Error(`Local model error: ${error.message}. Make sure Ollama is running.`);
    }
  }

  buildSystemPrompt(context) {
    const basePrompt = `You are an experienced, patient, and encouraging English teacher with over 20 years of experience.
Your goal is to help non-native English speakers improve their speaking and writing skills through contextual, practical learning.

Key principles:
- Provide constructive, specific feedback with clear examples
- Explain WHY certain phrases or words work better in specific contexts
- Focus on practical, real-world usage rather than just grammar rules
- Be encouraging and celebrate improvements
- Adapt your teaching style to the student's level
- Use natural, conversational English in your responses`;

    let fullPrompt = basePrompt;

    if (context.exerciseType) {
      fullPrompt += `\n\nCurrent exercise type: ${context.exerciseType}`;
    }

    if (context.userLevel) {
      fullPrompt += `\n\nStudent's current level: ${context.userLevel}`;
    }

    if (context.focusArea) {
      fullPrompt += `\n\nFocus area: ${context.focusArea}`;
    }

    if (context.scenario) {
      fullPrompt += `\n\nScenario context: ${context.scenario}`;
    }

    return fullPrompt;
  }

  // Assessment Methods
  async evaluateBaselineAssessment(answers) {
    const prompt = `Please evaluate this English language baseline assessment and provide:
1. An overall proficiency level (beginner/elementary/intermediate/upper-intermediate/advanced)
2. Scores (0-100) for each skill: vocabulary, grammar, fluency, context_usage, writing_quality
3. Specific strengths and weaknesses
4. Recommended focus areas

Student's answers:
${JSON.stringify(answers, null, 2)}

Provide your response in JSON format with this structure:
{
  "level": "...",
  "scores": {
    "vocabulary": 0-100,
    "grammar": 0-100,
    "fluency": 0-100,
    "context_usage": 0-100,
    "writing_quality": 0-100
  },
  "proficiency_score": 0-100,
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "focus_areas": ["...", "..."]
}`;

    const response = await this.chat(prompt);
    try {
      // Extract JSON from response
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      throw new Error('Could not parse assessment response');
    } catch (error) {
      console.error('Error parsing assessment:', error);
      return this.getDefaultAssessment();
    }
  }

  // Conversation Practice Methods
  async evaluateConversationResponse(scenario, userResponse, conversationHistory = []) {
    const historyText = conversationHistory.length > 0
      ? `Previous conversation:\n${conversationHistory.map(h => `${h.role}: ${h.message}`).join('\n')}\n\n`
      : '';

    const prompt = `${historyText}Scenario: ${scenario}

Student's response: "${userResponse}"

Please evaluate this response and provide:
1. A score (0-100) based on appropriateness, vocabulary usage, and naturalness
2. Specific feedback on what was good
3. Specific feedback on what could be improved
4. 2-3 alternative ways to express the same idea
5. Vocabulary suggestions with explanations
6. Your next response in the conversation to continue the practice

Provide your response in JSON format:
{
  "score": 0-100,
  "good_points": ["...", "..."],
  "improvements": ["...", "..."],
  "alternatives": ["...", "..."],
  "vocabulary_tips": [{"word": "...", "usage": "...", "why": "..."}],
  "next_message": "...",
  "encouragement": "..."
}`;

    const response = await this.chat(prompt, {
      exerciseType: 'conversation',
      scenario: scenario
    });

    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      throw new Error('Could not parse conversation evaluation');
    } catch (error) {
      console.error('Error parsing conversation evaluation:', error);
      return this.getDefaultConversationEvaluation(userResponse);
    }
  }

  // Writing Evaluation Methods
  async evaluateWriting(prompt, userWriting, focusArea = 'general') {
    const evaluationPrompt = `Writing prompt: "${prompt}"

Student's writing:
"""
${userWriting}
"""

Focus area: ${focusArea}

Please provide a detailed evaluation including:
1. Overall score (0-100)
2. Individual scores for: grammar, vocabulary, clarity, organization, style
3. Specific strengths (with examples from the text)
4. Specific areas for improvement (with examples)
5. Corrected version with improvements
6. 3-5 vocabulary suggestions that would enhance the writing
7. Grammar tips based on mistakes found

Provide response in JSON format:
{
  "overall_score": 0-100,
  "scores": {
    "grammar": 0-100,
    "vocabulary": 0-100,
    "clarity": 0-100,
    "organization": 0-100,
    "style": 0-100
  },
  "strengths": [{"point": "...", "example": "..."}],
  "improvements": [{"issue": "...", "example": "...", "suggestion": "..."}],
  "corrected_version": "...",
  "vocabulary_suggestions": [{"word": "...", "definition": "...", "usage": "..."}],
  "grammar_tips": ["...", "..."],
  "encouragement": "..."
}`;

    const response = await this.chat(evaluationPrompt, {
      exerciseType: 'writing',
      focusArea: focusArea
    });

    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      throw new Error('Could not parse writing evaluation');
    } catch (error) {
      console.error('Error parsing writing evaluation:', error);
      return this.getDefaultWritingEvaluation();
    }
  }

  // Vocabulary Context Methods
  async generateVocabularyExercise(difficulty, focusWords = []) {
    const prompt = `Generate a vocabulary exercise at ${difficulty} level${
      focusWords.length > 0 ? ` focusing on these words: ${focusWords.join(', ')}` : ''
    }.

Include:
1. A realistic scenario or situation
2. 5-8 target vocabulary words with definitions
3. A task for the student (describe the situation, fill in blanks, or write a short response)
4. Context clues to help understand the vocabulary

Provide response in JSON format:
{
  "title": "...",
  "scenario": "...",
  "vocabulary": [{"word": "...", "definition": "...", "example": "..."}],
  "task": "...",
  "difficulty": "${difficulty}"
}`;

    const response = await this.chat(prompt, {
      exerciseType: 'vocabulary_context'
    });

    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      throw new Error('Could not parse vocabulary exercise');
    } catch (error) {
      console.error('Error parsing vocabulary exercise:', error);
      return this.getDefaultVocabularyExercise(difficulty);
    }
  }

  // Grammar Practice Methods
  async generateGrammarExercise(topic, difficulty) {
    const prompt = `Generate a grammar exercise on "${topic}" at ${difficulty} level.

Include:
1. Clear explanation of the grammar rule
2. 3-4 examples demonstrating correct usage
3. 5-7 practice sentences (some correct, some with errors to fix)
4. Context for when to use this grammar structure

Provide response in JSON format:
{
  "title": "...",
  "rule_explanation": "...",
  "examples": ["...", "..."],
  "practice_items": [{"sentence": "...", "is_correct": true/false, "correction": "..."}],
  "usage_context": "...",
  "difficulty": "${difficulty}"
}`;

    const response = await this.chat(prompt, {
      exerciseType: 'grammar'
    });

    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      throw new Error('Could not parse grammar exercise');
    } catch (error) {
      console.error('Error parsing grammar exercise:', error);
      return this.getDefaultGrammarExercise(topic, difficulty);
    }
  }

  // Small Talk Practice Methods
  async generateSmallTalkScenario(difficulty) {
    const prompt = `Generate a small talk practice scenario at ${difficulty} level.

Include:
1. A realistic social situation (elevator, waiting room, networking event, etc.)
2. Conversation starter examples
3. Appropriate responses and follow-up questions
4. Common phrases and expressions for this situation
5. Cultural tips for natural conversation

Provide response in JSON format:
{
  "situation": "...",
  "starters": ["...", "..."],
  "responses": ["...", "..."],
  "phrases": ["...", "..."],
  "tips": ["...", "..."],
  "difficulty": "${difficulty}"
}`;

    const response = await this.chat(prompt, {
      exerciseType: 'small_talk'
    });

    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      throw new Error('Could not parse small talk scenario');
    } catch (error) {
      console.error('Error parsing small talk scenario:', error);
      return this.getDefaultSmallTalkScenario(difficulty);
    }
  }

  // Weekly Challenge Methods
  async generateWeeklyChallenge(userLevel, previousPerformance = {}) {
    const prompt = `Generate an engaging weekly English learning challenge for a ${userLevel} level student.

Previous performance: ${JSON.stringify(previousPerformance)}

Create a challenge that:
1. Is fun and engaging
2. Pushes the student slightly beyond their comfort zone
3. Can be completed in 15-30 minutes
4. Provides clear success criteria

Challenge types: creative writing, debate topic, vocabulary story, describe & explain, conversation simulation

Provide response in JSON format:
{
  "title": "...",
  "type": "...",
  "description": "...",
  "instructions": ["...", "..."],
  "success_criteria": ["...", "..."],
  "difficulty": "...",
  "estimated_time": "...",
  "learning_objectives": ["...", "..."]
}`;

    const response = await this.chat(prompt, {
      exerciseType: 'weekly_challenge',
      userLevel: userLevel
    });

    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      throw new Error('Could not parse weekly challenge');
    } catch (error) {
      console.error('Error parsing weekly challenge:', error);
      return this.getDefaultWeeklyChallenge();
    }
  }

  // Default fallback methods
  getDefaultAssessment() {
    return {
      level: 'intermediate',
      scores: {
        vocabulary: 50,
        grammar: 50,
        fluency: 50,
        context_usage: 50,
        writing_quality: 50
      },
      proficiency_score: 50,
      strengths: ['Willingness to learn', 'Basic communication skills'],
      weaknesses: ['Vocabulary recall', 'Context-appropriate language use'],
      focus_areas: ['Vocabulary in context', 'Conversational practice']
    };
  }

  getDefaultConversationEvaluation(response) {
    return {
      score: 70,
      good_points: ['You communicated your idea clearly'],
      improvements: ['Try using more varied vocabulary'],
      alternatives: ['Let me suggest some alternative phrasings...'],
      vocabulary_tips: [],
      next_message: 'That\'s interesting! Can you tell me more?',
      encouragement: 'Good effort! Keep practicing!'
    };
  }

  getDefaultWritingEvaluation() {
    return {
      overall_score: 70,
      scores: {
        grammar: 70,
        vocabulary: 65,
        clarity: 75,
        organization: 70,
        style: 65
      },
      strengths: [],
      improvements: [],
      corrected_version: '',
      vocabulary_suggestions: [],
      grammar_tips: [],
      encouragement: 'Good work! Keep practicing your writing skills.'
    };
  }

  getDefaultVocabularyExercise(difficulty) {
    return {
      title: 'Vocabulary Practice',
      scenario: 'Practice using new vocabulary in context.',
      vocabulary: [],
      task: 'Use the vocabulary words in sentences.',
      difficulty: difficulty
    };
  }

  getDefaultGrammarExercise(topic, difficulty) {
    return {
      title: topic,
      rule_explanation: 'Practice this grammar concept.',
      examples: [],
      practice_items: [],
      usage_context: 'Use in various contexts.',
      difficulty: difficulty
    };
  }

  getDefaultSmallTalkScenario(difficulty) {
    return {
      situation: 'Casual conversation',
      starters: ['How are you?', 'Nice weather today!'],
      responses: ['I\'m doing well, thanks!', 'Yes, it is!'],
      phrases: ['How about you?', 'What do you think?'],
      tips: ['Be friendly and natural'],
      difficulty: difficulty
    };
  }

  getDefaultWeeklyChallenge() {
    return {
      title: 'Weekly Practice Challenge',
      type: 'creative_writing',
      description: 'Complete this week\'s challenge!',
      instructions: ['Do your best', 'Have fun!'],
      success_criteria: ['Complete the task', 'Use proper grammar'],
      difficulty: 'intermediate',
      estimated_time: '20 minutes',
      learning_objectives: ['Practice writing', 'Build confidence']
    };
  }
}

export default new AIService();
