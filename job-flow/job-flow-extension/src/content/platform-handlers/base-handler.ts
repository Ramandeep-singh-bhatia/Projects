/**
 * Base Platform Handler
 * Abstract class that all platform-specific handlers extend
 */

import { FormDetector } from '../form-detector';
import { FieldMapper } from '../field-mapper';
import { backendClient } from '../../shared/api/backend-client';
import { contentLogger as logger } from '../../shared/utils/logger';
import type { FormField, UserProfile, QuestionMatch } from '../../shared/types';

export abstract class BasePlatformHandler {
  protected formDetector: FormDetector;
  protected fieldMapper: FieldMapper;
  protected userProfile: UserProfile | null = null;

  constructor() {
    this.formDetector = new FormDetector();
    this.fieldMapper = new FieldMapper();
  }

  /**
   * Set user profile
   */
  setUserProfile(profile: UserProfile): void {
    this.userProfile = profile;
  }

  /**
   * Detect if this handler can handle the current page
   */
  abstract canHandle(): boolean;

  /**
   * Get platform name
   */
  abstract getPlatformName(): string;

  /**
   * Detect form fields specific to this platform
   */
  abstract detectFormFields(): FormField[];

  /**
   * Fill a single field with human-like behavior
   */
  async fillField(field: FormField, value: any): Promise<boolean> {
    try {
      if (!field.element) {
        logger.warn('No element found for field:', field.label);
        return false;
      }

      const element = field.element as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;

      // Special handling for different field types
      if (element instanceof HTMLSelectElement) {
        return await this.fillSelectField(element, value);
      }

      if (element.type === 'checkbox') {
        return await this.fillCheckboxField(element as HTMLInputElement, value);
      }

      if (element.type === 'radio') {
        return await this.fillRadioField(element as HTMLInputElement, value);
      }

      if (element.type === 'file') {
        logger.info('File upload fields require manual handling:', field.label);
        return false;
      }

      // Standard text/textarea input
      return await this.fillTextInput(element, value);
    } catch (error) {
      logger.error('Failed to fill field:', field.label, error);
      return false;
    }
  }

  /**
   * Fill text input or textarea
   */
  protected async fillTextInput(
    element: HTMLInputElement | HTMLTextAreaElement,
    value: any
  ): Promise<boolean> {
    const stringValue = String(value);

    // Clear existing value
    element.value = '';
    element.dispatchEvent(new Event('input', { bubbles: true }));

    // Type value character by character for realism
    for (let i = 0; i < stringValue.length; i++) {
      element.value += stringValue[i];
      element.dispatchEvent(new Event('input', { bubbles: true }));
      await this.humanDelay(50, 100); // 50-100ms per character
    }

    // Trigger change event
    element.dispatchEvent(new Event('change', { bubbles: true }));
    element.dispatchEvent(new Event('blur', { bubbles: true }));

    // Visual feedback
    this.highlightField(element, '#D1FAE5'); // Green

    return true;
  }

  /**
   * Fill select/dropdown field
   */
  protected async fillSelectField(element: HTMLSelectElement, value: any): Promise<boolean> {
    const stringValue = String(value).toLowerCase();

    // Try exact match first
    for (let i = 0; i < element.options.length; i++) {
      const option = element.options[i];
      if (option.value.toLowerCase() === stringValue ||
          option.text.toLowerCase() === stringValue) {
        element.selectedIndex = i;
        element.dispatchEvent(new Event('change', { bubbles: true }));
        this.highlightField(element, '#D1FAE5');
        return true;
      }
    }

    // Try partial match
    for (let i = 0; i < element.options.length; i++) {
      const option = element.options[i];
      if (option.value.toLowerCase().includes(stringValue) ||
          option.text.toLowerCase().includes(stringValue)) {
        element.selectedIndex = i;
        element.dispatchEvent(new Event('change', { bubbles: true }));
        this.highlightField(element, '#FEF3C7'); // Yellow (partial match)
        return true;
      }
    }

    logger.warn('No matching option found for select field:', value);
    return false;
  }

