/**
 * Logging Utility
 * Centralized logging with levels and formatting
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

class Logger {
  private level: LogLevel = LogLevel.INFO;
  private prefix: string = '[JobFlow]';

  setLevel(level: LogLevel): void {
    this.level = level;
  }

  setPrefix(prefix: string): void {
    this.prefix = prefix;
  }

  private shouldLog(level: LogLevel): boolean {
    return level >= this.level;
  }

  private formatMessage(level: string, ...args: any[]): any[] {
    const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
    return [`${this.prefix} [${timestamp}] [${level}]`, ...args];
  }

  debug(...args: any[]): void {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.log(...this.formatMessage('DEBUG', ...args));
    }
  }

  info(...args: any[]): void {
    if (this.shouldLog(LogLevel.INFO)) {
      console.info(...this.formatMessage('INFO', ...args));
    }
  }

  warn(...args: any[]): void {
    if (this.shouldLog(LogLevel.WARN)) {
      console.warn(...this.formatMessage('WARN', ...args));
    }
  }

  error(...args: any[]): void {
    if (this.shouldLog(LogLevel.ERROR)) {
      console.error(...this.formatMessage('ERROR', ...args));
    }
  }

  group(label: string): void {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.group(label);
    }
  }

  groupEnd(): void {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.groupEnd();
    }
  }

  time(label: string): void {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.time(label);
    }
  }

  timeEnd(label: string): void {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.timeEnd(label);
    }
  }
}

// Export singleton instances for different contexts
export const contentLogger = new Logger();
contentLogger.setPrefix('[JobFlow:Content]');

export const backgroundLogger = new Logger();
backgroundLogger.setPrefix('[JobFlow:Background]');

export const popupLogger = new Logger();
popupLogger.setPrefix('[JobFlow:Popup]');

// Default export
export const logger = new Logger();
