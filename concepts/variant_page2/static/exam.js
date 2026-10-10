// Общее для каталога и страницы решения: правила ЕГЭ, состав варианта, попытки, блок статистики.
// Подключается после variants.js и tasks.js.

const EXAM = {
    // Профильная математика: 19 заданий, первичные баллы за каждое
    points: { 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 2, 14: 3, 15: 2, 16: 2, 17: 3, 18: 4, 19: 4 },
    part1: 12,          // задания 1–12 — краткий ответ
    maxPrimary: 32,
    minutes: 235,       // 3 ч 55 мин
    // Перевод первичных баллов во вторичные (тестовые), индекс — первичный балл. Шкала ЕГЭ-2025
    scale: [0, 6, 11, 17, 22, 27, 34, 40, 46, 52, 58, 64, 70, 72, 74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 95, 96, 97, 98, 99, 100, 100, 100],
};

const ATTEMPTS_KEY = 'concept-variants2:attempts';

const $ = (id) => document.getElementById(id);
const icons = () => lucide.createIcons();

const plural = (n, one, few, many) => {
    const m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return one;
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
    return many;
};

const formatDate = (iso) =>
    new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' }).replace(' г.', '');

/** 1284 -> «1 284 ученика» */
const solvedLabel = (n) => `${n.toLocaleString('ru-RU')} ${plural(n, 'ученик', 'ученика', 'учеников')}`;

/** 14100 секунд -> «3 ч 55 мин» */
function formatDuration(seconds) {
    const m = Math.round(seconds / 60);
    const h = Math.floor(m / 60);
    if (!h) return `${m} мин`;
    return m % 60 ? `${h} ч ${m % 60} мин` : `${h} ч`;
}

/** Номера заданий ЕГЭ: [1,2,3,5] -> «1–3, 5» */
function formatNumbers(numbers) {
    const parts = [];
    for (let i = 0; i < numbers.length; i++) {
        let j = i;
        while (j + 1 < numbers.length && numbers[j + 1] === numbers[j] + 1) j++;
        parts.push(j - i >= 2 ? `${numbers[i]}–${numbers[j]}` : numbers.slice(i, j + 1).join(', '));
        i = j;
    }
    return parts.join(', ');
}

/** Текст с формулами в $...$ -> HTML. Тексты свои, из tasks.js, поэтому без санитайзера */
const tex = (src) => src.replace(/\$([^$]+)\$/g, (_, f) => katex.renderToString(f, { throwOnError: false }));

const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

// Строки результатов — аккордеон (<details name="review">): открылась одна, предыдущая закрылась.
// Если закрылся длинный разбор выше, открытая строка уезжает под липкую шапку — возвращаем её в поле зрения.
// toggle не всплывает, поэтому слушаем на захвате.
document.addEventListener('toggle', (e) => {
    const row = e.target;
    if (!row.matches?.('.review-row') || !row.open) return;
    const header = document.querySelector('.solve-top');
    const top = header ? header.getBoundingClientRect().bottom : 0;
    if (row.getBoundingClientRect().top < top) row.scrollIntoView({ block: 'start', behavior: 'smooth' });
}, true);

/** Раскрытая строка результатов: условие задания, разбор и верный ответ */
const taskReviewHtml = (t) => `<div class="review-body">
    <div class="review-text">${tex(t.text)}</div>
    <div class="review-solution">
        <p class="review-solution-title"><i data-lucide="lightbulb"></i>Решение</p>
        <div class="review-solution-text">${tex(t.solution ?? '')}</div>
        <p class="review-solution-answer">Ответ: <b>${String(t.answer).replace('.', ',')}</b></p>
    </div>
</div>`;

const variantById = (id) => window.VARIANTS.find((v) => v.id === id);
const isStandard = (v) => v.kind === 'standard';
const timeLimit = (v) => (isStandard(v) ? EXAM.minutes * 60 : null); // секунды; у отработки времени нет

/**
 * Задания варианта. Стандартный — по одному на номера 1–19, отработка — `tasks` заданий
 * по номерам из `numbers`, сгруппированные по номеру.
 * max — сколько баллов стоит задание: в стандартном первичные баллы ЕГЭ, в отработке 1 (верно / неверно).
 */
function tasksOf(v) {
    const numbers = isStandard(v)
        ? Object.keys(EXAM.points).map(Number)
        : Array.from({ length: v.tasks }, (_, i) => v.numbers[i % v.numbers.length]).sort((a, b) => a - b);
    return numbers.map((n, i) => ({ ...makeTask(n, `${v.id}:${i}`), max: isStandard(v) ? EXAM.points[n] : 1 }));
}