  /**
   * Fill checkbox field
   */
  protected async fillCheckboxField(element: HTMLInputElement, value: any): Promise<boolean> {
    const shouldCheck = this.parseBoolean(value);

    if (element.checked !== shouldCheck) {
      element.checked = shouldCheck;
      element.dispatchEvent(new Event('change', { bubbles: true }));
      element.dispatchEvent(new Event('click', { bubbles: true }));
      this.highlightField(element, '#D1FAE5');
    }

    return true;
  }

  /**
   * Fill radio field
   */
  protected async fillRadioField(element: HTMLInputElement, value: any): Promise<boolean> {
    const stringValue = String(value).toLowerCase();

    // Find all radio buttons with same name
    const radios = document.querySelectorAll(
      `input[type="radio"][name="${element.name}"]`
    ) as NodeListOf<HTMLInputElement>;

    for (const radio of radios) {
      const radioValue = radio.value.toLowerCase();
      const radioLabel = this.getRadioLabel(radio).toLowerCase();

      if (radioValue === stringValue || radioLabel === stringValue ||
          radioValue.includes(stringValue) || radioLabel.includes(stringValue)) {
        radio.checked = true;
        radio.dispatchEvent(new Event('change', { bubbles: true }));
        radio.dispatchEvent(new Event('click', { bubbles: true }));
        this.highlightField(radio, '#D1FAE5');
        return true;
      }
    }

    return false;
  }

  /**
   * Get label for radio button
   */
  protected getRadioLabel(radio: HTMLInputElement): string {
    const label = radio.labels?.[0];
    if (label) {
      return label.textContent?.trim() || '';
    }

    const parentLabel = radio.closest('label');
    if (parentLabel) {
      return parentLabel.textContent?.trim() || '';
    }

    return radio.value;
  }

  /**
   * Parse boolean from various formats
   */
  protected parseBoolean(value: any): boolean {
    if (typeof value === 'boolean') return value;
    const str = String(value).toLowerCase();
    return str === 'true' || str === 'yes' || str === '1';
  }

  /**
   * Highlight field with color
   */
  protected highlightField(element: HTMLElement, color: string): void {
    const originalBg = element.style.backgroundColor;
    element.style.backgroundColor = color;
    element.style.transition = 'background-color 0.3s ease';

    setTimeout(() => {
      element.style.backgroundColor = originalBg;
    }, 1500);
  }

  /**
   * Human-like delay
   */
  protected humanDelay(min: number, max: number): Promise<void> {
    const delay = Math.random() * (max - min) + min;
    return new Promise(resolve => setTimeout(resolve, delay));
  }

  /**
   * Fill all detected fields
   */
  async fillAllFields(fields: FormField[]): Promise<{ filled: number; total: number }> {
    let filledCount = 0;

    for (const field of fields) {
      // Get value from user profile or backend
      let value = this.fieldMapper.mapFieldToValue(field, this.userProfile);

      // If no direct mapping, try backend question matching
      if (value === null || value === undefined) {
        value = await this.matchQuestionFromBackend(field.label);
      }

      if (value !== null && value !== undefined) {
        const success = await this.fillField(field, value);
        if (success) {
          filledCount++;
        }

        // Human delay between fields
        await this.humanDelay(300, 800);
      }
    }

    return { filled: filledCount, total: fields.length };
  }

  /**
   * Match question from backend
   */
  protected async matchQuestionFromBackend(questionText: string): Promise<string | null> {
    try {
      const response = await backendClient.matchQuestion(questionText);
      if (response.data && response.data.answer && response.data.confidence >= 85) {
        logger.debug('Matched question from backend:', questionText, '→', response.data.answer);
        return response.data.answer;
      }
      return null;
    } catch (error) {
      logger.error('Failed to match question from backend:', error);
      return null;
    }
  }

