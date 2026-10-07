import { CirclePlay, PencilLine, type LucideIcon } from 'lucide-react';
import type { LessonStep } from '../model/LessonStep';

export const stepIcon = (step: LessonStep): LucideIcon => (step.kind === 'video' ? CirclePlay : PencilLine);
