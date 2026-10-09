import type { JSX } from 'react';
import { Container } from '../../../../shared/ui';
import { PageHeader } from '../../../../widgets/page-header';
import { PersonalSetup } from '../../../../widgets/practice-feed';

/** Нарешка, настройка персонального режима: сложность, номера ЕГЭ и подтемы */
export const PracticePersonalPage = (): JSX.Element => {
    return (
        <Container variant="page">
            <PageHeader title="Персональный режим" />
            <PersonalSetup />
        </Container>
    );
};
