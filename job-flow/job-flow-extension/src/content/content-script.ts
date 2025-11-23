/**
 * Content Script - Main entry point
 * Runs on job application pages to detect and fill forms
 */

import { contentLogger as logger } from '../shared/utils/logger';
import { PlatformType, MessageType } from '../shared/types';
import type { FormField, Message } from '../shared/types';
import { FormDetector } from './form-detector';
import { FieldMapper } from './field-mapper';

class ContentScript {
  private formDetector: FormDetector;
  private fieldMapper: FieldMapper;
  private currentPlatform: PlatformType = PlatformType.UNKNOWN;
  private isActive: boolean = false;

  constructor() {
    this.formDetector = new FormDetector();
    this.fieldMapper = new FieldMapper();

    logger.info('Content script initialized');
  }

  /**
   * Initialize the content script
   */
  async init(): Promise<void> {
    // Detect platform
    this.currentPlatform = this.detectPlatform();
    logger.info('Detected platform:', this.currentPlatform);

    // Listen for messages from background script
    chrome.runtime.onMessage.addListener(this.handleMessage.bind(this));

    // Watch for form changes
    this.watchForForms();

    // Add keyboard shortcuts
    this.setupKeyboardShortcuts();

    // Initial form detection
    await this.detectAndProcessForm();
  }

  /**
   * Detect which platform we're on
   */
  private detectPlatform(): PlatformType {
    const url = window.location.href;
    const hostname = window.location.hostname;

    if (hostname.includes('linkedin.com')) {
      // Check if it's Easy Apply
      if (document.querySelector('.jobs-easy-apply-modal') ||
          document.querySelector('[data-test-modal-id="easy-apply-modal"]')) {
        return PlatformType.LINKEDIN_EASY_APPLY;
      }
      return PlatformType.LINKEDIN_EXTERNAL;
    }

    if (hostname.includes('myworkdayjobs.com')) {
      return PlatformType.WORKDAY;
    }

    if (hostname.includes('greenhouse.io')) {
      return PlatformType.GREENHOUSE;
    }

    if (hostname.includes('lever.co')) {
      return PlatformType.LEVER;
    }

    if (hostname.includes('taleo.net')) {
      return PlatformType.TALEO;
    }

    if (hostname.includes('icims.com')) {
      return PlatformType.ICIMS;
    }

    // Check for common form indicators
    if (this.hasJobApplicationForm()) {
      return PlatformType.UNKNOWN;
    }

    return PlatformType.UNKNOWN;
  }

  /**
   * Check if page has a job application form
   */
  private hasJobApplicationForm(): boolean {
    // Look for common job application indicators
    const indicators = [
      'application', 'apply', 'resume', 'cv',
      'first name', 'last name', 'email',
      'work authorization', 'years of experience'
    ];

    const pageText = document.body.innerText.toLowerCase();
    return indicators.some(indicator => pageText.includes(indicator));
  }

