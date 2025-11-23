export interface DailySummary {
  userId: number;
  date: string;
  totalCaloriesConsumed: number;
  totalCaloriesBurned: number;
  netCalories: number;
  totalProteinGrams: number;
  totalCarbsGrams: number;
  totalFatGrams: number;
  totalFiberGrams: number;
  workoutDurationMinutes: number;
  workoutCount: number;
  mealCount: number;
  targetCalories?: number;
  targetProtein?: number;
  targetCarbs?: number;
  targetFat?: number;
  calorieProgress?: number;
  proteinProgress?: number;
  carbsProgress?: number;
  fatProgress?: number;
}

export interface WeeklySummary {
  userId: number;
  weekStartDate: string;
  weekEndDate: string;
  averageCaloriesPerDay: number;
  averageProteinPerDay: number;
  averageCarbsPerDay: number;
  averageFatPerDay: number;
  totalWorkoutMinutes: number;
  totalWorkouts: number;
  averageWorkoutDuration: number;
  totalCaloriesBurned: number;
  dailySummaries: DailySummary[];
  weeklyGoalProgress: {
    calorieProgress: number;
    workoutProgress: number;
  };
}

export interface ProgressData {
  userId: number;
  currentWeight: number;
  targetWeight: number;
  startWeight: number;
  weightProgress: number;
  remainingKg: number;
  calorieGoal: {
    target: number;
    averageActual: number;
    progress: number;
  };
  workoutGoal: {
    targetWorkoutsPerWeek: number;
    actualWorkoutsThisWeek: number;
    progress: number;
  };
  macroGoals: {
    protein: MacroGoal;
    carbs: MacroGoal;
    fat: MacroGoal;
  };
  estimatedDaysToGoal?: number;
}

export interface MacroGoal {
  target: number;
  averageActual: number;
  progress: number;
}

export interface WeightEntry {
  date: string;
  weightKg: number;
}

export interface TrendData {
  date: string;
  value: number;
}

export interface DashboardData {
  dailySummary: DailySummary;
  weightTrend: TrendData[];
  caloriesTrend: {
    date: string;
    consumed: number;
    burned: number;
  }[];
  workoutFrequency: TrendData[];
  recentMeals: any[];
  recentWorkouts: any[];
}

export interface AnalyticsState {
  dashboardData: DashboardData | null;
  dailySummary: DailySummary | null;
  weeklySummary: WeeklySummary | null;
  progressData: ProgressData | null;
  loading: boolean;
  error: string | null;
}
