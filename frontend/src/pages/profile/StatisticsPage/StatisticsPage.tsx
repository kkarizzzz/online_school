import { type JSX } from 'react';
import { MOCK_UNLOCKED_ACHIEVEMENTS } from '../../../entities/achievement';
import { MOCK_EXAMS } from '../../../shared/constants';
import { Container } from '../../../shared/ui';
import { AchievementsOverview, HomeworkOverview, MetricsGrid, MockExamsOverview, ProfileSummary, SubjectProgress, WeeklyAttendance } from '../../../widgets/statistics-dashboard';
import styles from './StatisticsPage.module.css';


export const StatisticsPage = (): JSX.Element => {

    return (
        <Container className={styles.container}>
            <ProfileSummary />

            <MetricsGrid />

            <SubjectProgress />

            <div className={styles.graphicsContainer}>
                    <WeeklyAttendance />
                    <HomeworkOverview />
            </div>

            <MockExamsOverview exams={MOCK_EXAMS} />

            <AchievementsOverview unlockedIds={MOCK_UNLOCKED_ACHIEVEMENTS} />
        </Container>
    );
};