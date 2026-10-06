// Концепт страницы «Нарешка»: выбор темы -> бесконечная лента заданий (или «Торнадо» по всем темам).
// В React-версии renderMarkdown заменяется на
// <ReactMarkdown remarkPlugins={[remarkMath, remarkGfm]} rehypePlugins={[rehypeKatex]} />

const state = {
    topics: [],
    lastTopicId: null,
    mode: null,        // { type: 'topic', topic } | { type: 'tornado' }
    task: null,
    seen: [],          // показанные в ленте задания — чтобы не повторять, пока есть новые
    solved: 0,         // решено за сессию
    streak: 0,         // верных ответов подряд
};

const DIFFICULTY = { 1: 'Базовый', 2: 'Средний', 3: 'Сложный' };

const PLACEHOLDERS = {
    short: 'Введите ответ',
    digits_set: 'Например, 135',
    sequence: 'Числа через пробел',
};

const HINTS = {
    short: 'Десятичную дробь можно писать через запятую или точку.',
    digits_set: 'Номера ответов без пробелов, в любом порядке.',
    sequence: 'Несколько чисел через пробел, в указанном порядке.',
};

const icons = () => lucide.createIcons();

const plural = (n, one, few, many) => {
    const m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return one;
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
    return many;
};

// ------------------------------ markdown + LaTeX ------------------------------

const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[c]));

function renderMarkdown(src) {
    if (!src) return '';
    const code = [];
    const math = [];

    // 1. Прячем код, чтобы «$» внутри него не принять за формулу
    let text = src.replace(/```[\s\S]*?```|`[^`\n]*`/g, (m) => {
        code.push(m);
        return `\u0000CODE${code.length - 1}\u0000`;
    });

    // 2. Прячем формулы, чтобы Markdown не испортил «_», «*» и «\\» внутри LaTeX
    text = text
        .replace(/\$\$([\s\S]+?)\$\$/g, (_, tex) => {
            math.push({ tex, display: true });
            return `@@MATH${math.length - 1}@@`;
        })
        .replace(/\$([^$\n]+?)\$/g, (_, tex) => {
            math.push({ tex, display: false });
            return `@@MATH${math.length - 1}@@`;
        });

    text = text.replace(/\u0000CODE(\d+)\u0000/g, (_, i) => code[i]);

    // 3. Markdown -> HTML, чистим от XSS, затем подставляем отрендеренные формулы
    const html = DOMPurify.sanitize(marked.parse(text, { gfm: true }));
    return html.replace(/@@MATH(\d+)@@/g, (_, i) =>
        katex.renderToString(math[i].tex, { displayMode: math[i].display, throwOnError: false }),
    );
}

// ----------------------------------- API -----------------------------------

async function api(path, options) {
    const res = await fetch(`/api${path}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    if (!res.ok) throw new Error(`Ошибка сервера: ${res.status}`);
    return res.json();
}

/** Следующее задание ленты: из темы или из всех тем (торнадо) */
function fetchNext() {
    const params = new URLSearchParams();
    if (state.mode.type === 'topic') params.set('topic_id', state.mode.topic.id);
    if (state.task) params.set('current_id', state.task.id);
    state.seen.slice(-30).forEach((id) => params.append('exclude', id));
    return api(`/tasks/random?${params}`);
}

function fetchSimilar() {
    const params = new URLSearchParams();
    state.seen.slice(-30).forEach((id) => params.append('exclude', id));
    return api(`/tasks/${state.task.id}/similar?${params}`);
}

// ------------------------------ адрес страницы ------------------------------

function syncUrl() {
    const params = new URLSearchParams();
    if (state.mode?.type === 'tornado') params.set('mode', 'tornado');
    if (state.mode?.type === 'topic') params.set('topic', state.mode.topic.id);
    if (state.mode && state.task) params.set('task', state.task.id);
    const query = params.toString();
    history.replaceState(null, '', query ? `?${query}` : location.pathname);
}

// ------------------------------- выбор темы ---------------------------------

