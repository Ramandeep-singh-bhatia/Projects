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
