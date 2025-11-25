/**
 * Workday ATS Handler
 * Handles Workday's application system (myworkdayjobs.com)
 */

import { BasePlatformHandler } from './base-handler';
import { FieldType } from '../../shared/types';
import type { FormField } from '../../shared/types';
import { contentLogger as logger } from '../../shared/utils/logger';

export class WorkdayHandler extends BasePlatformHandler {
  /**
   * Check if we can handle this page
   */
  canHandle(): boolean {
    return window.location.hostname.includes('myworkdayjobs.com');
  }

  /**
   * Get platform name
   */
  getPlatformName(): string {
    return 'Workday';
  }

  /**
   * Detect form fields in Workday
   */
  detectFormFields(): FormField[] {
    const fields: FormField[] = [];

    // Workday uses specific data attributes
    const fieldContainers = document.querySelectorAll('[data-automation-id*="formField"]');

    fieldContainers.forEach((container, index) => {
      const field = this.extractWorkdayField(container as HTMLElement, index);
      if (field) {
        fields.push(field);
      }
    });

    // Also check for standard inputs not in automation containers
    if (fields.length === 0) {
      const inputs = document.querySelectorAll('input:not([type="hidden"]), textarea, select');
      inputs.forEach((input, index) => {
        if (this.isValidWorkdayInput(input as HTMLElement)) {
          const field = this.extractWorkdayField(input.parentElement as HTMLElement, index);
          if (field) {
            fields.push(field);
          }
        }
      });
    }

    logger.info(`Detected ${fields.length} Workday fields`);
    return fields;
  }

  /**
   * Check if input is valid Workday input
   */
  private isValidWorkdayInput(element: HTMLElement): boolean {
    if (element instanceof HTMLInputElement) {
      if (element.type === 'hidden' || element.disabled) {
        return false;
      }
    }

    const style = window.getComputedStyle(element);
    return style.display !== 'none' && style.visibility !== 'hidden';
  }

