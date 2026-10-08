// Концепт «Банк заданий», страница прототипа: задания выбранных тем одного номера ЕГЭ.
// Темы — чипы с множественным выбором (ничего не выбрано = все темы), статус — «Не решённые» / «Решённые».
// Сортировка — по дате добавления, сложности или числу решений других учеников, по возрастанию и убыванию.
// Каждое задание можно отметить решённым и снять отметку; ответ открывается по кнопке.
// Всё состояние — в адресе: ?n=6&topics=log,exp&status=todo&sort=level&order=asc

const PAGE_SIZE = 12;

const STATUSES = {
    todo: { label: 'Не решённые', icon: 'circle-dashed', test: (t) => !isSolved(t) },
    done: { label: 'Решённые', icon: 'circle-check', test: isSolved },
};

// key — значение для сравнения; desc/asc — подпись направления на кнопке
const SORTS = {
    date: { key: (t) => t.date, desc: 'Сначала новые', asc: 'Сначала старые' },
    level: { key: (t) => LEVELS[t.level].rank, desc: 'Сначала сложные', asc: 'Сначала простые' },
    solved: { key: (t) => t.solved, desc: 'Сначала популярные', asc: 'Сначала редкие' },
};
const DEFAULT_SORT = { field: 'date', order: 'desc' };

const params = new URLSearchParams(location.search);
const number = numberOf(Number(params.get('n'))) || BANK[0];
const topicName = Object.fromEntries(number.topics.map((t) => [t.id, t.name]));
const allTasks = tasksOfNumber(number);

const state = {
    topics: new Set((params.get('topics') || '').split(',').filter((id) => id in topicName)),
    status: params.get('status') in STATUSES ? params.get('status') : '',
    sort: params.get('sort') in SORTS ? params.get('sort') : DEFAULT_SORT.field,
    order: ['asc', 'desc'].includes(params.get('order')) ? params.get('order') : DEFAULT_SORT.order,
    shown: PAGE_SIZE, // сколько заданий показано — растёт по «Показать ещё»
};

const inTopics = (t) => state.topics.size === 0 || state.topics.has(t.topic);
const inStatus = (t) => !state.status || STATUSES[state.status].test(t);

function compare(a, b) {
    const { key } = SORTS[state.sort];
    const ka = key(a), kb = key(b);
    const diff = ka < kb ? -1 : ka > kb ? 1 : 0;
    // При равенстве — новые выше, затем по порядку в теме
    return (state.order === 'asc' ? diff : -diff) || b.date.localeCompare(a.date) || a.index - b.index;
}

// ----------------------------------- шапка -----------------------------------

function renderHeader() {
    document.title = `№${number.n} · ${number.title} — Банк заданий`;
    $('eyebrow').textContent = `Задание №${number.n} · ${PART_LABEL[number.part]}`;
    $('title').textContent = number.title;
    $('back-link').href = `index.html?n=${number.n}`;

    const i = BANK.indexOf(number);
    for (const [id, other] of [['prev-num', BANK[i - 1]], ['next-num', BANK[i + 1]]]) {
        const link = $(id);
        if (other) {
            link.href = `prototype.html?n=${other.n}`;
            link.title = `№${other.n} · ${other.title}`;
            link.removeAttribute('aria-disabled');
        } else {
            link.removeAttribute('href');
            link.setAttribute('aria-disabled', 'true');
        }
    }
}

// ----------------------------------- фильтры -----------------------------------

function renderFilters() {
    // На чипах тем — сколько всего заданий в теме; сколько решено, не показываем
    const topicChips = number.topics.map((t) => `<button type="button" class="chip" data-topic="${t.id}" aria-pressed="${state.topics.has(t.id)}">
        ${t.name} <span class="chip-count">${t.tasks.length}</span></button>`);
    $('filter-topics').innerHTML = `<button type="button" class="chip" data-topic="" aria-pressed="${state.topics.size === 0}">
        Все темы <span class="chip-count">${allTasks.length}</span></button>${topicChips.join('')}`;

    const statusChips = Object.entries(STATUSES).map(([value, s]) => `<button type="button" class="chip" data-status="${value}" aria-pressed="${state.status === value}">
        <i data-lucide="${s.icon}"></i>${s.label}</button>`);
    $('filter-status').innerHTML = `<button type="button" class="chip" data-status="" aria-pressed="${!state.status}">Все</button>${statusChips.join('')}`;
}

function onTopicChip(e) {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    const id = chip.dataset.topic;
    if (!id) state.topics.clear();
    else if (state.topics.has(id)) state.topics.delete(id);
    else state.topics.add(id);
    // Выбрали все по одной — то же, что «Все темы»
    if (state.topics.size === number.topics.length) state.topics.clear();
    state.shown = PAGE_SIZE;
    update();
}

function onStatusChip(e) {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    const value = chip.dataset.status;
    state.status = state.status === value ? '' : value;
    state.shown = PAGE_SIZE;
    update();
}

// ----------------------------------- список -----------------------------------

