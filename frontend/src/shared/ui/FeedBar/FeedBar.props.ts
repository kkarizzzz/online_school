import type { DetailedHTMLProps, FC, HTMLAttributes, ReactNode, SVGProps } from 'react';

export interface FeedStat {
    icon: FC<SVGProps<SVGSVGElement>>;
    label: string;
    value: ReactNode;
    title?: string;
    /** Иконка цвета «огонька» — для серии */
    hot?: boolean;
    /** Смена значения перезапускает короткую анимацию */
    bumpKey?: number;
}

export interface FeedBarProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    backLabel: string;
    onBack: () => void;
    /** Иконка или номер задания в плашке режима */
    modeIcon: ReactNode;
    modeAccent?: boolean;
    modeLabel: string;
    modeTitle: string;
    stats: FeedStat[];
}
