import type { DetailedHTMLProps, HTMLAttributes } from "react";

export interface AvatarProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    firstName?: string;
    lastName?: string;
    size?: number;
    variant?: 'circle' | 'rounded';
}