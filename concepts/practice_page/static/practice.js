// Данные Нарешки поверх банка заданий: номер ЕГЭ → подтема.
// Номера, подтемы и задания берутся из bank_page/static/bank.js, здесь — «подборка» (scope):
// множество подтем, из которых лента берёт задания.
//
// Ключ подтемы — «номер.id»: 6.quadratic. Подборка в адресе — токены через запятую:
//   part1 — «Торнадо» (номера первой части), personal — персональная подборка, 6 — номер целиком, 6.quadratic — подтема.

const PERSONAL_KEY = 'concept-practice:personal';

const keyOf = (n, topicId) => `${n}.${topicId}`;
const keysOfNumber = (b) => b.topics.map((t) => keyOf(b.n, t.id));
const PART1_KEYS = BANK.filter((b) => b.part === 1).flatMap(keysOfNumber);

/** Ключ -> { number, topic, index } (index — порядковый номер подтемы внутри номера, с 1) */
function topicByKey(key) {
    const [n, id] = key.split('.');
    const number = numberOf(Number(n));
    const index = number?.topics.findIndex((t) => t.id === id) ?? -1;
    return index < 0 ? null : { number, topic: number.topics[index], index: index + 1 };
}

const tasksOfKeys = (keys) => [...keys].flatMap((k) => topicByKey(k)?.topic.tasks ?? []);
const solvedOf = (tasks) => tasks.filter(isSolved).length;
const numbersOfKeys = (keys) => [...new Set([...keys].map((k) => Number(k.split('.')[0])))].sort((a, b) => a - b);

const sameSet = (a, b) => a.size === b.size && [...a].every((x) => b.has(x));

// ----------------------------------- персональная подборка -----------------------------------
// Множество ключей подтем в localStorage. Номер целиком = все его подтемы.

const personal = (() => {
    let keys;
    try { keys = JSON.parse(localStorage.getItem(PERSONAL_KEY)) || []; } catch { keys = []; }
    return new Set(keys.filter((k) => topicByKey(k)));
})();

function savePersonal() {
    try { localStorage.setItem(PERSONAL_KEY, JSON.stringify([...personal])); } catch { /* приватный режим */ }
}

// Уровни сложности персонального режима — ключи LEVELS из bank_page/static/common.js.
// Хранятся отдельно от тем (concept-practice:levels); по умолчанию — все.
const LEVELS_KEY = 'concept-practice:levels';
const ALL_LEVELS = Object.keys(LEVELS);

const personalLevels = (() => {
    let levels;
    try { levels = JSON.parse(localStorage.getItem(LEVELS_KEY)); } catch { levels = null; }
    levels = (Array.isArray(levels) ? levels : ALL_LEVELS).filter((l) => l in LEVELS);
    return new Set(levels.length ? levels : ALL_LEVELS);
})();

function savePersonalLevels() {
    try { localStorage.setItem(LEVELS_KEY, JSON.stringify([...personalLevels])); } catch { /* приватный режим */ }
}

const allLevels = (levels) => !levels || ALL_LEVELS.every((l) => levels.has(l));
/** Оставить задания выбранной сложности; levels не задан — все */
const byLevels = (tasks, levels) => (allLevels(levels) ? tasks : tasks.filter((t) => levels.has(t.level)));
/** «средний, сложный» — для подписей; все уровни — пустая строка */
const levelsText = (levels) => (allLevels(levels) ? ''
    : ALL_LEVELS.filter((l) => levels.has(l)).map((l) => LEVELS[l].label.toLowerCase()).join(', '));

const tasksWord = (n) => `${n} ${plural(n, 'задание', 'задания', 'заданий')}`;

/** Состав подборки по номерам: «№1 целиком» или «№6: 2 подтемы» */
function personalParts(set = personal) {
    return numbersOfKeys(set).map((n) => {
        const b = numberOf(n);
        const keys = keysOfNumber(b).filter((k) => set.has(k));
        const whole = keys.length === b.topics.length;
        return {
            n, keys, whole,
            short: whole ? `№${n} целиком` : `№${n}: ${keys.length} ${plural(keys.length, 'подтема', 'подтемы', 'подтем')}`,
        };
    });
}

// ----------------------------------- последние подборки -----------------------------------
// Три последние запущенные персональные подборки: [{ scope: 'encodeScope', levels: [...], at: ms }], новые первыми.

const RECENT_KEY = 'concept-practice:recent';
const RECENT_LIMIT = 3;

function recentList() {
    try { return (JSON.parse(localStorage.getItem(RECENT_KEY)) || []).filter((r) => r && r.scope); } catch { return []; }
}

/** Уровни записи истории как Set; в старых записях их нет — значит, все */
const recentLevels = (r) => new Set((r.levels || ALL_LEVELS).filter((l) => l in LEVELS));

/** Запомнить подборку вместе со сложностью; такая же уже есть — поднимается наверх */
function pushRecent(keys, levels) {
    const scope = encodeScope(keys);
    const lv = ALL_LEVELS.filter((l) => levels.has(l));
    const same = (r) => r.scope === scope && sameSet(recentLevels(r), new Set(lv));
    const list = [{ scope, levels: lv, at: Date.now() }, ...recentList().filter((r) => !same(r))].slice(0, RECENT_LIMIT);
    try { localStorage.setItem(RECENT_KEY, JSON.stringify(list)); } catch { /* приватный режим */ }
}

// ----------------------------------- подборка <-> адрес -----------------------------------

function parseScope(str) {
    const keys = new Set();
    for (const token of (str || '').split(',').filter(Boolean)) {
        if (token === 'part1') PART1_KEYS.forEach((k) => keys.add(k));
        if (token === 'personal') personal.forEach((k) => keys.add(k));
        if (/^\d+$/.test(token) && numberOf(Number(token))) keysOfNumber(numberOf(Number(token))).forEach((k) => keys.add(k));
        if (topicByKey(token)) keys.add(token);
    }
    return keys;
}

/** Обратно в короткую строку: номер, у которого выбраны все подтемы, — одним токеном */
function encodeScope(keys) {
    if (sameSet(keys, new Set(PART1_KEYS))) return 'part1';
    return numbersOfKeys(keys).flatMap((n) => {
        const all = keysOfNumber(numberOf(n));
        return all.every((k) => keys.has(k)) ? [String(n)] : all.filter((k) => keys.has(k));
    }).join(',');
}

/** Как назвать подборку в ленте: заголовок и строка над ним */
function describeScope(keys, isPersonal = false, levels = null) {
    if (isPersonal) {
        const lv = levelsText(levels);
        return { icon: 'star', title: 'Персональный', crumbs: lv ? ['Ваша подборка', `сложность: ${lv}`] : ['Ваша подборка номеров и подтем'] };
    }
    if (sameSet(keys, new Set(PART1_KEYS))) return { icon: 'tornado', title: 'Торнадо', crumbs: ['Номера первой части вперемешку'] };

    const numbers = numbersOfKeys(keys);
    if (numbers.length === 1) {
        const number = numberOf(numbers[0]);
        const crumbs = [`№${number.n} · ${number.title}`];
        if (keys.size === number.topics.length) return { icon: 'hash', title: number.title, number, crumbs: [`Задание №${number.n}`] };
        const names = [...keys].map((k) => topicByKey(k).topic.name);
        return {
            icon: 'hash', number, crumbs,
            title: names.length === 1 ? names[0] : `${names.length} ${plural(names.length, 'подтема', 'подтемы', 'подтем')}`,
        };
    }
    return { icon: 'list-checks', title: `Номера ${numbers.join(', ')}`, crumbs: ['Подборка'] };
}
