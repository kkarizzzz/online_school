// «Выпускникам»: таймер до экзамена и переключатель предмета, от которого зависят план по месяцам,
// карта номеров и калькулятор баллов. Выбранный предмет — в адресе (?subject=russian).
// Подключается перед main.js: рисует блоки, а иконки и появление включает main.js.

(() => {
const BANK = '../../bank_page/static/index.html'; // банк заданий в концептах пока только по математике
const EXAM = new Date('2027-06-01T10:00:00+03:00'); // та же дата, что в main.js
const SESSIONS_PER_WEEK = 3;

// Месяцы этапов плана (0 — январь) — общие для всех предметов
const STAGES = [
    { months: [8, 9], when: 'Сентябрь — октябрь' },
    { months: [10, 11], when: 'Ноябрь — декабрь' },
    { months: [0, 1], when: 'Январь — февраль' },
    { months: [2, 3], when: 'Март — апрель' },
    { months: [4, 5], when: 'Май — июнь' },
];

// Номера экзамена: [название, первичные баллы]. Номер = индекс + 1
const task = (title, pts = 1) => ({ title, pts });

// Предметы. Структура и шкалы — ЕГЭ 2026 (спецификации ФИПИ, шкалы Рособрнадзора).
//   parts — группы номеров на карте: [название, подпись, с какого номера, по какой];
//   order — порядок, в котором баллы набираются легче всего: номер или [номер, сколько баллов взять на этом шаге];
//   scale — тестовый балл, индекс = первичный балл;
//   plan — по шагу на каждый этап STAGES, tabs — вкладки кабинета, на которых держится шаг.
const SUBJECTS = [
    {
        id: 'math', label: 'Математика', icon: 'sigma', name: 'профильной математике', bank: true,
        facts: [['19', 'заданий'], ['32', 'первичных балла'], ['3 ч 55 мин', 'на экзамен'], ['12 + 7', 'часть 1 + часть 2']],
        tasks: [
            task('Планиметрия'), task('Векторы'), task('Стереометрия'), task('Простая вероятность'), task('Сложная вероятность'),
            task('Простейшие уравнения'), task('Вычисления и преобразования'), task('Производная и первообразная'),
            task('Прикладная задача'), task('Текстовая задача'), task('Графики функций'), task('Наибольшее и наименьшее значение'),
            task('Уравнения', 2), task('Стереометрия', 3), task('Неравенства', 2), task('Экономическая задача', 2),
            task('Планиметрия', 3), task('Задача с параметром', 4), task('Числа и их свойства', 4),
        ],
        parts: [['Часть 1', 'краткий ответ · по 1 баллу', 1, 12], ['Часть 2', 'развёрнутый ответ · 2–4 балла', 13, 19]],
        order: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 15, 19, 14, 17, 18],
        scale: [0, 6, 11, 17, 22, 27, 34, 40, 46, 52, 58, 64, 70, 72, 74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 95, 96, 97, 98, 99, 100, 100, 100],
        plan: [
            { title: 'Фундамент', text: 'Номера 1–7: планиметрия, векторы, вероятность, уравнения и вычисления. Самые быстрые баллы.', tabs: ['Теория', 'ДЗ'] },
            { title: 'Вся первая часть', text: 'Номера 8–12 — производная, графики, текстовые задачи. В конце — первый пробник первой части.', tabs: ['Банк', 'Нарешка'] },
            { title: 'Вторая часть', text: 'Номера 13, 15 и 16: уравнения, неравенства и экономика — по 2 балла каждый.', tabs: ['Теория', 'ДЗ', 'Банк'] },
            { title: 'Варианты на время', text: 'Полный вариант каждую неделю, разбор ошибок по номерам. Кто готов — берёт 14, 17 и 18.', tabs: ['Варианты'] },
            { title: 'Финиш', text: 'Повторение формул и слабых номеров, последние пробники в формате экзамена. Без новых тем.', tabs: ['Повторение', 'Варианты'] },
        ],
    },
    {
        id: 'russian', label: 'Русский язык', icon: 'book-open', name: 'русскому языку',
        facts: [['27', 'заданий'], ['50', 'первичных баллов'], ['3 ч 30 мин', 'на экзамен'], ['26 + 1', 'тест + сочинение']],
        tasks: [
            task('Смысл текста'), task('Лексическое значение'), task('Стилистика текста'), task('Ударения'), task('Паронимы'),
            task('Лексические нормы'), task('Формы слов'), task('Грамматические ошибки', 2), task('Корни'), task('Приставки'),
            task('Суффиксы'), task('Окончания глаголов и причастий'), task('НЕ с разными частями речи'),
            task('Слитно, раздельно, через дефис'), task('Н и НН'), task('Однородные члены и ССП'), task('Обособления'),
            task('Вводные слова и обращения'), task('Сложноподчинённое предложение'), task('Разные виды связи'),
            task('Пунктуационный анализ'), task('Смысловой анализ текста', 2), task('Типы речи'), task('Лексика текста'),
            task('Средства связи'), task('Средства выразительности'), task('Сочинение', 22),
        ],
        parts: [['Тестовая часть', 'краткий ответ · 28 баллов', 1, 26], ['Сочинение', 'развёрнутый ответ · 22 балла', 27, 27]],
        order: [[27, 12], 4, 9, 10, 11, 12, 13, 14, 15, 2, 5, 6, 7, 1, 3, 16, 18, 17, 19, 23, 24, 25, 8, 26, 20, 21, 22, 27],
        scale: [0, 3, 5, 8, 10, 12, 15, 17, 20, 22, 24, 27, 29, 32, 34, 36, 37, 39, 40, 42, 43, 45, 46, 48, 49, 51,
            52, 54, 55, 57, 58, 60, 61, 63, 64, 66, 67, 69, 70, 70, 73, 75, 78, 81, 83, 86, 89, 91, 94, 97, 100],
        plan: [
            { title: 'Орфография', text: 'Корни, приставки, суффиксы, Н и НН, НЕ с разными частями речи — самый большой блок теста.', tabs: ['Теория', 'Нарешка'] },
            { title: 'Пунктуация', text: 'Сложные предложения, обособления, вводные слова. Правило — серия коротких роликов, дальше задания.', tabs: ['Теория', 'Банк'] },
            { title: 'Текст и сочинение', text: 'Задания по тексту, речевые нормы и сочинение по критериям: одно в неделю с проверкой.', tabs: ['ДЗ', 'Банк'] },
            { title: 'Варианты на время', text: 'Тест плюс сочинение за 3,5 часа каждую неделю — чтобы хватало времени на черновик.', tabs: ['Варианты'] },
            { title: 'Финиш', text: 'Повторение правил и исключений, сочинения на свежих текстах. Без новых тем.', tabs: ['Повторение', 'Варианты'] },
        ],
    },
    {
        id: 'informatics', label: 'Информатика', icon: 'terminal', name: 'информатике',
        facts: [['27', 'заданий'], ['29', 'первичных баллов'], ['3 ч 55 мин', 'на экзамен'], ['КЕГЭ', 'на компьютере']],
        tasks: [
            task('Графы и таблицы'), task('Таблицы истинности'), task('Базы данных'), task('Кодирование'), task('Анализ алгоритма'),
            task('Исполнитель Черепаха'), task('Изображения и звук'), task('Комбинаторика'), task('Электронные таблицы'),
            task('Поиск в тексте'), task('Объём информации'), task('Исполнитель Редактор'), task('IP-адреса и маски'),
            task('Системы счисления'), task('Логические выражения'), task('Рекурсия'), task('Последовательности'),
            task('Динамика в таблице'), task('Теория игр: ход'), task('Теория игр: стратегия'), task('Теория игр: анализ'),
            task('Параллельные процессы'), task('Число программ'), task('Обработка строк'), task('Делители и маски чисел'),
            task('Сортировка данных', 2), task('Анализ данных', 2),
        ],
        parts: [['Основные задания', 'по 1 баллу', 1, 25], ['Программирование', 'по 2 балла', 26, 27]],
        order: [1, 2, 4, 7, 9, 10, 11, 14, 3, 5, 6, 8, 12, 13, 15, 16, 17, 19, 20, 21, 23, 25, 18, 22, 24, 26, 27],
        scale: [0, 7, 14, 20, 27, 34, 40, 43, 46, 48, 51, 54, 56, 59, 62, 64, 67, 70, 72, 75, 78, 80, 83, 85, 88, 90, 93, 95, 98, 100],
        plan: [
            { title: 'Фундамент', text: 'Системы счисления, логика, графы, Excel — задания, которые решаются без программирования.', tabs: ['Теория', 'ДЗ'] },
            { title: 'Python с нуля', text: 'Переменные, циклы, функции и первые задачи ЕГЭ, которые проще решить кодом, чем руками.', tabs: ['Теория', 'Нарешка'] },
            { title: 'Сложные задачи', text: 'Рекурсия, динамика, обработка файлов и теория игр — задания конца варианта.', tabs: ['Банк', 'ДЗ'] },
            { title: 'Варианты на время', text: 'Полный вариант в компьютерной форме, как на КЕГЭ: свой редактор, файлы, ответы в таблицу.', tabs: ['Варианты'] },
            { title: 'Финиш', text: 'Шаблоны решений по каждому номеру и разбор своих типичных ошибок. Без новых тем.', tabs: ['Повторение', 'Варианты'] },
        ],
    },
    {
        id: 'physics', label: 'Физика', icon: 'atom', name: 'физике',
        facts: [['26', 'заданий'], ['45', 'первичных баллов'], ['3 ч 55 мин', 'на экзамен'], ['20 + 6', 'часть 1 + часть 2']],
        tasks: [
            task('Кинематика'), task('Динамика'), task('Законы сохранения'), task('Колебания и статика'),
            task('Механика: анализ процесса', 2), task('Механика: изменение величин', 2), task('МКТ'), task('Термодинамика'),
            task('Молекулярка: анализ процесса', 2), task('Молекулярка: изменение величин', 2), task('Электрическое поле'),
            task('Постоянный ток'), task('Магнитное поле и индукция'), task('Электродинамика: анализ', 2),
            task('Электродинамика: изменение величин', 2), task('Квантовая физика'), task('Кванты: изменение величин', 2),
            task('Обобщение по разделам', 2), task('Измерения и погрешности'), task('Планирование опыта'),
            task('Качественная задача', 3), task('Расчётная задача', 2), task('Расчётная задача', 2),
            task('Расчётная задача', 3), task('Расчётная задача', 3), task('Механика с обоснованием', 4),
        ],
        parts: [['Часть 1', 'краткий ответ · 1–2 балла', 1, 20], ['Часть 2', 'развёрнутый ответ · 2–4 балла', 21, 26]],
        order: [1, 2, 3, 7, 8, 11, 12, 13, 16, 19, 20, 4, 5, 6, 9, 10, 14, 15, 17, 18, 22, 23, 24, 25, 21, 26],
        scale: [0, 5, 9, 14, 18, 23, 27, 32, 36, 39, 41, 43, 44, 46, 48, 49, 51, 53, 54, 56, 58, 59, 61, 62, 64, 65,
            67, 68, 70, 71, 73, 74, 76, 77, 79, 80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100],
        plan: [
            { title: 'Механика', text: 'Кинематика, динамика, законы сохранения — основа почти половины варианта.', tabs: ['Теория', 'ДЗ'] },
            { title: 'Молекулярка и электричество', text: 'МКТ, термодинамика, электростатика и цепи постоянного тока.', tabs: ['Теория', 'Банк'] },
            { title: 'Магнетизм, оптика, кванты', text: 'Оставшиеся разделы и первые расчётные задачи второй части.', tabs: ['Теория', 'Нарешка'] },
            { title: 'Варианты на время', text: 'Полный вариант каждую неделю, вторая часть — с экспертной проверкой по критериям.', tabs: ['Варианты'] },
            { title: 'Финиш', text: 'Повторение формул по разделам и качественные задачи. Без новых тем.', tabs: ['Повторение', 'Варианты'] },
        ],
    },
];

const $ = (id) => document.getElementById(id);
const maxOf = (subject) => subject.tasks.reduce((s, t) => s + t.pts, 0);

function plural(n, one, few, many) {
    const m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return one;
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
    return many;
}

const pointsWord = (n) => plural(n, 'балл', 'балла', 'баллов');

// ===================================== таймер =====================================

function tickClock() {
    const left = Math.max(0, EXAM - Date.now());
    const parts = {
        days: [Math.floor(left / 864e5), ['день', 'дня', 'дней']],
        hours: [Math.floor(left / 36e5) % 24, ['час', 'часа', 'часов']],
        mins: [Math.floor(left / 6e4) % 60, ['минута', 'минуты', 'минут']],
        secs: [Math.floor(left / 1e3) % 60, ['секунда', 'секунды', 'секунд']],
    };
    for (const [key, [value, words]] of Object.entries(parts)) {
        $(`t-${key}`).textContent = key === 'days' ? value : String(value).padStart(2, '0');
        $(`t-${key}-label`).textContent = plural(value, ...words);
    }
    const weeks = Math.floor(parts.days[0] / 7);
    $('clock-sum').textContent = `≈ ${weeks} ${plural(weeks, 'неделя', 'недели', 'недель')} — это ${weeks * SESSIONS_PER_WEEK} занятий на предмет при трёх в неделю`;
}

// ===================================== план =====================================

// Формат экзамена и пять шагов плана. Без .reveal: блок перерисовывается при смене предмета
function renderPlan(subject) {
    // Учебный год начинается в сентябре: индекс месяца от сентября
    const schoolIdx = (m) => (m - 8 + 12) % 12;
    const now = schoolIdx(new Date().getMonth());

    $('exam-facts').innerHTML = subject.facts.map(([value, label]) => `<div><b>${value}</b><span>${label}</span></div>`).join('');

    $('plan-list').innerHTML = STAGES.map((stage, i) => {
        const step = subject.plan[i];
        const [from, to] = stage.months.map(schoolIdx);
        const state = now > to ? 'is-past' : now >= from ? 'is-now' : '';
        return `
        <li class="card plan-item ${state}">
            <span class="plan-top">
                <span class="plan-when">${stage.when}</span>
                ${state === 'is-now' ? '<span class="chip chip-primary plan-now">Сейчас</span>' : ''}
            </span>
            <h4>${step.title}</h4>
            <p>${step.text}</p>
            <div class="plan-tabs">${step.tabs.map((t) => `<span class="chip chip-primary">${t}</span>`).join('')}</div>
        </li>`;
    }).join('');
}

// ===================================== карта =====================================

function renderMap(subject) {
    const total = subject.tasks.length;
    const max = maxOf(subject);
    $('map-title').innerHTML = `${total} ${plural(total, 'номер', 'номера', 'номеров')},<br><span class="accent">${max}</span> первичных ${pointsWord(max)}.`;
    $('map-lead').textContent = subject.bank
        ? 'Клик по номеру открывает его в банке заданий: все прототипы с разбивкой по темам.'
        : 'Под каждый номер в кабинете — уроки, прототипы в банке и нарешка. Чем больше баллов за номер, тем ярче рамка.';

    $('map-parts').innerHTML = subject.parts.map(([title, caption, from, to], partIdx) => {
        const cells = subject.tasks.slice(from - 1, to).map((t, i) => {
            const n = from + i;
            const tag = subject.bank ? 'a' : 'div';
            const href = subject.bank ? ` href="${BANK}?n=${n}"` : '';
            return `
            <${tag} class="card map-cell ${partIdx ? 'part2' : ''}"${href} style="--w:${Math.min(t.pts, 4)}">
                <span class="n"><b>${n}</b><span>${t.pts} ${pointsWord(t.pts)}</span></span>
                <span class="t">${t.title}</span>
            </${tag}>`;
        }).join('');
        return `
        <div class="map-part">
            <h3>${title} <small>№ ${from === to ? from : `${from}–${to}`} · ${caption}</small></h3>
            <div class="map-grid">${cells}</div>
        </div>`;
    }).join('');
}

// ===================================== калькулятор =====================================

// Раскладывает первичные баллы по номерам в порядке subject.order: { номер: набрано }
function distribute(subject, primary) {
    const got = {};
    let left = primary;
    for (const step of subject.order) {
        const [n, chunk] = Array.isArray(step) ? step : [step, Infinity];
        const room = subject.tasks[n - 1].pts - (got[n] ?? 0);
        const take = Math.min(room, chunk, left);
        got[n] = (got[n] ?? 0) + take;
        left -= take;
    }
    return got;
}

/** [1,2,3,5,7,8] -> «1–3, 5, 7–8» */
function ranges(nums) {
    const out = [];
    for (const n of nums) {
        const last = out.at(-1);
        if (last && n === last[1] + 1) last[1] = n; else out.push([n, n]);
    }
    return out.map(([a, b]) => (a === b ? `${a}` : `${a}–${b}`)).join(', ');
}

function hintFor(subject, primary, got) {
    const max = maxOf(subject);
    if (primary === 0) return 'Ноль — это старт, а не приговор. Первые номера обычно закрываются за полтора месяца.';
    if (primary === max) return 'Это все баллы экзамена — 100 тестовых. Мы в вас верим.';

    const full = subject.tasks.map((t, i) => i + 1).filter((n) => got[n] === subject.tasks[n - 1].pts);
    const partial = subject.tasks.map((t, i) => i + 1).filter((n) => got[n] > 0 && got[n] < subject.tasks[n - 1].pts);

    let text = full.length ? `Без ошибок: № ${ranges(full)}` : 'Пока ни одного номера целиком';
    if (partial.length) {
        text += `; частично: ${partial.map((n) => `№ ${n} — ${got[n]} из ${subject.tasks[n - 1].pts}`).join(', ')}`;
    }
    return `${text}.`;
}

let calcSubject = null;

function updateCalc() {
    const subject = calcSubject;
    const primary = Number($('calc-range').value);
    const got = distribute(subject, primary);
    const max = maxOf(subject);
    $('calc-prim').textContent = primary;
    $('calc-test').textContent = subject.scale[primary];
    [...$('calc-bar').children].forEach((cell, i) => {
        const t = subject.tasks[i];
        cell.classList.toggle('on', got[i + 1] === t.pts);
        cell.classList.toggle('half', got[i + 1] > 0 && got[i + 1] < t.pts);
    });
    $('calc-hint').textContent = hintFor(subject, primary, got);
    $('calc-prim-label').textContent = `первичных из ${max}`;
}

function renderCalc(subject) {
    calcSubject = subject;
    const max = maxOf(subject);
    const range = $('calc-range');
    const [, , , part1End] = subject.parts[0];
    const part1Max = subject.tasks.slice(0, part1End).reduce((s, t) => s + t.pts, 0);

    // Новый предмет — ползунок на ту же долю пути, чтобы не прыгал к краю
    const share = range.dataset.subject ? Number(range.value) / Number(range.max) : 0.44;
    range.max = max;
    range.value = Math.round(share * max);
    range.dataset.subject = subject.id;

    $('calc-title').textContent = `Сколько нужно решить по ${subject.name}?`;
    $('calc-mid').textContent = `${part1Max} — ${subject.parts[0][0].toLowerCase()}`;
    $('calc-max').textContent = max;
    $('calc-last').textContent = `№ ${subject.tasks.length}`;

    const bar = $('calc-bar');
    bar.style.gridTemplateColumns = `repeat(${subject.tasks.length}, 1fr)`;
    bar.innerHTML = subject.tasks.map((t, i) =>
        `<i class="${i + 1 > part1End ? 'part2' : ''}" title="№ ${i + 1} · ${t.pts} ${pointsWord(t.pts)}"></i>`).join('');
    updateCalc();
}

// ===================================== предмет =====================================

function initSubjects() {
    const tabs = $('subject-tabs');
    const fromUrl = new URLSearchParams(location.search).get('subject');

    tabs.innerHTML = SUBJECTS.map((s) =>
        `<button type="button" role="tab" data-id="${s.id}"><i data-lucide="${s.icon}"></i>${s.label}</button>`).join('');

    const select = (subject) => {
        tabs.querySelectorAll('[role="tab"]').forEach((b) => b.setAttribute('aria-selected', String(b.dataset.id === subject.id)));
        renderPlan(subject);
        renderMap(subject);
        renderCalc(subject);
        window.lucide?.createIcons();
    };

    tabs.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-id]');
        if (!btn) return;
        const subject = SUBJECTS.find((s) => s.id === btn.dataset.id);
        select(subject);
        const url = new URL(location.href);
        url.searchParams.set('subject', subject.id);
        history.replaceState(null, '', url);
    });

    select(SUBJECTS.find((s) => s.id === fromUrl) ?? SUBJECTS[0]);
}

tickClock();
setInterval(tickClock, 1000);
initSubjects();
$('calc-range').addEventListener('input', updateCalc);
})();
