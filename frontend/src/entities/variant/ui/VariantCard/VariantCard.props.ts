import type { DetailedHTMLProps, HTMLAttributes } from "react";
import type { Variant } from "../../model/types";


export interface VariantCardProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    variant: Variant;
}