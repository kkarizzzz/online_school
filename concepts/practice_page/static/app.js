// Концепт «Нарешка»: номера ЕГЭ с подтемами и бесконечная лента заданий.
// Режимы: «Торнадо» — номера первой части вперемешку — и «Персональный»: номера и подтемы выбираются
// на отдельной странице personal.html. Под режимами — три последние персональные подборки.
// Подборка — в адресе: ?scope=6, ?scope=6.quadratic, ?scope=part1, ?scope=personal.

const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[c]));

const state = {
    scope: null,           // Set ключей подтем, из которых берёт лента
    personal: false,       // лента идёт по персональной подборке
    levels: null,          // Set уровней сложности (персональный режим); null — все
    task: null,
    seen: [],              // показанные задания — чтобы не повторять, пока есть новые
    solved: 0,             // решено за сессию
    streak: 0,             // верных подряд
};

/** Прогресс: «3 из 8» и полоска */
function progress(tasks, { label = true } = {}) {
    const done = solvedOf(tasks);
    const pct = tasks.length ? Math.round((done / tasks.length) * 100) : 0;
    return `<span class="progress ${done === tasks.length && done ? 'is-full' : ''}" title="Решено ${done} из ${tasks.length}">
        <span class="bar"><i style="width:${pct}%"></i></span>
        ${label ? `<span class="progress-num">${done}<span>/${tasks.length}</span></span>` : ''}
    </span>`;
}

// ===================================== выбор тем =====================================

function renderModes() {
    const tornado = tasksOfKeys(PART1_KEYS);
    const mine = byLevels(tasksOfKeys(personal), personalLevels);
    const parts = personalParts();
    const lv = levelsText(personalLevels);

    $('modes').innerHTML = `
        <button type="button" class="mode-card accent" data-scope="part1">
            <span class="mode-head">
                <span class="mode-icon"><i data-lucide="tornado"></i></span>
                <i data-lucide="arrow-up-right" class="mode-arrow"></i>
            </span>
            <span class="mode-eyebrow">Номера 1–12 · ${tasksWord(tornado.length)}</span>
            <span class="mode-title">Торнадо</span>
            <span class="mode-desc">Задачи из всех номеров первой части вперемешку — как на экзамене, где не знаешь, что попадётся следующим.</span>
            ${progress(tornado)}
        </button>

        <div class="mode-card">
            <span class="mode-head">
                <span class="mode-icon"><i data-lucide="star"></i></span>
            </span>
            <span class="mode-eyebrow">${personal.size ? tasksWord(mine.length) : 'Пока пусто'}</span>
            <span class="mode-title">Персональный</span>
            <span class="mode-desc">${personal.size
                ? escapeHtml(parts.map((p) => p.short).join(' · ') + (lv ? ` · сложность: ${lv}` : ''))
                : 'Соберите свои номера и подтемы — и решайте только их.'}</span>
            ${personal.size ? progress(mine) : ''}
            <span class="mode-actions">
                ${personal.size ? `<button type="button" class="btn btn-primary" data-scope="personal" ${mine.length ? '' : 'disabled title="Нет заданий выбранной сложности"'}><i data-lucide="play"></i>Решать</button>` : ''}
                <a class="btn ${personal.size ? 'btn-outline' : 'btn-primary'}" href="personal.html">
                    <i data-lucide="${personal.size ? 'settings-2' : 'plus'}"></i>${personal.size ? 'Изменить' : 'Собрать подборку'}</a>
            </span>
        </div>`;
}

/** Когда запускали: «сегодня, 14:05», «вчера», «7 октября» */
function whenText(ms) {
    const d = new Date(ms);
    const days = Math.round((new Date().setHours(0, 0, 0, 0) - new Date(ms).setHours(0, 0, 0, 0)) / 86400000);
    const time = d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    if (days === 0) return `сегодня, ${time}`;
    if (days === 1) return `вчера, ${time}`;
    return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
}

