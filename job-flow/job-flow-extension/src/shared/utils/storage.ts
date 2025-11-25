/**
 * Chrome Storage Wrapper
 * Provides type-safe access to Chrome storage
 */

import type { StorageKey, Settings, UserProfile, Resume, Session } from '../types';

export class Storage {
  /**
   * Get item from storage
   */
  static async get<T>(key: StorageKey): Promise<T | null> {
    try {
      const result = await chrome.storage.local.get(key);
      return result[key] || null;
    } catch (error) {
      console.error(`Failed to get ${key} from storage:`, error);
      return null;
    }
  }

  /**
   * Set item in storage
   */
  static async set<T>(key: StorageKey, value: T): Promise<boolean> {
    try {
      await chrome.storage.local.set({ [key]: value });
      return true;
    } catch (error) {
      console.error(`Failed to set ${key} in storage:`, error);
      return false;
    }
  }

  /**
   * Remove item from storage
   */
  static async remove(key: StorageKey): Promise<boolean> {
    try {
      await chrome.storage.local.remove(key);
      return true;
    } catch (error) {
      console.error(`Failed to remove ${key} from storage:`, error);
      return false;
    }
  }

  /**
   * Clear all storage
   */
  static async clear(): Promise<boolean> {
    try {
      await chrome.storage.local.clear();
      return true;
    } catch (error) {
      console.error('Failed to clear storage:', error);
      return false;
    }
  }

  // ========== Typed Getters ==========

  static async getSettings(): Promise<Settings | null> {
    return this.get<Settings>(StorageKey.SETTINGS);
  }

  static async getUserProfile(): Promise<UserProfile | null> {
    return this.get<UserProfile>(StorageKey.USER_PROFILE);
  }

  static async getResumes(): Promise<Resume[] | null> {
    return this.get<Resume[]>(StorageKey.RESUMES);
  }

  static async getSession(): Promise<Session | null> {
    return this.get<Session>(StorageKey.SESSION);
  }

  static async getBackendUrl(): Promise<string> {
    const url = await this.get<string>(StorageKey.BACKEND_URL);
    return url || 'http://localhost:8000';
  }

  // ========== Typed Setters ==========

  static async setSettings(settings: Settings): Promise<boolean> {
    return this.set(StorageKey.SETTINGS, settings);
  }

  static async setUserProfile(profile: UserProfile): Promise<boolean> {
    return this.set(StorageKey.USER_PROFILE, profile);
  }

  static async setResumes(resumes: Resume[]): Promise<boolean> {
    return this.set(StorageKey.RESUMES, resumes);
  }

  static async setSession(session: Session): Promise<boolean> {
    return this.set(StorageKey.SESSION, session);
  }

  static async setBackendUrl(url: string): Promise<boolean> {
    return this.set(StorageKey.BACKEND_URL, url);
  }

  // ========== Default Settings ==========

  static getDefaultSettings(): Settings {
    return {
      backendUrl: 'http://localhost:8000',
      autoFillEnabled: true,
      showReviewInterface: true,
      keyboardShortcutsEnabled: true,
      notificationsEnabled: true,
    };
  }

  /**
   * Initialize settings if not exists
   */
  static async initializeSettings(): Promise<Settings> {
    const existing = await this.getSettings();
    if (existing) return existing;

    const defaultSettings = this.getDefaultSettings();
    await this.setSettings(defaultSettings);
    return defaultSettings;
  }
}
