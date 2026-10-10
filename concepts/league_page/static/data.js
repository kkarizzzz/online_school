// Заглушки вкладки «Лига». В рабочей версии всё это отдаёт GET /api/league/week (см. README → «API»).
// Числа согласованы с таблицей очков из README: активный ученик набирает 500–900 очков и 350–600 соток в неделю.

window.LEAGUE = {
    // Неделя сезона: понедельник 00:00 — воскресенье 23:59 по Москве
    season: { name: 'Осень-2026', week: 6, weeks: 12, endsAt: '2026-10-11T23:59:59+03:00' },

    me: { id: 7, name: 'Костя К.', points: 640, streak: 9, balance: 1240, earnedThisWeek: 320 },

    // Дивизионы снизу вверх. В группе 12 кланов: 3 первых поднимаются, 3 последних опускаются
    divisions: [
        { id: 'bronze', name: 'Бронзовая', color: '#c4834e' },
        { id: 'silver', name: 'Серебряная', color: '#9aa3ad' },
        { id: 'gold', name: 'Золотая', color: '#e0a526' },
        { id: 'platinum', name: 'Платиновая', color: '#3fb3b0' },
        { id: 'hundred', name: 'Лига Сотки', color: '#1219F3' },
    ],

    clan: {
        id: 12,
        name: 'Интегралы',
        tag: 'INT',
        icon: 'sigma',
        color: '#1219F3',
        motto: 'Берём 18-й номер штурмом',
        subject: 'Математика · профиль',
        division: 'gold',
        invite: 'INT-4821',
        bank: 3150,
        size: 20,
        limit: 20,
    },

    // Участники моего клана: очки за неделю, роль, серия дней
    members: [
        { id: 3, name: 'Маша Л.', role: 'leader', points: 980, streak: 34 },
        { id: 9, name: 'Артём С.', role: 'officer', points: 860, streak: 12 },
        { id: 7, name: 'Костя К.', role: 'member', points: 640, streak: 9 },
        { id: 14, name: 'Лиза П.', role: 'member', points: 610, streak: 21 },
        { id: 21, name: 'Даня Н.', role: 'officer', points: 540, streak: 4 },
        { id: 5, name: 'Вика Р.', role: 'member', points: 470, streak: 6 },
        { id: 18, name: 'Саша Г.', role: 'member', points: 455, streak: 15 },
        { id: 30, name: 'Егор Т.', role: 'member', points: 390, streak: 2 },
        { id: 11, name: 'Полина М.', role: 'member', points: 360, streak: 8 },
        { id: 27, name: 'Тимур А.', role: 'member', points: 300, streak: 3 },
        { id: 25, name: 'Ксюша Б.', role: 'member', points: 240, streak: 1 },
        { id: 33, name: 'Миша Д.', role: 'member', points: 180, streak: 0 },
        { id: 40, name: 'Аня Ж.', role: 'member', points: 95, streak: 0 },
        { id: 41, name: 'Глеб О.', role: 'member', points: 0, streak: 0 },
    ],

    // Группа Золотой лиги на эту неделю. Очки клана = сумма 10 лучших участников + бонусы клановых заданий
    standings: [
        { id: 4, name: 'Логарифмы', tag: 'LOG', icon: 'trending-up', color: '#7c3aed', points: 7420, members: 20 },
        { id: 8, name: 'Сотка или ничего', tag: '100', icon: 'flame', color: '#ef4444', points: 6980, members: 18 },
        { id: 12, name: 'Интегралы', tag: 'INT', icon: 'sigma', color: '#1219F3', points: 6195, members: 14, mine: true },
        { id: 2, name: 'Параметр 18', tag: 'P18', icon: 'variable', color: '#0ea5e9', points: 5870, members: 20 },
        { id: 17, name: 'Ночные решатели', tag: 'NGT', icon: 'moon-star', color: '#334155', points: 5410, members: 16 },
        { id: 23, name: 'Векторы', tag: 'VEC', icon: 'move-up-right', color: '#059669', points: 5130, members: 19 },
        { id: 31, name: 'Котангенс', tag: 'CTG', icon: 'cat', color: '#d97706', points: 4760, members: 12 },
        { id: 9, name: 'Физтех-2027', tag: 'MPT', icon: 'atom', color: '#2563eb', points: 4515, members: 20 },
        { id: 40, name: 'Без паники', tag: 'DNP', icon: 'leaf', color: '#16a34a', points: 3990, members: 11 },
        { id: 15, name: 'Пи-рамида', tag: 'PIR', icon: 'triangle', color: '#db2777', points: 3620, members: 15 },
        { id: 36, name: 'Дробь', tag: 'FRC', icon: 'divide', color: '#64748b', points: 2870, members: 9 },
        { id: 44, name: 'Синусоида', tag: 'SIN', icon: 'activity', color: '#0891b2', points: 2240, members: 7 },
    ],

    // Награда в сотках каждому участнику с ≥ 100 очками за неделю — по месту клана в группе
    placeRewards: [300, 220, 160, 120, 100, 80, 60, 50, 40, 30, 20, 20],

    // Личные задания: 3 в неделю, подбираются по слабым номерам из student_topic_stats.
    // kind: weak — по слабой теме, habit — регулярность, exam — пробник/ДЗ
    personalQuests: [
        { id: 'p1', kind: 'weak', icon: 'target', title: 'Добить №13 — тригонометрические уравнения',
            note: 'Ваша доля верных по №13 — 41%. Решите 8 задач верно.', progress: 8, goal: 8, reward: 120, claimed: false },
        { id: 'p2', kind: 'habit', icon: 'calendar-check', title: '5 дней занятий из 7',
            note: 'Засчитывается день, когда набрали хотя бы 30 очков.', progress: 4, goal: 5, reward: 100, claimed: false },
        { id: 'p3', kind: 'exam', icon: 'file-check', title: 'Пробник на 70+ баллов',
            note: 'Любой полный вариант из каталога, решённый на время.', progress: 0, goal: 1, reward: 180, claimed: false },
    ],
    // Бонус за все три личных задания недели
    personalChest: 150,

    // Клановые задания: общий прогресс, награда — в банк клана и каждому, кто внёс вклад
    clanQuests: [
        { id: 'c1', icon: 'swords', title: '600 верных задач кланом', note: 'Любые задачи: банк, нарешка, ДЗ, варианты.',
            progress: 512, goal: 600, reward: 80, bank: 400, mine: 46 },
        { id: 'c2', icon: 'users', title: 'Каждый сдал ДЗ в срок', note: 'Все участники, у кого есть ДЗ на этой неделе.',
            progress: 11, goal: 14, reward: 60, bank: 300, mine: 1 },
        { id: 'c3', icon: 'repeat', title: '100 сессий быстрого повторения', note: 'Повторение 10+ вопросов — одна сессия.',
            progress: 100, goal: 100, reward: 50, bank: 250, mine: 9, claimed: false },
    ],

    // Лента клана
    feed: [
        { who: 'Маша Л.', text: 'сдала пробник на 86 баллов', points: 186, ago: '12 мин' },
        { who: 'Лиза П.', text: 'закрыла задание «100 сессий повторения»', points: 0, ago: '40 мин', quest: true },
        { who: 'Артём С.', text: 'решил 6 задач №18 подряд', points: 180, ago: '1 ч' },
        { who: 'Вика Р.', text: 'сдала ДЗ «Производная» — 9 из 10', points: 95, ago: '2 ч' },
        { who: 'Даня Н.', text: 'вложил 200 соток в банк клана', points: 0, ago: '3 ч', bank: true },
        { who: 'Егор Т.', text: 'вернулся после 5 дней перерыва', points: 30, ago: '5 ч' },
    ],

    // Магазин. kind: use — расходник, look — оформление, clan — покупка из банка клана, real — реальная услуга
    shop: [
        { id: 'freeze', kind: 'use', icon: 'snowflake', title: 'Заморозка серии', note: 'Сохраняет серию, если пропустили день. В запасе не больше 2.', price: 150 },
        { id: 'retry', kind: 'use', icon: 'rotate-ccw', title: 'Вторая попытка в ДЗ', note: 'Переотправить одну задачу ДЗ после ошибки. Очки — половина.', price: 200 },
        { id: 'hint', kind: 'use', icon: 'lightbulb', title: 'Подсказка к задаче', note: 'Первый шаг решения без разбора. Задача приносит −50% очков.', price: 60 },
        { id: 'frame', kind: 'look', icon: 'circle-dashed', title: 'Рамка аватара «Сотка»', note: 'Видна в рейтинге клана и ленте.', price: 400 },
        { id: 'theme', kind: 'look', icon: 'palette', title: 'Тема кабинета «Ночной матан»', note: 'Своя палитра для тёмной темы.', price: 800 },
        { id: 'badge', kind: 'look', icon: 'badge-check', title: 'Значок рядом с именем', note: '12 значков на выбор, один на профиле.', price: 250 },
        { id: 'emblem', kind: 'clan', icon: 'shield', title: 'Новая эмблема клана', note: 'Иконка и цвет. Покупает глава или офицер из банка.', price: 1500 },
        { id: 'banner', kind: 'clan', icon: 'flag', title: 'Баннер клана в лиге', note: 'Цветная полоса строки клана на всю неделю.', price: 1000 },
        { id: 'expert', kind: 'real', icon: 'stamp', title: 'Проверка второй части экспертом', note: 'Одна задача 13–19 с разбором по критериям ФИПИ.', price: 2000 },
        { id: 'webinar', kind: 'real', icon: 'video', title: 'Место на закрытом разборе', note: 'Ежемесячный эфир «Сложные задачи» с преподавателем.', price: 1200 },
    ],

    // Кланы для поиска, когда ученик без клана (?clan=none)
    openClans: [
        { id: 31, name: 'Котангенс', tag: 'CTG', icon: 'cat', color: '#d97706', members: 12, division: 'gold', subject: 'Математика · профиль', target: '80+', open: true },
        { id: 40, name: 'Без паники', tag: 'DNP', icon: 'leaf', color: '#16a34a', members: 11, division: 'gold', subject: 'Математика · профиль', target: '70+', open: true },
        { id: 52, name: 'Ударение', tag: 'UDR', icon: 'type', color: '#be123c', members: 17, division: 'silver', subject: 'Русский язык', target: '90+', open: true },
        { id: 58, name: 'Бинарный поиск', tag: 'BIN', icon: 'binary', color: '#0f766e', members: 8, division: 'bronze', subject: 'Информатика', target: '85+', open: false },
    ],

    // ----------------------------------- друзья -----------------------------------
    // Друзья видят только очки недели, серию, клан и активность — не оценки (настраивается в «Настройках»)
    friendCode: 'KOSTYA-7314',
    // Бонус за приглашение: обоим, когда друг пройдёт первую неделю (5 дней занятий)
    inviteReward: 300,

    friends: [
        { id: 3, name: 'Маша Л.', clan: 'INT', points: 980, streak: 34, together: 21, online: true, last: 'сейчас решает №18', subject: 'Математика' },
        { id: 50, name: 'Ваня Ж.', clan: 'LOG', points: 870, streak: 15, together: 6, online: false, last: '2 ч назад', subject: 'Математика' },
        { id: 14, name: 'Лиза П.', clan: 'INT', points: 610, streak: 21, together: 9, online: true, last: 'сейчас в уроке', subject: 'Математика' },
        { id: 51, name: 'Даша С.', clan: 'UDR', points: 520, streak: 7, together: 0, online: false, last: 'вчера', subject: 'Русский язык' },
        { id: 52, name: 'Рома Е.', clan: null, points: 140, streak: 0, together: 0, online: false, last: '4 дня назад', subject: 'Математика' },
    ],

    requests: {
        incoming: [
            { id: 60, name: 'Олег В.', clan: 'P18', mutual: 3 },
            { id: 61, name: 'Настя К.', clan: null, mutual: 1 },
        ],
        outgoing: [
            { id: 62, name: 'Артём С.', clan: 'INT' },
        ],
    },

    // Вызовы 1 на 1: длятся 3 дня. Победитель +60 соток, проигравший +20, если набрал хоть что-то — без ставок
    challenges: [
        { id: 'd1', friend: 'Ваня Ж.', title: 'Больше верных задач №13', me: 7, them: 5, endsIn: '1 д 6 ч', unit: 'задач' },
        { id: 'd2', friend: 'Лиза П.', title: 'Больше очков за 3 дня', me: 310, them: 345, endsIn: '18 ч', unit: 'очков' },
        { id: 'd3', friend: 'Маша Л.', title: 'Пробник: кто выше', me: 78, them: 74, endsIn: 'завершён', unit: 'баллов', done: true, reward: 60 },
    ],

    challengeTemplates: [
        { id: 'num', icon: 'target', title: 'Больше верных задач номера', note: 'Номер выбираете вы, 3 дня' },
        { id: 'points', icon: 'zap', title: 'Больше очков', note: 'Любая учёба, 3 дня' },
        { id: 'mock', icon: 'file-check', title: 'Пробник: кто выше', note: 'Один вариант на время, до воскресенья' },
        { id: 'streak', icon: 'flame', title: 'Не пропустить ни дня', note: '7 дней подряд — оба получают +80' },
    ],
};