/** Последние три персональные подборки: состав, сколько заданий, прогресс; решать снова или изменить */
function renderRecent() {
    const list = recentList().map((r) => ({ ...r, keys: parseScope(r.scope), levels: recentLevels(r) })).filter((r) => r.keys.size);
    $('recent-block').hidden = !list.length;
    $('recent').innerHTML = list.map((r, i) => {
        const tasks = byLevels(tasksOfKeys(r.keys), r.levels);
        const parts = personalParts(r.keys);
        const lv = levelsText(r.levels);
        const current = sameSet(r.keys, personal) && sameSet(r.levels, personalLevels);
        return `
            <li class="recent-item ${current ? 'is-current' : ''}">
                <span class="recent-icon"><i data-lucide="history"></i></span>
                <span class="recent-text">
                    <span class="recent-title">${escapeHtml(parts.map((p) => p.short).join(' · '))}</span>
                    <span class="recent-meta">${lv ? `Сложность: ${escapeHtml(lv)} · ` : ''}${tasksWord(tasks.length)} · ${whenText(r.at)}${current ? ' · сейчас в персональном' : ''}</span>
                </span>
                ${progress(tasks)}
                <span class="recent-actions">
                    <button type="button" class="btn btn-ghost" data-recent-edit="${i}" title="Открыть в настройке персонального">
                        <i data-lucide="settings-2"></i><span>Изменить</span></button>
                    <button type="button" class="btn btn-outline" data-recent-go="${i}"><i data-lucide="play"></i><span>Решать</span></button>
                </span>
            </li>`;
    }).join('');
    $('recent').dataset.items = JSON.stringify(list.map((r) => ({ scope: r.scope, levels: [...r.levels] })));
}

/** Подборку из истории делаем персональной: решать её или править на странице настройки */
function useRecent(index) {
    const { scope, levels } = JSON.parse($('recent').dataset.items)[index];
    personal.clear();
    parseScope(scope).forEach((k) => personal.add(k));
    savePersonal();
    personalLevels.clear();
    levels.forEach((l) => personalLevels.add(l));
    savePersonalLevels();
}

function showPicker() {
    state.scope = null;
    state.task = null;
    history.replaceState(null, '', location.pathname);
    document.title = 'Нарешка — Из нуля в сотку';
    renderModes();
    renderRecent();
    icons();
    showScreen('picker');
}

function initPicker() {
    $('picker').addEventListener('click', (e) => {
        const go = e.target.closest('[data-recent-go]');
        if (go) {
            useRecent(Number(go.dataset.recentGo));
            return startFeed(new Set(personal), { personal: true });
        }
        const edit = e.target.closest('[data-recent-edit]');
        if (edit) {
            useRecent(Number(edit.dataset.recentEdit));
            location.href = 'personal.html';
            return;
        }
        const scopeBtn = e.target.closest('[data-scope]');
        if (scopeBtn) startFeed(parseScope(scopeBtn.dataset.scope), { personal: scopeBtn.dataset.scope === 'personal' });
    });
}

function showScreen(name) {
    $('picker').hidden = name !== 'picker';
    $('feed').hidden = name !== 'feed';
    window.scrollTo({ top: 0 });
}

// ======================================= лента =======================================

/** Задания подборки с учётом выбранной сложности (она есть только у персонального режима) */
const poolOf = (keys) => byLevels(tasksOfKeys(keys), state.levels);

function startFeed(scope, { personal: isPersonal = false, levels = null, taskId = null } = {}) {
    const lv = isPersonal ? new Set(personalLevels) : levels;
    if (!byLevels(tasksOfKeys(scope), lv).length) return;
    state.scope = scope;
    state.personal = isPersonal;
    state.levels = lv;
    state.seen = [];
    state.task = null;
    if (isPersonal) pushRecent(scope, lv);

    const pool = poolOf(scope);
    showTask(pool.find((t) => t.id === taskId) || pickTask(pool));
    showScreen('feed');
}

function syncUrl() {
    const params = new URLSearchParams({ scope: state.personal ? 'personal' : encodeScope(state.scope) });
    if (state.task) params.set('task', state.task.id);
    history.replaceState(null, '', `?${params.toString().replace(/%2C/g, ',')}`);
}

/** Случайное задание из пула: сначала нерешённые и ещё не показанные */
function pickTask(pool) {
    const fresh = pool.filter((t) => t.id !== state.task?.id && !state.seen.includes(t.id));
    const candidates = [fresh.filter((t) => !isSolved(t)), fresh, pool.filter((t) => t.id !== state.task?.id), pool]
        .find((list) => list.length);
    return candidates[Math.floor(Math.random() * candidates.length)];
}

