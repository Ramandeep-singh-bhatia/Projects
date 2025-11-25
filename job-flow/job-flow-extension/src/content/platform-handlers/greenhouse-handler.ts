/**
 * Greenhouse ATS Handler
 * Handles Greenhouse's application system (greenhouse.io)
 */

import { BasePlatformHandler } from './base-handler';
import { FieldType } from '../../shared/types';
import type { FormField } from '../../shared/types';
import { contentLogger as logger } from '../../shared/utils/logger';

export class GreenhouseHandler extends BasePlatformHandler {
  /**
   * Check if we can handle this page
   */
  canHandle(): boolean {
    return window.location.hostname.includes('greenhouse.io') ||
           window.location.hostname.includes('boards.greenhouse.io');
  }

  /**
   * Get platform name
   */
  getPlatformName(): string {
    return 'Greenhouse';
  }

  /**
   * Detect form fields in Greenhouse
   */
  detectFormFields(): FormField[] {
    const fields: FormField[] = [];

    // Greenhouse uses form fields with specific classes
    const fieldContainers = document.querySelectorAll('.field, .application-field');

    if (fieldContainers.length > 0) {
      fieldContainers.forEach((container, index) => {
        const field = this.extractGreenhouseField(container as HTMLElement, index);
        if (field) {
          fields.push(field);
        }
      });
    } else {
      // Fallback: look for all inputs in the form
      const form = document.querySelector('form');
      if (form) {
        const inputs = form.querySelectorAll('input:not([type="hidden"]), textarea, select');
        inputs.forEach((input, index) => {
          const field = this.extractFieldFromInput(input as HTMLElement, index);
          if (field) {
            fields.push(field);
          }
        });
      }
    }

    logger.info(`Detected ${fields.length} Greenhouse fields`);
    return fields;
  }

  /**
   * Extract field from Greenhouse container
   */
  private extractGreenhouseField(container: HTMLElement, index: number): FormField | null {
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

    const label = this.getGreenhouseLabel(input);
    const fieldType = this.detectGreenhouseFieldType(input);

    const field: FormField = {
      id: input.id || `greenhouse_field_${index}`,
      name: input.name || input.id || `field_${index}`,
      label: label,
      type: fieldType,
      required: input.required || input.getAttribute('aria-required') === 'true',
      element: input,
      selector: this.generateGreenhouseSelector(input),
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
   * Get label for Greenhouse field
   */
  private getGreenhouseLabel(input: HTMLElement): string {
    // Try associated label
    if (input.id) {
      const label = document.querySelector(`label[for="${input.id}"]`);
      if (label) {
        return this.cleanText(label.textContent || '');
      }
    }

    // Try parent label
    const parentLabel = input.closest('label');
    if (parentLabel) {
      // Get label text excluding the input's value
      const clone = parentLabel.cloneNode(true) as HTMLElement;
      const inputClone = clone.querySelector('input, textarea, select');
      if (inputClone) {
        inputClone.remove();
      }
      return this.cleanText(clone.textContent || '');
    }

    // Try sibling label
    const container = input.closest('.field, .application-field');
    if (container) {
      const label = container.querySelector('label');
      if (label) {
        return this.cleanText(label.textContent || '');
      }
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
   * Detect Greenhouse field type
   */
  private detectGreenhouseFieldType(element: HTMLElement): FieldType {
    if (element instanceof HTMLSelectElement) {
      return FieldType.SELECT;
    }

    if (element instanceof HTMLTextAreaElement) {
      return FieldType.TEXTAREA;
    }

    if (element instanceof HTMLInputElement) {
      const type = element.type.toLowerCase();
      const name = element.name.toLowerCase();
      const id = element.id.toLowerCase();

      // Phone detection
      if (type === 'tel' || name.includes('phone') || id.includes('phone')) {
        return FieldType.PHONE;
      }

      // Email detection
      if (type === 'email' || name.includes('email') || id.includes('email')) {
        return FieldType.EMAIL;
      }

      // File upload
      if (type === 'file') {
        return FieldType.FILE;
      }

      // Date
      if (type === 'date') {
        return FieldType.DATE;
      }

      // Number
      if (type === 'number') {
        return FieldType.NUMBER;
      }

      // Radio
      if (type === 'radio') {
        return FieldType.RADIO;
      }

      // Checkbox
      if (type === 'checkbox') {
        return FieldType.CHECKBOX;
      }

      return FieldType.TEXT;
    }

    return FieldType.TEXT;
  }

  /**
   * Generate selector for Greenhouse field
   */
  private generateGreenhouseSelector(input: HTMLElement): string {
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
   * Check for next/submit button
   */
  hasNextButton(): boolean {
    const submitButton = document.querySelector('input[type="submit"], button[type="submit"]');
    return !!submitButton;
  }

  /**
   * Click submit button
   */
  async clickNext(): Promise<boolean> {
    const submitButton = document.querySelector('input[type="submit"], button[type="submit"]') as HTMLButtonElement;
    if (submitButton) {
      submitButton.click();
      logger.info('Clicked Greenhouse submit button');
      return true;
    }

    return false;
  }

  /**
   * Get submit button
   */
  getSubmitButton(): HTMLButtonElement | null {
    const submitButton = document.querySelector('input[type="submit"], button[type="submit"]') as HTMLButtonElement;
    return submitButton || null;
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
}
