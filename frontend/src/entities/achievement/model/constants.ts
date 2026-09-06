import { Award, Compass, Flame, Medal, Sigma, Target } from "lucide-react";
import type { AchievementData, AchievementId } from "./types";

export const ACHIEVEMENTS_DICT: AchievementData[] = [
  { id: 'param_guru', icon: Sigma, title: 'Гуру параметров', description: '10 верных задач с параметрами' },
  { id: 'streak_7', icon: Flame, title: 'Огонь недели', description: 'Серия из 7 дней подряд' },
  { id: 'sniper', icon: Target, title: 'Снайпер', description: '50 задач без ошибок' },
  { id: 'marathon', icon: Award, title: 'Марафонец', description: '100 часов на платформе' },
  { id: 'pioneer', icon: Compass, title: 'Первопроходец', description: 'Пройден вводный модуль' },
  { id: 'perfect_score', icon: Medal, title: 'Стобалльник', description: 'Пробник на 100 баллов' },
];

export const MOCK_UNLOCKED_ACHIEVEMENTS: AchievementId[] = [
  'param_guru', 
  'streak_7', 
  'sniper', 
  'marathon', 
  'pioneer'
];