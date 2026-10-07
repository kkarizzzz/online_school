import type { JSX } from 'react'
import { useLearningProgress } from '../../../../entities/curriculum'
import { Container } from '../../../../shared/ui'
import { PageHeader } from '../../../../widgets/page-header'
import { TheoryRoadmap } from '../../../../widgets/theory-route'
import styles from './TheoryPage.module.css'


export const TheoryPage = (): JSX.Element => {
    const { data: progress } = useLearningProgress();

    return (
        <Container variant='page' className={styles.page}>
            <PageHeader />
            {progress
                ? <TheoryRoadmap progress={progress} />
                : <p className={styles.loading}>Загружаем программу…</p>}
        </Container>
    )
}
