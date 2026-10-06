// Концепт «Быстрое повторение»: выбор режима (теория / вычисления / микс) -> лента коротких вопросов.
// Порядок внутри режима случайный; вопрос с ошибкой возвращается через несколько карточек.
// Итоги повторений хранятся в localStorage и показываются на стартовом экране.
// Позже очередь будет строить алгоритм повторения на сервере, а история — браться из API.

const QUESTIONS = window.REVIEW_QUESTIONS;
const LETTERS = ['А', 'Б', 'В', 'Г', 'Д'];
const RETRY_AFTER = [3, 5]; // через сколько карточек вернуть вопрос с ошибкой
const STORAGE_KEY = 'concept-review:sessions';
const HISTORY_LIMIT = 50;   // сколько последних повторений хранить
const RECENT_SHOWN = 5;     // сколько показывать в списке

const KIND = {
    theory: { label: 'Теория', icon: 'book-open' },
    calc: { label: 'Вычисление', icon: 'calculator' },
};

const MODES = {
    theory: {
        label: 'Теория', icon: 'book-open',
        desc: 'Формулы, определения и свойства — проверить, что база в голове.',
    },
    calc: {
        label: 'Вычисления', icon: 'calculator',
        desc: 'Короткие примеры на счёт: степени, корни, проценты, производные.',
    },
    mix: {
        label: 'Микс', icon: 'shuffle',
        desc: 'Теория и вычисления вперемешку по всем темам.',
    },
};

const state = {
    mode: null,
    pool: [],        // индексы вопросов режима
    queue: [],       // { id, retry }
    current: null,   // { id, retry, order: перемешанные индексы вариантов, picked }
    lastId: null,
    count: 0,        // номер карточки в ленте
    session: null,   // { id, mode, started, answers, correct, streak, bestStreak }
};

const $ = (id) => document.getElementById(id);
const icons = () => lucide.createIcons();

const plural = (n, one, few, many) => {
    const m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return one;
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
    return many;
};

function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
}

const randInt = (min, max) => min + Math.floor(Math.random() * (max - min + 1));
const percent = (part, total) => (total ? Math.round((part / total) * 100) : 0);
const poolOf = (mode) => QUESTIONS.map((_, i) => i).filter((i) => mode === 'mix' || QUESTIONS[i].kind === mode);

/** Текст с формулами в $...$ -> HTML. Тексты свои, из questions.js, поэтому без санитайзера */
function tex(src) {
    return src.replace(/\$([^$]+)\$/g, (_, f) => katex.renderToString(f, { throwOnError: false }));
}

// ----------------------------------- история -----------------------------------

function loadSessions() {
    try {
        const list = JSON.parse(localStorage.getItem(STORAGE_KEY));
        return Array.isArray(list) ? list : [];
    } catch {
        return [];
    }
}

/** Сохраняет текущее повторение после каждого ответа — закрытая вкладка ничего не теряет */
function saveSession() {
    const s = state.session;
    const list = loadSessions().filter((x) => x.id !== s.id);
    list.push({ id: s.id, mode: s.mode, started: s.started, answers: s.answers, correct: s.correct, bestStreak: s.bestStreak });
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(list.slice(-HISTORY_LIMIT)));
    } catch { /* приватный режим — статистика просто не сохранится */ }
}

function formatWhen(ts) {
    const d = new Date(ts);
    const time = d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    const dayStart = (x) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime();
    const days = Math.round((dayStart(new Date()) - dayStart(d)) / 86400000);
    if (days === 0) return `Сегодня, ${time}`;
    if (days === 1) return `Вчера, ${time}`;
    return `${d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })}, ${time}`;
}

const accuracyLevel = (p) => (p >= 80 ? 'ok' : p >= 50 ? 'warn' : 'bad');

function historyHtml(sessions) {
    if (!sessions.length) {
        return `
            <div class="history-empty">
                <i data-lucide="chart-no-axes-column"></i>
                <p>Здесь появится статистика, когда вы ответите хотя бы на один вопрос.</p>
            </div>`;
    }

    const answers = sessions.reduce((sum, s) => sum + s.answers, 0);
    const correct = sessions.reduce((sum, s) => sum + s.correct, 0);
    const best = Math.max(...sessions.map((s) => s.bestStreak));
    const tiles = [
        { icon: 'repeat', value: sessions.length, label: plural(sessions.length, 'повторение', 'повторения', 'повторений') },
        { icon: 'list-checks', value: answers, label: plural(answers, 'ответ', 'ответа', 'ответов') },
        { icon: 'target', value: `${percent(correct, answers)}%`, label: 'точность' },
        { icon: 'flame', value: best, label: 'лучшая серия', cls: 'streak' },
    ];

    const recent = sessions.slice(-RECENT_SHOWN).reverse();
    return `
        <div class="tiles">
            ${tiles.map((t) => `
                <div class="tile ${t.cls ?? ''}">
                    <i data-lucide="${t.icon}"></i>
                    <span class="tile-value">${t.value}</span>
                    <span class="tile-label">${t.label}</span>
                </div>`).join('')}
        </div>
        <h3 class="c-title">Последние</h3>
        <ul class="recent">
            ${recent.map((s) => {
                const p = percent(s.correct, s.answers);
                return `
                    <li class="recent-row">
                        <span class="recent-ico"><i data-lucide="${MODES[s.mode].icon}"></i></span>
                        <span class="recent-text">
                            <span class="recent-mode">${MODES[s.mode].label}</span>
                            <span class="recent-when">${formatWhen(s.started)}</span>
                        </span>
                        <span class="recent-count">${s.correct} из ${s.answers}</span>
                        <span class="pill ${accuracyLevel(p)}">${p}%</span>
                    </li>`;
            }).join('')}
        </ul>`;
}

