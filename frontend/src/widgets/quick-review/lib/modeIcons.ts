import { BookOpen, Calculator, Shuffle, type LucideIcon } from 'lucide-react';
import type { ReviewQuestionKind } from '../../../entities/review-question';
import type { ReviewModeId } from '../model/ReviewMode';

export const MODE_ICONS: Record<ReviewModeId, LucideIcon> = {
    theory: BookOpen,
    calc: Calculator,
    mix: Shuffle,
};

export const KIND_META: Record<ReviewQuestionKind, { label: string; icon: LucideIcon }> = {
    theory: { label: 'Теория', icon: BookOpen },
    calc: { label: 'Вычисление', icon: Calculator },
};
