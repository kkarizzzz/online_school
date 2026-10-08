import type { ButtonHTMLAttributes, DetailedHTMLProps } from "react";

export interface NotificationBtnProps extends DetailedHTMLProps<ButtonHTMLAttributes<HTMLButtonElement>, HTMLButtonElement> {
    iconSize?: number;
}
