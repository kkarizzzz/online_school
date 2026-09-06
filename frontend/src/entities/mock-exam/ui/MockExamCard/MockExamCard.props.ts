import type { DetailedHTMLProps, HTMLAttributes } from "react";
import type { SubjectMetric } from "../../../../shared/config";

export interface MockExamCardProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    exam: SubjectMetric;
}