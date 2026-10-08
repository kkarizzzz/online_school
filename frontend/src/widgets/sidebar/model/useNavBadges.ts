import { useHomeworkList } from "../../../entities/homework";

export const useNavBadges = (): Record<string, number> => {
    const { data } = useHomeworkList();

    return {
        homework: data?.counts.current ?? 0,
    };
};
