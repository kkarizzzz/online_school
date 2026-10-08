import type { JSX } from 'react';
import { MockExamCard } from '../../../../entities/mock-exam';
import { useMyStats } from '../../../../entities/stats';
import { formatDayMonth } from '../../../../shared/lib';
import { Badge, Card } from '../../../../shared/ui';
import styles from './MockExamsOverview.module.css';
import type { MockExamsOverviewProps } from './MockExamsOverview.props';

/** Сколько последних пробников показываем */
const SHOWN = 4;


/** Последние сданные полные варианты во вторичных баллах */
export const MockExamsOverview = ({ exams: given, className, ...props }: MockExamsOverviewProps): JSX.Element => {
    const { data: stats } = useMyStats();
    const exams = given ?? (stats?.mockExams ?? [])
        .filter((e) => e.secondaryScore !== null)
        .slice(-SHOWN)
        .reverse()
        .map((e) => ({ subject: `${e.title} · ${formatDayMonth(e.submittedAt)}`, value: e.secondaryScore ?? 0, max: 100 }));

    const averageScore = exams.length > 0
        ? Math.round(exams.reduce((sum, e) => sum + e.value, 0) / exams.length)
        : 0;

    return (
        <Card variant="glass" className={className} {...props}>
            <div className={styles.header}>
                <h2 className={styles.title}>Пробники</h2>

                {exams.length > 0 && (
                    <Badge variant="soft" size="l">
                        <span>Средний балл</span>
                        <span className={styles.averageScore}>{averageScore}</span>
                    </Badge>
                )}
            </div>

            {exams.length > 0 ? (
                <div className={styles.grid}>
                    {/* Один вариант можно сдать дважды за день — названия совпадут, поэтому ключ — позиция */}
                    {exams.map((exam, i) => (
                        <MockExamCard key={i} exam={exam} />
                    ))}
                </div>
            ) : (
                <p className={styles.empty}>Сдайте полный вариант в каталоге — результат появится здесь.</p>
            )}
        </Card>
    );
};