/** Шапка ленты: что решаем, прогресс подборки и её состав */
function renderScope() {
    const info = describeScope(state.scope, state.personal, state.levels);
    $('scope-icon').innerHTML = `<i data-lucide="${info.icon}"></i>`;
    $('scope-crumbs').innerHTML = info.crumbs.map(escapeHtml).join('<i data-lucide="chevron-right"></i>');
    $('scope-title').textContent = info.title;
    document.title = `${info.title} — Нарешка`;

    // Сколько всего заданий в подборке, во время решения не показываем — лента бесконечная

    // Состав: в «Торнадо» выбора тем нет — только задание; внутри одного номера — подтемы
    // (включаются и выключаются), иначе — номера
    const current = state.task && keyOf(state.task.n, state.task.topic);
    if (isTornado()) {
        $('scope-parts').innerHTML = '';
    } else if (info.number) {
        $('scope-parts').innerHTML = info.number.topics.map((t) => {
            const key = keyOf(info.number.n, t.id);
            return `<button type="button" class="chip ${key === current ? 'is-current' : ''}" data-toggle="${key}" aria-pressed="${state.scope.has(key)}">
                ${escapeHtml(t.name)}</button>`;
        }).join('');
    } else {
        $('scope-parts').innerHTML = numbersOfKeys(state.scope).map((n) => {
            return `<button type="button" class="chip ${n === state.task?.n ? 'is-current' : ''}" data-narrow="${n}" title="Решать только №${n}">
                <b>№${n}</b> ${escapeHtml(numberOf(n).title)}</button>`;
        }).join('');
    }
}

const isTornado = () => !state.personal && sameSet(state.scope, new Set(PART1_KEYS));

/** Кнопка в задании: подтема текущего задания в персональной подборке или нет */
function renderPersonalToggle() {
    const key = keyOf(state.task.n, state.task.topic);
    const added = personal.has(key);
    const btn = $('to-personal');
    btn.setAttribute('aria-pressed', added);
    btn.classList.toggle('is-added', added);
    btn.innerHTML = `<i data-lucide="${added ? 'check' : 'plus'}"></i>${added ? 'В персональном' : 'В персональный'}`;
    btn.title = `Подтема «${topicByKey(key).topic.name}» ${added ? '— убрать из персонального' : '— добавить в персональный'}`;
    icons();
}

function showTask(task) {
    state.task = task;
    state.seen.push(task.id);
    syncUrl();
    renderScope();

    const { number, topic, index } = topicByKey(keyOf(task.n, task.topic));
    const code = `${task.n}.${index}.${String(task.index).padStart(2, '0')}`;

    $('task-slot').innerHTML = `
        <article class="task glass ${isSolved(task) ? 'is-solved' : ''}" id="task">
            <div class="task-meta">
                <span class="task-code">${code}</span>
                <span class="task-topic"><b>№${number.n}</b> ${escapeHtml(number.title)} <i data-lucide="chevron-right"></i> ${escapeHtml(topic.name)}</span>
                ${levelMeter(task.level)}
                ${isSolved(task) ? '<span class="solved-mark"><i data-lucide="circle-check"></i>Решено раньше</span>' : ''}
                <button type="button" class="to-personal" id="to-personal"></button>
            </div>
            <div class="task-text">${tex(task.text)}</div>
            <form class="answer" id="answer-form" autocomplete="off">
                <input class="answer-input" id="answer" inputmode="decimal" placeholder="Введите ответ" aria-label="Ответ">
                <button type="submit" class="btn btn-primary">Проверить</button>
            </form>
            <p class="hint">Десятичную дробь можно писать через запятую или точку.</p>
            <div class="verdict" id="verdict" hidden></div>
            <section class="solution" id="solution" hidden aria-label="Решение">
                <p class="solution-title"><i data-lucide="lightbulb"></i>Решение</p>
                <div class="solution-text">${tex(task.solution)}</div>
                <p class="solution-answer">Ответ: <b>${formatAnswer(task.answer)}</b></p>
            </section>
            <div class="task-actions">
                <button type="button" class="btn btn-ghost" id="reveal" aria-expanded="false" aria-controls="solution"></button>
                <span class="spacer"></span>
                <!-- «Похожее» появляется после любого ответа или после просмотра решения -->
                <button type="button" class="btn btn-outline" id="similar" hidden
                    title="Ещё задание из подтемы «${escapeHtml(topic.name)}»"><i data-lucide="copy"></i>Похожее</button>
                <button type="button" class="btn btn-outline" id="next"><i data-lucide="arrow-right"></i>Следующее</button>
            </div>
        </article>`;

    $('answer-form').addEventListener('submit', (e) => { e.preventDefault(); check(); });
    $('reveal').addEventListener('click', () => toggleSolution());
    toggleSolution(false);
    $('next').addEventListener('click', () => showTask(pickTask(poolOf(state.scope))));
    $('similar').addEventListener('click', () => showTask(pickTask(byLevels(topic.tasks, state.levels))));
    $('to-personal').addEventListener('click', () => {
        const key = keyOf(task.n, task.topic);
        if (personal.has(key)) personal.delete(key); else personal.add(key);
        savePersonal();
        renderPersonalToggle();
    });
    renderPersonalToggle();
}

