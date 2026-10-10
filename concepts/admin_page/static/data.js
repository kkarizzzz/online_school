// Админка преподавателя (заглушка): группы, ученики, выданные ДЗ и сдачи. Подключается после bank_page/static/bank.js.
// Всё генерируется по зерну — одинаково при каждой загрузке. Позже — с сервера.
//
// window.ADMIN = { TODAY, GROUPS, STUDENTS, HOMEWORK, SUBMISSIONS, MAX_POINTS }
// Student:    { id, name, group, lastSeen (дней назад), mastery: { [n]: 0..1 } } — точность по номерам ЕГЭ
// Homework:   { id, title, topic, tasks: [taskId], groups: [groupId], students: [studentId], deadline, created, options }
// Submission: SUBMISSIONS[`${hwId}:${studentId}`] = { status, date, late, minutes, results: { [taskId]: Result } }
//   status — 'none' | 'progress' | 'submitted'
//   Result — { points, max, pending } — часть 2: pending, пока преподаватель не проверил; часть 1: points 0/1 автоматически

(() => {
    function rng(seed) {
        let h = 1779033703 ^ seed.length;
        for (let i = 0; i < seed.length; i++) {
            h = Math.imul(h ^ seed.charCodeAt(i), 3432918353);
            h = (h << 13) | (h >>> 19);
        }
        let a = h >>> 0;
        return () => {
            a = (a + 0x6D2B79F5) | 0;
            let t = Math.imul(a ^ (a >>> 15), 1 | a);
            t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
            return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
    }

    const TODAY = new Date('2026-10-09T12:00:00');
    const day = (offset) => new Date(TODAY.getTime() + offset * 86400000).toISOString().slice(0, 10);
    const clamp = (x) => Math.max(0.03, Math.min(0.98, x));

    // Первичные баллы за номер: часть 1 — 1 балл, часть 2 — по критериям ЕГЭ
    const MAX_POINTS = { 13: 2, 14: 3, 15: 2, 16: 2, 17: 3, 18: 4, 19: 4 };
    const maxOf = (n) => MAX_POINTS[n] || 1;

    const GROUPS = [
        { id: 'g-11a', name: '11А · пн, чт', color: 'b1' },
        { id: 'g-11b', name: '11Б · вт, пт', color: 'b2' },
        { id: 'g-ind', name: 'Индивидуально', color: 'b4' },
    ];

    const NAMES = [
        ['Алина Котова', 'g-11a'], ['Артём Белов', 'g-11a'], ['Вероника Сафина', 'g-11a'], ['Глеб Орлов', 'g-11a'],
        ['Дарья Миронова', 'g-11a'], ['Егор Лапин', 'g-11a'], ['Злата Руденко', 'g-11a'],
        ['Илья Ганиев', 'g-11b'], ['Кира Волкова', 'g-11b'], ['Лев Сорокин', 'g-11b'], ['Мария Ефимова', 'g-11b'],
        ['Никита Пак', 'g-11b'], ['Полина Зуева', 'g-11b'],
        ['Роман Исаев', 'g-ind'], ['София Ткач', 'g-ind'],
    ];

    const STUDENTS = NAMES.map(([name, group], i) => {
        const r = rng(`student:${i}`);
        const skill = 0.5 + r() * 0.45;
        const mastery = {};
        for (let n = 1; n <= 19; n++) {
            // Вторая часть даётся тяжелее, чем первая
            const drop = n <= 12 ? 0 : 0.1 + (n - 13) * 0.04;
            mastery[n] = Number(clamp(skill - drop + (r() - 0.5) * 0.3).toFixed(2));
        }
        return { id: `s${i + 1}`, name, group, lastSeen: Math.floor(r() * r() * 12), mastery };
    });

    // Задачи ДЗ берутся из банка по номерам — по зерну ДЗ
    function pickTasks(hwId, plan) {
        const r = rng(`hw:${hwId}`);
        return plan.flatMap(([n, count]) => {
            const pool = window.BANK.find((b) => b.n === n).topics.flatMap((t) => t.tasks);
            const out = [];
            while (out.length < count && out.length < pool.length) {
                const t = pool[Math.floor(r() * pool.length)];
                if (!out.includes(t.id)) out.push(t.id);
            }
            return out;
        });
    }

    const SEED = [
        { id: 'hw-ineq', title: 'Неравенства: метод интервалов', topic: 'Алгебра', plan: [[15, 3], [6, 3]], groups: ['g-11a', 'g-11b'], deadline: -1, created: -8 },
        { id: 'hw-circle', title: 'Планиметрия: углы окружности', topic: 'Геометрия', plan: [[1, 5], [17, 1]], groups: ['g-11b'], deadline: -4, created: -11 },
        { id: 'hw-derivative', title: 'Производная сложной функции', topic: 'Начала анализа', plan: [[8, 4], [12, 4]], groups: ['g-11a', 'g-11b', 'g-ind'], deadline: 4, created: -3 },
        { id: 'hw-trig', title: 'Тригонометрические уравнения', topic: 'Тригонометрия', plan: [[6, 2], [13, 3]], groups: ['g-11a'], deadline: 6, created: -2 },
        { id: 'hw-stereo', title: 'Стереометрия: сечения', topic: 'Геометрия', plan: [[3, 4], [14, 2]], groups: ['g-ind'], deadline: 9, created: -1 },
    ];

    const HOMEWORK = SEED.map((s) => ({
        id: s.id, title: s.title, topic: s.topic,
        tasks: pickTasks(s.id, s.plan),
        groups: s.groups, students: [],
        deadline: day(s.deadline), created: day(s.created),
        options: { showAnswers: true, allowLate: true },
    }));

    const n = (taskId) => Number(taskId.split('-')[0]);

    /** Срок ДЗ в днях от сегодня */
    const dl = (hw) => Math.round((new Date(hw.deadline + 'T12:00') - TODAY) / 86400000);

    const SUBMISSIONS = {};
    for (const hw of HOMEWORK) {
        const passed = new Date(hw.deadline + 'T23:59') < TODAY;
        const roster = STUDENTS.filter((s) => hw.groups.includes(s.group));
        for (const st of roster) {
            const r = rng(`sub:${hw.id}:${st.id}`);
            const x = r();
            const status = passed ? (x < 0.82 ? 'submitted' : x < 0.92 ? 'progress' : 'none')
                : (x < 0.4 ? 'submitted' : x < 0.65 ? 'progress' : 'none');
            const results = {};
            const done = status === 'submitted' ? hw.tasks.length : status === 'progress' ? Math.floor(r() * hw.tasks.length) : 0;
            hw.tasks.slice(0, done).forEach((id) => {
                const max = maxOf(n(id));
                const p = st.mastery[n(id)];
                if (max === 1) {
                    results[id] = { points: r() < p ? 1 : 0, max, pending: false };
                } else {
                    // Часть 2: свежие сдачи ещё не проверены
                    const pending = status === 'submitted' && r() < (passed ? 0.35 : 0.8);
                    results[id] = { points: pending ? null : Math.round(max * Math.min(1, p * (0.6 + r() * 0.6))), max, pending };
                }
            });
            const lateDays = passed && status === 'submitted' && r() < 0.15 ? 1 + Math.floor(r() * 2) : 0;
            SUBMISSIONS[`${hw.id}:${st.id}`] = {
                status, results,
                late: lateDays > 0,
                // Сдано за 0–2 дня до срока (или на 1–2 дня позже), текущие — сегодня или вчера
                date: status === 'submitted' ? day(passed ? dl(hw) - Math.floor(r() * 3) * !lateDays + lateDays : -Math.floor(r() * 2)) : null,
                minutes: status === 'submitted' ? 15 + Math.floor(r() * 60) : null,
            };
        }
    }

    window.ADMIN = { TODAY, GROUPS, STUDENTS, HOMEWORK, SUBMISSIONS, MAX_POINTS, maxOf };
})();
