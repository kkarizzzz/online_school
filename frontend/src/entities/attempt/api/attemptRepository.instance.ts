import type { AttemptRepository } from './AttemptRepository';
import { HttpAttemptRepository } from './HttpAttemptRepository';

export const attemptRepository: AttemptRepository = new HttpAttemptRepository();
