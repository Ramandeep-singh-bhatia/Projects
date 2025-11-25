/**
 * Background Service Worker
 * Coordinates extension operations and communicates with backend
 */

import { backgroundLogger as logger } from '../shared/utils/logger';
import { Storage } from '../shared/utils/storage';
import { backendClient } from '../shared/api/backend-client';
import { MessageType } from '../shared/types';
import type { Message, UserProfile, Question } from '../shared/types';

class BackgroundService {
  private userProfile: UserProfile | null = null;
  private questions: Question[] = [];
  private backendConnected: boolean = false;

  constructor() {
    logger.info('Background service worker initialized');
  }

  /**
   * Initialize the background service
   */
  async init(): Promise<void> {
    // Load settings and configure backend URL
    const settings = await Storage.initializeSettings();
    backendClient.setBaseURL(settings.backendUrl);

    // Check backend connection
    await this.checkBackendConnection();

    // Load user profile and questions if backend is connected
    if (this.backendConnected) {
      await this.loadUserProfile();
      await this.loadQuestions();
    }

    // Listen for messages
    chrome.runtime.onMessage.addListener(this.handleMessage.bind(this));

    // Setup periodic backend sync
    this.setupPeriodicSync();

    logger.info('Background service initialized');
  }

  /**
   * Check if backend is connected
   */
  private async checkBackendConnection(): Promise<void> {
    try {
      this.backendConnected = await backendClient.healthCheck();
      logger.info('Backend connection:', this.backendConnected ? 'OK' : 'Failed');

      if (this.backendConnected) {
        const info = await backendClient.getServerInfo();
        if (info.data) {
          logger.info('Backend server:', info.data);
        }
      }
    } catch (error) {
      logger.error('Backend connection check failed:', error);
      this.backendConnected = false;
    }
  }

  /**
   * Load user profile from backend
   */
  private async loadUserProfile(): Promise<void> {
    try {
      const response = await backendClient.getProfile();

      if (response.data) {
        this.userProfile = response.data;
        await Storage.setUserProfile(response.data);
        logger.info('User profile loaded');
      } else {
        logger.warn('No user profile found:', response.error);
        // Load from storage cache
        this.userProfile = await Storage.getUserProfile();
      }
    } catch (error) {
      logger.error('Failed to load user profile:', error);
      // Load from storage cache
      this.userProfile = await Storage.getUserProfile();
    }
  }

  /**
   * Load questions from backend
   */
  private async loadQuestions(): Promise<void> {
    try {
      const response = await backendClient.listQuestions({ limit: 200 });

      if (response.data) {
        this.questions = response.data;
        logger.info(`Loaded ${this.questions.length} questions`);
      } else {
        logger.warn('Failed to load questions:', response.error);
      }
    } catch (error) {
      logger.error('Failed to load questions:', error);
    }
  }

  /**
   * Setup periodic sync with backend
   */
  private setupPeriodicSync(): void {
    // Sync every 5 minutes
    setInterval(async () => {
      if (this.backendConnected) {
        await this.loadUserProfile();
        await this.loadQuestions();
      } else {
        await this.checkBackendConnection();
      }
    }, 5 * 60 * 1000);
  }

  /**
   * Handle messages from content script or popup
   */
  private async handleMessage(
    message: Message,
    sender: chrome.runtime.MessageSender,
    sendResponse: (response?: any) => void
  ): Promise<void> {
    logger.debug('Received message:', message.type);

    try {
      switch (message.type) {
        case MessageType.GET_PROFILE:
          sendResponse({
            success: true,
            data: this.userProfile,
            backendConnected: this.backendConnected,
          });
          break;

        case MessageType.GET_QUESTIONS:
          sendResponse({
            success: true,
            data: this.questions,
          });
          break;

        case MessageType.MATCH_QUESTION:
          await this.handleMatchQuestion(message.payload, sendResponse);
          break;

        case MessageType.FILL_FORM:
          await this.handleFillForm(message.payload, sender, sendResponse);
          break;

        case MessageType.SUBMIT_APPLICATION:
          await this.handleSubmitApplication(message.payload, sendResponse);
          break;

        case MessageType.LOG_APPLICATION:
          await this.handleLogApplication(message.payload, sendResponse);
          break;

        default:
          logger.warn('Unknown message type:', message.type);
          sendResponse({
            success: false,
            error: 'Unknown message type',
          });
      }
    } catch (error) {
      logger.error('Error handling message:', error);
      sendResponse({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }

  /**
   * Handle question matching request
   */
  private async handleMatchQuestion(
    payload: { questionText: string },
    sendResponse: (response: any) => void
  ): Promise<void> {
    try {
      const response = await backendClient.matchQuestion(payload.questionText);

      sendResponse({
        success: true,
        data: response.data,
      });
    } catch (error) {
      logger.error('Question matching failed:', error);
      sendResponse({
        success: false,
        error: 'Failed to match question',
      });
    }
  }

  /**
   * Handle fill form request
   */
  private async handleFillForm(
    payload: any,
    sender: chrome.runtime.MessageSender,
    sendResponse: (response: any) => void
  ): Promise<void> {
    if (!this.userProfile) {
      sendResponse({
        success: false,
        error: 'No user profile available. Please set up your profile first.',
      });
      return;
    }

    if (!sender.tab?.id) {
      sendResponse({
        success: false,
        error: 'No tab ID available',
      });
      return;
    }

    try {
      // Send profile data to content script to fill the form
      await chrome.tabs.sendMessage(sender.tab.id, {
        type: MessageType.FILL_FORM,
        payload: {
          profile: this.userProfile,
          questions: this.questions,
        },
      });

      sendResponse({
        success: true,
      });
    } catch (error) {
      logger.error('Fill form failed:', error);
      sendResponse({
        success: false,
        error: 'Failed to fill form',
      });
    }
  }

  /**
   * Handle submit application request
   */
  private async handleSubmitApplication(
    payload: any,
    sendResponse: (response: any) => void
  ): Promise<void> {
    // Application submission is handled by the content script
    // This is just for logging
    logger.info('Application submitted:', payload);
    sendResponse({ success: true });
  }

  /**
   * Handle log application request
   */
  private async handleLogApplication(
    payload: any,
    sendResponse: (response: any) => void
  ): Promise<void> {
    try {
      const response = await backendClient.createApplication(payload);

      if (response.data) {
        logger.info('Application logged successfully');
        sendResponse({
          success: true,
          data: response.data,
        });
      } else {
        logger.error('Failed to log application:', response.error);
        sendResponse({
          success: false,
          error: response.error,
        });
      }
    } catch (error) {
      logger.error('Failed to log application:', error);
      sendResponse({
        success: false,
        error: 'Failed to log application',
      });
    }
  }
}

// Initialize background service
const backgroundService = new BackgroundService();
backgroundService.init();

export {};