/** Ответ ученика совпадает с верным: «0,25» = «0.25» = «.25» */
function isCorrect(input, answer) {
    const x = Number(String(input ?? '').trim().replace(',', '.').replace(/\s/g, ''));
    return String(input ?? '').trim() !== '' && Number.isFinite(x) && Math.abs(x - answer) < 1e-6;
}

const toSecondary = (primary) => EXAM.scale[Math.min(primary, EXAM.maxPrimary)];

// ----------------------------------- попытки -----------------------------------
// Результат попытки: { points: [баллы по заданиям], answers?: [ответы], seconds, date, timeUp? }.
// У заглушек в variants.js points — строка цифр, ответов нет.

function loadAttempts() {
    try {
        const data = JSON.parse(localStorage.getItem(ATTEMPTS_KEY));
        return data && typeof data === 'object' ? data : {};
    } catch {
        return {};
    }
}

function saveAttempt(id, result) {
    const all = loadAttempts();
    all[id] = result;
    try { localStorage.setItem(ATTEMPTS_KEY, JSON.stringify(all)); } catch { /* приватный режим */ }
}

/** Последний результат варианта: своя попытка из браузера, иначе заглушка */
function resultOf(v) {
    const own = loadAttempts()[v.id];
    if (own) return own;
    if (!v.result) return null;
    return {
        points: [...v.result.points].map(Number),
        seconds: v.result.minutes * 60,
        date: v.result.date,
    };
}

/** Факты о варианте для стартовой страницы: [[название, значение], …] */
function variantFacts(v) {
    return isStandard(v)
        ? [
            ['Заданий', '19 — как на ЕГЭ'],
            ['Время', `${formatDuration(EXAM.minutes * 60)}, таймер`],
            ['Максимум', `${EXAM.maxPrimary} первичных = 100 баллов`],
            ['Решили', solvedLabel(v.solved)],
        ]
        : [
            ['Заданий', `${v.tasks} — ${v.numbers.length === 1 ? 'задание' : 'задания'} №${formatNumbers(v.numbers)}`],
            ['Время', 'Без ограничения'],
            ['Оценка', 'Верно / неверно по каждому'],
            ['Решили', solvedLabel(v.solved)],
        ];
}

function variantRules(v) {
    return isStandard(v)
        ? [
            'Часть 1 (задания 1–12) — краткий ответ, по 1 баллу.',
            'Часть 2 (задания 13–19) — 2–4 балла. В концепте проверяется только итоговый ответ.',
            'Таймер запустится, как только вы приступите. Когда время выйдет, вариант завершится сам.',
            'Попытку нельзя отложить: если закрыть или перезагрузить страницу, ответы пропадут.',
        ]
        : [
            'Отработка без таймера — решайте в своём темпе.',
            'Между заданиями можно свободно переключаться.',
            'Попытку нельзя отложить: если закрыть или перезагрузить страницу, ответы пропадут.',
            'После завершения — верные ответы и разбор по каждому заданию.',
        ];
}

/** Сводка: первичные/вторичные баллы или «верно из», по частям */
function summarize(v, result) {
    const tasks = tasksOf(v);
    const earned = result.points.reduce((s, p) => s + p, 0);
    const max = tasks.reduce((s, t) => s + t.max, 0);
    const sum = (from, to) => result.points.slice(from, to).reduce((s, p) => s + p, 0);
    return {
        tasks, earned, max,
        secondary: isStandard(v) ? toSecondary(earned) : null,
        part1: sum(0, EXAM.part1),
        part2: sum(EXAM.part1),
        percent: Math.round((earned / max) * 100),
    };
}

/** Короткая подпись результата для строки каталога */
function scoreLabel(v, result) {
    const s = summarize(v, result);
    return isStandard(v)
        ? `${s.secondary} ${plural(s.secondary, 'балл', 'балла', 'баллов')}`
        : `${s.earned} из ${s.max}`;
}

/**
 * Кольцо прогресса — как shared/ui/ProgressRing во frontend (вкладка «Статистика», «Домашние задания»):
 * одна дуга --primary со скруглёнными концами и свечением, дорожка --glass-border, в центре значение и подпись.
 * value — заполнение в процентах, center — крупный текст в середине.
 */
