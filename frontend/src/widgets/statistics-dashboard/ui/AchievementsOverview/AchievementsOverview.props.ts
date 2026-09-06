import type { DetailedHTMLProps, HTMLAttributes } from "react";
import type { AchievementId } from "../../../../entities/achievement";

export interface AchievementsOverviewProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    unlockedIds?: AchievementId[];
}