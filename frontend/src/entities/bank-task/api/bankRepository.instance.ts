import type { BankRepository } from './BankRepository';
import { HttpBankRepository } from './HttpBankRepository';

export const bankRepository: BankRepository = new HttpBankRepository();
