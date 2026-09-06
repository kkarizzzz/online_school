import type { DetailedHTMLProps, HTMLAttributes } from "react";
import type { AchievementData } from "../../model/types";

export interface AchievementBadgeProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    achievement: AchievementData;
    unlocked: boolean;
}