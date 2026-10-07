import type { JSX } from 'react';
import { Container } from '../../../../shared/ui';
import { PageHeader } from '../../../../widgets/page-header';
import { PracticeTrainer } from '../../../../widgets/practice-feed';

export const PracticePage = (): JSX.Element => {
    return (
        <Container variant="page">
            <PageHeader />
            <PracticeTrainer />
        </Container>
    );
};
