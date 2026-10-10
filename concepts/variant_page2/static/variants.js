// Каталог вариантов (заглушка). Позже список будет приходить с сервера.
//
// kind:      'standard' — полный вариант, комплектация как на ЕГЭ (задания 1–19);
//            'drill' — отработка: один тип заданий или набор из нескольких прототипов
// numbers:   для отработки — номера заданий ЕГЭ, из которых собран вариант
// publisher: 'author' — авторские варианты школы, 'statgrad' — СтатГрад
// level:     'base' | 'medium' | 'hard' | 'coffin' (гроб)
// tasks:     число заданий
// solved:    сколько учеников решило вариант — по нему сортировка «по популярности»
// date:      дата публикации, YYYY-MM-DD — список сортируется по ней, новые сверху
// result:    последняя попытка (заглушка) — нет, если вариант не решали.
//            points — баллы по заданиям строкой цифр: в стандартном первичные баллы ЕГЭ
//            (задания 13–19 стоят 2, 3, 2, 2, 3, 4, 4), в отработке 1 — верно, 0 — неверно.
//            Вторичный балл считается по шкале из exam.js. minutes — сколько решали, date — когда

window.VARIANTS = [
    // Тестовые: короткая отработка — быстро пройти путь до результатов, и полный стандартный вариант
    { id: 'test-drill', title: 'Тестовый вариант: 3 задания', kind: 'drill', numbers: [1, 4, 6], publisher: 'author', level: 'base', tasks: 3, solved: 3, date: '2026-10-07' },
    { id: 'test-standard', title: 'Тестовый стандартный вариант', kind: 'standard', publisher: 'statgrad', level: 'medium', tasks: 19, solved: 12, date: '2026-10-07' },
    { id: 'a-21', title: 'Авторский вариант №21', kind: 'standard', publisher: 'author', level: 'medium', tasks: 19, solved: 148, date: '2026-10-01' },
    { id: 'd-13-2', title: 'Тригонометрические уравнения', kind: 'drill', numbers: [13], publisher: 'author', level: 'medium', tasks: 10, solved: 412, date: '2026-09-30', result: { points: '1111011101', minutes: 42, date: '2026-10-02' } },
    { id: 's-2610', title: 'СтатГрад, тренировочная работа №1', kind: 'standard', publisher: 'statgrad', level: 'medium', tasks: 19, solved: 2310, date: '2026-09-28' },
    { id: 'a-20', title: 'Гроб №5: параметры и экономика', kind: 'drill', numbers: [16, 18], publisher: 'author', level: 'coffin', tasks: 8, solved: 57, date: '2026-09-24' },
    { id: 'd-1-5', title: 'Планиметрия, векторы и вероятности', kind: 'drill', numbers: [1, 2, 4, 5], publisher: 'author', level: 'base', tasks: 12, solved: 890, date: '2026-09-22' },
    { id: 'a-19', title: 'Авторский вариант №19', kind: 'standard', publisher: 'author', level: 'base', tasks: 19, solved: 1240, date: '2026-09-20', result: { points: '1111110111111000000', minutes: 168, date: '2026-09-21' } },
    { id: 's-d-15', title: 'СтатГрад, тематическая: неравенства', kind: 'drill', numbers: [15], publisher: 'statgrad', level: 'hard', tasks: 8, solved: 634, date: '2026-09-10' },
    { id: 's-2605', title: 'СтатГрад, диагностическая работа (май)', kind: 'standard', publisher: 'statgrad', level: 'hard', tasks: 19, solved: 4120, date: '2026-05-14', result: { points: '1111011110112010100', minutes: 214, date: '2026-05-16' } },
    { id: 'a-18', title: 'Авторский вариант №18', kind: 'standard', publisher: 'author', level: 'hard', tasks: 19, solved: 980, date: '2026-05-02' },
    { id: 'd-14', title: 'Стереометрия: углы и расстояния', kind: 'drill', numbers: [14], publisher: 'author', level: 'hard', tasks: 6, solved: 356, date: '2026-04-25', result: { points: '110110', minutes: 55, date: '2026-04-27' } },
    { id: 's-2604', title: 'СтатГрад, тренировочная работа №5', kind: 'standard', publisher: 'statgrad', level: 'medium', tasks: 19, solved: 3870, date: '2026-04-16', result: { points: '1111111111112020200', minutes: 226, date: '2026-04-18' } },
    { id: 'a-17', title: 'Первая часть без ошибок №4', kind: 'drill', numbers: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], publisher: 'author', level: 'base', tasks: 12, solved: 1520, date: '2026-04-05' },
    { id: 'a-16', title: 'Гроб №4: стереометрия и планиметрия', kind: 'drill', numbers: [14, 17], publisher: 'author', level: 'coffin', tasks: 6, solved: 211, date: '2026-03-22' },
    { id: 's-2603', title: 'СтатГрад, тренировочная работа №4', kind: 'standard', publisher: 'statgrad', level: 'hard', tasks: 19, solved: 3410, date: '2026-03-12' },
    { id: 'a-15', title: 'Авторский вариант №15', kind: 'standard', publisher: 'author', level: 'medium', tasks: 19, solved: 1105, date: '2026-03-01', result: { points: '1111111111102020000', minutes: 231, date: '2026-03-04' } },
    { id: 'd-12', title: 'Исследование функции без производной', kind: 'drill', numbers: [12], publisher: 'author', level: 'medium', tasks: 10, solved: 468, date: '2026-02-20' },
    { id: 's-2602', title: 'СтатГрад, тренировочная работа №3', kind: 'standard', publisher: 'statgrad', level: 'medium', tasks: 19, solved: 2960, date: '2026-02-11' },
    { id: 'a-14', title: 'Первая часть без ошибок №3', kind: 'drill', numbers: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], publisher: 'author', level: 'base', tasks: 12, solved: 1730, date: '2026-02-01', result: { points: '111111110111', minutes: 24, date: '2026-02-03' } },
    { id: 's-2601', title: 'СтатГрад, тренировочная работа №2', kind: 'standard', publisher: 'statgrad', level: 'base', tasks: 19, solved: 2640, date: '2026-01-21' },
    { id: 'a-13', title: 'Гроб №3: задачи с параметром', kind: 'drill', numbers: [18], publisher: 'author', level: 'coffin', tasks: 5, solved: 96, date: '2026-01-10' },
    { id: 'a-12', title: 'Авторский вариант №12', kind: 'standard', publisher: 'author', level: 'hard', tasks: 19, solved: 1340, date: '2025-12-20', result: { points: '1101111011112000000', minutes: 195, date: '2025-12-22' } },
    { id: 's-2512', title: 'СтатГрад, диагностическая работа (декабрь)', kind: 'standard', publisher: 'statgrad', level: 'medium', tasks: 19, solved: 4480, date: '2025-12-10' },
];
