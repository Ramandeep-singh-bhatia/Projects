/**
 * Shared TypeScript types and interfaces for JobFlow Extension
 */

// Platform types
export enum PlatformType {
  LINKEDIN_EASY_APPLY = 'linkedin_easy_apply',
  LINKEDIN_EXTERNAL = 'linkedin_external',
  WORKDAY = 'workday',
  GREENHOUSE = 'greenhouse',
  LEVER = 'lever',
  TALEO = 'taleo',
  ICIMS = 'icims',
  UNKNOWN = 'unknown',
}

// Field types
export enum FieldType {
  TEXT = 'text',
  EMAIL = 'email',
  PHONE = 'phone',
  NUMBER = 'number',
  SELECT = 'select',
  RADIO = 'radio',
  CHECKBOX = 'checkbox',
  TEXTAREA = 'textarea',
  FILE = 'file',
  DATE = 'date',
}

// Form field interface
export interface FormField {
  id: string;
  name: string;
  label: string;
  type: FieldType;
  required: boolean;
  value?: string | number | boolean;
  options?: string[]; // For select/radio fields
  placeholder?: string;
  element?: HTMLElement;
  selector?: string;
}

// User profile
export interface UserProfile {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country: string;
  work_authorized: boolean;
  requires_sponsorship: boolean;
  security_clearance: boolean;
  preferred_roles?: string[];
  preferred_locations?: string[];
  remote_preference?: string;
  min_salary?: number;
  max_salary?: number;
  total_years_experience?: number;
  current_title?: string;
  tech_skills?: Record<string, number>;
  notice_period_weeks: number;
  available_start_date?: string;
  professional_summary?: string;
}

// Resume
export interface Resume {
  id: number;
  user_id: number;
  name: string;
  file_path: string;
  file_format: string;
  file_size: number;
  is_master: boolean;
  focus_areas?: string[];
  keywords?: string[];
  technologies?: string[];
  times_used: number;
  success_rate: number;
}

// Question
export interface Question {
  id: number;
  user_id: number;
  question_text: string;
  answer: string;
  category?: string;
  field_type: string;
  keywords?: string[];
  variants?: string[];
  times_used: number;
  confidence_score: number;
  auto_learned: boolean;
  user_verified: boolean;
}

// Question match result
export interface QuestionMatch {
  answer?: string;
  confidence: number;
  matched_question?: string;
  question_id?: number;
  suggestions: Array<{
    question: string;
    answer: string;
    score: number;
    category?: string;
    question_id: number;
  }>;
}

// Application
export interface Application {
  id?: number;
  user_id: number;
  company: string;
  job_title: string;
  job_url: string;
  job_description?: string;
  job_location?: string;
  job_type?: string;
  salary_range?: string;
  platform: string;
  status: string;
  match_score?: number;
  match_reasons?: Record<string, any>;
  resume_id?: number;
  session_id?: string;
  time_to_fill?: number;
  time_to_review?: number;
  notes?: string;
  applied_at?: string;
}

// Prepared application (ready for review)
export interface PreparedApplication {
  job: {
    id?: number;
    title: string;
    company: string;
    url: string;
    description?: string;
    location?: string;
  };
  resume: {
    id?: number;
    name: string;
    path?: string;
  };
  fields: FormField[];
  answers: Record<string, string>;
  match_score: number;
  ready_for_review: boolean;
  estimated_time: string;
  sessionStats?: {
    submitted: number;
    skipped: number;
    timeElapsed: string;
  };
}

// Session tracking
export interface Session {
  session_id: string;
  started_at: string;
  applications_submitted: number;
  applications_skipped: number;
  total_time_seconds: number;
}

// Extension state
export interface ExtensionState {
  isEnabled: boolean;
  currentPlatform?: PlatformType;
  detectedFields: FormField[];
  filledFields: FormField[];
  currentApplication?: PreparedApplication;
  session?: Session;
  backendUrl: string;
  backendConnected: boolean;
}

// Messages between content script and background
export enum MessageType {
  // From content script to background
  FORM_DETECTED = 'form_detected',
  FILL_FORM = 'fill_form',
  SUBMIT_APPLICATION = 'submit_application',
  SKIP_APPLICATION = 'skip_application',

  // From background to content script
  FILL_RESPONSE = 'fill_response',
  ERROR = 'error',

  // Bidirectional
  GET_PROFILE = 'get_profile',
  GET_QUESTIONS = 'get_questions',
  MATCH_QUESTION = 'match_question',
  LOG_APPLICATION = 'log_application',
}

export interface Message {
  type: MessageType;
  payload?: any;
  error?: string;
}

// API responses
export interface APIResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

// Storage keys
export enum StorageKey {
  BACKEND_URL = 'backend_url',
  USER_PROFILE = 'user_profile',
  RESUMES = 'resumes',
  SESSION = 'session',
  SETTINGS = 'settings',
}

// Settings
export interface Settings {
  backendUrl: string;
  autoFillEnabled: boolean;
  showReviewInterface: boolean;
  keyboardShortcutsEnabled: boolean;
  notificationsEnabled: boolean;
  defaultResumeId?: number;
}
