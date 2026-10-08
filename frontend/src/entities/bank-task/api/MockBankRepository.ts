import { JsonStorage } from '../../../shared/lib';
import type { BankNumber } from '../model/types';
import type { BankRepository } from './BankRepository';
import { buildBankMock } from './mock/bank.data';

/** Банк из генератора, отметки «решено» — в localStorage этого браузера. Позже — с сервера */
export class MockBankRepository implements BankRepository {
    private readonly solved = new JsonStorage<string[]>('bank:solved');
    private numbers: BankNumber[] | null = null;

    async getNumbers(): Promise<BankNumber[]> {
        this.numbers ??= buildBankMock();
        return this.numbers;
    }

    async getSolved(): Promise<string[]> {
        const list = this.solved.read();
        return Array.isArray(list) ? list : [];
    }

    async setSolved(taskId: string, solved: boolean): Promise<void> {
        const set = new Set(await this.getSolved());
        if (solved) set.add(taskId);
        else set.delete(taskId);
        this.solved.write([...set]);
    }
}
