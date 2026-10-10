// Концепт «Каталог вариантов»: список вариантов с фильтрами по формату, издателю, сложности и статусу.
// В формате, издателе и статусе выбирается одно значение (клик переключает), в сложности — несколько;
// ничего не выбрано — показываются все. Панель фильтров открывается кнопкой «Фильтры».
// Сортировка — по дате добавления, сложности или популярности (сколько учеников решило), по возрастанию и убыванию.
// Фильтры и сортировка хранятся в адресе (?kind=drill&level=hard,coffin&sort=popular&order=asc).
// Нерешённый вариант («Начать» или клик по строке) ведёт на стартовую страницу solve.html?id=<id>,
// там «Приступить к варианту» запускает решение. Решённый открывает панель справа со статистикой попытки.
// Общие правила, задания и попытки — в exam.js. Позже список и результаты будут браться из API.

const VARIANTS = window.VARIANTS;

const KINDS = {
    standard: { label: 'Стандартный', icon: 'file-text' },
    drill: { label: 'Отработка', icon: 'target' },
};

const PUBLISHERS = {
    author: { label: 'Авторский', icon: 'pen-line' },
    statgrad: { label: 'СтатГрад', icon: 'landmark' },
};

const LEVELS = {
    base: { label: 'Базовый', rank: 1 },
    medium: { label: 'Средний', rank: 2 },
    hard: { label: 'Сложный', rank: 3 },
    coffin: { label: 'Гроб', rank: 4, icon: 'skull' },
};

const STATUSES = {
    todo: { label: 'Не решён', icon: 'circle-dashed' },
    done: { label: 'Решён', icon: 'circle-check' },
};

const isDone = (v) => resultOf(v) != null;

// get — значение варианта для группы фильтров; multi — можно выбрать несколько значений
const FILTERS = {
    kind: { el: 'filter-kind', options: KINDS, get: (v) => v.kind },
    publisher: { el: 'filter-publisher', options: PUBLISHERS, get: (v) => v.publisher },
    level: { el: 'filter-level', options: LEVELS, get: (v) => v.level, multi: true },
    status: { el: 'filter-status', options: STATUSES, get: (v) => (isDone(v) ? 'done' : 'todo') },
};

const PANEL_KEY = 'concept-variants:filters-open';

// key — значение для сравнения; desc/asc — подпись направления на кнопке
const SORTS = {
    date: { label: 'По дате добавления', key: (v) => v.date, desc: 'Сначала новые', asc: 'Сначала старые' },
    level: { label: 'По сложности', key: (v) => LEVELS[v.level].rank, desc: 'Сначала сложные', asc: 'Сначала простые' },
    popular: { label: 'По популярности', key: (v) => v.solved, desc: 'Сначала популярные', asc: 'Сначала редкие' },
};
const DEFAULT_SORT = { field: 'date', order: 'desc' };
const sort = { ...DEFAULT_SORT };

/** Сравнение по выбранному полю; при равенстве — новые выше */
function compare(a, b) {
    const { key } = SORTS[sort.field];
    const ka = key(a), kb = key(b);
    const diff = ka < kb ? -1 : ka > kb ? 1 : 0;
    return (sort.order === 'asc' ? diff : -diff) || b.date.localeCompare(a.date);
}

const state = Object.fromEntries(Object.keys(FILTERS).map((key) => [key, new Set()]));

/** Проходит ли вариант фильтры; `except` — группа, которую не учитывать (для счётчиков на чипах) */
function matches(v, except) {
    return Object.entries(FILTERS).every(([key, { get }]) =>
        key === except || state[key].size === 0 || state[key].has(get(v)));
}

const isFiltered = () => Object.keys(FILTERS).some((key) => state[key].size > 0);

// ----------------------------------- фильтры -----------------------------------

function renderFilters() {
    for (const [key, { el, options, get }] of Object.entries(FILTERS)) {
        // Счётчик на чипе — сколько вариантов будет с учётом остальных групп
        const pool = VARIANTS.filter((v) => matches(v, key));
        const all = `<button type="button" class="chip" data-key="${key}" data-value="" aria-pressed="${state[key].size === 0}">
            Все <span class="chip-count">${pool.length}</span></button>`;

        const chips = Object.entries(options).map(([value, opt]) => {
            const count = pool.filter((v) => get(v) === value).length;
            const icon = opt.icon ? `<i data-lucide="${opt.icon}"></i>` : '';
            const dot = key === 'level' ? `<span class="lvl-dot lvl-${value}"></span>` : '';
            return `<button type="button" class="chip" data-key="${key}" data-value="${value}"
                aria-pressed="${state[key].has(value)}" ${count === 0 && !state[key].has(value) ? 'disabled' : ''}>
                ${dot}${icon}${opt.label} <span class="chip-count">${count}</span></button>`;
        });

        $(el).innerHTML = all + chips.join('');
    }
}