  /**
   * Watch for form changes (dynamic content)
   */
  private watchForForms(): void {
    const observer = new MutationObserver((mutations) => {
      // Check if new forms or inputs were added
      const hasNewForm = mutations.some(mutation =>
        Array.from(mutation.addedNodes).some(node =>
          node instanceof HTMLElement && (
            node.tagName === 'FORM' ||
            node.querySelector('form') ||
            node.querySelector('input')
          )
        )
      );

      if (hasNewForm) {
        logger.debug('New form detected via mutation observer');
        this.detectAndProcessForm();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }

  /**
   * Detect and process form on current page
   */
  private async detectAndProcessForm(): Promise<void> {
    logger.time('Form detection');

    const forms = this.formDetector.detectForms();

    if (forms.length === 0) {
      logger.debug('No forms detected');
      return;
    }

    logger.info(`Detected ${forms.length} form(s)`);

    // For now, process the first form
    const form = forms[0];
    const fields = this.formDetector.extractFields(form);

    logger.info(`Extracted ${fields.length} fields`);
    logger.timeEnd('Form detection');

    // Show notification to user
    this.showDetectionNotification(fields.length);

    // Store detected fields
    await this.storeDetectedFields(fields);
  }

  /**
   * Store detected fields for popup
   */
  private async storeDetectedFields(fields: FormField[]): Promise<void> {
    try {
      await chrome.storage.local.set({
        detected_fields: fields,
        detected_platform: this.currentPlatform,
        detected_url: window.location.href,
        detected_at: new Date().toISOString(),
      });
    } catch (error) {
      logger.error('Failed to store detected fields:', error);
    }
  }

  /**
   * Show notification that form was detected
   */
  private showDetectionNotification(fieldCount: number): void {
    // Create notification element
    const notification = document.createElement('div');
    notification.id = 'jobflow-notification';
    notification.innerHTML = `
      <div style="
        position: fixed;
        top: 20px;
        right: 20px;
        background: #10B981;
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 14px;
        font-weight: 500;
        animation: slideIn 0.3s ease-out;
      ">
        ✓ JobFlow detected ${fieldCount} form fields
        <br>
        <small style="opacity: 0.9; font-size: 12px;">
          Click extension icon to fill
        </small>
      </div>
      <style>
        @keyframes slideIn {
          from {
            transform: translateX(400px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      </style>
    `;

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      notification.remove();
    }, 5000);
  }

  /**
   * Setup keyboard shortcuts
   */
  private setupKeyboardShortcuts(): void {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + Shift + F - Fill form
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'F') {
        e.preventDefault();
        this.handleFillRequest();
      }
    });
  }

  /**
   * Handle fill request from user
   */
  private async handleFillRequest(): Promise<void> {
    logger.info('Fill request initiated');

    // Send message to background script to get data and fill
    chrome.runtime.sendMessage({
      type: MessageType.FILL_FORM,
      payload: {
        platform: this.currentPlatform,
        url: window.location.href,
      },
    });
  }

  /**
   * Handle messages from background script
   */
  private handleMessage(
    message: Message,
    sender: chrome.runtime.MessageSender,
    sendResponse: (response?: any) => void
  ): boolean | void {
    logger.debug('Received message:', message.type);

    switch (message.type) {
      case MessageType.FILL_FORM:
        this.fillForm(message.payload);
        sendResponse({ success: true });
        break;

      case MessageType.ERROR:
        logger.error('Error from background:', message.error);
        this.showError(message.error || 'An error occurred');
        sendResponse({ success: false });
        break;

      default:
        logger.warn('Unknown message type:', message.type);
    }
  }

  /**
   * Fill the form with provided data
   */
  private async fillForm(data: any): Promise<void> {
    logger.info('Filling form...');
    logger.time('Form fill');

    const forms = this.formDetector.detectForms();
    if (forms.length === 0) {
      this.showError('No form found on page');
      return;
    }

    const form = forms[0];
    const fields = this.formDetector.extractFields(form);

    let filledCount = 0;

    for (const field of fields) {
      const value = this.fieldMapper.mapFieldToValue(field, data);

      if (value !== null && value !== undefined) {
        const success = await this.fillField(field, value);
        if (success) filledCount++;
      }
    }

    logger.info(`Filled ${filledCount}/${fields.length} fields`);
    logger.timeEnd('Form fill');

    this.showSuccess(`Filled ${filledCount} fields!`);
  }

  /**
   * Fill a single field
   */
  private async fillField(field: FormField, value: any): Promise<boolean> {
    try {
      if (!field.element) return false;

      const element = field.element as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;

      // Set value
      element.value = String(value);

      // Trigger events to ensure the value is registered
      element.dispatchEvent(new Event('input', { bubbles: true }));
      element.dispatchEvent(new Event('change', { bubbles: true }));

      // Add visual indicator
      element.style.backgroundColor = '#D1FAE5';
      setTimeout(() => {
        element.style.backgroundColor = '';
      }, 1000);

      // Random delay to simulate human behavior
      await this.humanDelay(100, 300);

      return true;
    } catch (error) {
      logger.error('Failed to fill field:', field.label, error);
      return false;
    }
  }

  /**
   * Human-like delay
   */
  private humanDelay(min: number, max: number): Promise<void> {
    const delay = Math.random() * (max - min) + min;
    return new Promise(resolve => setTimeout(resolve, delay));
  }

  /**
   * Show success notification
   */
  private showSuccess(message: string): void {
    this.showNotification(message, '#10B981'); // Green
  }

  /**
   * Show error notification
   */
  private showError(message: string): void {
    this.showNotification(message, '#EF4444'); // Red
  }

  /**
   * Show notification
   */
  private showNotification(message: string, color: string): void {
    const notification = document.createElement('div');
    notification.innerHTML = `
      <div style="
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${color};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 14px;
        font-weight: 500;
      ">
        ${message}
      </div>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.remove();
    }, 3000);
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    const contentScript = new ContentScript();
    contentScript.init();
  });
} else {
  const contentScript = new ContentScript();
  contentScript.init();
}

export {};
