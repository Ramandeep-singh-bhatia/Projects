// Common API response types
export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  content: T[];
  page: number;
  size: number;
  totalElements: number;
  totalPages: number;
  isFirst: boolean;
  isLast: boolean;
  hasNext: boolean;
  hasPrevious: boolean;
}

export interface ErrorResponse {
  success: false;
  message: string;
  data: null;
  timestamp: string;
  errors?: FieldError[];
}

export interface FieldError {
  field: string;
  message: string;
}

// Enums (using const objects instead of TypeScript enums for better compatibility)
export const Gender = {
  MALE: 'MALE',
  FEMALE: 'FEMALE',
  OTHER: 'OTHER',
  PREFER_NOT_TO_SAY: 'PREFER_NOT_TO_SAY'
} as const;
export type Gender = typeof Gender[keyof typeof Gender];

export const ActivityLevel = {
  SEDENTARY: 'SEDENTARY',
  LIGHTLY_ACTIVE: 'LIGHTLY_ACTIVE',
  MODERATELY_ACTIVE: 'MODERATELY_ACTIVE',
  VERY_ACTIVE: 'VERY_ACTIVE',
  EXTRA_ACTIVE: 'EXTRA_ACTIVE'
} as const;
export type ActivityLevel = typeof ActivityLevel[keyof typeof ActivityLevel];

export const FitnessGoal = {
  WEIGHT_LOSS: 'WEIGHT_LOSS',
  WEIGHT_GAIN: 'WEIGHT_GAIN',
  MUSCLE_GAIN: 'MUSCLE_GAIN',
  MAINTENANCE: 'MAINTENANCE'
} as const;
export type FitnessGoal = typeof FitnessGoal[keyof typeof FitnessGoal];

export const MealType = {
  BREAKFAST: 'BREAKFAST',
  LUNCH: 'LUNCH',
  DINNER: 'DINNER',
  SNACK: 'SNACK'
} as const;
export type MealType = typeof MealType[keyof typeof MealType];

export const MuscleGroup = {
  CHEST: 'CHEST',
  BACK: 'BACK',
  LEGS: 'LEGS',
  ARMS: 'ARMS',
  SHOULDERS: 'SHOULDERS',
  CORE: 'CORE',
  FULL_BODY: 'FULL_BODY'
} as const;
export type MuscleGroup = typeof MuscleGroup[keyof typeof MuscleGroup];

export const DifficultyLevel = {
  BEGINNER: 'BEGINNER',
  INTERMEDIATE: 'INTERMEDIATE',
  ADVANCED: 'ADVANCED'
} as const;
export type DifficultyLevel = typeof DifficultyLevel[keyof typeof DifficultyLevel];

export const WorkoutStatus = {
  IN_PROGRESS: 'IN_PROGRESS',
  COMPLETED: 'COMPLETED',
  CANCELLED: 'CANCELLED'
} as const;
export type WorkoutStatus = typeof WorkoutStatus[keyof typeof WorkoutStatus];