  /**
   * Check if form has next button (multi-step)
   */
  hasNextButton(): boolean {
    const nextButtonSelectors = [
      'button[type="submit"]',
      'button:contains("Next")',
      'button:contains("Continue")',
      '[aria-label*="next"]',
      '[aria-label*="continue"]',
      '.next-button',
      '.continue-button'
    ];

    for (const selector of nextButtonSelectors) {
      const button = document.querySelector(selector);
      if (button) {
        const text = button.textContent?.toLowerCase() || '';
        if (text.includes('next') || text.includes('continue')) {
          return true;
        }
      }
    }

    return false;
  }

  /**
   * Click next button
   */
  async clickNext(): Promise<boolean> {
    const nextButtonSelectors = [
      'button[type="submit"]:not([type="button"])',
      'button:contains("Next")',
      'button:contains("Continue")',
      '[aria-label*="next"]',
      '.next-button',
      '.continue-button'
    ];

    for (const selector of nextButtonSelectors) {
      const buttons = Array.from(document.querySelectorAll(selector));

      for (const button of buttons) {
        const text = button.textContent?.toLowerCase() || '';
        const ariaLabel = button.getAttribute('aria-label')?.toLowerCase() || '';

        if (text.includes('next') || text.includes('continue') ||
            ariaLabel.includes('next') || ariaLabel.includes('continue')) {
          (button as HTMLButtonElement).click();
          return true;
        }
      }
    }

    return false;
  }

  /**
   * Wait for next step to load
   */
  async waitForNextStep(timeout: number = 3000): Promise<boolean> {
    return new Promise((resolve) => {
      const startTime = Date.now();

      const checkInterval = setInterval(() => {
        // Check if new form elements appeared
        const newInputs = document.querySelectorAll('input, textarea, select');

        if (newInputs.length > 0) {
          clearInterval(checkInterval);
          resolve(true);
        }

        if (Date.now() - startTime > timeout) {
          clearInterval(checkInterval);
          resolve(false);
        }
      }, 100);
    });
  }

  /**
   * Handle multi-step form
   */
  async handleMultiStepForm(): Promise<void> {
    let stepCount = 0;
    const maxSteps = 10; // Safety limit

    while (stepCount < maxSteps) {
      logger.info(`Processing step ${stepCount + 1}`);

      // Detect and fill current step
      const fields = this.detectFormFields();
      const result = await this.fillAllFields(fields);

      logger.info(`Step ${stepCount + 1}: Filled ${result.filled}/${result.total} fields`);

      // Check for next button
      if (!this.hasNextButton()) {
        logger.info('No next button found - final step');
        break;
      }

      // Click next
      await this.humanDelay(500, 1000);
      const clicked = await this.clickNext();

      if (!clicked) {
        logger.warn('Failed to click next button');
        break;
      }

      // Wait for next step
      const loaded = await this.waitForNextStep();

      if (!loaded) {
        logger.warn('Next step did not load');
        break;
      }

      stepCount++;
      await this.humanDelay(1000, 2000);
    }

    if (stepCount >= maxSteps) {
      logger.warn('Reached maximum step limit');
    }
  }

  /**
   * Get submit button
   */
  getSubmitButton(): HTMLButtonElement | null {
    const submitSelectors = [
      'button[type="submit"]',
      'input[type="submit"]',
      'button:contains("Submit")',
      'button:contains("Apply")',
      '[aria-label*="submit"]',
      '[aria-label*="apply"]'
    ];

    for (const selector of submitSelectors) {
      const buttons = Array.from(document.querySelectorAll(selector));

      for (const button of buttons) {
        const text = button.textContent?.toLowerCase() || '';
        const ariaLabel = button.getAttribute('aria-label')?.toLowerCase() || '';

        if (text.includes('submit') || text.includes('apply') ||
            ariaLabel.includes('submit') || ariaLabel.includes('apply')) {
          return button as HTMLButtonElement;
        }
      }
    }

    return null;
  }
}