const topicStats = (t) => `
    <span><i data-lucide="layers"></i>${t.task_count} ${plural(t.task_count, 'задание', 'задания', 'заданий')}</span>
    ${t.solved_count ? `<span class="solved"><i data-lucide="circle-check"></i>решено ${t.solved_count}</span>` : ''}`;

async function showPicker() {
    state.mode = null;
    state.task = null;
    syncUrl();

    const data = await api('/topics');
    state.topics = data.topics;
    state.lastTopicId = data.last_topic_id;
    const last = state.topics.find((t) => t.id === state.lastTopicId);

    const picker = document.getElementById('picker');
    picker.innerHTML = `
        <div class="hero-grid ${last ? 'two' : ''}">
            ${last ? `
                <button type="button" class="dash-card" data-topic="${last.id}">
                    <span class="glow"></span>
                    <div class="dash-head">
                        <span class="dash-icon"><i data-lucide="history"></i></span>
                        <span class="dash-arrow"><i data-lucide="arrow-up-right"></i></span>
                    </div>
                    <div>
                        <p class="dash-eyebrow">Продолжить · №${last.task_number}</p>
                        <h3 class="dash-title">${escapeHtml(last.name)}</h3>
                        <p class="dash-desc">Вы остановились на этой теме. ${escapeHtml(last.subtopics.join(', '))}</p>
                    </div>
                </button>` : ''}
            <button type="button" class="dash-card tornado" data-tornado>
                <span class="glow"></span>
                <div class="dash-head">
                    <span class="dash-icon"><i data-lucide="tornado"></i></span>
                    <span class="dash-arrow"><i data-lucide="arrow-up-right"></i></span>
                </div>
                <div>
                    <p class="dash-eyebrow">Все темы</p>
                    <h3 class="dash-title">Нарешка «Торнадо»</h3>
                    <p class="dash-desc">Задачи по всем темам вперемешку — как на экзамене,
                        где не знаешь, что попадётся следующим.</p>
                </div>
            </button>
        </div>

        <h2 class="section-title">Выберите тему</h2>
        <div class="topic-grid">
            ${state.topics.map((t) => `
                <button type="button" class="topic-card ${t.id === state.lastTopicId ? 'is-last' : ''}" data-topic="${t.id}">
                    <span class="number-badge">№${t.task_number}</span>
                    <span class="topic-info">
                        <span class="topic-name">${escapeHtml(t.name)}</span>
                        <span class="topic-subs">${escapeHtml(t.subtopics.join(' · '))}</span>
                        <span class="topic-foot">
                            ${topicStats(t)}
                            ${t.id === state.lastTopicId ? '<span class="chip-last">Последняя тема</span>' : ''}
                        </span>
                    </span>
                </button>`).join('')}
        </div>
    `;

    picker.querySelectorAll('[data-topic]').forEach((btn) => {
        const topic = state.topics.find((t) => t.id === Number(btn.dataset.topic));
        btn.addEventListener('click', () => startFeed({ type: 'topic', topic }));
    });
    picker.querySelector('[data-tornado]').addEventListener('click', () => startFeed({ type: 'tornado' }));

    showScreen('picker');
    icons();
}

function showScreen(name) {
    document.getElementById('loading').hidden = true;
    document.getElementById('picker').hidden = name !== 'picker';
    document.getElementById('feed').hidden = name !== 'feed';
    window.scrollTo({ top: 0 });
}

// ---------------------------------- лента ----------------------------------

async function startFeed(mode, taskId = null) {
    state.mode = mode;
    state.task = null;
    state.seen = [];

    const modeBox = document.getElementById('feed-mode');
    modeBox.innerHTML = mode.type === 'tornado'
        ? `<span class="mode-icon tornado"><i data-lucide="tornado"></i></span>
           <span class="mode-text"><span class="mode-label">Нарешка</span>
           <span class="mode-name">Торнадо · все темы</span></span>`
        : `<span class="mode-icon">№${mode.topic.task_number}</span>
           <span class="mode-text"><span class="mode-label">Тема</span>
           <span class="mode-name">${escapeHtml(mode.topic.name)}</span></span>`;

    showScreen('feed');
    document.getElementById('task-slot').innerHTML = '<p class="empty">Подбираем задание…</p>';
    renderStats();
    icons();

    const task = taskId ? await api(`/tasks/${taskId}`).catch(() => null) : null;
    showTask(task ?? await fetchNext());
}

