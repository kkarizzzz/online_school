import { useEffect, type JSX } from 'react';
import { Link, useParams } from 'react-router';
import { BANK_ROUTE, useBankNumber, useBankNumbers } from '../../../../entities/bank-task';
import { Container } from '../../../../shared/ui';
import { PrototypeTasks } from '../../../../widgets/task-bank';
import styles from './TaskBankPrototypePage.module.css';


/** Задания одного номера ЕГЭ из банка: /task-bank/6?topics=…&status=…&sort=…&order=… */
export const TaskBankPrototypePage = (): JSX.Element => {
    const { number: param = '' } = useParams();
    const n = Number(param);
    const valid = Number.isInteger(n) && n > 0;
    const { data: numbers } = useBankNumbers();
    const { data: number, isPending, isError } = useBankNumber(n);

    useEffect(() => {
        window.scrollTo(0, 0);
    }, [param]);

    if (valid && !isError && (isPending || !numbers)) {
        return (
            <Container variant='page'>
                <p className={styles.message}>Загружаем задания…</p>
            </Container>
        );
    }

    if (!number || !numbers) {
        return (
            <Container variant='page'>
                <div className={styles.message}>
                    <p>Номера {param} нет в банке заданий.</p>
                    <Link to={BANK_ROUTE}>Ко всем номерам</Link>
                </div>
            </Container>
        );
    }

    return (
        <Container variant='page'>
            <PrototypeTasks key={number.n} number={number} numbers={numbers} />
        </Container>
    );
};
