/**
 * Lever ATS Handler
 * Handles Lever's application system (lever.co)
 */

import { BasePlatformHandler } from './base-handler';
import { FieldType } from '../../shared/types';
import type { FormField } from '../../shared/types';
import { contentLogger as logger } from '../../shared/utils/logger';

export class LeverHandler extends BasePlatformHandler {
  /**
   * Check if we can handle this page
   */
  canHandle(): boolean {
    return window.location.hostname.includes('lever.co') ||
           window.location.hostname.includes('jobs.lever.co');
  }

  /**
   * Get platform name
   */
  getPlatformName(): string {
    return 'Lever';
  }

  /**
   * Detect form fields in Lever
   */
  detectFormFields(): FormField[] {
    const fields: FormField[] = [];

    // Lever uses application-form class
    const form = document.querySelector('.application-form, form.job-apply-form');

    if (!form) {
      logger.warn('Lever application form not found');
      return fields;
    }

    // Lever field containers
    const fieldContainers = form.querySelectorAll('.application-question, .form-field');

    if (fieldContainers.length > 0) {
      fieldContainers.forEach((container, index) => {
        const field = this.extractLeverField(container as HTMLElement, index);
        if (field) {
          fields.push(field);
        }
      });
    } else {
      // Fallback to all inputs
      const inputs = form.querySelectorAll('input:not([type="hidden"]), textarea, select');
      inputs.forEach((input, index) => {
        const field = this.extractFieldFromInput(input as HTMLElement, index);
        if (field) {
          fields.push(field);
        }
      });
    }

    logger.info(`Detected ${fields.length} Lever fields`);
    return fields;
  }

  /**
   * Extract field from Lever container
   */
  private extractLeverField(container: HTMLElement, index: number): FormField | null {
    const input = container.querySelector('input:not([type="hidden"]), textarea, select') as
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;

    if (!input) {
      return null;
    }

    return this.extractFieldFromInput(input, index);
  }