function progressRing(value, center, label, { size = 168, stroke = 12 } = {}) {
    const radius = (size - stroke) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (Math.min(Math.max(value, 0), 100) / 100) * circumference;
    const c = size / 2;
    return `<div class="ring" style="width:${size}px;height:${size}px" role="img" aria-label="${center} ${label}">
        <svg width="${size}" height="${size}" aria-hidden="true">
            <circle class="ring-bg" cx="${c}" cy="${c}" r="${radius}" stroke-width="${stroke}"></circle>
            <circle class="ring-progress" cx="${c}" cy="${c}" r="${radius}" stroke-width="${stroke}"
                stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"
                style="--ring-from:${circumference};--ring-to:${offset}"></circle>
        </svg>
        <div class="ring-content">
            <span class="ring-value">${center}</span>
            <span class="ring-label">${label}</span>
        </div>
    </div>`;
}

/** Легенда как в «Домашних заданиях»: круглая точка основного цвета или серая и «Подпись — число» */
const ringLegend = (items) => `<div class="ring-legend">
    ${items.map(([text, primary]) => `<div class="ring-legend-item">
        <span class="ring-dot${primary ? ' is-primary' : ''}"></span><span>${text}</span>
    </div>`).join('')}
</div>`;

/** Блок статистики попытки — в панели «Разбор» и на странице результатов */
function statsHtml(v, result) {
    const s = summarize(v, result);
    const limit = timeLimit(v);

    // Кольцо: стандартный — вторичные баллы ЕГЭ из 100, отработка — доля верно решённых заданий
    const correct = s.tasks.filter((t, i) => (result.points[i] ?? 0) >= t.max).length;
    const wrong = s.tasks.length - correct;
    const score = isStandard(v)
        ? `<div class="score">
                ${progressRing(s.secondary, s.secondary, `${plural(s.secondary, 'балл', 'балла', 'баллов')} ЕГЭ`)}
                ${ringLegend([
                    [`Набрано — ${s.secondary} из 100`, true],
                    [`Первичных — ${s.earned} из ${s.max}`, false],
                ])}
            </div>`
        : `<div class="score">
                ${progressRing(s.percent, `${s.percent}%`, 'решено верно')}
                ${ringLegend([
                    [`Верно — ${correct}`, true],
                    [`Неверно — ${wrong}`, false],
                ])}
            </div>`;

    const bar = (label, value, max) => `
        <div class="part">
            <div class="part-head"><span>${label}</span><b>${value} из ${max}</b></div>
            <div class="part-bar"><i style="width:${Math.round((value / max) * 100)}%"></i></div>
        </div>`;

    const parts = isStandard(v)
        ? bar('Часть 1 · задания 1–12', s.part1, EXAM.part1) + bar('Часть 2 · задания 13–19', s.part2, EXAM.maxPrimary - EXAM.part1)
        : '';

    const cells = s.tasks.map((t, i) => {
        const p = result.points[i] ?? 0;
        const cls = p >= t.max ? 'is-full' : p > 0 ? 'is-part' : 'is-zero';
        const label = isStandard(v) ? '' : `<small>№${t.number}</small>`;
        return `<span class="cell ${cls}" title="Задание ${i + 1} (№${t.number} ЕГЭ): ${p} из ${t.max}">
            <b>${i + 1}</b>${isStandard(v) ? `<small>${p}/${t.max}</small>` : label}</span>`;
    }).join('');

    const time = limit
        ? `${formatDuration(result.seconds)} из ${formatDuration(limit)}`
        : formatDuration(result.seconds);

    return `<div class="stats">
        ${score}
        <dl class="facts">
            <div><dt>Дата</dt><dd>${formatDate(result.date)}</dd></div>
            <div><dt>Время</dt><dd>${time}${result.timeUp ? ' · время вышло' : ''}</dd></div>
            <div class="facts-wide"><dt>Решили вариант</dt><dd>${solvedLabel(v.solved)}</dd></div>
        </dl>
        ${parts}
        <div class="cells-wrap">
            <p class="cells-title">По заданиям</p>
            <div class="cells">${cells}</div>
            <p class="cells-legend">
                <span><i class="is-full"></i>верно</span>
                ${isStandard(v) ? '<span><i class="is-part"></i>частично</span>' : ''}
                <span><i class="is-zero"></i>неверно или без ответа</span>
            </p>
        </div>
    </div>`;
}

// Тема — общая для всех концептов
function initThemeToggle() {
    $('theme-toggle')?.addEventListener('click', () => {
        const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
        document.documentElement.dataset.theme = next;
        try { localStorage.setItem('concept-theme', next); } catch { /* приватный режим */ }
    });
}
