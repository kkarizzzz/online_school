import { ArrowLeft, FileQuestion } from 'lucide-react';
import { useEffect, type JSX } from 'react';
import { Link, useParams } from 'react-router';
import { HOMEWORK_LIST_ROUTE, useHomework } from '../../../../entities/homework';
import { cn } from '../../../../shared/lib';
import { Button, Container } from '../../../../shared/ui';
import { HomeworkSolver } from '../../../../widgets/homework-solver';
import styles from './HomeworkSolvePage.module.css';


export const HomeworkSolvePage = (): JSX.Element => {
    const { homeworkId = '' } = useParams();
    const { data: homework, isPending } = useHomework(homeworkId);

    useEffect(() => {
        window.scrollTo(0, 0);
    }, [homeworkId]);

    if (isPending) {
        return (
            <Container variant='page'>
                <p className={styles.message}>Загружаем домашнее задание…</p>
            </Container>
        );
    }

    if (!homework) {
        return (
            <Container variant='page'>
                <div className={cn('glass', styles.missing)}>
                    <FileQuestion size={34} />
                    <p className={styles.missingTitle}>Домашнее задание не найдено</p>
                    <Button as={Link} to={HOMEWORK_LIST_ROUTE} variant="outline" size="m" radius={12}>
                        <ArrowLeft size={18} />К домашним заданиям
                    </Button>
                </div>
            </Container>
        );
    }

    return (
        <Container variant='page'>
            <HomeworkSolver key={homework.id} homework={homework} />
        </Container>
    );
};