function renderStats(bump) {
    document.getElementById('solved-count').textContent = state.solved;
    document.getElementById('streak-count').textContent = state.streak;
    if (bump) {
        document.querySelectorAll('.feed-stats .stat').forEach((el) => {
            el.classList.remove('bump');
            void el.offsetWidth; // перезапуск анимации
            el.classList.add('bump');
        });
    }
}

function showTask(task) {
    state.task = task;
    state.seen.push(task.id);
    syncUrl();

    const meta = [
        task.subtopic ? escapeHtml(task.topic) : null,
        `Часть ${task.part}`,
        DIFFICULTY[task.difficulty],
        `${task.max_score} ${plural(task.max_score, 'балл', 'балла', 'баллов')}`,
        ...task.sources.map(escapeHtml),
    ].filter(Boolean).join('<span class="dot">·</span>');

    const slot = document.getElementById('task-slot');
    slot.innerHTML = `
        <article class="card glass task">
            <div class="task-head">
                <span class="number-badge">№${task.task_number}</span>
                <div class="task-info">
                    <h2 class="task-title">${escapeHtml(task.subtopic ?? task.topic ?? 'Задание')}</h2>
                    <p class="task-meta">${meta}</p>
                </div>
                <button type="button" class="md-toggle" aria-pressed="false"
                        title="Показать, как условие хранится в базе">MD</button>
            </div>

            <pre class="source" hidden></pre>
            <div class="md condition">${renderMarkdown(task.condition)}</div>

            <form class="answer" autocomplete="off" novalidate>
                <input class="input" name="answer" placeholder="${PLACEHOLDERS[task.answer_type] ?? 'Ответ'}"
                       aria-label="Ответ" inputmode="decimal">
                <button class="btn btn-primary" type="submit"><i data-lucide="check"></i>Проверить</button>
            </form>
            <p class="hint">${HINTS[task.answer_type] ?? ''}</p>

            <div class="feedback"></div>
        </article>
    `;

    const card = slot.querySelector('.task');
    const source = card.querySelector('.source');
    const mdToggle = card.querySelector('.md-toggle');
    source.textContent = task.condition;
    mdToggle.addEventListener('click', () => {
        source.hidden = !source.hidden;
        mdToggle.setAttribute('aria-pressed', String(!source.hidden));
    });

    const form = card.querySelector('.answer');
    const input = form.elements.answer;
    input.addEventListener('input', () => input.classList.remove('error'));
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        submitAnswer(task, card);
    });

    icons();
    input.focus({ preventScroll: true });
}

async function submitAnswer(task, card) {
    const form = card.querySelector('.answer');
    const input = form.elements.answer;
    const button = form.querySelector('.btn');
    const feedback = card.querySelector('.feedback');

    if (!input.value.trim()) {
        input.classList.add('error');
        input.focus();
        return;
    }

    button.disabled = true;
    try {
        const result = await api(`/tasks/${task.id}/submit`, {
            method: 'POST',
            body: JSON.stringify({ answer: input.value }),
        });

        if (result.is_correct) {
            state.solved += 1;
            state.streak += 1;
            renderStats(true);

            input.classList.add('success');
            input.readOnly = true;
            button.hidden = true;

            const streakText = state.streak >= 3 ? ` · серия ${state.streak} 🔥` : '';
            feedback.outerHTML = `
                <div class="result ok">
                    <i data-lucide="circle-check"></i>
                    <div><div class="result-title">Верно! +${result.score} ${plural(result.score, 'балл', 'балла', 'баллов')}${streakText}</div></div>
                </div>
                ${nextActionsHtml(task)}
                ${solutionHtml(result, false)}
            `;
            bindNextActions(card);
            icons();
            card.querySelector('.next-actions .btn').focus({ preventScroll: true });
        } else {
            state.streak = 0;
            renderStats();

            input.classList.add('error');
            feedback.innerHTML = `
                <div class="result fail">
                    <i data-lucide="circle-x"></i>
                    <div>
                        <div class="result-title">Неверно</div>
                        <div class="result-text">Проверьте вычисления и попробуйте ещё раз.</div>
                    </div>
                </div>
                <button type="button" class="btn btn-ghost-secondary reveal">
                    <i data-lucide="eye"></i>Показать ответ и решение
                </button>
            `;
            feedback.querySelector('.reveal').addEventListener('click', () => revealSolution(card, task, result));
            icons();
            input.select();
        }
    } catch (err) {
        feedback.innerHTML = `
            <div class="result fail"><i data-lucide="wifi-off"></i>
                <div><div class="result-title">Не удалось проверить ответ</div>
                <div class="result-text">${escapeHtml(err.message)}</div></div>
            </div>`;
        icons();
    } finally {
        button.disabled = false;
    }
}