  /**
   * Extract field from input element
   */
  private extractFieldFromInput(input: HTMLElement, index: number): FormField | null {
    if (!(input instanceof HTMLInputElement ||
          input instanceof HTMLTextAreaElement ||
          input instanceof HTMLSelectElement)) {
      return null;
    }

    // Skip hidden or disabled
    if (input instanceof HTMLInputElement) {
      if (input.type === 'hidden' || input.disabled) {
        return null;
      }
    }

    const label = this.getLeverLabel(input);
    const fieldType = this.detectLeverFieldType(input);

    const field: FormField = {
      id: input.id || `lever_field_${index}`,
      name: input.name || input.id || `field_${index}`,
      label: label,
      type: fieldType,
      required: this.isLeverFieldRequired(input),
      element: input,
      selector: this.generateLeverSelector(input),
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
   * Get label for Lever field
   */
  private getLeverLabel(input: HTMLElement): string {
    // Try associated label
    if (input.id) {
      const label = document.querySelector(`label[for="${input.id}"]`);
      if (label) {
        return this.cleanText(label.textContent || '');
      }
    }

    // Try parent container label
    const container = input.closest('.application-question, .form-field');
    if (container) {
      const label = container.querySelector('label, .application-label');
      if (label) {
        return this.cleanText(label.textContent || '');
      }

      // Try question text
      const questionText = container.querySelector('.application-question-text');
      if (questionText) {
        return this.cleanText(questionText.textContent || '');
      }
    }

    // Try parent label
    const parentLabel = input.closest('label');
    if (parentLabel) {
      const clone = parentLabel.cloneNode(true) as HTMLElement;
      const inputClone = clone.querySelector('input, textarea, select');
      if (inputClone) {
        inputClone.remove();
      }
      return this.cleanText(clone.textContent || '');
    }

    // Try aria-label
    const ariaLabel = input.getAttribute('aria-label');
    if (ariaLabel) {
      return this.cleanText(ariaLabel);
    }

    // Try placeholder
    if (input instanceof HTMLInputElement || input instanceof HTMLTextAreaElement) {
      if (input.placeholder) {
        return this.cleanText(input.placeholder);
      }
    }

    // Try name attribute
    const name = input.getAttribute('name');
    if (name) {
      return this.humanizeFieldName(name);
    }

    return 'Unknown Field';
  }

  /**
   * Detect Lever field type
   */
  private detectLeverFieldType(element: HTMLElement): FieldType {
    if (element instanceof HTMLSelectElement) {
      return FieldType.SELECT;
    }

    if (element instanceof HTMLTextAreaElement) {
      return FieldType.TEXTAREA;
    }

    if (element instanceof HTMLInputElement) {
      const type = element.type.toLowerCase();
      const name = element.name.toLowerCase();
      const className = element.className.toLowerCase();

      // Phone detection
      if (type === 'tel' || name.includes('phone') || className.includes('phone')) {
        return FieldType.PHONE;
      }

      // Email detection
      if (type === 'email' || name.includes('email') || className.includes('email')) {
        return FieldType.EMAIL;
      }

      // File upload
      if (type === 'file') {
        return FieldType.FILE;
      }

      // Standard types
      switch (type) {
        case 'date':
          return FieldType.DATE;
        case 'number':
          return FieldType.NUMBER;
        case 'radio':
          return FieldType.RADIO;
        case 'checkbox':
          return FieldType.CHECKBOX;
        default:
          return FieldType.TEXT;
      }
    }

    return FieldType.TEXT;
  }

  /**
   * Check if Lever field is required
   */
  private isLeverFieldRequired(input: HTMLElement): boolean {
    // Check required attribute
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

    // Check container for required class
    const container = input.closest('.application-question, .form-field');
    if (container) {
      if (container.classList.contains('required')) {
        return true;
      }

      // Check for asterisk in label
      const label = container.querySelector('label, .application-label');
      if (label) {
        const text = label.textContent || '';
        if (text.includes('*')) {
          return true;
        }
      }
    }

    return false;
  }

  /**
   * Generate selector for Lever field
   */
  private generateLeverSelector(input: HTMLElement): string {
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
   * Check for submit button
   */
  hasNextButton(): boolean {
    const submitButton = document.querySelector('.template-btn-submit, button[type="submit"], input[type="submit"]');
    return !!submitButton;
  }

  /**
   * Click submit button
   */
  async clickNext(): Promise<boolean> {
    const submitButton = document.querySelector('.template-btn-submit, button[type="submit"], input[type="submit"]') as HTMLButtonElement;
    if (submitButton) {
      submitButton.click();
      logger.info('Clicked Lever submit button');
      return true;
    }

    return false;
  }

  /**
   * Get submit button
   */
  getSubmitButton(): HTMLButtonElement | null {
    return document.querySelector('.template-btn-submit, button[type="submit"], input[type="submit"]') as HTMLButtonElement || null;
  }

  /**
   * Wait for form submission response
   */
  async waitForSubmissionResponse(timeout: number = 5000): Promise<boolean> {
    return new Promise((resolve) => {
      const startTime = Date.now();

      const checkInterval = setInterval(() => {
        // Check for success message
        const successMessage = document.querySelector('.application-confirmation, .success-message');
        if (successMessage) {
          clearInterval(checkInterval);
          resolve(true);
        }

        // Check for error message
        const errorMessage = document.querySelector('.application-error, .error-message');
        if (errorMessage) {
          clearInterval(checkInterval);
          resolve(false);
        }

        if (Date.now() - startTime > timeout) {
          clearInterval(checkInterval);
          resolve(false);
        }
      }, 100);
    });
  }

  /**
   * Humanize field name
   */
  private humanizeFieldName(name: string): string {
    return name
      .replace(/[_-]/g, ' ')
      .replace(/([A-Z])/g, ' $1')
      .trim()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
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
   * Handle Lever file upload
   */
  async handleFileUpload(field: FormField, resumeId?: number): Promise<boolean> {
    logger.info('Lever file upload detected:', field.label);

    // Check if file is already uploaded
    const uploadedFile = document.querySelector('.file-input-value, .uploaded-file');
    if (uploadedFile) {
      logger.info('File already uploaded');
      return true;
    }

    logger.warn('File upload requires manual intervention');
    return false;
  }
}