function onChip(e) {
    const chip = e.target.closest('.chip');
    if (!chip || chip.disabled) return;
    const { key, value } = chip.dataset;
    const set = state[key];

    if (!value) set.clear();
    else if (set.has(value)) set.delete(value);
    else {
        // Одиночный выбор: «Отработка» -> «Стандартный» переключает, а не выбирает оба
        if (!FILTERS[key].multi) set.clear();
        set.add(value);
    }

    update();
}

/** Сколько групп фильтров сейчас сужают список — для бейджа на кнопке */
const activeGroups = () => Object.keys(FILTERS).filter((key) => state[key].size > 0).length;

function setPanel(open) {
    $('filters').hidden = !open;
    $('filter-toggle').setAttribute('aria-expanded', open);
    try { localStorage.setItem(PANEL_KEY, open ? '1' : ''); } catch { /* приватный режим */ }
}

function resetFilters() {
    Object.keys(FILTERS).forEach((key) => state[key].clear());
    update();
}

// ----------------------------------- список -----------------------------------

function levelMeter(level) {
    const { rank, label } = LEVELS[level];
    const bars = [1, 2, 3, 4].map((i) => `<i class="${i <= rank ? 'on' : ''}"></i>`).join('');
    return `<span class="level lvl-${level}" title="Сложность: ${label}">
        <span class="level-bars" aria-hidden="true">${bars}</span>
        ${level === 'coffin' ? '<i data-lucide="skull"></i>' : ''}${label}</span>`;
}

function statusOf(v) {
    const result = resultOf(v);
    if (result) {
        return {
            html: `<span class="status is-done"><i data-lucide="circle-check"></i>${scoreLabel(v, result)}</span>`,
            action: 'Разбор', btn: 'btn-outline',
        };
    }
    return { html: '<span class="status">Не решён</span>', action: 'Начать', btn: 'btn-primary', href: startUrl(v) };
}

function kindTag(v) {
    if (v.kind === 'standard') return '<span class="kind-tag"><i data-lucide="file-text"></i>Как на ЕГЭ</span>';
    const label = v.numbers.length === 1 ? 'Задание' : 'Задания';
    return `<span class="kind-tag is-drill" title="Отработка"><i data-lucide="target"></i>${label} №${formatNumbers(v.numbers)}</span>`;
}

function renderList() {
    const list = VARIANTS.filter((v) => matches(v)).sort(compare);

    $('list').innerHTML = list.map((v) => {
        const pub = PUBLISHERS[v.publisher];
        const st = statusOf(v);
        return `<li class="variant lvl-${v.level}" data-id="${v.id}">
            <span class="variant-ico pub-${v.publisher}" aria-hidden="true"><i data-lucide="${pub.icon}"></i></span>
            <div class="variant-main">
                <h2 class="variant-title">${v.title}</h2>
                <p class="variant-meta">
                    <span class="pub-tag pub-${v.publisher}">${pub.label}</span>
                    ${kindTag(v)}
                    <span>${v.tasks} ${plural(v.tasks, 'задание', 'задания', 'заданий')}</span>
                    <span>${formatDate(v.date)}</span>
                    <span class="solved-by" title="Решили ${solvedLabel(v.solved)}"><i data-lucide="users"></i>${v.solved.toLocaleString('ru-RU')}</span>
                </p>
            </div>
            ${levelMeter(v.level)}
            <div class="variant-side">
                ${st.html}
                ${st.href
                    ? `<a class="btn-sm ${st.btn}" href="${st.href}">${st.action}<i data-lucide="arrow-right"></i></a>`
                    : `<button type="button" class="btn-sm ${st.btn}" aria-haspopup="dialog">${st.action}<i data-lucide="arrow-right"></i></button>`}
            </div>
        </li>`;
    }).join('');

    const n = list.length;
    $('found').textContent = isFiltered()
        ? `Найдено ${n} ${plural(n, 'вариант', 'варианта', 'вариантов')} из ${VARIANTS.length}`
        : `${n} ${plural(n, 'вариант', 'варианта', 'вариантов')}`;
    $('list').hidden = n === 0;
    $('empty').hidden = n > 0;
    $('reset').hidden = !isFiltered();

    const active = activeGroups();
    $('filter-badge').textContent = active;
    $('filter-badge').hidden = active === 0;
}

