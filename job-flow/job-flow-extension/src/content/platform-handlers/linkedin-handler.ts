/**
 * LinkedIn Easy Apply Handler
 * Handles LinkedIn's Easy Apply modal and multi-step forms
 */

import { BasePlatformHandler } from './base-handler';
import { FieldType } from '../../shared/types';
import type { FormField } from '../../shared/types';
import { contentLogger as logger } from '../../shared/utils/logger';

export class LinkedInEasyApplyHandler extends BasePlatformHandler {
  private modalSelector = '.jobs-easy-apply-modal';
  private formSelector = 'form.jobs-easy-apply-form-section__grouping';

  /**
   * Check if we can handle this page
   */
  canHandle(): boolean {
    return window.location.hostname.includes('linkedin.com') &&
           this.hasEasyApplyModal();
  }

  /**
   * Get platform name
   */
  getPlatformName(): string {
    return 'LinkedIn Easy Apply';
  }

  /**
   * Check if Easy Apply modal is present
   */
  private hasEasyApplyModal(): boolean {
    return !!document.querySelector(this.modalSelector);
  }

  /**
   * Detect form fields in LinkedIn modal
   */
  detectFormFields(): FormField[] {
    const fields: FormField[] = [];
    const modal = document.querySelector(this.modalSelector);

    if (!modal) {
      logger.warn('LinkedIn Easy Apply modal not found');
      return fields;
    }

    // LinkedIn uses specific field containers
    const fieldContainers = modal.querySelectorAll('.jobs-easy-apply-form-element');

    fieldContainers.forEach((container, index) => {
      const field = this.extractLinkedInField(container as HTMLElement, index);
      if (field) {
        fields.push(field);
      }
    });

    logger.info(`Detected ${fields.length} LinkedIn fields`);
    return fields;
  }

  /**
   * Extract field information from LinkedIn container
   */
  private extractLinkedInField(container: HTMLElement, index: number): FormField | null {
    // Find input element
    const input = container.querySelector('input, textarea, select') as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;

    if (!input) {
      return null;
    }

    // Skip hidden fields
    if (input.type === 'hidden' || input.style.display === 'none') {
      return null;
    }

    // Get label
    const label = this.getLinkedInLabel(container, input);

    // Determine field type
    const fieldType = this.detectLinkedInFieldType(input);

    const field: FormField = {
      id: input.id || `linkedin_field_${index}`,
      name: input.name || input.id || `field_${index}`,
      label: label,
      type: fieldType,
      required: input.required || input.getAttribute('aria-required') === 'true',
      element: input,
      selector: this.generateLinkedInSelector(input),
    };

    // Get placeholder
    if (input instanceof HTMLInputElement || input instanceof HTMLTextAreaElement) {
      field.placeholder = input.placeholder;
    }

    // Get options for select
    if (input instanceof HTMLSelectElement) {
      field.options = Array.from(input.options).map(opt => opt.text);
    }

    return field;
  }

  /**
   * Get label for LinkedIn field
   */
  private getLinkedInLabel(container: HTMLElement, input: HTMLElement): string {
    // Try label element
    const labelElement = container.querySelector('label');
    if (labelElement) {
      return this.cleanText(labelElement.textContent || '');
    }

    // Try aria-label
    const ariaLabel = input.getAttribute('aria-label');
    if (ariaLabel) {
      return this.cleanText(ariaLabel);
    }

    // Try data-test-form-element-label
    const dataLabel = container.querySelector('[data-test-form-element-label]');
    if (dataLabel) {
      return this.cleanText(dataLabel.textContent || '');
    }

    // Try placeholder
    if (input instanceof HTMLInputElement || input instanceof HTMLTextAreaElement) {
      if (input.placeholder) {
        return this.cleanText(input.placeholder);
      }
    }

    // Fallback to container text
    return this.cleanText(container.textContent || '').substring(0, 50);
  }

