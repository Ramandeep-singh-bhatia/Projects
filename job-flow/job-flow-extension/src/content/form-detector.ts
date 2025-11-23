/**
 * Form Detector
 * Detects and analyzes forms on the page
 */

import { FieldType } from '../shared/types';
import type { FormField } from '../shared/types';
import { contentLogger as logger } from '../shared/utils/logger';

export class FormDetector {
  /**
   * Detect all forms on the page
   */
  detectForms(): HTMLFormElement[] {
    const forms = Array.from(document.querySelectorAll('form'));

    // Also look for form-like structures without <form> tag
    const formLikeContainers = this.detectFormLikeContainers();

    return [...forms, ...formLikeContainers];
  }

  /**
   * Detect form-like containers (divs with many inputs)
   */
  private detectFormLikeContainers(): HTMLFormElement[] {
    const containers: HTMLFormElement[] = [];
    const allDivs = document.querySelectorAll('div');

    for (const div of allDivs) {
      const inputs = div.querySelectorAll('input, textarea, select');

      // If container has 5+ input fields, consider it a form
      if (inputs.length >= 5) {
        // Check if it's not nested in an actual form
        if (!div.closest('form')) {
          containers.push(div as any); // Treat as form-like
        }
      }
    }

    return containers;
  }

  /**
   * Extract all fields from a form
   */
  extractFields(form: HTMLFormElement): FormField[] {
    const fields: FormField[] = [];

    // Get all input, textarea, and select elements
    const inputs = form.querySelectorAll('input, textarea, select');

    for (const element of inputs) {
      const field = this.extractFieldInfo(element as HTMLElement);
      if (field) {
        fields.push(field);
      }
    }

    return fields.filter(f => !this.shouldSkipField(f));
  }

  /**
   * Extract field information from an element
   */
  private extractFieldInfo(element: HTMLElement): FormField | null {
    const tagName = element.tagName.toLowerCase();

    // Skip hidden, disabled, or readonly fields
    if (this.isHiddenOrDisabled(element)) {
      return null;
    }

    const field: FormField = {
      id: this.generateFieldId(element),
      name: this.getFieldName(element),
      label: this.getFieldLabel(element),
      type: this.detectFieldType(element),
      required: this.isRequired(element),
      element: element,
      selector: this.generateSelector(element),
    };

    // Get placeholder if available
    if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) {
      field.placeholder = element.placeholder;
    }

    // Get options for select fields
    if (element instanceof HTMLSelectElement) {
      field.options = Array.from(element.options).map(opt => opt.text);
    }

    // Get current value if any
    if (element instanceof HTMLInputElement ||
        element instanceof HTMLTextAreaElement ||
        element instanceof HTMLSelectElement) {
      field.value = element.value;
    }

    return field;
  }

  /**
   * Detect field type
   */
  private detectFieldType(element: HTMLElement): FieldType {
    const tagName = element.tagName.toLowerCase();

    if (tagName === 'select') {
      return FieldType.SELECT;
    }

    if (tagName === 'textarea') {
      return FieldType.TEXTAREA;
    }

    if (element instanceof HTMLInputElement) {
      const type = element.type.toLowerCase();

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
   * Get field label
   */
  private getFieldLabel(element: HTMLElement): string {
    // Try to find associated label
    const id = element.id;
    if (id) {
      const label = document.querySelector(`label[for="${id}"]`);
      if (label) {
        return this.cleanText(label.textContent || '');
      }
    }

    // Try parent label
    const parentLabel = element.closest('label');
    if (parentLabel) {
      return this.cleanText(parentLabel.textContent || '');
    }

    // Try sibling label
    const prevSibling = element.previousElementSibling;
    if (prevSibling && prevSibling.tagName.toLowerCase() === 'label') {
      return this.cleanText(prevSibling.textContent || '');
    }

    // Try aria-label
    const ariaLabel = element.getAttribute('aria-label');
    if (ariaLabel) {
      return this.cleanText(ariaLabel);
    }

    // Try placeholder
    if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) {
      if (element.placeholder) {
        return this.cleanText(element.placeholder);
      }
    }

    // Try name attribute
    const name = element.getAttribute('name');
    if (name) {
      return this.cleanText(this.humanizeFieldName(name));
    }

    // Fallback to element text content around it
    const parent = element.parentElement;
    if (parent) {
      return this.cleanText(parent.textContent || '').substring(0, 50);
    }

    return 'Unknown Field';
  }

  /**
   * Get field name
   */
  private getFieldName(element: HTMLElement): string {
    return element.getAttribute('name') ||
           element.getAttribute('id') ||
           this.generateFieldId(element);
  }

  /**
   * Generate unique field ID
   */
  private generateFieldId(element: HTMLElement): string {
    return element.id ||
           element.getAttribute('name') ||
           `field_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Generate CSS selector for element
   */
  private generateSelector(element: HTMLElement): string {
    if (element.id) {
      return `#${element.id}`;
    }

    const name = element.getAttribute('name');
    if (name) {
      return `[name="${name}"]`;
    }

    // Generate path-based selector
    const path: string[] = [];
    let current: Element | null = element;

    while (current && current !== document.body) {
      let selector = current.tagName.toLowerCase();

      if (current.className) {
        const classes = Array.from(current.classList)
          .filter(c => !c.includes('focus') && !c.includes('hover'))
          .slice(0, 2);
        if (classes.length > 0) {
          selector += '.' + classes.join('.');
        }
      }

      path.unshift(selector);
      current = current.parentElement;

      if (path.length > 5) break; // Limit depth
    }

    return path.join(' > ');
  }

  /**
   * Check if element is hidden or disabled
   */
  private isHiddenOrDisabled(element: HTMLElement): boolean {
    if (element instanceof HTMLInputElement ||
        element instanceof HTMLTextAreaElement ||
        element instanceof HTMLSelectElement) {
      if (element.disabled || element.readOnly) {
        return true;
      }
    }

    // Check visibility
    const style = window.getComputedStyle(element);
    if (style.display === 'none' || style.visibility === 'hidden') {
      return true;
    }

    // Check if element has zero size
    const rect = element.getBoundingClientRect();
    if (rect.width === 0 && rect.height === 0) {
      return true;
    }

    return false;
  }

  /**
   * Check if field is required
   */
  private isRequired(element: HTMLElement): boolean {
    if (element instanceof HTMLInputElement ||
        element instanceof HTMLTextAreaElement ||
        element instanceof HTMLSelectElement) {
      return element.required;
    }

    // Check aria-required
    return element.getAttribute('aria-required') === 'true';
  }

  /**
   * Check if field should be skipped
   */
  private shouldSkipField(field: FormField): boolean {
    const skipPatterns = [
      'password',
      'captcha',
      'csrf',
      'token',
      'submit',
      'button',
    ];

    const labelLower = field.label.toLowerCase();
    const nameLower = field.name.toLowerCase();

    return skipPatterns.some(pattern =>
      labelLower.includes(pattern) || nameLower.includes(pattern)
    );
  }

  /**
   * Clean and normalize text
   */
  private cleanText(text: string): string {
    return text
      .trim()
      .replace(/\s+/g, ' ')
      .replace(/\*/g, '') // Remove asterisks (required indicators)
      .replace(/:/g, '')  // Remove colons
      .trim();
  }

  /**
   * Convert field name to human-readable format
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
}