function renderSort() {
    $('sort-field').value = sort.field;
    const label = SORTS[sort.field][sort.order];
    $('sort-order-label').textContent = label;
    $('sort-order').setAttribute('aria-label', `Порядок: ${label.toLowerCase()}`);
    $('sort-order').dataset.order = sort.order;
}

// ----------------------------------- панель справа -----------------------------------

let drawerReturn = null; // куда вернуть фокус после закрытия

/** Стартовая страница варианта: правила и «Приступить к варианту» */
const startUrl = (v) => `solve.html?id=${encodeURIComponent(v.id)}`;

/** Панель решённого варианта: статистика последней попытки */
function drawerHtml(v, result) {
    const pub = PUBLISHERS[v.publisher];
    return `
        <div class="drawer-tags">
            <span class="pub-tag pub-${v.publisher}">${pub.label}</span>
            ${kindTag(v)}
            ${levelMeter(v.level)}
        </div>
        <h2 class="drawer-title" id="drawer-title">${v.title}</h2>
        <p class="drawer-sub">Последняя попытка</p>
        ${statsHtml(v, result)}
        <div class="drawer-actions">
            <a class="btn btn-primary" href="${startUrl(v)}"><i data-lucide="rotate-ccw"></i>Попробовать снова</a>
            <p class="drawer-hint">Новая попытка заменит этот результат.</p>
        </div>`;
}

function openDrawer(id) {
    const v = variantById(id);
    const result = v && resultOf(v);
    if (!result) return;
    drawerReturn = document.activeElement;
    $('drawer-body').innerHTML = drawerHtml(v, result);
    $('drawer').hidden = false;
    $('backdrop').hidden = false;
    document.body.classList.add('no-scroll');
    icons();
    $('drawer-close').focus();
}

function closeDrawer() {
    if ($('drawer').hidden) return;
    $('drawer').hidden = true;
    $('backdrop').hidden = true;
    document.body.classList.remove('no-scroll');
    drawerReturn?.focus?.();
}

function onListClick(e) {
    const row = e.target.closest('.variant');
    if (!row || e.target.closest('a')) return;
    const v = variantById(row.dataset.id);
    if (resultOf(v)) openDrawer(v.id);
    else location.href = startUrl(v);
}

// ----------------------------------- адрес -----------------------------------

function readUrl() {
    const params = new URLSearchParams(location.search);
    for (const [key, { options, multi }] of Object.entries(FILTERS)) {
        const values = (params.get(key) || '').split(',').filter((v) => v in options);
        state[key] = new Set(multi ? values : values.slice(0, 1));
    }
    if (params.get('sort') in SORTS) sort.field = params.get('sort');
    if (['asc', 'desc'].includes(params.get('order'))) sort.order = params.get('order');
}

function writeUrl() {
    const params = new URLSearchParams();
    for (const key of Object.keys(FILTERS)) {
        if (state[key].size) params.set(key, [...state[key]].join(','));
    }
    if (sort.field !== DEFAULT_SORT.field) params.set('sort', sort.field);
    if (sort.order !== DEFAULT_SORT.order) params.set('order', sort.order);
    const query = params.toString().replaceAll('%2C', ',');
    history.replaceState(null, '', query ? `?${query}` : location.pathname);
}

function update() {
    writeUrl();
    renderFilters();
    renderSort();
    renderList();
    icons();
}

// ----------------------------------- запуск -----------------------------------

Object.values(FILTERS).forEach(({ el }) => $(el).addEventListener('click', onChip));
$('reset').addEventListener('click', resetFilters);
$('filter-toggle').addEventListener('click', () => setPanel($('filters').hidden));
$('empty-reset').addEventListener('click', resetFilters);

$('sort-field').addEventListener('change', (e) => { sort.field = e.target.value; update(); });
$('sort-order').addEventListener('click', () => { sort.order = sort.order === 'desc' ? 'asc' : 'desc'; update(); });
$('list').addEventListener('click', onListClick);
$('drawer-close').addEventListener('click', closeDrawer);
$('backdrop').addEventListener('click', closeDrawer);
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeDrawer(); });
initThemeToggle();

// ?open=<id> — со страницы результатов: сразу открыть разбор варианта
const openId = new URLSearchParams(location.search).get('open');
readUrl();
update();
if (openId) openDrawer(openId);

// Панель по умолчанию закрыта; открытой остаётся, если её оставили открытой в прошлый раз
let panelOpen = false;
try { panelOpen = localStorage.getItem(PANEL_KEY) === '1'; } catch { /* приватный режим */ }
setPanel(panelOpen);
