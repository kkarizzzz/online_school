import type { BankRepository } from './BankRepository';
import { MockBankRepository } from './MockBankRepository';

export const bankRepository: BankRepository = new MockBankRepository();
