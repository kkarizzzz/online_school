// Концепт «Банк заданий»: номера ЕГЭ 1–19 по частям, на карточке — число тем и заданий.
// Клик по номеру открывает панель справа со списком тем (прототипов): темы отмечаются галочками,
// «Все темы» выбирает или снимает все сразу. Кнопка внизу ведёт на prototype.html?n=<номер>&topics=<id,id>
// (если выбраны все темы — без topics). Выбор тем для номера запоминается на время сессии вкладки.

const choiceKey = (n) => `concept-bank:topics:${n}`;

let current = null;         // открытый номер
let chosen = new Set();     // id выбранных тем
let drawerReturn = null;    // куда вернуть фокус после закрытия

// ----------------------------------- номера -----------------------------------

function cardHtml(b) {
    const tasks = tasksOfNumber(b);
    return `<li>
        <button type="button" class="num-card" data-n="${b.n}" aria-haspopup="dialog">
            <span class="num-badge">${b.n}</span>
            <span class="num-main">
                <span class="num-title">${b.title}</span>
                <span class="num-meta">${b.topics.length} ${plural(b.topics.length, 'тема', 'темы', 'тем')} · ${tasks.length} ${plural(tasks.length, 'задание', 'задания', 'заданий')}</span>
            </span>
        </button>
    </li>`;
}

function renderNumbers() {
    $('part1').innerHTML = BANK.filter((b) => b.part === 1).map(cardHtml).join('');
    $('part2').innerHTML = BANK.filter((b) => b.part === 2).map(cardHtml).join('');
    icons();
}

// ----------------------------------- панель тем -----------------------------------

function loadChoice(b) {
    try {
        const saved = JSON.parse(sessionStorage.getItem(choiceKey(b.n)));
        const ids = (saved || []).filter((id) => b.topics.some((t) => t.id === id));
        if (ids.length) return new Set(ids);
    } catch { /* приватный режим */ }
    return new Set(b.topics.map((t) => t.id)); // по умолчанию — все темы
}

function saveChoice() {
    try { sessionStorage.setItem(choiceKey(current.n), JSON.stringify([...chosen])); } catch { /* приватный режим */ }
}

function topicRow(t) {
    return `<li>
        <label class="topic">
            <input type="checkbox" class="check" data-topic="${t.id}" ${chosen.has(t.id) ? 'checked' : ''}>
            <span class="topic-main">
                <span class="topic-name">${t.name}</span>
                <span class="topic-meta">${t.tasks.length} ${plural(t.tasks.length, 'задание', 'задания', 'заданий')}</span>
            </span>
        </label>
    </li>`;
}

function renderDrawer() {
    const b = current;
    const tasks = tasksOfNumber(b);
    const allChosen = chosen.size === b.topics.length;

    $('drawer-body').innerHTML = `
        <div class="drawer-tags"><span class="part-tag">${PART_LABEL[b.part]}</span></div>
        <h2 class="drawer-title" id="drawer-title"><span class="drawer-num">№${b.n}</span>${b.title}</h2>
        <p class="drawer-sub">Выберите темы, задания которых хотите решать.</p>

        <label class="topic topic-all">
            <input type="checkbox" class="check" id="all-topics" ${allChosen ? 'checked' : ''}>
            <span class="topic-main">
                <span class="topic-name">Все темы</span>
                <span class="topic-meta">${b.topics.length} ${plural(b.topics.length, 'тема', 'темы', 'тем')} · ${tasks.length} ${plural(tasks.length, 'задание', 'задания', 'заданий')}</span>
            </span>
        </label>
        <ul class="topics" id="topics">${b.topics.map(topicRow).join('')}</ul>`;

    // «Все темы» в промежуточном состоянии, когда выбрана часть
    $('all-topics').indeterminate = chosen.size > 0 && !allChosen;
    renderGo();
}

/** Кнопка внизу: сколько заданий в выбранных темах и ссылка на страницу прототипа */
function renderGo() {
    const b = current;
    const count = b.topics.filter((t) => chosen.has(t.id)).reduce((s, t) => s + t.tasks.length, 0);
    const go = $('go');
    const params = new URLSearchParams({ n: b.n });
    if (chosen.size && chosen.size < b.topics.length) params.set('topics', [...chosen].join(','));
    go.href = `prototype.html?${params.toString().replaceAll('%2C', ',')}`;
    go.classList.toggle('is-disabled', count === 0);
    go.setAttribute('aria-disabled', count === 0);
    $('go-label').textContent = count
        ? `К заданиям · ${count}`
        : 'Выберите хотя бы одну тему';
}

function onTopicChange(e) {
    const box = e.target;
    if (box.id === 'all-topics') {
        chosen = box.checked ? new Set(current.topics.map((t) => t.id)) : new Set();
    } else if (box.dataset.topic) {
        if (box.checked) chosen.add(box.dataset.topic);
        else chosen.delete(box.dataset.topic);
    } else return;
    saveChoice();
    renderDrawer();
    icons();
}

function openDrawer(n) {
    const b = numberOf(n);
    if (!b) return;
    current = b;
    chosen = loadChoice(b);
    drawerReturn = document.activeElement;
    renderDrawer();
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

// ----------------------------------- запуск -----------------------------------

document.querySelector('.page').addEventListener('click', (e) => {
    const card = e.target.closest('.num-card');
    if (card) openDrawer(Number(card.dataset.n));
});
$('drawer-body').addEventListener('change', onTopicChange);
$('go').addEventListener('click', (e) => { if ($('go').classList.contains('is-disabled')) e.preventDefault(); });
$('drawer-close').addEventListener('click', closeDrawer);
$('backdrop').addEventListener('click', closeDrawer);
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeDrawer(); });
initThemeToggle();

renderNumbers();

// ?n=<номер> — сразу открыть темы номера (так возвращает страница прототипа)
const openN = Number(new URLSearchParams(location.search).get('n'));
if (openN) openDrawer(openN);