function revealSolution(card, task, result) {
    const form = card.querySelector('.answer');
    form.elements.answer.readOnly = true;
    form.querySelector('.btn').hidden = true;

    card.querySelector('.feedback').outerHTML = `
        <div class="result fail">
            <i data-lucide="info"></i>
            <div>
                <div class="result-title">Правильный ответ: ${escapeHtml(result.correct_answer)}</div>
                <div class="result-text">Разберите решение и закрепите тему похожей задачей.</div>
            </div>
        </div>
        ${solutionHtml(result, true)}
        ${nextActionsHtml(task)}
    `;
    bindNextActions(card);
    icons();
}

function nextActionsHtml(task) {
    return `
        <div class="next-actions">
            <button type="button" class="btn btn-primary" data-action="next">
                Следующее задание<i data-lucide="arrow-right"></i>
            </button>
            <button type="button" class="btn btn-outline-primary" data-action="similar"
                    ${task.similar_count ? '' : 'disabled title="Похожих заданий пока нет"'}>
                <i data-lucide="shuffle"></i>Решить похожее
            </button>
        </div>`;
}

function solutionHtml(result, open) {
    if (!result.solution) return '';
    return `
        <details class="solution" ${open ? 'open' : ''}>
            <summary><i data-lucide="chevron-right"></i>Решение</summary>
            <div class="md">${renderMarkdown(result.solution)}</div>
        </details>`;
}

function bindNextActions(card) {
    const run = (load) => async (e) => {
        const btn = e.currentTarget;
        btn.disabled = true;
        try {
            showTask(await load());
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } catch (err) {
            btn.disabled = false;
            alert(err.message);
        }
    };
    card.querySelector('[data-action="next"]').addEventListener('click', run(fetchNext));
    card.querySelector('[data-action="similar"]').addEventListener('click', run(fetchSimilar));
}

// ----------------------------------- тема ----------------------------------

function initTheme() {
    document.getElementById('theme-toggle').addEventListener('click', () => {
        const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
        document.documentElement.dataset.theme = next;
        try { localStorage.setItem('concept-theme', next); } catch { /* приватный режим */ }
    });
}

// ---------------------------------- старт ----------------------------------

async function init() {
    icons();
    initTheme();
    document.getElementById('back').addEventListener('click', () => showPicker());

    try {
        // ?topic=ID&task=ID или ?mode=tornado&task=ID — продолжить ленту после перезагрузки
        const params = new URLSearchParams(location.search);
        const taskId = params.get('task');

        if (params.get('mode') === 'tornado') {
            await startFeed({ type: 'tornado' }, taskId);
            return;
        }
        if (params.get('topic')) {
            const { topics } = await api('/topics');
            const topic = topics.find((t) => t.id === Number(params.get('topic')));
            if (topic) {
                await startFeed({ type: 'topic', topic }, taskId);
                return;
            }
        }
        await showPicker();
    } catch (err) {
        document.getElementById('loading').textContent = `Не удалось загрузить: ${err.message}`;
    }
}

init();
