import type { JSX } from 'react';
import { Container } from '../../../../shared/ui';
import { PageHeader } from '../../../../widgets/page-header';
import { QuickReview } from '../../../../widgets/quick-review';


export const RepetionQuickPage = (): JSX.Element => {
    return (
        <Container variant='page'>
            <PageHeader />
            <QuickReview />
        </Container>
    );
};
