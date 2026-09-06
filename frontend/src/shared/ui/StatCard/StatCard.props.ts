import type { DetailedHTMLProps, FC, HTMLAttributes, SVGProps } from "react";

export interface StatCardProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    label: string;
    value: string | number;
    delta?: string;
    icon: FC<SVGProps<SVGSVGElement>>;
}