import type { FC, SVGProps } from "react";

export type AchievementId = 
    | 'param_guru'
    | 'streak_7'
    | 'sniper'
    | 'marathon'
    | 'pioneer'
    | 'perfect_score';

export type AchievementData = {
    id: AchievementId;
    icon: FC<SVGProps<SVGSVGElement>>;
    title: string;
    description: string;
};