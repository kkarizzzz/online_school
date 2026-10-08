import type { JSX } from 'react';
import { Container } from '../../../../shared/ui';
import { PageHeader } from '../../../../widgets/page-header';
import { BankNumbers } from '../../../../widgets/task-bank';
import styles from './TaskBankPage.module.css';


export const TaskBankPage = (): JSX.Element => {
    return (
        <Container variant='page'>
            <PageHeader />
            <div className={styles.list}>
                <BankNumbers />
            </div>
        </Container>
    );
};