// ----------------------------------- старт -----------------------------------

function showStart() {
    state.mode = null;
    state.current = null;
    history.replaceState(null, '', location.pathname);

    const sessions = loadSessions();
    $('modes').innerHTML = Object.entries(MODES).map(([key, m]) => {
        const n = poolOf(key).length;
        const last = sessions.filter((s) => s.mode === key).at(-1);
        const lastText = last ? `В прошлый раз ${percent(last.correct, last.answers)}%` : 'Ещё не проходили';
        return `
            <button type="button" class="mode-card ${key === 'mix' ? 'accent' : ''}" data-mode="${key}">
                <span class="glow"></span>
                <span class="mode-head">
                    <span class="mode-ico"><i data-lucide="${m.icon}"></i></span>
                    <span class="mode-arrow"><i data-lucide="arrow-up-right"></i></span>
                </span>
                <span class="mode-body">
                    <span class="mode-title">${m.label}</span>
                    <span class="mode-desc">${m.desc}</span>
                </span>
                <span class="mode-foot">
                    <span>${n} ${plural(n, 'вопрос', 'вопроса', 'вопросов')}</span>
                    <span class="dot">·</span>
                    <span>${lastText}</span>
                </span>
            </button>`;
    }).join('');
    $('modes').querySelectorAll('[data-mode]').forEach((btn) => {
        btn.addEventListener('click', () => startFeed(btn.dataset.mode));
    });

    $('history').innerHTML = historyHtml(sessions);
    showScreen('start');
    icons();
}

function showScreen(name) {
    $('start').hidden = name !== 'start';
    $('feed').hidden = name !== 'feed';
    window.scrollTo({ top: 0 });
}

// ----------------------------------- лента -----------------------------------

function startFeed(mode) {
    state.mode = mode;
    state.pool = poolOf(mode);
    state.queue = [];
    state.lastId = null;
    state.count = 0;
    state.session = { id: Date.now(), mode, started: Date.now(), answers: 0, correct: 0, streak: 0, bestStreak: 0 };
    history.replaceState(null, '', `?mode=${mode}`);

    const m = MODES[mode];
    $('feed-mode').innerHTML = `
        <span class="fm-ico ${mode === 'mix' ? 'accent' : ''}"><i data-lucide="${m.icon}"></i></span>
        <span class="fm-text"><span class="fm-label">Повторение</span><span class="fm-name">${m.label}</span></span>`;

    renderStats();
    showScreen('feed');
    showCard();
}

function nextQuestion() {
    if (!state.queue.length) {
        // Новый круг по вопросам режима; первым не ставим только что показанный
        const ids = shuffle(state.pool);
        if (ids[0] === state.lastId && ids.length > 1) ids.push(ids.shift());
        state.queue = ids.map((id) => ({ id, retry: false }));
    }
    const item = state.queue.shift();
    state.lastId = item.id;
    return item;
}

function scheduleRetry(id) {
    // Убираем вопрос из текущего круга и ставим его поближе
    state.queue = state.queue.filter((q) => q.id !== id);
    const pos = Math.min(randInt(...RETRY_AFTER) - 1, state.queue.length);
    state.queue.splice(pos, 0, { id, retry: true });
}