const formatAnswer = (x) => String(x).replace('.', ',');

/** «Похожее» — после ответа (верного или нет) или просмотра решения, если в подтеме есть ещё задания */
function showSimilar() {
    $('similar').hidden = byLevels(topicByKey(keyOf(state.task.n, state.task.topic)).topic.tasks, state.levels).length < 2;
}

/** Решение с ответом: открыть, закрыть или переключить */
function toggleSolution(open = $('solution').hidden) {
    $('solution').hidden = !open;
    if (open) showSimilar();
    $('reveal').setAttribute('aria-expanded', open);
    $('reveal').innerHTML = open
        ? '<i data-lucide="eye-off"></i>Скрыть решение'
        : '<i data-lucide="lightbulb"></i>Показать решение';
    icons();
}

function check() {
    const raw = $('answer').value.trim().replace(',', '.').replace(/\s/g, '');
    if (!raw) return $('answer').focus();
    const ok = Math.abs(Number(raw) - state.task.answer) < 1e-6;
    if (ok) {
        if (!isSolved(state.task)) setSolved(state.task, true);
        state.solved += 1;
        state.streak += 1;
    } else {
        state.streak = 0;
    }
    $('solved-count').textContent = state.solved;
    $('streak-count').textContent = state.streak;
    verdict(ok ? 'right' : 'wrong');
    renderScope();
    icons();
}

function verdict(kind) {
    const box = $('verdict');
    const answer = `<b>${formatAnswer(state.task.answer)}</b>`;
    const text = {
        right: `<i data-lucide="circle-check"></i>Верно! Ответ: ${answer}`,
        wrong: `<i data-lucide="circle-x"></i>Пока неверно — попробуйте ещё раз или посмотрите решение.`,
    }[kind];
    box.className = `verdict is-${kind}`;
    box.innerHTML = text;
    box.hidden = false;
    $('task').classList.toggle('is-solved', kind === 'right' || isSolved(state.task));
    showSimilar();
    // После верного ответа главная кнопка — «Следующее»
    if (kind === 'right') {
        $('next').className = 'btn btn-primary';
        $('next').focus();
    }
    icons();
}

function initFeed() {
    $('back').addEventListener('click', showPicker);

    $('scope-parts').addEventListener('click', (e) => {
        const toggle = e.target.closest('[data-toggle]');
        if (toggle) {
            const key = toggle.dataset.toggle;
            const next = new Set(state.scope); // не трогаем персональную подборку
            if (next.has(key)) next.delete(key); else next.add(key);
            if (!poolOf(next).length) return; // хотя бы одно задание остаётся
            state.scope = next;
            state.personal = false;
            // Текущее задание выпало из подборки — берём новое
            if (!state.scope.has(keyOf(state.task.n, state.task.topic))) showTask(pickTask(poolOf(state.scope)));
            else { syncUrl(); renderScope(); icons(); }
            return;
        }
        const narrow = e.target.closest('[data-narrow]');
        if (narrow) {
            const n = Number(narrow.dataset.narrow);
            startFeed(new Set([...state.scope].filter((k) => k.startsWith(`${n}.`))), { levels: state.levels });
        }
    });
}

// ======================================= старт =======================================

initThemeToggle();
initPicker();
initFeed();

const params = new URLSearchParams(location.search);
const initialScope = parseScope(params.get('scope'));
if (initialScope.size) startFeed(initialScope, { personal: params.get('scope') === 'personal', taskId: params.get('task') });
else showPicker();
