export enum TopicCategory {
  DSA = 'DSA',
  HLD = 'HLD',
  LLD = 'LLD',
  BEHAVIORAL = 'BEHAVIORAL',
}

export enum DifficultyLevel {
  EASY = 'EASY',
  MEDIUM = 'MEDIUM',
  HARD = 'HARD',
}

export enum SessionType {
  FIRST_LEARNING = 'FIRST_LEARNING',
  REVISION = 'REVISION',
  MOCK_INTERVIEW = 'MOCK_INTERVIEW',
  QUICK_REVIEW = 'QUICK_REVIEW',
}

export enum WeekStartDay {
  MONDAY = 'MONDAY',
  SUNDAY = 'SUNDAY',
}

export enum Theme {
  LIGHT = 'LIGHT',
  DARK = 'DARK',
  AUTO = 'AUTO',
}

export interface Topic {
  id?: number;
  topic: string;
  subtopic?: string;
  confidence: number;
  sourceUrl?: string;
  notes?: string;
  thingsToRemember?: string;
  createdDate?: string;
  lastModifiedDate?: string;
  lastStudiedDate?: string;
  category: TopicCategory;
  totalTimeSpent?: number;
  sessionCount?: number;
  practiceSessions?: PracticeSession[];
  files?: FileMetadata[];
}

export interface DSATopic extends Topic {
  difficulty: DifficultyLevel;
}

export interface HLDTopic extends Topic {
  pagesRead?: number;
}

export interface LLDTopic extends Topic {}

export interface BehavioralTopic extends Topic {
  questionCategory: string;
}

export interface PracticeSession {
  id?: number;
  sessionDate?: string;
  duration: number;
  performanceRating: number;
  whatWentWell?: string;
  mistakesMade?: string;
  sessionNotes?: string;
  sessionType: SessionType;
}

export interface FileMetadata {
  id?: number;
  fileName: string;
  filePath: string;
  fileType: string;
  fileSize: number;
  uploadDate?: string;
}

export interface Settings {
  id: number;
  dailyStudyHours: number;
  weeklyDsaGoal: number;
  weeklyHldGoal: number;
  weeklyLldGoal: number;
  weeklyBehavioralGoal: number;
  weekStartDay: WeekStartDay;
  theme: Theme;
  // Phase 2: Confidence Decay
  confidenceDecayEnabled: boolean;
  decayThresholdDays: number;
  decayIntervalDays: number;
  decayRate: number;
  decayRateEasy: number;
  decayRateMedium: number;
  decayRateHard: number;
  decayStopAtConfidence: number;
  applyDecayToNew: boolean;
  // Phase 2: Pomodoro
  pomodoroWorkDuration: number;
  pomodoroShortBreak: number;
  pomodoroLongBreak: number;
  pomodorosBeforeLongBreak: number;
  autoStartBreaks: boolean;
  autoStartPomodoros: boolean;
  soundEnabled: boolean;
  notificationsEnabled: boolean;
  tickingSoundEnabled: boolean;
}

export interface DashboardSuggestion {
  topicId: number;
  topic: string;
  subtopic?: string;
  category: TopicCategory;
  confidence: number;
  daysSinceLastStudied: number;
  estimatedTime: number;
  difficulty?: DifficultyLevel;
  priorityScore: number;
}

export interface WeeklyProgress {
  weekStartDate: string;
  weekEndDate: string;
  dsaGoal: number;
  dsaActual: number;
  hldGoal: number;
  hldActual: number;
  lldGoal: number;
  lldActual: number;
  behavioralGoal: number;
  behavioralActual: number;
  dsaStatus: string;
  hldStatus: string;
  lldStatus: string;
  behavioralStatus: string;
  dsaPercentage: number;
  hldPercentage: number;
  lldPercentage: number;
  behavioralPercentage: number;
}

export interface AnalyticsSummary {
  totalTopics: number;
  totalSessions: number;
  totalTimeSpent: number;
  averageConfidence: number;
  currentStreak: number;
  longestStreak: number;
  daysStudiedThisMonth: number;
  topicsByCategory: Record<string, number>;
  topicsByConfidenceLevel: Record<string, number>;
  timeByCategory: Record<string, number>;
  timeThisWeek: number;
  timeLastWeek: number;
  averageDailyTime: number;
}

// Phase 2 Types

export enum ChangeReason {
  PRACTICE_SESSION = 'PRACTICE_SESSION',
  DECAY = 'DECAY',
  MANUAL_UPDATE = 'MANUAL_UPDATE',
  INITIAL = 'INITIAL',
}

export enum PomodoroPhase {
  WORK = 'WORK',
  SHORT_BREAK = 'SHORT_BREAK',
  LONG_BREAK = 'LONG_BREAK',
}

export enum StudyPlanItemType {
  NEW_TOPIC = 'NEW_TOPIC',
  REVISION = 'REVISION',
  REST = 'REST',
  CONSOLIDATION = 'CONSOLIDATION',
}

export interface ConfidenceHistory {
  id?: number;
  changeDate: string;
  oldConfidence: number;
  newConfidence: number;
  changeReason: ChangeReason;
  notes?: string;
}

export interface Pomodoro {
  id?: number;
  startTime: string;
  endTime?: string;
  duration: number;
  phase: PomodoroPhase;
  completed: boolean;
  pomodoroNumber?: number;
  notes?: string;
}

export interface MockInterview {
  id?: number;
  startTime: string;
  endTime?: string;
  plannedDuration: number;
  actualDuration?: number;
  questionCount: number;
  overallPerformance?: number;
  overallConfidence?: number;
  generalNotes?: string;
  pressureLevel?: number;
  completed: boolean;
  questions?: MockInterviewQuestion[];
}

export interface MockInterviewQuestion {
  id?: number;
  questionNumber: number;
  timeSpent: number;
  performanceRating?: number;
  whatWentWell?: string;
  whatNeedsImprovement?: string;
  couldSolveInRealInterview?: boolean;
  scratchpadContent?: string;
  topic?: Topic;
}

export interface StudyPlan {
  id?: number;
  name: string;
  interviewDate: string;
  startDate: string;
  daysAvailable: number;
  hoursPerDay: number;
  priorityFocus: string;
  topicSelection: string;
  createdDate?: string;
  lastModifiedDate?: string;
  active: boolean;
  items?: StudyPlanItem[];
  totalTopics?: number;
  completedTopics?: number;
}

export interface StudyPlanItem {
  id?: number;
  scheduledDate: string;
  itemType: StudyPlanItemType;
  estimatedMinutes: number;
  displayOrder: number;
  completed: boolean;
  actualMinutesSpent?: number;
  notes?: string;
  topic?: Topic;
}

export interface EnhancedAnalytics {
  overallEfficiency: number;
  efficiencyByCategory: Record<string, number>;
  mostEfficientTopics: Array<{topicName: string; category: string; efficiency: number}>;
  leastEfficientTopics: Array<{topicName: string; category: string; efficiency: number}>;
  optimalDuration: number;
  performanceByDuration: Record<number, number>;
  bestTimeOfDay: string;
  performanceByHour: Record<string, number>;
  revisionEffectiveness: number;
  averageLearningRating: number;
  averageRevisionRating: number;
  readinessScore: number;
  readinessComponents: Record<string, number>;
  categoryReadiness: Record<string, number>;
  actionableInsights: string[];
  thisMonthVsLast: Record<string, any>;
  achievements: Array<Record<string, any>>;
  nextMilestone: Record<string, any>;
  sessionSuccessRate: number;
  successRateByCategory: Record<string, number>;
  learningVelocity: number;
}
