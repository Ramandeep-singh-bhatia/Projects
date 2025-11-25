/**
 * Field Mapper
 * Maps form fields to user profile data
 */

import { FieldType } from '../shared/types';
import type { FormField, UserProfile } from '../shared/types';
import { contentLogger as logger } from '../shared/utils/logger';

export class FieldMapper {
  /**
   * Map a field to a value from user data
   */
  mapFieldToValue(field: FormField, data: any): any {
    const label = field.label.toLowerCase();
    const name = field.name.toLowerCase();

    // Try direct mapping first
    const directValue = this.tryDirectMapping(field, data);
    if (directValue !== null) {
      return directValue;
    }

    // Try fuzzy matching
    return this.tryFuzzyMapping(field, data);
  }

  /**
   * Try direct mapping based on field patterns
   */
  private tryDirectMapping(field: FormField, data: any): any {
    const label = field.label.toLowerCase();
    const name = field.name.toLowerCase();

    // First name
    if (this.matches(label, ['first name', 'given name', 'firstname']) ||
        this.matches(name, ['firstname', 'fname', 'first_name'])) {
      return data.first_name;
    }

    // Last name
    if (this.matches(label, ['last name', 'family name', 'surname', 'lastname']) ||
        this.matches(name, ['lastname', 'lname', 'last_name'])) {
      return data.last_name;
    }

    // Email
    if (this.matches(label, ['email', 'e-mail', 'email address']) ||
        field.type === FieldType.EMAIL ||
        this.matches(name, ['email', 'mail'])) {
      return data.email;
    }

    // Phone
    if (this.matches(label, ['phone', 'telephone', 'mobile', 'phone number']) ||
        field.type === FieldType.PHONE ||
        this.matches(name, ['phone', 'tel', 'mobile'])) {
      return data.phone;
    }

    // LinkedIn
    if (this.matches(label, ['linkedin', 'linkedin url', 'linkedin profile']) ||
        this.matches(name, ['linkedin'])) {
      return data.linkedin_url;
    }

    // GitHub
    if (this.matches(label, ['github', 'github url', 'github profile']) ||
        this.matches(name, ['github'])) {
      return data.github_url;
    }

    // Portfolio/Website
    if (this.matches(label, ['website', 'portfolio', 'personal website']) ||
        this.matches(name, ['website', 'portfolio'])) {
      return data.portfolio_url;
    }

    // Address
    if (this.matches(label, ['street', 'address line 1', 'address']) ||
        this.matches(name, ['address', 'street', 'address1'])) {
      return data.address_line1;
    }

    // City
    if (this.matches(label, ['city', 'town']) ||
        this.matches(name, ['city'])) {
      return data.city;
    }

    // State
    if (this.matches(label, ['state', 'province', 'region']) ||
        this.matches(name, ['state', 'province'])) {
      return data.state;
    }

    // ZIP code
    if (this.matches(label, ['zip', 'zip code', 'postal code', 'postcode']) ||
        this.matches(name, ['zip', 'zipcode', 'postal'])) {
      return data.zip_code;
    }

    // Country
    if (this.matches(label, ['country']) ||
        this.matches(name, ['country'])) {
      return data.country || 'United States';
    }

    // Work authorization
    if (this.matches(label, ['authorized to work', 'work authorization', 'legally authorized'])) {
      return data.work_authorized ? 'Yes' : 'No';
    }

    // Sponsorship
    if (this.matches(label, ['sponsorship', 'visa sponsorship', 'require sponsorship'])) {
      return data.requires_sponsorship ? 'Yes' : 'No';
    }

    // Years of experience
    if (this.matches(label, ['years of experience', 'years experience', 'total experience']) ||
        this.matches(name, ['experience_years', 'years_experience'])) {
      return data.total_years_experience;
    }

    // Current title
    if (this.matches(label, ['current title', 'current position', 'job title']) ||
        this.matches(name, ['title', 'current_title'])) {
      return data.current_title;
    }

    // Desired salary
    if (this.matches(label, ['salary', 'desired salary', 'salary expectation', 'expected salary']) ||
        this.matches(name, ['salary', 'compensation'])) {
      return data.min_salary ? `$${data.min_salary.toLocaleString()}` : '';
    }

    // Notice period
    if (this.matches(label, ['notice period', 'availability', 'how soon can you start']) ||
        this.matches(name, ['notice', 'availability'])) {
      return `${data.notice_period_weeks} weeks`;
    }

    return null;
  }

  /**
   * Try fuzzy mapping by checking question database
   */
  private tryFuzzyMapping(field: FormField, data: any): any {
    // This would call the backend API to match question
    // For now, return null to indicate no match
    // The background script will handle API calls
    return null;
  }

  /**
   * Check if text matches any of the patterns
   */
  private matches(text: string, patterns: string[]): boolean {
    return patterns.some(pattern => text.includes(pattern));
  }

  /**
   * Get mapping suggestions for a field
   */
  getSuggestions(field: FormField): string[] {
    const suggestions: string[] = [];
    const label = field.label.toLowerCase();

    // Provide context-aware suggestions
    if (label.includes('name')) {
      suggestions.push('first_name', 'last_name');
    }

    if (label.includes('email') || field.type === FieldType.EMAIL) {
      suggestions.push('email');
    }

    if (label.includes('phone') || field.type === FieldType.PHONE) {
      suggestions.push('phone');
    }

    if (label.includes('experience') || label.includes('years')) {
      suggestions.push('total_years_experience');
    }

    if (label.includes('address') || label.includes('location')) {
      suggestions.push('address_line1', 'city', 'state', 'zip_code');
    }

    return suggestions;
  }

  /**
   * Validate that a value is appropriate for a field
   */
  validateValue(field: FormField, value: any): boolean {
    // Check type compatibility
    if (field.type === FieldType.NUMBER && isNaN(Number(value))) {
      return false;
    }

    if (field.type === FieldType.EMAIL && !this.isValidEmail(String(value))) {
      return false;
    }

    if (field.type === FieldType.PHONE && !this.isValidPhone(String(value))) {
      return false;
    }

    // Check required fields
    if (field.required && (value === null || value === undefined || value === '')) {
      return false;
    }

    return true;
  }

  /**
   * Validate email format
   */
  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Validate phone format
   */
  private isValidPhone(phone: string): boolean {
    // Remove formatting characters
    const digitsOnly = phone.replace(/\D/g, '');
    // US phone numbers are typically 10 digits
    return digitsOnly.length >= 10;
  }
}
