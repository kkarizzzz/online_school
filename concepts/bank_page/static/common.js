// Общее для страниц банка: хелперы, сложность, отметки «решено». Подключается после bank.js.

const BANK = window.BANK;

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

/** Текст с формулами в $...$ -> HTML. Тексты свои, из bank.js, поэтому без санитайзера */
const tex = (src) => src.replace(/\$([^$]+)\$/g, (_, f) => katex.renderToString(f, { throwOnError: false }));

const numberOf = (n) => BANK.find((b) => b.n === n);
const tasksOfNumber = (b) => b.topics.flatMap((t) => t.tasks);
const PART_LABEL = { 1: 'Часть 1 · краткий ответ', 2: 'Часть 2 · развёрнутый ответ' };

const LEVELS = {
    base: { label: 'Базовый', rank: 1 },
    medium: { label: 'Средний', rank: 2 },
    hard: { label: 'Сложный', rank: 3 },
    coffin: { label: 'Гроб', rank: 4 },
};

/** Сложность: четыре деления + подпись, как в каталоге вариантов */
function levelMeter(level) {
    const { rank, label } = LEVELS[level];
    const bars = [1, 2, 3, 4].map((i) => `<i class="${i <= rank ? 'on' : ''}"></i>`).join('');
    return `<span class="level lvl-${level}" title="Сложность: ${label}">
        <span class="level-bars" aria-hidden="true">${bars}</span>
        ${level === 'coffin' ? '<i data-lucide="skull"></i>' : ''}${label}</span>`;
}

// ----------------------------------- отметки «решено» -----------------------------------
// Множество id решённых заданий в localStorage. Позже — с сервера.

const SOLVED_KEY = 'concept-bank:solved';

const solvedSet = (() => {
    try { return new Set(JSON.parse(localStorage.getItem(SOLVED_KEY)) || []); } catch { return new Set(); }
})();

const isSolved = (task) => solvedSet.has(task.id);

function setSolved(task, value) {
    if (value) solvedSet.add(task.id);
    else solvedSet.delete(task.id);
    try { localStorage.setItem(SOLVED_KEY, JSON.stringify([...solvedSet])); } catch { /* приватный режим */ }
}

// Тема — общая для всех концептов
function initThemeToggle() {
    $('theme-toggle')?.addEventListener('click', () => {
        const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
        document.documentElement.dataset.theme = next;
        try { localStorage.setItem('concept-theme', next); } catch { /* приватный режим */ }
    });
}