function taskHtml(t) {
    const solved = isSolved(t);
    const topicIndex = number.topics.findIndex((x) => x.id === t.topic) + 1;
    return `<li class="task${solved ? ' is-solved' : ''}" data-id="${t.id}">
        <div class="task-head">
            <span class="task-id">${number.n}.${topicIndex}.${String(t.index).padStart(2, '0')}</span>
            <span class="topic-tag">${topicName[t.topic]}</span>
            ${levelMeter(t.level)}
            <span class="task-facts">
                <span title="Решили ${t.solved.toLocaleString('ru-RU')} ${plural(t.solved, 'ученик', 'ученика', 'учеников')}"><i data-lucide="users"></i>${t.solved.toLocaleString('ru-RU')}</span>
                <span title="Добавлено"><i data-lucide="calendar"></i>${formatDate(t.date)}</span>
            </span>
        </div>
        <div class="task-text">${tex(t.text)}</div>
        <div class="task-foot">
            <button type="button" class="link-btn" data-action="answer" aria-expanded="false">
                <i data-lucide="eye"></i><span>Показать ответ</span></button>
            <span class="task-answer" hidden>Ответ: <b>${String(t.answer).replace('.', ',')}</b></span>
            <button type="button" class="mark-btn" data-action="mark" aria-pressed="${solved}">
                <i data-lucide="${solved ? 'circle-check' : 'circle'}"></i>
                <span>${solved ? 'Решено' : 'Отметить решённым'}</span>
            </button>
        </div>
    </li>`;
}

function renderList() {
    const list = allTasks.filter((t) => inTopics(t) && inStatus(t)).sort(compare);
    const page = list.slice(0, state.shown);

    $('list').innerHTML = page.map(taskHtml).join('');

    // Всего заданий в выбранных темах — без учёта статуса, чтобы не выдавать число решённых
    const total = allTasks.filter(inTopics).length;
    $('found').textContent = `${total} ${plural(total, 'задание', 'задания', 'заданий')}`;
    const n = list.length;
    $('list').hidden = n === 0;
    $('empty').hidden = n > 0;

    // Всё отфильтрованное решено — не ошибка, а повод порадоваться
    const allDone = n === 0 && state.status === 'todo' && allTasks.some(inTopics);
    $('empty-title').textContent = allDone ? 'Все задания решены' : 'Таких заданий нет';
    $('empty-text').textContent = allDone
        ? 'В выбранных темах не осталось нерешённых заданий.'
        : 'Попробуйте выбрать другие темы или статус.';

    const rest = n - page.length;
    $('more').hidden = rest <= 0;
    $('more').textContent = `Показать ещё ${Math.min(rest, PAGE_SIZE)} из ${rest}`;
}

function renderSort() {
    $('sort-field').value = state.sort;
    const label = SORTS[state.sort][state.order];
    $('sort-order-label').textContent = label;
    $('sort-order').setAttribute('aria-label', `Порядок: ${label.toLowerCase()}`);
    $('sort-order').dataset.order = state.order;
}

/** Отметка задания: меняем карточку на месте, чтобы список не прыгал; фильтр по статусу применится при следующей перерисовке */
function toggleMark(row) {
    const task = allTasks.find((t) => t.id === row.dataset.id);
    const value = !isSolved(task);
    setSolved(task, value);

    row.classList.toggle('is-solved', value);
    const btn = row.querySelector('[data-action="mark"]');
    btn.setAttribute('aria-pressed', value);
    btn.innerHTML = `<i data-lucide="${value ? 'circle-check' : 'circle'}"></i><span>${value ? 'Решено' : 'Отметить решённым'}</span>`;
    icons();
}

function toggleAnswer(row) {
    const btn = row.querySelector('[data-action="answer"]');
    const answer = row.querySelector('.task-answer');
    const open = answer.hidden;
    answer.hidden = !open;
    btn.setAttribute('aria-expanded', open);
    btn.innerHTML = `<i data-lucide="${open ? 'eye-off' : 'eye'}"></i><span>${open ? 'Скрыть ответ' : 'Показать ответ'}</span>`;
    icons();
}

function onListClick(e) {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;
    const row = btn.closest('.task');
    if (btn.dataset.action === 'mark') toggleMark(row);
    else toggleAnswer(row);
}

// ----------------------------------- адрес -----------------------------------

function writeUrl() {
    const p = new URLSearchParams({ n: number.n });
    if (state.topics.size) p.set('topics', [...state.topics].join(','));
    if (state.status) p.set('status', state.status);
    if (state.sort !== DEFAULT_SORT.field) p.set('sort', state.sort);
    if (state.order !== DEFAULT_SORT.order) p.set('order', state.order);
    history.replaceState(null, '', `?${p.toString().replaceAll('%2C', ',')}`);
}

function update() {
    writeUrl();
    renderFilters();
    renderSort();
    renderList();
    icons();
}

// ----------------------------------- запуск -----------------------------------

$('filter-topics').addEventListener('click', onTopicChip);
$('filter-status').addEventListener('click', onStatusChip);
$('sort-field').addEventListener('change', (e) => { state.sort = e.target.value; update(); });
$('sort-order').addEventListener('click', () => { state.order = state.order === 'desc' ? 'asc' : 'desc'; update(); });
$('list').addEventListener('click', onListClick);
$('more').addEventListener('click', () => { state.shown += PAGE_SIZE; renderList(); icons(); });
$('empty-reset').addEventListener('click', () => { state.topics.clear(); state.status = ''; update(); });
initThemeToggle();

renderHeader();
update();
