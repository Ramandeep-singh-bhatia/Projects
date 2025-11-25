/**
 * Platform Handlers Index
 * Exports all platform handlers and provides factory function
 */

import { BasePlatformHandler } from './base-handler';
import { LinkedInEasyApplyHandler } from './linkedin-handler';
import { WorkdayHandler } from './workday-handler';
import { GreenhouseHandler } from './greenhouse-handler';
import { LeverHandler } from './lever-handler';
import { contentLogger as logger } from '../../shared/utils/logger';

/**
 * Get the appropriate platform handler for the current page
 */
export function getPlatformHandler(): BasePlatformHandler | null {
  const handlers: BasePlatformHandler[] = [
    new LinkedInEasyApplyHandler(),
    new WorkdayHandler(),
    new GreenhouseHandler(),
    new LeverHandler(),
  ];

  for (const handler of handlers) {
    if (handler.canHandle()) {
      logger.info('Selected platform handler:', handler.getPlatformName());
      return handler;
    }
  }

  logger.info('No specific platform handler found - using generic form detection');
  return null;
}

/**
 * Check if current page has a known platform handler
 */
export function hasKnownPlatform(): boolean {
  const handler = getPlatformHandler();
  return handler !== null;
}

/**
 * Get platform name for current page
 */
export function getCurrentPlatformName(): string {
  const handler = getPlatformHandler();
  return handler ? handler.getPlatformName() : 'Generic';
}

// Export all handlers
export {
  BasePlatformHandler,
  LinkedInEasyApplyHandler,
  WorkdayHandler,
  GreenhouseHandler,
  LeverHandler,
};