  /**
   * Detect LinkedIn-specific field types
   */
  private detectLinkedInFieldType(element: HTMLElement): FieldType {
    if (element instanceof HTMLSelectElement) {
      return FieldType.SELECT;
    }

    if (element instanceof HTMLTextAreaElement) {
      return FieldType.TEXTAREA;
    }

    if (element instanceof HTMLInputElement) {
      const type = element.type.toLowerCase();
      const className = element.className.toLowerCase();
      const ariaLabel = element.getAttribute('aria-label')?.toLowerCase() || '';

      // Phone detection
      if (type === 'tel' || ariaLabel.includes('phone') || className.includes('phone')) {
        return FieldType.PHONE;
      }

      // Email detection
      if (type === 'email' || ariaLabel.includes('email')) {
        return FieldType.EMAIL;
      }

      // File upload (resume, cover letter)
      if (type === 'file') {
        return FieldType.FILE;
      }

      // Radio buttons
      if (type === 'radio') {
        return FieldType.RADIO;
      }

      // Checkboxes
      if (type === 'checkbox') {
        return FieldType.CHECKBOX;
      }

      // Number fields
      if (type === 'number' || ariaLabel.includes('years') || ariaLabel.includes('salary')) {
        return FieldType.NUMBER;
      }

      return FieldType.TEXT;
    }

    return FieldType.TEXT;
  }

  /**
   * Generate CSS selector for LinkedIn field
   */
  private generateLinkedInSelector(input: HTMLElement): string {
    if (input.id) {
      return `#${input.id}`;
    }

    const name = input.getAttribute('name');
    if (name) {
      return `input[name="${name}"]`;
    }

    // LinkedIn-specific data attributes
    const dataTestId = input.getAttribute('data-test-text-entity-list-form-component');
    if (dataTestId) {
      return `[data-test-text-entity-list-form-component="${dataTestId}"]`;
    }

    return 'input'; // Fallback
  }

  /**
   * Check if modal has next button
   */
  hasNextButton(): boolean {
    const modal = document.querySelector(this.modalSelector);
    if (!modal) return false;

    // LinkedIn uses specific button classes
    const nextButton = modal.querySelector('button[aria-label*="Continue"], button[aria-label*="next"], button.artdeco-button--primary');
    if (!nextButton) return false;

    const buttonText = nextButton.textContent?.toLowerCase() || '';
    const ariaLabel = nextButton.getAttribute('aria-label')?.toLowerCase() || '';

    return buttonText.includes('next') || buttonText.includes('continue') ||
           ariaLabel.includes('next') || ariaLabel.includes('continue') ||
           buttonText.includes('review');
  }

  /**
   * Click next button in LinkedIn modal
   */
  async clickNext(): Promise<boolean> {
    const modal = document.querySelector(this.modalSelector);
    if (!modal) return false;

    // Try primary action button
    const primaryButton = modal.querySelector('button.artdeco-button--primary') as HTMLButtonElement;
    if (primaryButton) {
      const buttonText = primaryButton.textContent?.toLowerCase() || '';
      if (!buttonText.includes('submit') && !buttonText.includes('apply')) {
        primaryButton.click();
        logger.info('Clicked LinkedIn next button');
        return true;
      }
    }

    // Try by aria-label
    const buttons = modal.querySelectorAll('button');
    for (const button of buttons) {
      const ariaLabel = button.getAttribute('aria-label')?.toLowerCase() || '';
      const text = button.textContent?.toLowerCase() || '';

      if ((ariaLabel.includes('continue') || ariaLabel.includes('next') ||
           text.includes('continue') || text.includes('next')) &&
          !text.includes('submit') && !text.includes('apply')) {
        (button as HTMLButtonElement).click();
        logger.info('Clicked LinkedIn next button');
        return true;
      }
    }

    return false;
  }

  /**
   * Get submit button
   */
  getSubmitButton(): HTMLButtonElement | null {
    const modal = document.querySelector(this.modalSelector);
    if (!modal) return null;

    // LinkedIn submit button
    const submitButton = modal.querySelector('button[aria-label*="Submit application"], button.artdeco-button--primary') as HTMLButtonElement;

    if (submitButton) {
      const text = submitButton.textContent?.toLowerCase() || '';
      const ariaLabel = submitButton.getAttribute('aria-label')?.toLowerCase() || '';

      if (text.includes('submit') || text.includes('apply') ||
          ariaLabel.includes('submit') || ariaLabel.includes('apply')) {
        return submitButton;
      }
    }

    return null;
  }