function showCard() {
    const item = nextQuestion();
    const q = QUESTIONS[item.id];
    state.count += 1;
    state.current = { ...item, order: shuffle(q.options.map((_, i) => i)), picked: null };

    const kind = KIND[q.kind];
    $('slot').innerHTML = `
        <article class="glass card q-card">
            <div class="q-head">
                <span class="q-num">Вопрос ${state.count}</span>
                <span class="tag">${q.topic}</span>
                <span class="tag kind-${q.kind}"><i data-lucide="${kind.icon}"></i>${kind.label}</span>
                ${item.retry ? '<span class="tag retry"><i data-lucide="rotate-ccw"></i>Повтор ошибки</span>' : ''}
            </div>

            <p class="q-text">${tex(q.q)}</p>

            <div class="options" role="group" aria-label="Варианты ответа">
                ${state.current.order.map((oi, pos) => `
                    <button type="button" class="option" data-opt="${oi}">
                        <span class="opt-letter">${LETTERS[pos]}</span>
                        <span class="opt-text">${tex(q.options[oi])}</span>
                    </button>`).join('')}
            </div>

            <div class="q-feedback" id="feedback"></div>

            <div class="q-foot" id="foot">
                <span class="key-hint">Клавиши <kbd>1</kbd>–<kbd>${q.options.length}</kbd> выбирают ответ</span>
                <button type="button" class="chip-btn" id="dont-know"><i data-lucide="circle-help"></i>Не знаю</button>
            </div>
        </article>`;

    $('slot').querySelectorAll('[data-opt]').forEach((btn) => {
        btn.addEventListener('click', () => answer(Number(btn.dataset.opt)));
    });
    $('dont-know').addEventListener('click', () => answer(-1));
    icons();
}

/** opt — индекс варианта в банке (0 — правильный), -1 — «Не знаю» */
function answer(opt) {
    const cur = state.current;
    if (cur.picked !== null) return;
    cur.picked = opt;

    const q = QUESTIONS[cur.id];
    const ok = opt === 0;
    const s = state.session;
    s.answers += 1;
    if (ok) {
        s.correct += 1;
        s.streak += 1;
        s.bestStreak = Math.max(s.bestStreak, s.streak);
    } else {
        s.streak = 0;
        scheduleRetry(cur.id);
    }
    saveSession();
    renderStats(ok);

    const card = $('slot').querySelector('.q-card');
    card.classList.add(ok ? 'is-ok' : opt === -1 ? 'is-shown' : 'is-bad');
    card.querySelectorAll('[data-opt]').forEach((btn) => {
        const oi = Number(btn.dataset.opt);
        btn.disabled = true;
        if (oi === 0) {
            btn.classList.add('is-right');
            btn.insertAdjacentHTML('beforeend', '<i data-lucide="check"></i>');
        } else if (oi === opt) {
            btn.classList.add('is-wrong');
            btn.insertAdjacentHTML('beforeend', '<i data-lucide="x"></i>');
        }
    });

    const title = ok
        ? `Верно!${s.streak >= 3 ? ` Серия ${s.streak} 🔥` : ''}`
        : opt === -1 ? 'Правильный ответ отмечен зелёным.' : 'Неверно.';
    const note = ok ? '' : '<span class="fb-note">Этот вопрос вернётся через пару карточек.</span>';
    $('feedback').innerHTML = `
        <div class="fb ${ok ? 'ok' : opt === -1 ? 'shown' : 'bad'}">
            <i data-lucide="${ok ? 'circle-check' : opt === -1 ? 'info' : 'circle-x'}"></i>
            <div><b>${title}</b> ${tex(q.explain)} ${note}</div>
        </div>`;

    $('foot').innerHTML = `
        <span class="key-hint"><kbd>Enter</kbd> — следующий вопрос</span>
        <button type="button" class="btn btn-primary" id="next">Дальше<i data-lucide="arrow-right"></i></button>`;
    $('next').addEventListener('click', showCard);
    icons();
    $('next').focus({ preventScroll: true });
}

function renderStats(bump) {
    const s = state.session;
    $('stat-total').textContent = s.answers;
    $('stat-accuracy').textContent = s.answers ? `${percent(s.correct, s.answers)}%` : '—';
    $('stat-streak').textContent = s.streak;
    if (bump) {
        const el = $('stat-streak').closest('.stat');
        el.classList.remove('bump');
        void el.offsetWidth; // перезапуск анимации
        el.classList.add('bump');
    }
}

// ----------------------------------- клавиатура -----------------------------------

document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey || e.target.closest?.('input, textarea')) return;
    const cur = state.current;
    if (!cur || $('feed').hidden) return;

    if (cur.picked === null) {
        const pos = Number(e.key) - 1;
        if (pos >= 0 && pos < cur.order.length) answer(cur.order[pos]);
    } else if (e.key === 'Enter') {
        e.preventDefault(); // иначе фокус на «Дальше» нажмёт её второй раз
        showCard();
    }
});

// ----------------------------------- тема и старт -----------------------------------

$('theme-toggle').addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('concept-theme', next); } catch { /* приватный режим */ }
});

$('back').addEventListener('click', showStart);

// ?mode=theory|calc|mix — продолжить ленту после перезагрузки
const initialMode = new URLSearchParams(location.search).get('mode');
if (MODES[initialMode]) startFeed(initialMode);
else showStart();
