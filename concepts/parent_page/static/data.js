/* Заглушка данных кабинета родителя. Генерируется по зерну — одинаково при каждой загрузке.

   window.PARENT = {
     today: 'YYYY-MM-DD',
     children: [{
       id, name, f (девочка — для окончаний), grade, examDate,
       subjects: [{ id, title, goal, planDone, planTotal, planBehind, mocks: [{date, score}], numbers: [{n, acc, tries}] }],
       days:     [{ date, minutes, lessons, tasks }]            — последние 56 дней, по возрастанию
       homework: [{ id, subject, title, due, status, score, total }] — status: done | work | late
       events:   [{ date, time, kind, subject, text }]           — лента, свежие сверху
     }]
   }
*/
(function () {
    let seed = 20261011;
    const rnd = () => ((seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296);
    const pick = (a) => a[Math.floor(rnd() * a.length)];

    const TODAY = new Date(2026, 9, 11);
    const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    const shift = (n) => { const d = new Date(TODAY); d.setDate(d.getDate() + n); return d; };

    const TOPICS = {
        math: ['Планиметрия', 'Векторы', 'Стереометрия', 'Вероятность', 'Сложная вероятность', 'Простейшие уравнения',
            'Вычисления', 'Производная', 'Прикладная задача', 'Текстовая задача', 'Графики функций', 'Исследование функции',
            'Уравнения (ч. 2)', 'Стереометрия (ч. 2)', 'Неравенства', 'Экономическая задача', 'Планиметрия (ч. 2)', 'Параметр', 'Теория чисел'],
        rus: ['Средства связи', 'Лексическое значение', 'Стилистика', 'Ударения', 'Паронимы', 'Лексические нормы',
            'Морфологические нормы', 'Синтаксические нормы', 'Корни', 'Приставки', 'Суффиксы', 'Окончания глаголов',
            'НЕ с разными частями речи', 'Слитно / раздельно', 'Н и НН', 'Пунктуация в ССП', 'Обособления', 'Вводные слова', 'Сочинение'],
        inf: ['Графы', 'Таблицы истинности', 'Поиск путей', 'Электронные таблицы', 'Кодирование', 'Алгоритмы',
            'Графика', 'Комбинаторика', 'Excel', 'Поиск в тексте', 'Объём информации', 'Редактор', 'Маски IP',
            'Системы счисления', 'Логика', 'Игры', 'Обработка чисел', 'Робот', 'Динамика'],
    };
    const TITLES = { math: 'Математика', rus: 'Русский', inf: 'Информатика' };

    function numbers(subject, base) {
        return TOPICS[subject].map((t, i) => {
            const hard = i >= 12 ? 0.28 : 0;
            const acc = Math.max(0.05, Math.min(0.98, base - hard + (rnd() - 0.5) * 0.45));
            return { n: i + 1, topic: t, acc: Math.round(acc * 100) / 100, tries: 4 + Math.floor(rnd() * 20) };
        });
    }

    function mocks(start, step, count) {
        const out = []; let s = start;
        for (let i = 0; i < count; i++) {
            out.push({ date: iso(shift(-7 * (count - 1 - i) - 2)), score: Math.round(s) });
            s += step + (rnd() - 0.45) * 6;
        }
        return out;
    }

    function days(activeRate, avgMin, dip) {
        const out = [];
        for (let i = 55; i >= 0; i--) {
            const d = shift(-i);
            const weekend = d.getDay() === 0 || d.getDay() === 6;
            const inDip = dip && i >= dip[0] && i <= dip[1];
            const active = !inDip && rnd() < (weekend ? activeRate - 0.25 : activeRate);
            const minutes = active ? Math.round(avgMin * (0.4 + rnd() * 1.1)) : 0;
            out.push({ date: iso(d), minutes, lessons: active ? Math.floor(minutes / 25) : 0, tasks: active ? Math.floor(minutes / 4) : 0 });
        }
        return out;
    }

    const HW = {
        math: ['Логарифмические уравнения', 'Производная и касательная', 'Стереометрия: объёмы', 'Вероятность: формула Бернулли', 'Текстовые задачи на движение', 'Тригонометрия: отбор корней'],
        rus: ['Н и НН в суффиксах', 'Пунктуация в ССП', 'Ударения: глаголы', 'Сочинение: проблема текста', 'Паронимы'],
        inf: ['Системы счисления', 'Электронные таблицы', 'Рекурсия в Python', 'Маски IP'],
    };

    function homework(subjects, lateCount) {
        const out = []; let id = 1;
        subjects.forEach((s) => HW[s].forEach((title, i) => {
            const offset = -20 + i * 5 + Math.floor(rnd() * 4);
            const total = 6 + Math.floor(rnd() * 6);
            let status = offset < 0 ? 'done' : 'work';
            out.push({ id: id++, subject: s, title, due: iso(shift(offset)), status, total, score: status === 'done' ? Math.round(total * (0.5 + rnd() * 0.5)) : null });
        }));
        out.filter((h) => h.status === 'done').slice(-lateCount).forEach((h) => { h.status = 'late'; h.score = null; });
        return out.sort((a, b) => a.due.localeCompare(b.due));
    }

    function events(child) {
        const out = [];
        const recent = child.days.slice(-14).filter((d) => d.minutes > 0);
        recent.forEach((d) => {
            const s = pick(child.subjects);
            const t = TOPICS[s.id];
            out.push({ date: d.date, time: `${17 + Math.floor(rnd() * 5)}:${String(Math.floor(rnd() * 60)).padStart(2, '0')}`, kind: 'lesson', subject: s.id,
                text: `${child.f ? 'Прошла' : 'Прошёл'} урок «${pick(t)}» — ${d.lessons || 1} ${d.lessons > 1 ? 'урока' : 'урок'}, ${d.minutes} мин` });
            if (rnd() < 0.45) out.push({ date: d.date, time: '21:' + String(Math.floor(rnd() * 50) + 10), kind: 'review', subject: s.id, text: `Быстрое повторение: ${8 + Math.floor(rnd() * 8)} из 15 верно` });
        });
        child.homework.filter((h) => h.status === 'done' && h.due >= iso(shift(-14))).forEach((h) => out.push({
            date: h.due, time: '20:15', kind: 'hw', subject: h.subject, text: `${child.f ? 'Сдала' : 'Сдал'} ДЗ «${h.title}» — ${h.score} из ${h.total}` }));
        child.homework.filter((h) => h.status === 'late').forEach((h) => out.push({
            date: h.due, time: '23:59', kind: 'late', subject: h.subject, text: `Просрочено ДЗ «${h.title}»` }));
        child.subjects.forEach((s) => {
            const m = s.mocks[s.mocks.length - 1], p = s.mocks[s.mocks.length - 2];
            out.push({ date: m.date, time: '14:00', kind: 'mock', subject: s.id, text: `Пробник: ${m.score} баллов (${m.score - p.score >= 0 ? '+' : ''}${m.score - p.score})` });
        });
        return out.sort((a, b) => (b.date + b.time).localeCompare(a.date + a.time));
    }

    function subject(id, goal, planDone, planTotal, planBehind, mk, base) {
        return { id, title: TITLES[id], goal, planDone, planTotal, planBehind, mocks: mk, numbers: numbers(id, base) };
    }

    const alexey = {
        id: 'alexey', name: 'Алексей', grade: '11 класс', examDate: '2027-06-01',
        subjects: [
            subject('math', 80, 41, 120, 0, mocks(52, 3.2, 8), 0.72),
            subject('rus', 85, 58, 110, 2, mocks(64, 1.6, 8), 0.78),
            subject('inf', 75, 22, 105, 5, mocks(48, 1.2, 6), 0.6),
        ],
        days: days(0.78, 48, [9, 11]),
    };
    alexey.homework = homework(['math', 'rus', 'inf'], 1);

    const masha = {
        id: 'masha', name: 'Маша', f: true, grade: '10 класс', examDate: '2028-06-01',
        subjects: [
            subject('math', 70, 18, 120, 7, mocks(38, 1.1, 5), 0.55),
            subject('rus', 80, 30, 110, 0, mocks(55, 2.4, 5), 0.74),
        ],
        days: days(0.5, 30, [0, 5]),
    };
    masha.homework = homework(['math', 'rus'], 3);

    [alexey, masha].forEach((c) => { c.events = events(c); });

    window.PARENT = { today: iso(TODAY), children: [alexey, masha] };
})();
