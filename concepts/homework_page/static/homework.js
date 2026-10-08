// Домашние задания (заглушка). Позже список будет приходить с сервера — его выдаёт преподаватель.
//
// topic:    раздел программы — подпись под названием
// numbers:  номера заданий ЕГЭ, из которых собрано ДЗ (задания берутся генератором из variants_page/tasks.js)
// tasks:    число задач
// deadline: срок сдачи, YYYY-MM-DD (до 23:59)
// status:   'current' | 'overdue' | 'done' — как во frontend; своя сданная попытка из браузера делает ДЗ выполненным
// answered: сколько задач уже решено в начатом ДЗ (заглушка) — первые answered задач подставляются с верными ответами
// result:   сданное ДЗ (заглушка): points — 1 верно / 0 неверно по задачам, minutes — сколько решали, date — когда сдано

window.HOMEWORK = [
    // Тестовое: короткое ДЗ — быстро пройти путь до результатов
    { id: 'hw-test', title: 'Тестовое ДЗ: 3 задачи', topic: 'Разное', numbers: [1, 4, 6], tasks: 3, deadline: '2026-10-20', status: 'current' },
    { id: 'hw-derivative', title: 'Производная сложной функции', topic: 'Начала анализа', numbers: [8, 12], tasks: 8, deadline: '2026-10-13', status: 'current' },
    { id: 'hw-trig', title: 'Тригонометрические уравнения', topic: 'Тригонометрия', numbers: [13], tasks: 10, deadline: '2026-10-15', status: 'current', answered: 3 },
    { id: 'hw-stereo', title: 'Стереометрия: сечения', topic: 'Геометрия', numbers: [3, 14], tasks: 6, deadline: '2026-10-18', status: 'current' },
    { id: 'hw-ineq', title: 'Неравенства: метод интервалов', topic: 'Алгебра', numbers: [15], tasks: 9, deadline: '2026-10-08', status: 'done', result: { points: '111101111', minutes: 47, date: '2026-10-07' } },
    { id: 'hw-circle', title: 'Планиметрия: углы окружности', topic: 'Геометрия', numbers: [1, 17], tasks: 7, deadline: '2026-10-05', status: 'overdue', answered: 2 },
];
