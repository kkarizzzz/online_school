import { useHomeworkList } from "../../../entities/homework";

export const useNavBadges = (): Record<string, number> => {
    const { data: homework } = useHomeworkList();
    const activeHomeworkCount = (homework ?? []).filter((hw) => hw.status === 'current').length;

    return {
        homework: activeHomeworkCount,
    };
};
