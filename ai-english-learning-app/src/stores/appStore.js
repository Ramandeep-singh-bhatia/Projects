import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAppStore = create(
  persist(
    (set, get) => ({
      // User state
      user: {
        id: 1,
        username: 'default_user',
        currentLevel: 'beginner',
        proficiencyScore: 0,
        hasCompletedAssessment: false,
      },

      // Learning progress
      learningProgress: {
        vocabulary: 0,
        grammar: 0,
        fluency: 0,
        context_usage: 0,
        writing_quality: 0,
      },

      // Streak data
      streak: {
        current: 0,
        longest: 0,
        lastActivity: null,
      },

      // AI configuration
      aiConfig: {
        useLocalModel: false,
        apiKey: null,
      },

      // Current exercise
      currentExercise: null,

      // Exercise history (limited to recent)
      exerciseHistory: [],

      // Vocabulary mastery
      vocabularyMastery: [],

      // Mistakes journal
      mistakes: [],

      // Settings
      settings: {
        notificationsEnabled: true,
        dailyGoalMinutes: 30,
        difficultyPreference: 'adaptive',
        focusAreas: [],
      },

      // Actions
      setUser: (user) => set({ user: { ...get().user, ...user } }),

      setLearningProgress: (progress) =>
        set({ learningProgress: { ...get().learningProgress, ...progress } }),

      setStreak: (streak) => set({ streak: { ...get().streak, ...streak } }),

      setAIConfig: (config) =>
        set({ aiConfig: { ...get().aiConfig, ...config } }),

      setCurrentExercise: (exercise) => set({ currentExercise: exercise }),

      addExerciseToHistory: (exercise) =>
        set((state) => ({
          exerciseHistory: [exercise, ...state.exerciseHistory].slice(0, 50),
        })),

      addMistake: (mistake) =>
        set((state) => ({
          mistakes: [mistake, ...state.mistakes].slice(0, 100),
        })),

      updateVocabularyMastery: (wordId, mastery) =>
        set((state) => {
          const existing = state.vocabularyMastery.findIndex(
            (v) => v.wordId === wordId
          );
          if (existing >= 0) {
            const updated = [...state.vocabularyMastery];
            updated[existing] = { ...updated[existing], ...mastery };
            return { vocabularyMastery: updated };
          } else {
            return {
              vocabularyMastery: [
                ...state.vocabularyMastery,
                { wordId, ...mastery },
              ],
            };
          }
        }),

      updateSettings: (settings) =>
        set({ settings: { ...get().settings, ...settings } }),

      resetProgress: () =>
        set({
          user: {
            id: 1,
            username: 'default_user',
            currentLevel: 'beginner',
            proficiencyScore: 0,
            hasCompletedAssessment: false,
          },
          learningProgress: {
            vocabulary: 0,
            grammar: 0,
            fluency: 0,
            context_usage: 0,
            writing_quality: 0,
          },
          streak: {
            current: 0,
            longest: 0,
            lastActivity: null,
          },
          exerciseHistory: [],
          vocabularyMastery: [],
          mistakes: [],
        }),
    }),
    {
      name: 'english-learning-storage',
      partialize: (state) => ({
        user: state.user,
        learningProgress: state.learningProgress,
        streak: state.streak,
        aiConfig: state.aiConfig,
        settings: state.settings,
        exerciseHistory: state.exerciseHistory.slice(0, 20), // Only persist recent
        vocabularyMastery: state.vocabularyMastery,
        mistakes: state.mistakes.slice(0, 50), // Only persist recent
      }),
    }
  )
);

export default useAppStore;