  /**
   * Extract field from Workday container
   */
  private extractWorkdayField(container: HTMLElement, index: number): FormField | null {
    // Find input element
    const input = container.querySelector('input:not([type="hidden"]), textarea, select') as
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;

    if (!input) {
      return null;
    }

    // Get label
    const label = this.getWorkdayLabel(container, input);

    // Determine field type
    const fieldType = this.detectWorkdayFieldType(input, container);

    const field: FormField = {
      id: input.id || `workday_field_${index}`,
      name: input.name || input.id || `field_${index}`,
      label: label,
      type: fieldType,
      required: this.isWorkdayFieldRequired(container, input),
      element: input,
      selector: this.generateWorkdaySelector(input),
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
   * Get label for Workday field
   */
  private getWorkdayLabel(container: HTMLElement, input: HTMLElement): string {
    // Try data-automation-label
    const automationLabel = container.querySelector('[data-automation-id*="label"]');
    if (automationLabel) {
      return this.cleanText(automationLabel.textContent || '');
    }

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

    // Try data-automation-label on input
    const inputAutomationLabel = input.getAttribute('data-automation-label');
    if (inputAutomationLabel) {
      return this.cleanText(inputAutomationLabel);
    }

    // Try placeholder
    if (input instanceof HTMLInputElement || input instanceof HTMLTextAreaElement) {
      if (input.placeholder) {
        return this.cleanText(input.placeholder);
      }
    }

    // Try previous sibling
    const prevSibling = container.previousElementSibling;
    if (prevSibling && prevSibling.tagName.toLowerCase() === 'label') {
      return this.cleanText(prevSibling.textContent || '');
    }

    return 'Unknown Field';
  }

  /**
   * Detect Workday field type
   */
  private detectWorkdayFieldType(element: HTMLElement, container: HTMLElement): FieldType {
    if (element instanceof HTMLSelectElement) {
      return FieldType.SELECT;
    }

    if (element instanceof HTMLTextAreaElement) {
      return FieldType.TEXTAREA;
    }

    if (element instanceof HTMLInputElement) {
      const type = element.type.toLowerCase();
      const automationId = element.getAttribute('data-automation-id')?.toLowerCase() || '';

      // Check automation ID for hints
      if (automationId.includes('phone')) {
        return FieldType.PHONE;
      }

      if (automationId.includes('email')) {
        return FieldType.EMAIL;
      }

      if (automationId.includes('file') || automationId.includes('upload')) {
        return FieldType.FILE;
      }

      if (automationId.includes('date')) {
        return FieldType.DATE;
      }

      // Standard type detection
      switch (type) {
        case 'email':
          return FieldType.EMAIL;
        case 'tel':
        case 'phone':
          return FieldType.PHONE;
        case 'number':
          return FieldType.NUMBER;
        case 'radio':
          return FieldType.RADIO;
        case 'checkbox':
          return FieldType.CHECKBOX;
        case 'file':
          return FieldType.FILE;
        case 'date':
          return FieldType.DATE;
        default:
          return FieldType.TEXT;
      }
    }

    return FieldType.TEXT;
  }

  /**
   * Check if Workday field is required
   */
  private isWorkdayFieldRequired(container: HTMLElement, input: HTMLElement): boolean {
    // Check input required attribute
    if (input instanceof HTMLInputElement ||
        input instanceof HTMLTextAreaElement ||
        input instanceof HTMLSelectElement) {
      if (input.required) {
        return true;
      }
    }

    // Check aria-required
    if (input.getAttribute('aria-required') === 'true') {
      return true;
    }

    // Check for required indicator in label
    const label = container.querySelector('label');
    if (label) {
      const labelText = label.textContent || '';
      if (labelText.includes('*') || labelText.toLowerCase().includes('required')) {
        return true;
      }
    }

    // Check data-automation-required
    const automationRequired = input.getAttribute('data-automation-required');
    if (automationRequired === 'true') {
      return true;
    }

    return false;
  }

  /**
   * Generate selector for Workday field
   */
  private generateWorkdaySelector(input: HTMLElement): string {
    // Prefer data-automation-id
    const automationId = input.getAttribute('data-automation-id');
    if (automationId) {
      return `[data-automation-id="${automationId}"]`;
    }

    if (input.id) {
      return `#${input.id}`;
    }

    const name = input.getAttribute('name');
    if (name) {
      return `[name="${name}"]`;
    }

    return 'input';
  }

  /**
   * Check for next button in Workday
   */
  hasNextButton(): boolean {
    // Workday uses specific button automation IDs
    const nextButton = document.querySelector('[data-automation-id*="bottom-navigation-next-button"]');
    if (nextButton) return true;

    // Also check for buttons with "Next" text
    const buttons = document.querySelectorAll('button');
    for (const button of buttons) {
      const text = button.textContent?.toLowerCase() || '';
      if (text.includes('next') || text.includes('continue')) {
        return true;
      }
    }

    return false;
  }

  /**
   * Click next button in Workday
   */
  async clickNext(): Promise<boolean> {
    // Try automation ID first
    const nextButton = document.querySelector('[data-automation-id*="bottom-navigation-next-button"]') as HTMLButtonElement;
    if (nextButton) {
      nextButton.click();
      logger.info('Clicked Workday next button');
      return true;
    }

    // Try buttons with "Next" text
    const buttons = document.querySelectorAll('button');
    for (const button of buttons) {
      const text = button.textContent?.toLowerCase() || '';
      if (text.includes('next') || text.includes('continue')) {
        (button as HTMLButtonElement).click();
        logger.info('Clicked Workday next button');
        return true;
      }
    }

    return false;
  }

  /**
   * Get submit button
   */
  getSubmitButton(): HTMLButtonElement | null {
    // Workday submit button
    const submitButton = document.querySelector('[data-automation-id*="bottom-navigation-submit-button"]') as HTMLButtonElement;
    if (submitButton) {
      return submitButton;
    }

    // Look for button with "Submit" text
    const buttons = document.querySelectorAll('button');
    for (const button of buttons) {
      const text = button.textContent?.toLowerCase() || '';
      if (text.includes('submit') || text.includes('apply')) {
        return button as HTMLButtonElement;
      }
    }

    return null;
  }

  /**
   * Wait for next step in Workday
   */
  async waitForNextStep(timeout: number = 5000): Promise<boolean> {
    return new Promise((resolve) => {
      const startTime = Date.now();

      const checkInterval = setInterval(() => {
        // Check for new form fields
        const newFields = document.querySelectorAll('[data-automation-id*="formField"]');

        if (newFields.length > 0) {
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
   * Handle Workday file upload
   */
  async handleFileUpload(field: FormField, resumeId?: number): Promise<boolean> {
    logger.info('Workday file upload detected:', field.label);

    // Workday typically has resume attached from profile
    // Check for already uploaded file
    const uploadedFile = document.querySelector('[data-automation-id*="file-upload-item"]');
    if (uploadedFile) {
      logger.info('File already uploaded');
      return true;
    }

    logger.warn('File upload requires manual intervention');
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
      .trim();
  }

  /**
   * Check if on review page
   */
  isReviewPage(): boolean {
    const pageText = document.body.textContent?.toLowerCase() || '';
    return pageText.includes('review your application') ||
           pageText.includes('review and submit') ||
           !!document.querySelector('[data-automation-id*="review"]');
  }
}