  /**
   * Wait for next step in LinkedIn modal
   */
  async waitForNextStep(timeout: number = 5000): Promise<boolean> {
    return new Promise((resolve) => {
      const startTime = Date.now();
      const modal = document.querySelector(this.modalSelector);

      if (!modal) {
        resolve(false);
        return;
      }

      const observer = new MutationObserver(() => {
        const newFields = modal.querySelectorAll('.jobs-easy-apply-form-element');
        if (newFields.length > 0) {
          observer.disconnect();
          resolve(true);
        }
      });

      observer.observe(modal, {
        childList: true,
        subtree: true,
      });

      setTimeout(() => {
        observer.disconnect();
        resolve(false);
      }, timeout);
    });
  }

  /**
   * Handle LinkedIn file upload (resume/cover letter)
   */
  async handleFileUpload(field: FormField, resumeId?: number): Promise<boolean> {
    logger.info('File upload detected:', field.label);

    // LinkedIn auto-attaches resume from profile
    // Check if resume is already attached
    const modal = document.querySelector(this.modalSelector);
    if (!modal) return false;

    const attachedFile = modal.querySelector('.jobs-document-upload__file-name');
    if (attachedFile) {
      logger.info('Resume already attached:', attachedFile.textContent);
      return true;
    }

    // If no resume attached, user needs to manually upload
    // We can't programmatically trigger file upload for security reasons
    logger.warn('No resume attached - manual upload required');
    return false;
  }

  /**
   * Clean text
   */
  private cleanText(text: string): string {
    return text
      .trim()
      .replace(/\s+/g, ' ')
      .replace(/\*/g, '')
      .replace(/:/g, '')
      .replace(/\n/g, ' ')
      .trim();
  }

  /**
   * Close LinkedIn modal
   */
  closeModal(): void {
    const closeButton = document.querySelector(`${this.modalSelector} button[aria-label*="Dismiss"]`) as HTMLButtonElement;
    if (closeButton) {
      closeButton.click();
    }
  }

  /**
   * Check if on final step (review page)
   */
  isReviewStep(): boolean {
    const modal = document.querySelector(this.modalSelector);
    if (!modal) return false;

    const reviewText = modal.textContent?.toLowerCase() || '';
    return reviewText.includes('review your application') ||
           reviewText.includes('review and submit');
  }

  /**
   * Handle complete LinkedIn Easy Apply flow
   */
  async handleCompleteFlow(): Promise<{ success: boolean; stepsCompleted: number }> {
    logger.info('Starting LinkedIn Easy Apply flow');

    if (!this.canHandle()) {
      logger.error('Cannot handle this page - not LinkedIn Easy Apply');
      return { success: false, stepsCompleted: 0 };
    }

    let stepsCompleted = 0;
    const maxSteps = 10;

    try {
      while (stepsCompleted < maxSteps) {
        logger.info(`Processing LinkedIn step ${stepsCompleted + 1}`);

        // Detect and fill current step
        const fields = this.detectFormFields();
        logger.info(`Found ${fields.length} fields in current step`);

        if (fields.length === 0) {
          logger.warn('No fields found in current step');
          break;
        }

        const result = await this.fillAllFields(fields);
        logger.info(`Filled ${result.filled}/${result.total} fields`);

        stepsCompleted++;

        // Check if this is the review/final step
        if (this.isReviewStep()) {
          logger.info('Reached review step - stopping before submit');
          return { success: true, stepsCompleted };
        }

        // Check for next button
        if (!this.hasNextButton()) {
          logger.info('No next button found - assuming final step');
          return { success: true, stepsCompleted };
        }

        // Wait before clicking next
        await this.humanDelay(800, 1500);

        // Click next
        const clicked = await this.clickNext();
        if (!clicked) {
          logger.warn('Failed to click next button');
          return { success: false, stepsCompleted };
        }

        // Wait for next step to load
        const loaded = await this.waitForNextStep();
        if (!loaded) {
          logger.warn('Next step did not load');
          return { success: false, stepsCompleted };
        }

        // Small delay before processing next step
        await this.humanDelay(1000, 2000);
      }

      if (stepsCompleted >= maxSteps) {
        logger.warn('Reached maximum step limit');
        return { success: false, stepsCompleted };
      }

      return { success: true, stepsCompleted };
    } catch (error) {
      logger.error('Error in LinkedIn Easy Apply flow:', error);
      return { success: false, stepsCompleted };
    }
  }
}
