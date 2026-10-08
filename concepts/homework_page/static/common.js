// Общее для списка ДЗ и страницы выполнения: задачи, начатые и сданные попытки, статус и подписи.
// Подключается после homework.js и variants_page/static/{tasks,exam}.js — оттуда генератор задач,
// проверка ответа, кольцо прогресса и мелкие помощники ($, icons, plural, tex…).

const HW_ATTEMPTS_KEY = 'concept-homework:attempts';
const hwSessionKey = (id) => `concept-homework:session:${id}`;

const homeworkById = (id) => window.HOMEWORK.find((hw) => hw.id === id);

/** Задачи ДЗ — как у отработки в каталоге вариантов: по номерам ЕГЭ, каждая стоит 1 (верно / неверно) */
const homeworkTasks = (hw) => tasksOf({ ...hw, kind: 'drill' });

/** «2026-10-13» -> «13 октября» */
const dayMonth = (iso) => new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });

// ----------------------------------- попытки -----------------------------------
// Начатое ДЗ: { startedAt, answers: [], current } — в concept-homework:session:<id>.
// Сданное: { points: [1|0], answers?, seconds, date, late? } — в concept-homework:attempts.

function loadHwSession(id) {
    try {
        const s = JSON.parse(localStorage.getItem(hwSessionKey(id)));
        return s && Array.isArray(s.answers) ? s : null;
    } catch {
        return null;
    }
}

function saveHwSession(id, session) {
    try { localStorage.setItem(hwSessionKey(id), JSON.stringify(session)); } catch { /* приватный режим */ }
}

function dropHwSession(id) {
    try { localStorage.removeItem(hwSessionKey(id)); } catch { /* приватный режим */ }
}

function loadHwAttempts() {
    try {
        const data = JSON.parse(localStorage.getItem(HW_ATTEMPTS_KEY));
        return data && typeof data === 'object' ? data : {};
    } catch {
        return {};
    }
}

function saveHwAttempt(id, result) {
    const all = loadHwAttempts();
    all[id] = result;
    try { localStorage.setItem(HW_ATTEMPTS_KEY, JSON.stringify(all)); } catch { /* приватный режим */ }
}

/** Сданное ДЗ: своя попытка из браузера, иначе заглушка */
function hwResultOf(hw) {
    const own = loadHwAttempts()[hw.id];
    if (own) return own;
    if (!hw.result) return null;
    return { points: [...hw.result.points].map(Number), seconds: hw.result.minutes * 60, date: hw.result.date };
}

/** Начатое ДЗ: своя сессия, иначе заглушка — первые `answered` задач с верными ответами */
function hwSessionOf(hw) {
    const own = loadHwSession(hw.id);
    if (own) return own;
    if (!hw.answered) return null;
    const tasks = homeworkTasks(hw);
    return {
        startedAt: Date.now(),
        answers: tasks.slice(0, hw.answered).map((t) => String(t.answer).replace('.', ',')),
        current: Math.min(hw.answered, tasks.length - 1),
    };
}

const answeredIn = (session) => (session?.answers ?? []).filter((a) => String(a ?? '').trim() !== '').length;

/** Статус с учётом своих попыток: сданное ДЗ — выполнено, даже если сдано после срока */
const hwStatus = (hw) => (hwResultOf(hw) ? 'done' : hw.status);

/** Подпись срока, как во frontend: «до 13 октября, 23:59», «сдано 8 октября», «дедлайн истёк 5 октября» */
function deadlineLabel(hw) {
    const result = hwResultOf(hw);
    if (result) return `сдано ${dayMonth(result.date)}${result.late ? ' · после срока' : ''}`;
    if (hw.status === 'overdue') return `дедлайн истёк ${dayMonth(hw.deadline)}`;
    return `до ${dayMonth(hw.deadline)}, 23:59`;
}

/** Подпись прогресса: «Не начато», «3 из 10 решено», «8 из 9 верно» */
function progressLabel(hw) {
    const result = hwResultOf(hw);
    if (result) {
        const correct = result.points.filter((p) => p > 0).length;
        return `${correct} из ${result.points.length} верно`;
    }
    const n = answeredIn(hwSessionOf(hw));
    return n ? `${n} из ${hw.tasks} решено` : 'Не начато';
}
