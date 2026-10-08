// «Выпускникам»: план по месяцам, карта номеров, калькулятор баллов, отсчёт недель.
// Подключается перед main.js: рисует блоки, а иконки и появление включает main.js.

(() => {
const BANK = '../../bank_page/static/index.html';
const EXAM = new Date('2027-06-01T10:00:00+03:00'); // та же дата, что в main.js
const SESSIONS_PER_WEEK = 3;

// Этапы плана. months — месяцы учебного года (0 — январь), tabs — вкладки кабинета на этом этапе
const PLAN = [
    { months: [8, 9], when: 'Сентябрь — октябрь', title: 'Фундамент', text: 'Номера 1–7: планиметрия, векторы, вероятность, уравнения и вычисления. Самые быстрые баллы.', tabs: ['Теория', 'ДЗ'] },
    { months: [10, 11], when: 'Ноябрь — декабрь', title: 'Вся первая часть', text: 'Номера 8–12 — производная, графики, текстовые задачи. В конце — первый пробник первой части.', tabs: ['Банк', 'Нарешка'] },
    { months: [0, 1], when: 'Январь — февраль', title: 'Вторая часть', text: 'Номера 13, 15 и 16: уравнения, неравенства и экономика — по 2 балла каждый.', tabs: ['Теория', 'ДЗ', 'Банк'] },
    { months: [2, 3], when: 'Март — апрель', title: 'Варианты на время', text: 'Полный вариант каждую неделю, разбор ошибок по номерам. Кто готов — берёт 14, 17 и 18.', tabs: ['Варианты'] },
    { months: [4, 5], when: 'Май — июнь', title: 'Финиш', text: 'Повторение формул и слабых номеров, последние пробники в формате экзамена. Без новых тем.', tabs: ['Повторение', 'Варианты'] },
];

// Номера профильного ЕГЭ: название и первичный балл
const TASKS = [
    { n: 1, title: 'Планиметрия', pts: 1 },
    { n: 2, title: 'Векторы', pts: 1 },
    { n: 3, title: 'Стереометрия', pts: 1 },
    { n: 4, title: 'Простая вероятность', pts: 1 },
    { n: 5, title: 'Сложная вероятность', pts: 1 },
    { n: 6, title: 'Простейшие уравнения', pts: 1 },
    { n: 7, title: 'Вычисления и преобразования', pts: 1 },
    { n: 8, title: 'Производная и первообразная', pts: 1 },
    { n: 9, title: 'Прикладная задача', pts: 1 },
    { n: 10, title: 'Текстовая задача', pts: 1 },
    { n: 11, title: 'Графики функций', pts: 1 },
    { n: 12, title: 'Наибольшее и наименьшее значение', pts: 1 },
    { n: 13, title: 'Уравнения', pts: 2 },
    { n: 14, title: 'Стереометрия', pts: 3 },
    { n: 15, title: 'Неравенства', pts: 2 },
    { n: 16, title: 'Экономическая задача', pts: 2 },
    { n: 17, title: 'Планиметрия', pts: 3 },
    { n: 18, title: 'Задача с параметром', pts: 4 },
    { n: 19, title: 'Числа и их свойства', pts: 4 },
];

// Порядок, в котором баллы набираются легче всего: часть 1 подряд, потом «доступные» номера части 2
const EASIEST_ORDER = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 15, 19, 14, 17, 18];

// Перевод первичных баллов в тестовые — шкала ЕГЭ 2025, индекс = первичный балл
const SCALE = [0, 6, 11, 17, 22, 27, 34, 40, 46, 52, 58, 64, 70, 72, 74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 95, 96, 97, 98, 99, 100, 100, 100];

const DAY = 24 * 60 * 60 * 1000;

function plural(n, one, few, many) {
    const m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return one;
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
    return many;
}

function renderClock() {
    const days = Math.max(0, Math.ceil((EXAM - Date.now()) / DAY));
    const weeks = Math.floor(days / 7);
    document.getElementById('clock-days').textContent = plural(days, 'день', 'дня', 'дней');
    document.getElementById('clock-weeks').textContent = weeks;
    document.getElementById('clock-weeks-label').textContent = plural(weeks, 'неделя', 'недели', 'недель');
    document.getElementById('clock-lessons').textContent = weeks * SESSIONS_PER_WEEK;
}

function renderPlan() {
    // Учебный год начинается в сентябре: индекс месяца от сентября
    const schoolIdx = (m) => (m - 8 + 12) % 12;
    const now = schoolIdx(new Date().getMonth());

    document.getElementById('plan-list').innerHTML = PLAN.map((stage, i) => {
        const [from, to] = stage.months.map(schoolIdx);
        const state = now > to ? 'is-past' : now >= from ? 'is-now' : '';
        return `
        <li class="card plan-item reveal ${state}" style="--d:${i * 70}ms">
            ${state === 'is-now' ? '<span class="chip chip-primary plan-now">Сейчас</span>' : ''}
            <span class="plan-when">${stage.when}</span>
            <h4>${stage.title}</h4>
            <p>${stage.text}</p>
            <div class="plan-tabs">${stage.tabs.map((t) => `<span class="chip chip-primary">${t}</span>`).join('')}</div>
        </li>`;
    }).join('');
}

function renderMap() {
    const cell = (t) => `
        <a class="card map-cell ${t.n > 12 ? 'part2' : ''}" href="${BANK}?n=${t.n}">
            <span class="n"><b>${t.n}</b><span>${t.pts} ${plural(t.pts, 'балл', 'балла', 'баллов')}</span></span>
            <span class="t">${t.title}</span>
        </a>`;
    document.getElementById('map-part1').innerHTML = TASKS.filter((t) => t.n <= 12).map(cell).join('');
    document.getElementById('map-part2').innerHTML = TASKS.filter((t) => t.n > 12).map(cell).join('');
}

// Раскладывает первичные баллы по номерам в порядке EASIEST_ORDER: { n: набрано }
function distribute(primary) {
    const got = {};
    let left = primary;
    for (const n of EASIEST_ORDER) {
        const pts = TASKS[n - 1].pts;
        got[n] = Math.min(pts, left);
        left -= got[n];
    }
    return got;
}

function hintFor(primary, got) {
    if (primary === 0) return 'Ноль — это старт, а не приговор. Первые 5 номеров обычно закрываются за полтора месяца.';
    const full = TASKS.filter((t) => got[t.n] === t.pts).map((t) => t.n);
    const part1 = full.filter((n) => n <= 12);
    const part2 = full.filter((n) => n > 12);
    const partial = TASKS.filter((t) => got[t.n] > 0 && got[t.n] < t.pts).map((t) => t.n);

    let text = part1.length === 12
        ? 'Вся первая часть без ошибок'
        : `Номера ${part1.length > 1 ? `1–${part1.length}` : '1'} без ошибок`;
    if (part2.length) text += `, плюс полностью № ${part2.join(', ')}`;
    if (partial.length) text += `${part2.length ? ' и' : ', плюс'} часть баллов за № ${partial.join(', ')}`;
    text += '.';
    if (primary < 12) text += ' Дальше самые дешёвые баллы — оставшиеся номера первой части.';
    else if (primary < 20) text += ' Следующий шаг — номера 15 и 16: по 2 балла за понятные алгоритмы.';
    else if (primary < 32) text += ' Здесь уже решают параметр и числа — без них к 100 не подойти.';
    else text += ' Это 100 баллов. Мы в вас верим.';
    return text;
}

function initCalc() {
    const range = document.getElementById('calc-range');
    const bar = document.getElementById('calc-bar');
    bar.innerHTML = TASKS.map((t) => `<i class="${t.n > 12 ? 'part2' : ''}" title="№ ${t.n}"></i>`).join('');
    const cells = [...bar.children];

    const update = () => {
        const primary = Number(range.value);
        const got = distribute(primary);
        document.getElementById('calc-prim').textContent = primary;
        document.getElementById('calc-test').textContent = SCALE[primary];
        cells.forEach((c, i) => {
            const t = TASKS[i];
            c.classList.toggle('on', got[t.n] === t.pts);
            c.classList.toggle('half', got[t.n] > 0 && got[t.n] < t.pts);
        });
        document.getElementById('calc-hint').textContent = hintFor(primary, got);
    };
    range.addEventListener('input', update);
    update();
}

renderClock();
renderPlan();
renderMap();
initCalc();
})();
