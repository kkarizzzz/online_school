// Концепт «Кабинет преподавателя»: обзор, банк заданий, выдача и проверка ДЗ, ученики.
// Одна страница, разделы — по адресу: #/overview, #/bank, #/homework, #/homework/new, #/homework/<id>,
// #/students, #/students/<id>. Данные — заглушки bank_page/bank.js и data.js; всё, что меняет
// преподаватель (свои задания, правки, выданные ДЗ, проверка, заметки), хранится в localStorage (concept-admin:*).

const A = window.ADMIN;
const $ = (id) => document.getElementById(id);
const icons = () => lucide.createIcons();
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const tex = (src) => src.replace(/\$([^$]+)\$/g, (_, f) => katex.renderToString(f, { throwOnError: false }));

const plural = (n, one, few, many) => {
    const m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return one;
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
    return many;
};

const pct = (x) => `${Math.round(x * 100)}%`;
const dateLong = (iso) => new Date(iso + 'T12:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
const daysFromToday = (iso) => Math.round((new Date(iso + 'T12:00') - A.TODAY) / 86400000);
const isPassed = (hw) => new Date(hw.deadline + 'T23:59') < A.TODAY;

function deadlineLabel(hw) {
    const d = daysFromToday(hw.deadline);
    if (d < 0) return `срок истёк ${dateLong(hw.deadline)}`;
    if (d === 0) return 'срок сегодня, 23:59';
    if (d === 1) return 'срок завтра, 23:59';
    return `до ${dateLong(hw.deadline)} · ${d} ${plural(d, 'день', 'дня', 'дней')}`;
}

function seenLabel(days) {
    if (days === 0) return 'сегодня';
    if (days === 1) return 'вчера';
    return `${days} ${plural(days, 'день', 'дня', 'дней')} назад`;
}

/** Точность -> класс цвета: зелёный / жёлтый / красный */
const tone = (x) => (x >= 0.75 ? 'good' : x >= 0.5 ? 'mid' : 'bad');

// ----------------------------------- хранилище -----------------------------------

const store = {
    get(key, fallback) {
        try { return JSON.parse(localStorage.getItem(`concept-admin:${key}`)) ?? fallback; } catch { return fallback; }
    },
    set(key, value) {
        try { localStorage.setItem(`concept-admin:${key}`, JSON.stringify(value)); } catch { /* приватный режим */ }
    },
};

const S = {
    homework: store.get('homework', []),       // выданные в этом браузере ДЗ
    deadlines: store.get('deadlines', {}),     // hwId -> новый срок (продление)
    reviews: store.get('reviews', {}),         // `${hw}:${st}:${task}` -> { points, comment }
    edits: store.get('task-edits', {}),        // taskId -> { src, answer, level }
    custom: store.get('custom-tasks', []),     // свои задания
    basket: store.get('basket', []),           // taskId, отобранные в банке
    notes: store.get('notes', {}),             // studentId -> заметка
};
const save = (key) => store.set({ homework: 'homework', deadlines: 'deadlines', reviews: 'reviews', edits: 'task-edits', custom: 'custom-tasks', basket: 'basket', notes: 'notes' }[key], S[key]);

// ----------------------------------- банк -----------------------------------

const LEVELS = { base: 'Базовый', medium: 'Средний', hard: 'Сложный', coffin: 'Гроб' };
const LEVEL_RANK = { base: 1, medium: 2, hard: 3, coffin: 4 };

// Свои задания — в конец своей темы
for (const t of S.custom) A_topic(t.n, t.topic)?.tasks.push(t);
function A_topic(n, topicId) { return window.BANK.find((b) => b.n === n)?.topics.find((t) => t.id === topicId); }

const TASKS = new Map();
for (const b of window.BANK) for (const tp of b.topics) for (const t of tp.tasks) TASKS.set(t.id, Object.assign(t, { topicName: tp.name }));

/** Задача с правками преподавателя */
function task(id) {
    const t = TASKS.get(id);
    return t && { ...t, ...S.edits[id] };
}

/** Своё условие (src) — простой текст: экранируем, перенос строки -> <br>. Условия банка — уже HTML */
const srcHtml = (src) => tex(esc(src).replace(/\n/g, '<br>'));
const taskHtml = (t) => (t.src != null ? srcHtml(t.src) : tex(t.text));
const nOf = (id) => Number(id.split('-')[0]);
const part = (n) => (n <= 12 ? 1 : 2);

function levelMeter(level) {
    const bars = [1, 2, 3, 4].map((i) => `<i class="${i <= LEVEL_RANK[level] ? 'on' : ''}"></i>`).join('');
    return `<span class="level lvl-${level}" title="Сложность: ${LEVELS[level]}"><span class="level-bars" aria-hidden="true">${bars}</span>${LEVELS[level]}</span>`;
}

// ----------------------------------- ДЗ и сдачи -----------------------------------

const allHomework = () => [...A.HOMEWORK, ...S.homework]
    .map((hw) => ({ ...hw, deadline: S.deadlines[hw.id] || hw.deadline }))
    .sort((a, b) => a.deadline.localeCompare(b.deadline));

const homework = (id) => allHomework().find((h) => h.id === id);
const student = (id) => A.STUDENTS.find((s) => s.id === id);
const group = (id) => A.GROUPS.find((g) => g.id === id);
const roster = (hw) => A.STUDENTS.filter((s) => hw.groups.includes(s.group) || hw.students.includes(s.id));

/** Сдача ученика с учётом проверки преподавателя */
function sub(hw, st) {
    const base = A.SUBMISSIONS[`${hw.id}:${st.id}`] || { status: 'none', results: {} };
    const results = {};
    for (const [tid, r] of Object.entries(base.results)) {
        const rv = S.reviews[`${hw.id}:${st.id}:${tid}`];
        results[tid] = rv ? { ...r, points: rv.points, comment: rv.comment, pending: false } : r;
    }
    return { ...base, results };
}

/** Итог сдачи: баллы по проверенным задачам, сколько ждёт проверки */
function score(s) {
    let points = 0, max = 0, pending = 0;
    for (const r of Object.values(s.results)) {
        if (r.pending) { pending++; continue; }
        points += r.points; max += r.max;
    }
    return { points, max, pending, ratio: max ? points / max : null };
}

/** Состояние сдачи для подписи: сдано / сдано с опозданием / в работе / не начато / просрочено */
function subState(hw, s) {
    if (s.status === 'submitted') return s.late ? { key: 'late', label: 'Сдано позже' } : { key: 'done', label: 'Сдано' };
    if (isPassed(hw)) return { key: 'overdue', label: s.status === 'progress' ? 'Не досдано' : 'Не сдано' };
    return s.status === 'progress' ? { key: 'progress', label: 'В работе' } : { key: 'none', label: 'Не начато' };
}

function hwStats(hw) {
    const list = roster(hw).map((st) => ({ st, s: sub(hw, st) }));
    const submitted = list.filter((x) => x.s.status === 'submitted');
    const ratios = submitted.map((x) => score(x.s).ratio).filter((r) => r != null);
    return {
        total: list.length,
        submitted: submitted.length,
        progress: list.filter((x) => x.s.status === 'progress').length,
        pending: list.reduce((acc, x) => acc + score(x.s).pending, 0),
        avg: ratios.length ? ratios.reduce((a, b) => a + b, 0) / ratios.length : null,
    };
}

/** Все непроверенные задачи: [{ hw, st, taskId }] */
function pendingQueue(filter = () => true) {
    const out = [];
    for (const hw of allHomework()) for (const st of roster(hw)) {
        if (!filter(hw, st)) continue;
        const s = sub(hw, st);
        for (const [tid, r] of Object.entries(s.results)) if (r.pending) out.push({ hw, st, taskId: tid });
    }
    return out;
}

function studentStats(st) {
    const list = allHomework().filter((hw) => roster(hw).includes(st)).map((hw) => ({ hw, s: sub(hw, st) }));
    const vals = Object.values(st.mastery);
    return {
        accuracy: vals.reduce((a, b) => a + b, 0) / vals.length,
        list,
        done: list.filter((x) => x.s.status === 'submitted').length,
        overdue: list.filter((x) => x.s.status !== 'submitted' && isPassed(x.hw)).length,
        active: list.filter((x) => x.s.status !== 'submitted' && !isPassed(x.hw)).length,
    };
}

const weakest = (st, k = 3) => Object.entries(st.mastery).sort((a, b) => a[1] - b[1]).slice(0, k).map(([n]) => Number(n));

// ----------------------------------- общие куски -----------------------------------

function toast(text) {
    const el = $('toast');
    el.textContent = text;
    el.classList.add('is-on');
    clearTimeout(toast.t);
    toast.t = setTimeout(() => el.classList.remove('is-on'), 2600);
}

function pageHead(eyebrow, title, desc, actions = '') {
    return `<div class="page-header">
        <div><p class="eyebrow">${eyebrow}</p><h1 class="title">${title}</h1>${desc ? `<p class="description">${desc}</p>` : ''}</div>
        ${actions ? `<div class="head-actions">${actions}</div>` : ''}
    </div>`;
}

const kpi = (label, value, note = '', cls = '') =>
    `<div class="glass kpi ${cls}"><span class="kpi-label">${label}</span><span class="kpi-value">${value}</span>${note ? `<span class="kpi-note">${note}</span>` : ''}</div>`;

const groupChip = (gid) => {
    const g = group(gid);
    return `<span class="chip chip-${g.color}">${g.name}</span>`;
};

const bar = (value, total, cls = '') =>
    `<span class="bar ${cls}" role="img" aria-label="${value} из ${total}"><i style="width:${total ? (value / total) * 100 : 0}%"></i></span>`;

const statePill = (st) => `<span class="pill pill-${st.key}">${st.label}</span>`;

const ratioCell = (r) => (r == null ? '<span class="muted">—</span>' : `<span class="tone-${tone(r)} mono">${pct(r)}</span>`);

// ----------------------------------- Обзор -----------------------------------

function viewOverview() {
    const hws = allHomework();
    const active = hws.filter((h) => !isPassed(h));
    const queue = pendingQueue();
    const studs = A.STUDENTS.map((st) => ({ st, ...studentStats(st) }));
    const avg = studs.reduce((a, x) => a + x.accuracy, 0) / studs.length;
    const atRisk = studs.filter((x) => x.overdue > 0 || x.accuracy < 0.45 || x.st.lastSeen >= 7)
        .sort((a, b) => b.overdue - a.overdue || a.accuracy - b.accuracy).slice(0, 6);

    // Непроверенное — по сдачам
    const bySub = new Map();
    for (const q of queue) {
        const k = `${q.hw.id}:${q.st.id}`;
        if (!bySub.has(k)) bySub.set(k, { ...q, count: 0 });
        bySub.get(k).count++;
    }

    return `
    ${pageHead('Пятница, 9 октября', 'Обзор', 'Что требует внимания сегодня: проверка второй части, ближайшие сроки и ученики, которые отстают.')}

    <div class="kpis">
        ${kpi('Ученики', A.STUDENTS.length, `${A.GROUPS.length} ${plural(A.GROUPS.length, 'группа', 'группы', 'групп')}`)}
        ${kpi('Активные ДЗ', active.length, `${hws.length - active.length} завершено`)}
        ${kpi('Ждут проверки', queue.length, `${plural(queue.length, 'задача', 'задачи', 'задач')} второй части`, queue.length ? 'is-accent' : '')}
        ${kpi('Средняя точность', pct(avg), 'по всем номерам')}
    </div>

    <div class="grid-2">
        <section class="glass panel">
            <div class="panel-head">
                <h2>Ждут проверки</h2>
                ${queue.length ? '<button class="btn btn-primary btn-s" data-action="review-all"><i data-lucide="check-check"></i>Проверить все</button>' : ''}
            </div>
            ${bySub.size ? `<ul class="rows">${[...bySub.values()].slice(0, 6).map((x) => `
                <li class="row">
                    <span class="row-main"><b>${x.st.name}</b><span class="muted">${x.hw.title}</span></span>
                    <span class="badge-warn">${x.count} ${plural(x.count, 'задача', 'задачи', 'задач')}</span>
                    <button class="btn btn-outline btn-s" data-action="review" data-hw="${x.hw.id}" data-st="${x.st.id}">Проверить</button>
                </li>`).join('')}</ul>
                ${bySub.size > 6 ? `<p class="muted small">и ещё ${bySub.size - 6} ${plural(bySub.size - 6, 'сдача', 'сдачи', 'сдач')}</p>` : ''}` : '<p class="empty-s">Всё проверено.</p>'}
        </section>

        <section class="glass panel">
            <div class="panel-head"><h2>Ближайшие сроки</h2><a class="link" href="#/homework">Все ДЗ</a></div>
            <ul class="rows">${active.slice(0, 5).map((hw) => {
                const s = hwStats(hw);
                return `<li class="row is-link" data-href="#/homework/${hw.id}">
                    <span class="row-main"><b>${hw.title}</b><span class="muted">${deadlineLabel(hw)}</span></span>
                    <span class="row-progress">${bar(s.submitted, s.total)}<span class="mono">${s.submitted}/${s.total}</span></span>
                </li>`;
            }).join('') || '<p class="empty-s">Активных ДЗ нет.</p>'}</ul>
        </section>
    </div>

    <section class="glass panel">
        <div class="panel-head"><h2>Нужна помощь</h2><a class="link" href="#/students">Все ученики</a></div>
        <ul class="rows">${atRisk.map((x) => {
            const why = [
                x.overdue ? `${x.overdue} ${plural(x.overdue, 'просроченное ДЗ', 'просроченных ДЗ', 'просроченных ДЗ')}` : '',
                x.accuracy < 0.45 ? `точность ${pct(x.accuracy)}` : '',
                x.st.lastSeen >= 7 ? `не заходил ${seenLabel(x.st.lastSeen)}` : '',
            ].filter(Boolean).join(' · ');
            return `<li class="row is-link" data-href="#/students/${x.st.id}">
                <span class="row-main"><b>${x.st.name}</b><span class="muted">${why}</span></span>
                ${groupChip(x.st.group)}
                <span class="muted row-weak">слабые: ${weakest(x.st).map((n) => `№${n}`).join(', ')}</span>
            </li>`;
        }).join('')}</ul>
    </section>`;
}

// ----------------------------------- Банк -----------------------------------

const bankF = { n: 0, topic: '', level: '', q: '', sort: 'new', limit: 30 };

function bankTasks() {
    const q = bankF.q.trim().toLowerCase();
    let list = [...TASKS.keys()].map(task).filter((t) =>
        (!bankF.n || t.n === bankF.n) &&
        (!bankF.topic || t.topic === bankF.topic) &&
        (!bankF.level || t.level === bankF.level) &&
        (!q || (t.src ?? t.text).toLowerCase().includes(q) || t.topicName.toLowerCase().includes(q) || t.id.includes(q)));
    const sorts = {
        new: (a, b) => b.date.localeCompare(a.date),
        num: (a, b) => a.n - b.n || a.index - b.index,
        hard: (a, b) => LEVEL_RANK[b.level] - LEVEL_RANK[a.level] || a.solved - b.solved,
        rare: (a, b) => a.solved - b.solved,
    };
    return list.sort(sorts[bankF.sort]);
}

function viewBank() {
    const num = window.BANK.find((b) => b.n === bankF.n);
    const list = bankTasks();
    const shown = list.slice(0, bankF.limit);

    return `
    ${pageHead('Банк заданий', 'Задания', `${TASKS.size} ${plural(TASKS.size, 'задание', 'задания', 'заданий')} по 19 номерам ЕГЭ. Отмечайте задачи — из отобранных собирается домашнее задание.`,
        '<button class="btn btn-outline btn-s" data-action="task-new"><i data-lucide="file-plus"></i>Новое задание</button>')}

    <div class="numbers" role="tablist" aria-label="Номер ЕГЭ">
        <button class="num ${!bankF.n ? 'is-on' : ''}" data-action="bank-n" data-n="0">Все</button>
        ${window.BANK.map((b) => `<button class="num ${bankF.n === b.n ? 'is-on' : ''} ${b.part === 2 ? 'is-p2' : ''}" data-action="bank-n" data-n="${b.n}" title="${b.title}">${b.n}</button>`).join('')}
    </div>

    <div class="glass toolbar">
        <label class="field field-grow"><i data-lucide="search"></i><input type="search" id="bank-q" placeholder="Текст условия, тема или id" value="${esc(bankF.q)}"></label>
        <select class="select" id="bank-topic" ${num ? '' : 'disabled'} aria-label="Тема">
            <option value="">${num ? 'Все темы номера' : 'Сначала выберите номер'}</option>
            ${num ? num.topics.map((t) => `<option value="${t.id}" ${bankF.topic === t.id ? 'selected' : ''}>${t.name}</option>`).join('') : ''}
        </select>
        <select class="select" id="bank-level" aria-label="Сложность">
            <option value="">Любая сложность</option>
            ${Object.entries(LEVELS).map(([k, v]) => `<option value="${k}" ${bankF.level === k ? 'selected' : ''}>${v}</option>`).join('')}
        </select>
        <select class="select" id="bank-sort" aria-label="Сортировка">
            ${[['new', 'Сначала новые'], ['num', 'По номеру'], ['hard', 'Сначала сложные'], ['rare', 'Реже всего решали']].map(([k, v]) => `<option value="${k}" ${bankF.sort === k ? 'selected' : ''}>${v}</option>`).join('')}
        </select>
    </div>

    <p class="muted list-count">${num ? `№${num.n} · ${num.title} · ` : ''}найдено ${list.length}</p>

    <ul class="tasks">${shown.map(taskRow).join('')}</ul>
    ${!list.length ? '<div class="glass empty">Ничего не найдено.</div>' : ''}
    ${list.length > shown.length ? `<button class="btn btn-outline more" data-action="bank-more">Показать ещё ${Math.min(30, list.length - shown.length)}</button>` : ''}`;
}

function taskRow(t) {
    const on = S.basket.includes(t.id);
    return `<li class="glass task ${on ? 'is-picked' : ''}" data-id="${t.id}">
        <label class="task-check"><input type="checkbox" data-action="pick" data-id="${t.id}" ${on ? 'checked' : ''} aria-label="Отобрать в ДЗ"></label>
        <div class="task-body">
            <div class="task-meta">
                <span class="tag-n">№${t.n}</span><span class="muted">${t.topicName}</span>
                ${t.custom ? '<span class="pill pill-progress">своё</span>' : S.edits[t.id] ? '<span class="pill pill-none">изменено</span>' : ''}
            </div>
            <div class="task-text">${taskHtml(t)}</div>
            <div class="task-foot">
                ${levelMeter(t.level)}
                <span class="muted">ответ <b class="mono">${part(t.n) === 1 ? esc(t.answer) : '—'}</b></span>
                <span class="muted">решили ${t.solved}</span>
                <span class="muted mono">${t.id}</span>
            </div>
        </div>
        <button class="icon-btn" data-action="task-edit" data-id="${t.id}" aria-label="Редактировать"><i data-lucide="pencil"></i></button>
    </li>`;
}

function renderBasket() {
    const el = $('basket');
    const hide = !S.basket.length || route.name === 'homework-new';
    el.hidden = hide;
    if (hide) return;
    const tasks = S.basket.map(task).filter(Boolean);
    const numbers = [...new Set(tasks.map((t) => t.n))].sort((a, b) => a - b);
    el.innerHTML = `
        <span class="basket-count">${tasks.length}</span>
        <span class="basket-text"><b>${plural(tasks.length, 'задача отобрана', 'задачи отобраны', 'задач отобрано')}</b><span class="muted">${numbers.map((n) => `№${n}`).join(', ')}</span></span>
        <button class="btn btn-ghost btn-s" data-action="basket-clear">Очистить</button>
        <a class="btn btn-primary btn-s" href="#/homework/new">Собрать ДЗ<i data-lucide="arrow-right"></i></a>`;
    icons();
}

// Редактор задания: правка своего / банковского, живой предпросмотр
function openTaskEditor(id) {
    const t = id ? task(id) : { n: bankF.n || 1, topic: bankF.topic, level: 'base', src: '', answer: '' };
    const m = $('modal');
    const numSel = (n) => window.BANK.find((b) => b.n === n);
    m.innerHTML = `
    <form method="dialog" class="modal-box" id="task-form">
        <div class="modal-head"><h2>${id ? `Задание ${t.id}` : 'Новое задание'}</h2><button class="icon-btn" value="cancel" aria-label="Закрыть"><i data-lucide="x"></i></button></div>
        <div class="form-grid">
            <label class="lbl">Номер ЕГЭ
                <select class="select" name="n" ${id ? 'disabled' : ''}>${window.BANK.map((b) => `<option value="${b.n}" ${b.n === t.n ? 'selected' : ''}>№${b.n} · ${b.title}</option>`).join('')}</select></label>
            <label class="lbl">Тема (прототип)
                <select class="select" name="topic" ${id ? 'disabled' : ''}></select></label>
            <label class="lbl">Сложность
                <select class="select" name="level">${Object.entries(LEVELS).map(([k, v]) => `<option value="${k}" ${t.level === k ? 'selected' : ''}>${v}</option>`).join('')}</select></label>
            <label class="lbl">Ответ
                <input class="input mono" name="answer" value="${esc(t.answer ?? '')}" placeholder="Число; для части 2 — необязательно"></label>
        </div>
        <label class="lbl">Условие <span class="muted">— формулы в $…$, например $\\sqrt{x+3} = 5$</span>
            <textarea class="input area" name="src" rows="5" required>${esc(t.src ?? t.text.replace(/<br\s*\/?>/g, '\n'))}</textarea></label>
        <div class="preview"><span class="preview-label">Как увидит ученик</span><div class="task-text" id="task-preview"></div></div>
        <div class="modal-foot">
            ${id && !t.custom && S.edits[id] ? '<button type="button" class="btn btn-ghost" data-action="task-reset">Вернуть исходное</button>' : '<span></span>'}
            <div class="modal-foot-r"><button class="btn btn-outline" value="cancel">Отмена</button><button class="btn btn-primary" value="ok">Сохранить</button></div>
        </div>
    </form>`;
    const f = m.querySelector('form');
    const fillTopics = () => {
        const b = numSel(Number(f.n.value));
        f.topic.innerHTML = b.topics.map((tp) => `<option value="${tp.id}" ${tp.id === t.topic ? 'selected' : ''}>${tp.name}</option>`).join('');
    };
    const preview = () => { $('task-preview').innerHTML = srcHtml(f.src.value) || '<span class="muted">Пусто</span>'; };
    fillTopics(); preview();
    f.n.addEventListener('change', fillTopics);
    f.src.addEventListener('input', preview);
    m.querySelector('[data-action="task-reset"]')?.addEventListener('click', () => {
        delete S.edits[id]; save('edits'); m.close(); render(); toast('Задание возвращено к исходному');
    });
    m.onclose = () => {
        if (m.returnValue !== 'ok') return;
        const src = f.src.value.trim();
        if (!src) return;
        if (id && !t.custom) {
            S.edits[id] = { src, answer: f.answer.value.trim(), level: f.level.value };
            save('edits');
        } else if (id) {
            const c = S.custom.find((x) => x.id === id);
            Object.assign(c, { src, answer: f.answer.value.trim(), level: f.level.value });
            Object.assign(TASKS.get(id), c);
            save('custom');
        } else {
            const n = Number(f.n.value);
            const tp = A_topic(n, f.topic.value);
            const c = {
                id: `${n}-${tp.id}-c${Date.now().toString(36)}`, n, topic: tp.id, index: tp.tasks.length + 1,
                src, text: '', answer: f.answer.value.trim(), level: f.level.value,
                date: A.TODAY.toISOString().slice(0, 10), solved: 0, custom: true,
            };
            S.custom.push(c); save('custom');
            tp.tasks.push(c);
            TASKS.set(c.id, Object.assign(c, { topicName: tp.name }));
            Object.assign(bankF, { n, topic: tp.id, sort: 'new' });
        }
        render();
        toast(id ? 'Задание сохранено' : 'Задание добавлено в банк');
    };
    icons();
    m.returnValue = '';
    m.showModal();
}

// ----------------------------------- Список ДЗ -----------------------------------

let hwTab = 'active';

function viewHomeworkList() {
    const all = allHomework();
    const tabs = { active: all.filter((h) => !isPassed(h)), past: [...all.filter(isPassed)].reverse() };
    const list = tabs[hwTab];
    return `
    ${pageHead('Домашние задания', 'Выданные ДЗ', 'Ход выполнения по группам, проверка второй части и продление сроков.',
        '<a class="btn btn-primary btn-s" href="#/homework/new"><i data-lucide="plus"></i>Новое ДЗ</a>')}

    <div class="glass tabs" role="tablist">
        <button class="tab ${hwTab === 'active' ? 'is-active' : ''}" data-action="hw-tab" data-tab="active">Активные<span class="tab-n">${tabs.active.length}</span></button>
        <button class="tab ${hwTab === 'past' ? 'is-active' : ''}" data-action="hw-tab" data-tab="past">Завершённые<span class="tab-n">${tabs.past.length}</span></button>
    </div>

    <div class="glass table-wrap">
        <table class="table">
            <thead><tr><th>Задание</th><th>Кому</th><th>Срок</th><th>Сдали</th><th>Средний</th><th></th></tr></thead>
            <tbody>${list.map((hw) => {
                const s = hwStats(hw);
                return `<tr class="is-link" data-href="#/homework/${hw.id}">
                    <td><b>${hw.title}</b><div class="muted">${hw.topic} · ${hw.tasks.length} ${plural(hw.tasks.length, 'задача', 'задачи', 'задач')}</div></td>
                    <td><div class="chips">${hw.groups.map(groupChip).join('')}${hw.students.length ? `<span class="chip">+${hw.students.length} ${plural(hw.students.length, 'ученик', 'ученика', 'учеников')}</span>` : ''}</div></td>
                    <td class="${isPassed(hw) ? 'muted' : ''}">${deadlineLabel(hw)}</td>
                    <td><span class="row-progress">${bar(s.submitted, s.total)}<span class="mono">${s.submitted}/${s.total}</span></span></td>
                    <td>${ratioCell(s.avg)}</td>
                    <td>${s.pending ? `<span class="badge-warn" title="Ждут проверки">${s.pending} на проверку</span>` : ''}</td>
                </tr>`;
            }).join('')}</tbody>
        </table>
        ${!list.length ? '<div class="empty">Здесь пока пусто.</div>' : ''}
    </div>`;
}

// ----------------------------------- Карточка ДЗ -----------------------------------

function viewHomework(id) {
    const hw = homework(id);
    if (!hw) return `<div class="glass empty">ДЗ не найдено. <a class="link" href="#/homework">К списку</a></div>`;
    const st = hwStats(hw);
    const rows = roster(hw).map((s) => ({ s, sub: sub(hw, s) }));
    const order = { overdue: 0, none: 1, progress: 2, late: 3, done: 4 };
    rows.sort((a, b) => order[subState(hw, a.sub).key] - order[subState(hw, b.sub).key] || a.s.name.localeCompare(b.s.name));
    const notDone = rows.filter((r) => r.sub.status !== 'submitted').length;
    const tasks = hw.tasks.map(task);

    // Верно по каждой задаче — среди тех, кто её решил и она проверена
    const perTask = tasks.map((t) => {
        const rs = rows.map((r) => r.sub.results[t.id]).filter((r) => r && !r.pending);
        return rs.length ? rs.reduce((a, r) => a + r.points / r.max, 0) / rs.length : null;
    });

    return `
    <a class="back" href="#/homework"><i data-lucide="arrow-left"></i>Все ДЗ</a>
    ${pageHead(`${hw.topic} · выдано ${dateLong(hw.created)}`, hw.title, `<span class="${isPassed(hw) ? 'tone-bad' : ''}">${deadlineLabel(hw)}</span> · ${hw.groups.map((g) => group(g).name).join(', ')}`,
        `<button class="btn btn-outline btn-s" data-action="hw-extend" data-hw="${hw.id}"><i data-lucide="calendar-plus"></i>Продлить на 2 дня</button>
         ${notDone ? `<button class="btn btn-outline btn-s" data-action="hw-remind" data-n="${notDone}"><i data-lucide="bell-ring"></i>Напомнить (${notDone})</button>` : ''}
         ${st.pending ? `<button class="btn btn-primary btn-s" data-action="review-hw" data-hw="${hw.id}"><i data-lucide="check-check"></i>Проверить ${st.pending}</button>` : ''}`)}

    <div class="kpis">
        ${kpi('Сдали', `${st.submitted}<small>/${st.total}</small>`, bar(st.submitted, st.total))}
        ${kpi('В работе', st.progress, `не начали ${st.total - st.submitted - st.progress}`)}
        ${kpi('Средний результат', st.avg == null ? '—' : pct(st.avg), 'по проверенным задачам')}
        ${kpi('Ждут проверки', st.pending, 'задач второй части', st.pending ? 'is-accent' : '')}
    </div>

    <section class="glass panel">
        <div class="panel-head"><h2>Результаты по задачам</h2>
            <span class="legend"><i class="cell c-ok"></i>верно <i class="cell c-part"></i>частично <i class="cell c-bad"></i>неверно <i class="cell c-pend"></i>проверить <i class="cell"></i>нет ответа</span></div>
        <div class="matrix-wrap">
            <table class="matrix">
                <thead><tr><th class="m-name">Ученик</th>${tasks.map((t, i) => `<th title="${esc(t.topicName)}"><span class="m-i">${i + 1}</span><span class="m-n">№${t.n}</span></th>`).join('')}<th>Итог</th><th>Статус</th></tr></thead>
                <tbody>${rows.map(({ s, sub: x }) => {
                    const sc = score(x);
                    return `<tr>
                        <td class="m-name"><a href="#/students/${s.id}">${s.name}</a></td>
                        ${tasks.map((t) => cell(hw, s, t, x.results[t.id])).join('')}
                        <td class="mono">${sc.max ? `${sc.points}/${sc.max}` : '—'}</td>
                        <td>${statePill(subState(hw, x))}</td>
                    </tr>`;
                }).join('')}</tbody>
                <tfoot><tr><td class="m-name muted">Верно</td>${perTask.map((r) => `<td>${r == null ? '<span class="muted">—</span>' : `<span class="tone-${tone(r)}">${Math.round(r * 100)}</span>`}</td>`).join('')}<td></td><td></td></tr></tfoot>
            </table>
        </div>
        ${perTask.some((r) => r != null && r < 0.5) ? `<p class="hint"><i data-lucide="lightbulb"></i>Задачи ${perTask.map((r, i) => (r != null && r < 0.5 ? i + 1 : null)).filter(Boolean).join(', ')} решили меньше половины — стоит разобрать на занятии.</p>` : ''}
    </section>

    <section class="glass panel">
        <div class="panel-head"><h2>Задачи</h2><span class="muted">${hw.options.showAnswers ? 'ответы откроются после срока' : 'ответы скрыты'} · ${hw.options.allowLate ? 'досдача разрешена' : 'без досдачи'}</span></div>
        <ol class="hw-tasks">${tasks.map((t) => `<li><span class="tag-n">№${t.n}</span><div class="task-text">${taskHtml(t)}</div>${part(t.n) === 1 ? `<span class="mono muted">${esc(t.answer)}</span>` : `<span class="muted">${A.maxOf(t.n)} б.</span>`}</li>`).join('')}</ol>
    </section>`;
}

function cell(hw, s, t, r) {
    if (!r) return '<td><span class="cell" title="Нет ответа"></span></td>';
    const p2 = part(t.n) === 2;
    const cls = r.pending ? 'c-pend' : r.points === r.max ? 'c-ok' : r.points === 0 ? 'c-bad' : 'c-part';
    const label = r.pending ? '?' : p2 ? r.points : '';
    const attrs = p2 ? `data-action="review" data-hw="${hw.id}" data-st="${s.id}" data-task="${t.id}"` : '';
    const title = r.pending ? 'Ждёт проверки' : p2 ? `${r.points} из ${r.max}` : r.points ? 'Верно' : 'Неверно';
    return `<td>${p2 ? `<button class="cell ${cls}" ${attrs} title="${title}">${label}</button>` : `<span class="cell ${cls}" title="${title}"></span>`}</td>`;
}

// ----------------------------------- Проверка второй части -----------------------------------

const CRITERIA = {
    2: ['Обоснованно получен верный ответ', 'Решение верное, но есть вычислительная ошибка или не доведено до ответа', 'Решение не соответствует ни одному из критериев'],
    3: ['Обоснованно получен верный ответ', 'Верное решение с недочётами или доказан только пункт а)', 'Верно выполнена часть решения', 'Решение не соответствует ни одному из критериев'],
    4: ['Обоснованно получен верный ответ', 'Ответ верный, но есть недочёты в обосновании', 'Верно выполнена большая часть решения', 'Верно выполнена часть решения', 'Решение не соответствует критериям'],
};

/** Очередь проверки: [{ hw, st, taskId }] — «Сохранить и далее» ведёт к следующей */
function openReview(queue, i = 0) {
    const q = queue[i];
    if (!q) return;
    const { hw, st, taskId } = q;
    const t = task(taskId);
    const r = sub(hw, st).results[taskId];
    const key = `${hw.id}:${st.id}:${taskId}`;
    const max = r.max;
    let points = r.pending ? null : r.points;
    const m = $('modal');
    const crit = CRITERIA[max];

    m.innerHTML = `
    <form method="dialog" class="modal-box modal-wide">
        <div class="modal-head">
            <div><p class="eyebrow">${hw.title} · задача ${hw.tasks.indexOf(taskId) + 1} · №${t.n}</p><h2>${st.name}</h2></div>
            <span class="muted">${queue.length > 1 ? `${i + 1} из ${queue.length}` : ''}</span>
            <button class="icon-btn" value="cancel" aria-label="Закрыть"><i data-lucide="x"></i></button>
        </div>
        <div class="review">
            <div class="review-col">
                <span class="preview-label">Условие</span>
                <div class="task-text">${taskHtml(t)}</div>
                <span class="preview-label">Решение ученика</span>
                <div class="photo"><i data-lucide="image"></i><span>IMG_${(parseInt(st.id.slice(1)) * 37 + 2000)}.jpg · фото решения</span></div>
                <div class="photo photo-2"><i data-lucide="image"></i><span>стр. 2</span></div>
            </div>
            <div class="review-col">
                <span class="preview-label">Оценка · максимум ${max}</span>
                <div class="scores" role="radiogroup" aria-label="Баллы">
                    ${Array.from({ length: max + 1 }, (_, p) => max - p).map((p) => `
                        <button type="button" class="score-opt ${points === p ? 'is-on' : ''}" data-p="${p}" role="radio" aria-checked="${points === p}">
                            <b>${p}</b><span>${crit[max - p]}</span></button>`).join('')}
                </div>
                <label class="lbl">Комментарий ученику
                    <textarea class="input area" name="comment" rows="3" placeholder="Например: потерян корень при делении на cos x">${esc(r.comment ?? '')}</textarea></label>
            </div>
        </div>
        <div class="modal-foot">
            <span class="muted" id="review-err"></span>
            <div class="modal-foot-r">
                <button class="btn btn-outline" value="cancel">Закрыть</button>
                <button class="btn btn-primary" value="ok">${i + 1 < queue.length ? 'Сохранить и далее' : 'Сохранить'}</button>
            </div>
        </div>
    </form>`;

    m.querySelectorAll('.score-opt').forEach((b) => b.addEventListener('click', () => {
        points = Number(b.dataset.p);
        m.querySelectorAll('.score-opt').forEach((x) => { x.classList.toggle('is-on', x === b); x.setAttribute('aria-checked', x === b); });
        $('review-err').textContent = '';
    }));
    const form = m.querySelector('form');
    form.addEventListener('submit', (e) => {
        if (e.submitter?.value === 'ok' && points == null) { e.preventDefault(); $('review-err').textContent = 'Выберите балл'; }
    });
    m.onclose = () => {
        if (m.returnValue !== 'ok') { render(); return; }
        S.reviews[key] = { points, comment: form.comment.value.trim() };
        save('reviews');
        if (i + 1 < queue.length) { openReview(queue, i + 1); return; }
        render();
        toast(queue.length > 1 ? `Проверено: ${queue.length} ${plural(queue.length, 'задача', 'задачи', 'задач')}` : 'Оценка сохранена');
    };
    icons();
    m.returnValue = '';
    m.showModal();
}

// ----------------------------------- Конструктор ДЗ -----------------------------------

let draft = null;
let autoPick = { n: 1, level: '', count: 3 };  // последний выбор автоподбора

function newDraft(params) {
    const st = params.get('student');
    const d = {
        title: '', topic: '', tasks: [...S.basket], groups: [], students: st ? [st] : [],
        deadline: new Date(A.TODAY.getTime() + 7 * 86400000).toISOString().slice(0, 10),
        options: { showAnswers: true, allowLate: true },
    };
    if (st && params.get('weak')) {
        const s = student(st);
        const ns = weakest(s);
        d.title = `Работа над ошибками: ${ns.map((n) => `№${n}`).join(', ')}`;
        d.topic = 'Индивидуально';
        for (const n of ns) addAuto(d, n, 3);
    }
    if (!d.topic && d.tasks.length) d.topic = window.BANK.find((b) => b.n === nOf(d.tasks[0])).title;
    return d;
}

/** Случайные задачи номера, которых ещё нет в ДЗ; сначала те, что реже решали */
function addAuto(d, n, count, level = '') {
    const pool = window.BANK.find((b) => b.n === n).topics.flatMap((t) => t.tasks)
        .filter((t) => !d.tasks.includes(t.id) && (!level || task(t.id).level === level));
    for (let k = 0; k < count && pool.length; k++) {
        const j = Math.floor(Math.random() * pool.length);
        d.tasks.push(pool.splice(j, 1)[0].id);
    }
}

function draftSummary(d) {
    const tasks = d.tasks.map(task);
    const p1 = tasks.filter((t) => part(t.n) === 1).length;
    const minutes = p1 * 4 + (tasks.length - p1) * 15;
    const ids = new Set([...A.STUDENTS.filter((s) => d.groups.includes(s.group)).map((s) => s.id), ...d.students]);
    return { count: tasks.length, p1, p2: tasks.length - p1, minutes, points: tasks.reduce((a, t) => a + A.maxOf(t.n), 0), recipients: ids.size };
}

function viewBuilder() {
    const d = draft;
    const tasks = d.tasks.map(task);
    const sum = draftSummary(d);
    return `
    <a class="back" href="#/homework"><i data-lucide="arrow-left"></i>Все ДЗ</a>
    ${pageHead('Новое домашнее задание', 'Собрать ДЗ', 'Задачи — из отобранных в банке или автоподбором по номерам. Выдайте группе целиком или отдельным ученикам.')}

    <div class="builder">
        <div class="builder-main">
            <section class="glass panel">
                <h2 class="panel-title"><span class="step">1</span>Название</h2>
                <div class="form-grid">
                    <label class="lbl">Название<input class="input" data-bind="title" value="${esc(d.title)}" placeholder="Например: Логарифмические неравенства"></label>
                    <label class="lbl">Раздел<input class="input" data-bind="topic" value="${esc(d.topic)}" placeholder="Алгебра"></label>
                </div>
            </section>

            <section class="glass panel">
                <div class="panel-head"><h2 class="panel-title"><span class="step">2</span>Задачи <span class="muted">${tasks.length}</span></h2>
                    <a class="link" href="#/bank">Выбрать в банке</a></div>
                <div class="auto">
                    <select class="select" id="auto-n" aria-label="Номер">${window.BANK.map((b) => `<option value="${b.n}" ${b.n === autoPick.n ? 'selected' : ''}>№${b.n} · ${b.title}</option>`).join('')}</select>
                    <select class="select" id="auto-level" aria-label="Сложность"><option value="">любая</option>${Object.entries(LEVELS).map(([k, v]) => `<option value="${k}" ${k === autoPick.level ? 'selected' : ''}>${v.toLowerCase()}</option>`).join('')}</select>
                    <input class="input input-num" id="auto-count" type="number" min="1" max="10" value="${autoPick.count}" aria-label="Сколько задач">
                    <button type="button" class="btn btn-outline btn-s" data-action="auto-add"><i data-lucide="sparkles"></i>Подобрать</button>
                </div>
                ${tasks.length ? `<ol class="draft-tasks">${tasks.map((t, i) => `
                    <li class="draft-task">
                        <span class="tag-n">№${t.n}</span>
                        <div class="task-body"><div class="task-text clamp">${taskHtml(t)}</div><span class="muted">${t.topicName} · ${LEVELS[t.level].toLowerCase()}</span></div>
                        <span class="draft-tools">
                            <button type="button" class="icon-btn" data-action="d-up" data-i="${i}" ${i === 0 ? 'disabled' : ''} aria-label="Выше"><i data-lucide="chevron-up"></i></button>
                            <button type="button" class="icon-btn" data-action="d-down" data-i="${i}" ${i === tasks.length - 1 ? 'disabled' : ''} aria-label="Ниже"><i data-lucide="chevron-down"></i></button>
                            <button type="button" class="icon-btn" data-action="d-del" data-i="${i}" aria-label="Убрать"><i data-lucide="trash-2"></i></button>
                        </span>
                    </li>`).join('')}</ol>` : '<p class="empty-s">Задач пока нет — подберите по номеру или отметьте в банке.</p>'}
            </section>

            <section class="glass panel">
                <h2 class="panel-title"><span class="step">3</span>Кому</h2>
                <div class="pick-groups">${A.GROUPS.map((g) => {
                    const n = A.STUDENTS.filter((s) => s.group === g.id).length;
                    return `<label class="pick ${d.groups.includes(g.id) ? 'is-on' : ''}"><input type="checkbox" data-action="d-group" value="${g.id}" ${d.groups.includes(g.id) ? 'checked' : ''}>
                        <b>${g.name}</b><span class="muted">${n} ${plural(n, 'ученик', 'ученика', 'учеников')}</span></label>`;
                }).join('')}</div>
                <details class="pick-students" ${d.students.length ? 'open' : ''}>
                    <summary>Отдельные ученики${d.students.length ? ` · ${d.students.length}` : ''}</summary>
                    <div class="students-grid">${A.STUDENTS.map((s) => {
                        const viaGroup = d.groups.includes(s.group);
                        return `<label class="st-pick ${viaGroup ? 'is-dim' : ''}"><input type="checkbox" data-action="d-student" value="${s.id}" ${d.students.includes(s.id) || viaGroup ? 'checked' : ''} ${viaGroup ? 'disabled' : ''}>${s.name}</label>`;
                    }).join('')}</div>
                </details>
            </section>

            <section class="glass panel">
                <h2 class="panel-title"><span class="step">4</span>Срок и настройки</h2>
                <div class="form-grid">
                    <label class="lbl">Сдать до (23:59)<input class="input" type="date" data-bind="deadline" value="${d.deadline}" min="${A.TODAY.toISOString().slice(0, 10)}"></label>
                    <div class="lbl">Быстро
                        <div class="quick">${[[2, 'через 2 дня'], [7, 'через неделю'], [14, 'через 2 недели']].map(([k, v]) => `<button type="button" class="chip chip-btn" data-action="d-quick" data-days="${k}">${v}</button>`).join('')}</div>
                    </div>
                </div>
                <label class="switch"><input type="checkbox" data-opt="showAnswers" ${d.options.showAnswers ? 'checked' : ''}><span>Показать верные ответы и разбор после срока</span></label>
                <label class="switch"><input type="checkbox" data-opt="allowLate" ${d.options.allowLate ? 'checked' : ''}><span>Разрешить досдачу после срока (с пометкой «позже»)</span></label>
            </section>
        </div>

        <aside class="glass panel builder-aside" id="draft-summary">${summaryHtml(sum)}</aside>
    </div>`;
}

function summaryHtml(sum) {
    return `
        <h2>Итого</h2>
        <dl class="sum">
            <dt>Задач</dt><dd>${sum.count}${sum.count ? ` <span class="muted">(${sum.p1} + ${sum.p2})</span>` : ''}</dd>
            <dt>Первичных баллов</dt><dd>${sum.points}</dd>
            <dt>Примерно</dt><dd>${sum.minutes ? `${Math.floor(sum.minutes / 60) ? `${Math.floor(sum.minutes / 60)} ч ` : ''}${sum.minutes % 60} мин` : '—'}</dd>
            <dt>Получат</dt><dd>${sum.recipients} ${plural(sum.recipients, 'ученик', 'ученика', 'учеников')}</dd>
            <dt>Срок</dt><dd>${draft.deadline ? dateLong(draft.deadline) : '—'}</dd>
        </dl>
        ${sum.p2 ? `<p class="muted small">Вторую часть (${sum.p2}) проверяете вы — придут в «Ждут проверки».</p>` : ''}
        <p class="err" id="draft-err"></p>
        <button type="button" class="btn btn-primary btn-block" data-action="d-submit"><i data-lucide="send"></i>Выдать ДЗ</button>`;
}

function refreshSummary() {
    $('draft-summary').innerHTML = summaryHtml(draftSummary(draft));
    icons();
}

function submitDraft() {
    const d = draft;
    const sum = draftSummary(d);
    const err = !d.title.trim() ? 'Введите название' : !sum.count ? 'Добавьте хотя бы одну задачу' : !sum.recipients ? 'Выберите группу или учеников' : !d.deadline ? 'Укажите срок' : '';
    if (err) { $('draft-err').textContent = err; return; }
    const hw = {
        id: `hw-c${Date.now().toString(36)}`, title: d.title.trim(), topic: d.topic.trim() || 'Разное',
        tasks: d.tasks, groups: d.groups, students: d.students.filter((id) => !d.groups.includes(student(id).group)),
        deadline: d.deadline, created: A.TODAY.toISOString().slice(0, 10), options: d.options,
    };
    S.homework.push(hw); save('homework');
    S.basket = []; save('basket');
    draft = null;
    location.hash = `#/homework/${hw.id}`;
    toast(`ДЗ выдано: ${sum.recipients} ${plural(sum.recipients, 'ученик', 'ученика', 'учеников')}`);
}

// ----------------------------------- Ученики -----------------------------------

const stF = { group: '', q: '', sort: 'name' };

function strip(st) {
    return `<span class="strip" aria-label="Точность по номерам">${Object.entries(st.mastery).map(([n, v]) => `<i class="t-${tone(v)}" title="№${n}: ${pct(v)}"></i>`).join('')}</span>`;
}

function viewStudents() {
    const q = stF.q.trim().toLowerCase();
    const list = A.STUDENTS.map((st) => ({ st, ...studentStats(st) }))
        .filter((x) => (!stF.group || x.st.group === stF.group) && (!q || x.st.name.toLowerCase().includes(q)));
    const sorts = {
        name: (a, b) => a.st.name.localeCompare(b.st.name),
        weak: (a, b) => a.accuracy - b.accuracy,
        overdue: (a, b) => b.overdue - a.overdue || a.accuracy - b.accuracy,
        seen: (a, b) => b.st.lastSeen - a.st.lastSeen,
    };
    list.sort(sorts[stF.sort]);

    return `
    ${pageHead('Ученики', 'Ученики и группы', 'Точность по номерам ЕГЭ, выполнение ДЗ и активность. Полоска — 19 номеров: зелёный ≥ 75%, жёлтый ≥ 50%, красный — ниже.')}

    <div class="glass toolbar">
        <label class="field field-grow"><i data-lucide="search"></i><input type="search" id="st-q" placeholder="Имя ученика" value="${esc(stF.q)}"></label>
        <select class="select" id="st-group" aria-label="Группа"><option value="">Все группы</option>${A.GROUPS.map((g) => `<option value="${g.id}" ${stF.group === g.id ? 'selected' : ''}>${g.name}</option>`).join('')}</select>
        <select class="select" id="st-sort" aria-label="Сортировка">${[['name', 'По имени'], ['weak', 'Сначала слабые'], ['overdue', 'Больше просрочек'], ['seen', 'Давно не заходили']].map(([k, v]) => `<option value="${k}" ${stF.sort === k ? 'selected' : ''}>${v}</option>`).join('')}</select>
    </div>

    <div class="glass table-wrap">
        <table class="table">
            <thead><tr><th>Ученик</th><th>Точность</th><th class="hide-s">По номерам 1–19</th><th>ДЗ</th><th>Заходил</th></tr></thead>
            <tbody>${list.map((x) => `
                <tr class="is-link" data-href="#/students/${x.st.id}">
                    <td><b>${x.st.name}</b><div>${groupChip(x.st.group)}</div></td>
                    <td>${ratioCell(x.accuracy)}</td>
                    <td class="hide-s">${strip(x.st)}</td>
                    <td><span class="mono">${x.done}</span><span class="muted"> сдано</span>${x.overdue ? ` · <span class="tone-bad">${x.overdue} просроч.</span>` : ''}${x.active ? `<div class="muted">${x.active} в работе</div>` : ''}</td>
                    <td class="${x.st.lastSeen >= 7 ? 'tone-bad' : 'muted'}">${seenLabel(x.st.lastSeen)}</td>
                </tr>`).join('')}</tbody>
        </table>
        ${!list.length ? '<div class="empty">Никого не нашли.</div>' : ''}
    </div>`;
}

function viewStudent(id) {
    const st = student(id);
    if (!st) return `<div class="glass empty">Ученик не найден. <a class="link" href="#/students">К списку</a></div>`;
    const x = studentStats(st);
    const weak = weakest(st);
    const ratios = x.list.filter((y) => y.s.status === 'submitted').map((y) => score(y.s).ratio).filter((r) => r != null);
    const hwAvg = ratios.length ? ratios.reduce((a, b) => a + b, 0) / ratios.length : null;

    return `
    <a class="back" href="#/students"><i data-lucide="arrow-left"></i>Все ученики</a>
    ${pageHead(group(st.group).name, st.name, `Заходил ${seenLabel(st.lastSeen)}. Слабые номера: ${weak.map((n) => `№${n} (${pct(st.mastery[n])})`).join(', ')}.`,
        `<a class="btn btn-outline btn-s" href="#/homework/new?student=${st.id}"><i data-lucide="plus"></i>Выдать ДЗ</a>
         <a class="btn btn-primary btn-s" href="#/homework/new?student=${st.id}&weak=1"><i data-lucide="target"></i>ДЗ по слабым номерам</a>`)}

    <div class="kpis">
        ${kpi('Точность', pct(x.accuracy), 'по всем номерам')}
        ${kpi('Результат ДЗ', hwAvg == null ? '—' : pct(hwAvg), 'средний по сданным')}
        ${kpi('Сдано ДЗ', `${x.done}<small>/${x.list.length}</small>`, x.active ? `${x.active} в работе` : '')}
        ${kpi('Просрочено', x.overdue, '', x.overdue ? 'is-bad' : '')}
    </div>

    <section class="glass panel">
        <div class="panel-head"><h2>Карта номеров</h2><span class="muted">клик — задания номера в банке</span></div>
        <div class="map">${window.BANK.map((b) => {
            const v = st.mastery[b.n];
            return `<a class="map-tile t-${tone(v)}" href="#/bank" data-action="bank-goto" data-n="${b.n}" title="${b.title}">
                <span class="map-n">№${b.n}</span><span class="map-v">${pct(v)}</span><span class="map-t">${b.title}</span></a>`;
        }).join('')}</div>
    </section>

    <div class="grid-2">
        <section class="glass panel">
            <h2>Домашние задания</h2>
            <ul class="rows">${x.list.slice().reverse().map(({ hw, s }) => {
                const sc = score(s);
                return `<li class="row is-link" data-href="#/homework/${hw.id}">
                    <span class="row-main"><b>${hw.title}</b><span class="muted">${deadlineLabel(hw)}</span></span>
                    ${sc.pending ? `<span class="badge-warn">${sc.pending} проверить</span>` : ''}
                    ${s.status === 'submitted' ? ratioCell(sc.ratio) : ''}
                    ${statePill(subState(hw, s))}
                </li>`;
            }).join('') || '<p class="empty-s">ДЗ ещё не выдавали.</p>'}</ul>
        </section>

        <section class="glass panel">
            <h2>Заметка преподавателя</h2>
            <textarea class="input area" id="note" rows="7" placeholder="Видна только вам: цели, договорённости с родителями, на что обратить внимание">${esc(S.notes[st.id] ?? '')}</textarea>
            <p class="muted small">Сохраняется сразу.</p>
        </section>
    </div>`;
}

// ----------------------------------- роутер -----------------------------------

let route = { name: 'overview' };

function parseRoute() {
    const [path, query = ''] = location.hash.replace(/^#\/?/, '').split('?');
    const [a, b] = path.split('/');
    const params = new URLSearchParams(query);
    if (a === 'bank') return { name: 'bank', nav: 'bank' };
    if (a === 'homework' && b === 'new') return { name: 'homework-new', nav: 'homework', params };
    if (a === 'homework' && b) return { name: 'homework', nav: 'homework', id: b };
    if (a === 'homework') return { name: 'homework-list', nav: 'homework' };
    if (a === 'students' && b) return { name: 'student', nav: 'students', id: b };
    if (a === 'students') return { name: 'students', nav: 'students' };
    return { name: 'overview', nav: 'overview' };
}

const VIEWS = {
    overview: viewOverview,
    bank: viewBank,
    'homework-list': viewHomeworkList,
    homework: () => viewHomework(route.id),
    'homework-new': viewBuilder,
    students: viewStudents,
    student: () => viewStudent(route.id),
};

function render() {
    const view = $('view');
    view.innerHTML = VIEWS[route.name]();
    document.querySelectorAll('[data-route]').forEach((a) => {
        const on = a.dataset.route === route.nav;
        a.classList.toggle('active', on);
        a.classList.toggle('is-on', on);
        if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
    const pending = pendingQueue().length;
    $('nav-pending').hidden = !pending;
    $('nav-pending').textContent = pending;
    renderBasket();
    icons();
}

function onRoute() {
    const prev = route.name;
    if ($('modal').open) $('modal').close('cancel');
    route = parseRoute();
    if (route.name === 'homework-new' && (prev !== 'homework-new' || !draft)) draft = newDraft(route.params);
    if (route.name !== 'homework-new') draft = null;
    render();
    if (prev !== route.name) window.scrollTo(0, 0);
}

// ----------------------------------- события -----------------------------------

const view = $('view');

view.addEventListener('click', (e) => {
    const el = e.target.closest('[data-action]');
    if (!el) {
        // Строки-ссылки: таблицы и списки
        const row = e.target.closest('[data-href]');
        if (row && !e.target.closest('a, button, input, select, textarea')) location.hash = row.dataset.href;
        return;
    }
    const a = el.dataset.action;
    const d = draft;

    if (a === 'bank-n') { Object.assign(bankF, { n: Number(el.dataset.n), topic: '', limit: 30 }); render(); }
    else if (a === 'bank-more') { bankF.limit += 30; render(); }
    else if (a === 'bank-goto') { e.preventDefault(); Object.assign(bankF, { n: Number(el.dataset.n), topic: '', level: '', q: '', limit: 30 }); location.hash = '#/bank'; }
    else if (a === 'task-new') openTaskEditor(null);
    else if (a === 'task-edit') openTaskEditor(el.dataset.id);
    else if (a === 'hw-tab') { hwTab = el.dataset.tab; render(); }
    else if (a === 'hw-extend') {
        const hw = homework(el.dataset.hw);
        const base = new Date(Math.max(new Date(hw.deadline + 'T12:00'), A.TODAY));
        S.deadlines[hw.id] = new Date(base.getTime() + 2 * 86400000).toISOString().slice(0, 10);
        save('deadlines'); render(); toast(`Новый срок — ${dateLong(S.deadlines[hw.id])}`);
    }
    else if (a === 'hw-remind') toast(`Напоминание отправлено: ${el.dataset.n} ${plural(Number(el.dataset.n), 'ученик', 'ученика', 'учеников')} (заглушка)`);
    else if (a === 'review') {
        const hw = homework(el.dataset.hw), st = student(el.dataset.st);
        if (el.dataset.task) openReview([{ hw, st, taskId: el.dataset.task }]);
        else openReview(pendingQueue((h, s) => h.id === hw.id && s.id === st.id));
    }
    else if (a === 'review-hw') openReview(pendingQueue((h) => h.id === el.dataset.hw));
    else if (a === 'review-all') openReview(pendingQueue());
    else if (a === 'auto-add') {
        const before = d.tasks.length;
        autoPick = { n: Number($('auto-n').value), level: $('auto-level').value, count: Math.max(1, Math.min(10, Number($('auto-count').value) || 1)) };
        const { n } = autoPick;
        addAuto(d, n, autoPick.count, autoPick.level);
        if (!d.topic) d.topic = window.BANK.find((b) => b.n === n).title;
        render();
        toast(d.tasks.length > before ? `Добавлено задач: ${d.tasks.length - before}` : 'Подходящих задач больше нет');
    }
    else if (a === 'd-up' || a === 'd-down') {
        const i = Number(el.dataset.i), j = a === 'd-up' ? i - 1 : i + 1;
        [d.tasks[i], d.tasks[j]] = [d.tasks[j], d.tasks[i]];
        render();
    }
    else if (a === 'd-del') { d.tasks.splice(Number(el.dataset.i), 1); render(); }
    else if (a === 'd-quick') { d.deadline = new Date(A.TODAY.getTime() + Number(el.dataset.days) * 86400000).toISOString().slice(0, 10); render(); }
    else if (a === 'd-submit') submitDraft();
});

view.addEventListener('change', (e) => {
    const el = e.target;
    const d = draft;
    if (el.dataset.action === 'pick') {
        const id = el.dataset.id;
        S.basket = el.checked ? [...S.basket, id] : S.basket.filter((x) => x !== id);
        save('basket');
        el.closest('.task').classList.toggle('is-picked', el.checked);
        renderBasket();
    }
    else if (el.id === 'bank-topic') { bankF.topic = el.value; bankF.limit = 30; render(); }
    else if (el.id === 'bank-level') { bankF.level = el.value; bankF.limit = 30; render(); }
    else if (el.id === 'bank-sort') { bankF.sort = el.value; render(); }
    else if (el.id === 'st-group') { stF.group = el.value; render(); }
    else if (el.id === 'st-sort') { stF.sort = el.value; render(); }
    else if (el.dataset.action === 'd-group') {
        d.groups = el.checked ? [...d.groups, el.value] : d.groups.filter((g) => g !== el.value);
        render();
    }
    else if (el.dataset.action === 'd-student') {
        d.students = el.checked ? [...d.students, el.value] : d.students.filter((s) => s !== el.value);
        refreshSummary();
    }
    else if (el.dataset.opt) d.options[el.dataset.opt] = el.checked;
    else if (el.dataset.bind === 'deadline') { d.deadline = el.value; refreshSummary(); }
});

// Поиск и текстовые поля — без перерисовки всего раздела, чтобы не терять фокус
let searchT;
view.addEventListener('input', (e) => {
    const el = e.target;
    if (el.id === 'bank-q' || el.id === 'st-q') {
        clearTimeout(searchT);
        searchT = setTimeout(() => {
            if (el.id === 'bank-q') { bankF.q = el.value; bankF.limit = 30; } else stF.q = el.value;
            const pos = el.selectionStart;
            render();
            const again = $(el.id);
            again.focus();
            again.setSelectionRange(pos, pos);
        }, 200);
    }
    else if (el.dataset.bind && el.dataset.bind !== 'deadline') draft[el.dataset.bind] = el.value;
    else if (el.id === 'note') { S.notes[route.id] = el.value; save('notes'); }
});

$('basket').addEventListener('click', (e) => {
    if (e.target.closest('[data-action="basket-clear"]')) {
        S.basket = []; save('basket'); render(); toast('Отбор очищен');
    }
});

// Поиск в шапке: ученик или ДЗ по названию
$('global-search').addEventListener('keydown', (e) => {
    if (e.key !== 'Enter') return;
    const q = e.target.value.trim().toLowerCase();
    if (!q) return;
    const st = A.STUDENTS.find((s) => s.name.toLowerCase().includes(q));
    const hw = allHomework().find((h) => h.title.toLowerCase().includes(q));
    if (st) location.hash = `#/students/${st.id}`;
    else if (hw) location.hash = `#/homework/${hw.id}`;
    else { stF.q = e.target.value; location.hash = '#/students'; }
    e.target.value = '';
});

$('modal').addEventListener('click', (e) => { if (e.target === e.currentTarget) e.currentTarget.close('cancel'); });

$('theme-toggle').addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('concept-theme', next); } catch { /* приватный режим */ }
});

window.addEventListener('hashchange', onRoute);
onRoute();
