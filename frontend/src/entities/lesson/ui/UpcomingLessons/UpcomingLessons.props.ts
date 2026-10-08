import type { DetailedHTMLProps, HTMLAttributes } from 'react';
import type { LessonModel } from '../../model/types';


export interface UpcomingLessonsProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    title: string;
    lessons: LessonModel[];
}