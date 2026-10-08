import type { JSX } from 'react';
import { useSearchParams } from 'react-router';
import { HomeworkCard, useHomeworkList, type HomeworkStatus } from '../../../../entities/homework';
import { cn } from '../../../../shared/lib';
import { Container, Tabs } from '../../../../shared/ui';
import type { TabItem } from '../../../../shared/ui/Tabs/Tabs.props';
import { PageHeader } from '../../../../widgets/page-header';
import styles from './HomeworkPage.module.css';

const TAB_IDS: HomeworkStatus[] = ['current', 'done', 'overdue'];


export const HomeworkPage = (): JSX.Element => {
    const { data: homework, isPending } = useHomeworkList();
    // Вкладка — в адресе (?tab=done), чтобы «Назад» со страницы ДЗ вернул на неё же
    const [params, setParams] = useSearchParams();
    const tab = params.get('tab') as HomeworkStatus;
    const activeFilter: HomeworkStatus = TAB_IDS.includes(tab) ? tab : 'current';

    const list = homework ?? [];
    const visibleHomework = list.filter((hw) => hw.status === activeFilter);
    const overdueCount = list.filter((hw) => hw.status === 'overdue').length;

    const tabsConfig: TabItem[] = [
        { id: 'current', label: 'Текущие' },
        { id: 'done', label: 'Выполненные' },
        { id: 'overdue', label: 'Просроченные', badge: overdueCount > 0 ? overdueCount : undefined },
    ];

    const changeTab = (id: string) => setParams(id === 'current' ? {} : { tab: id }, { replace: true });

    return (
        <Container variant="page">
            <PageHeader />

            <div className={styles.container}>

                <Tabs
                    tabs={tabsConfig}
                    activeTab={activeFilter}
                    onChange={changeTab}
                />

                <div className={styles.list}>
                    {visibleHomework.map((hw) => (
                        <HomeworkCard key={hw.id} homework={hw} />
                    ))}

                    {!isPending && visibleHomework.length === 0 && (
                        <div className={cn('glass', styles.empty)}>
                            Не найдено.
                        </div>
                    )}
                </div>
            </div>
        </Container>
    );
};
