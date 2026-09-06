import type { FC, SVGProps } from "react";

export type MenuItem = {
    route: string;
    name: string;
}

export interface NavItem {
    id: string;
    href: string;
    label: string;
    icon: FC<SVGProps<SVGSVGElement>>;
    description?: string;
}

export type SubjectMetric = {
    subject: string;
    value: number;
    max: number; 
};