import type { DetailedHTMLProps, HTMLAttributes } from "react";
import type { SubjectMetric } from "../../../../shared/config";

export interface MockExamsOverviewProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    exams?: SubjectMetric[];
}