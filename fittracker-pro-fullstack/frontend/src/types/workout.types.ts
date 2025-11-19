import { MuscleGroup, DifficultyLevel, WorkoutStatus } from './common.types';

export interface ExerciseCategory {
  id: number;
  name: string;
  description: string;
  createdAt: string;
}

export interface Exercise {
  id: number;
  name: string;
  description: string;
  category: ExerciseCategory;
  muscleGroup: MuscleGroup;
  difficultyLevel: DifficultyLevel;
  equipmentNeeded: string;
  isVerified: boolean;
  instructions: string;
  caloriesPerMinute: number;
  createdAt: string;
  updatedAt: string;
}

export interface WorkoutExercise {
  id: number;
  workoutId: number;
  exercise: Exercise;
  exerciseOrder: number;
  plannedSets?: number;
  plannedReps?: number;
  plannedDurationSeconds?: number;
  actualSets?: number;
  actualReps?: number;
  actualDurationSeconds?: number;
  weightKg?: number;
  caloriesBurned: number;
  createdAt: string;
}

export interface Workout {
  id: number;
  userId: number;
  workoutName: string;
  workoutDate: string;
  startTime: string;
  endTime?: string;
  totalDurationMinutes?: number;
  totalCaloriesBurned?: number;
  status: WorkoutStatus;
  notes?: string;
  exercises: WorkoutExercise[];
  createdAt: string;
  updatedAt: string;
}

export interface WorkoutExerciseRequest {
  exerciseId: number;
  plannedSets?: number;
  plannedReps?: number;
  plannedDurationSeconds?: number;
  actualSets?: number;
  actualReps?: number;
  actualDurationSeconds?: number;
  weightKg?: number;
}

export interface CreateWorkoutRequest {
  userId: number;
  workoutName: string;
  workoutDate: string;
  startTime: string;
  notes?: string;
  exercises: WorkoutExerciseRequest[];
}

export interface CompleteWorkoutRequest {
  endTime: string;
}

export interface UpdateWorkoutRequest {
  workoutName?: string;
  notes?: string;
  exercises?: WorkoutExerciseRequest[];
}

export interface WorkoutTemplate {
  id: number;
  name: string;
  description: string;
  estimatedDuration: number;
  difficultyLevel: DifficultyLevel;
  exercises: WorkoutExerciseRequest[];
  createdAt: string;
  updatedAt: string;
}

export interface WorkoutState {
  workouts: Workout[];
  currentWorkout: Workout | null;
  exercises: Exercise[];
  templates: WorkoutTemplate[];
  searchResults: Exercise[];
  loading: boolean;
  error: string | null;
}
