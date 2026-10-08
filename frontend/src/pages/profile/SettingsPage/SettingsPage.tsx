import { useState, type JSX } from 'react';
import { Container, Tabs } from '../../../shared/ui';
import type { TabItem } from '../../../shared/ui/Tabs/Tabs.props';
import { SubscriptionSubjects, SubscriptionTier } from '../../../widgets/subscription-manager';
import { ProfileData } from '../../../widgets/user-profile-settings';
import styles from './SettingsPage.module.css';


const TABS_CONFIG: TabItem[] = [
    { id: 'profile', label: 'Профиль' },
    { id: 'subscription', label: 'Подписка' },
];

export const SettingsPage = (): JSX.Element => {
    const [activeTab, setActiveTab] = useState<string>('profile');

    return (
        <Container className={styles.container}>
            <Tabs 
                tabs={TABS_CONFIG} 
                activeTab={activeTab} 
                onChange={setActiveTab} 
            />

            {activeTab === 'profile' ? (
                <ProfileData /> 
            ) : (
                <>
                    <SubscriptionTier />
                    <SubscriptionSubjects />
                </>
            )}
        </Container>
    );
};