import type { DetailedHTMLProps, HTMLAttributes } from 'react';
import type { Homework } from '../../model/Homework';

export interface HomeworkCardProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    homework: Homework;
}
