// Концепт «Домашнее задание»: вкладки «Текущие / Выполненные / Просроченные» и карточки, как во frontend
// (pages/profile/learning/HomeworkPage + entities/homework/HomeworkCard).
// «Приступить к выполнению» / «Продолжить» / «Досдать» открывают solve.html?id=<id>, «Разбор» — результаты сданного.
// Выбранная вкладка хранится в адресе (?tab=done).

const TABS = [
    { id: 'current', label: 'Текущие' },
    { id: 'done', label: 'Выполненные' },
    { id: 'overdue', label: 'Просроченные' },
];

const params = new URLSearchParams(location.search);
let active = TABS.some((t) => t.id === params.get('tab')) ? params.get('tab') : 'current';

function renderTabs() {
    const overdue = window.HOMEWORK.filter((hw) => hwStatus(hw) === 'overdue').length;
    $('tabs').innerHTML = TABS.map((t) => {
        const badge = t.id === 'overdue' && overdue ? `<span class="tab-badge">${overdue}</span>` : '';
        return `<button type="button" role="tab" class="tab${t.id === active ? ' is-active' : ''}"
            data-tab="${t.id}" aria-selected="${t.id === active}">${t.label}${badge}</button>`;
    }).join('');
}

function action(hw, status) {
    const url = `solve.html?id=${encodeURIComponent(hw.id)}`;
    if (status === 'done') {
        return `<div class="hw-side">
            <span class="done-badge"><i data-lucide="check-circle-2"></i>Выполнено</span>
            <a class="hw-btn hw-btn-ghost" href="${url}&view=result">Разбор<i data-lucide="arrow-right"></i></a>
        </div>`;
    }
    const started = answeredIn(hwSessionOf(hw)) > 0;
    const label = status === 'overdue' ? 'Досдать' : started ? 'Продолжить выполнение' : 'Приступить к выполнению';
    return `<a class="hw-btn ${status === 'overdue' ? 'hw-btn-overdue' : 'hw-btn-primary'}" href="${url}">
        ${label}<i data-lucide="arrow-right"></i></a>`;
}

function card(hw) {
    const status = hwStatus(hw);
    const icon = status === 'overdue' ? 'alert-triangle' : status === 'done' ? 'check-circle-2' : 'clock';
    return `<li class="glass hw-card">
        <div class="hw-info">
            <h3 class="hw-title">${hw.title}</h3>
            <p class="hw-topic">${hw.topic} · ${hw.tasks} ${plural(hw.tasks, 'задача', 'задачи', 'задач')}</p>
            <div class="hw-meta">
                <span class="hw-meta-item is-${status}"><i data-lucide="${icon}"></i>${deadlineLabel(hw)}</span>
                <span class="hw-meta-item">${progressLabel(hw)}</span>
            </div>
        </div>
        ${action(hw, status)}
    </li>`;
}

function render() {
    renderTabs();
    const visible = window.HOMEWORK.filter((hw) => hwStatus(hw) === active);
    $('list').innerHTML = visible.map(card).join('');
    $('empty').hidden = visible.length > 0;
    icons();
}

$('tabs').addEventListener('click', (e) => {
    const tab = e.target.closest('.tab');
    if (!tab || tab.dataset.tab === active) return;
    active = tab.dataset.tab;
    history.replaceState(null, '', active === 'current' ? location.pathname : `?tab=${active}`);
    render();
});

// Вернулись кнопкой «Назад» со страницы выполнения — обновить прогресс
window.addEventListener('pageshow', (e) => { if (e.persisted) render(); });

initThemeToggle();
render();
