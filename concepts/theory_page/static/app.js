// Страница «Теория»: маршрут по карте ЕГЭ.
// Порядок тем уже задан в data.js (уровень → ветка → номер темы), здесь только прогресс и отрисовка.

const { branches: BRANCHES, levels: LEVELS, topics: TOPICS } = window.THEORY;
const DEMO_POSITION = '3.2.3'; // демо: всё до этого урока уже пройдено (прогресс придёт с бэкенда)
// Ведёт на концепт страницы урока (в приложении будет /learning/lesson/:id, как в entities/lesson/NextLesson)
const lessonUrl = (id) => `../../lesson_page/static/index.html?id=${id}`;

const $ = (id) => document.getElementById(id);
const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const plural = (n, one, few, many) => {
    const m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return one;
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
    return many;
};
const leaves = (nodes) => nodes.reduce((a, n) => a + (n.c ? leaves(n.c) : 1), 0);

// ------------------------------- модель -------------------------------

TOPICS.forEach((t, i) => { t.order = i + 1; });
const LESSONS = TOPICS.flatMap((t) => t.lessons.map((l, i) => Object.assign(l, {
    topic: t,
    index: i + 1,
    minutes: 12 + 3 * Math.min(leaves(l.outline), 8),
})));
LESSONS.forEach((l, i) => { l.seq = i; });
const lessonById = Object.fromEntries(LESSONS.map((l) => [l.id, l]));
const topicById = Object.fromEntries(TOPICS.map((t) => [t.id, t]));

// Уроки засчитываются только по итогам прохождения, вручную отметить нельзя
const done = new Set(LESSONS.slice(0, lessonById[DEMO_POSITION].seq).map((l) => l.id));

const doneIn = (t) => t.lessons.filter((l) => done.has(l.id)).length;
const nextLesson = () => LESSONS.find((l) => !done.has(l.id)) || null;
// Тема со следующим уроком считается «в процессе», даже если в ней ещё ничего не пройдено
const statusOf = (t) => {
    const d = doneIn(t);
    if (d === t.lessons.length) return 'done';
    return d || nextLesson()?.topic === t ? 'progress' : 'todo';
};

const state = {
    level: (nextLesson() || LESSONS.at(-1)).topic.l,
    status: 'progress',
    query: '',
    view: 'route',
    open: new Set([nextLesson()?.topic.id].filter(Boolean)),
};

// ------------------------------ отрисовка ------------------------------

function renderNext() {
    const l = nextLesson();
    const card = $('next-card');
    if (!l) {
        $('next-badge').textContent = 'Программа пройдена';
        $('next-title').textContent = 'Все 72 темы закрыты — время для вариантов';
        $('next-meta').textContent = `${LESSONS.length} уроков позади`;
        card.removeAttribute('href');
        return;
    }
    const t = l.topic;
    $('next-badge').textContent = `Уровень ${t.l} · Ветка ${t.b + 1} · ${t.id}. ${t.name}`;
    $('next-title').textContent = l.name;
    $('next-meta').textContent = `Примерно ${l.minutes} ${plural(l.minutes, 'минута', 'минуты', 'минут')} · Урок ${l.index} из ${t.lessons.length} · Тема ${t.order} из ${TOPICS.length}`;
    card.href = lessonUrl(l.id);
}

function renderProgress() {
    const d = done.size;
    const topicsDone = TOPICS.filter((t) => statusOf(t) === 'done').length;
    const pc = Math.round((d / LESSONS.length) * 100);
    $('ring-arc').setAttribute('stroke-dasharray', `${(d / LESSONS.length) * 100} 100`);
    $('ring-pc').textContent = `${pc}%`;
    $('progress-sub').textContent = `${topicsDone} из ${TOPICS.length} тем · ${d} из ${LESSONS.length} уроков`;

    $('level-bars').innerHTML = LEVELS.map((lv, i) => {
        const ls = LESSONS.filter((l) => l.topic.l === i);
        const ld = ls.filter((l) => done.has(l.id)).length;
        return `<li><button type="button" class="level-row" data-level="${i}">
            <span class="lr-name">${i}. ${lv.name} <span>· ${lv.desc.split(',')[0]}</span></span>
            <span class="lr-count">${ld}/${ls.length}</span>
            <span class="bar ${ld === ls.length ? 'done' : ''}"><i style="width:${(ld / ls.length) * 100}%"></i></span>
        </button></li>`;
    }).join('');
}

function renderLevelTabs() {
    const cur = nextLesson()?.topic.l;
    $('level-tabs').innerHTML = LEVELS.map((lv, i) => {
        const ls = LESSONS.filter((l) => l.topic.l === i);
        const ld = ls.filter((l) => done.has(l.id)).length;
        const nTopics = TOPICS.filter((t) => t.l === i).length;
        let st = `<span class="lt-state">${ld}/${ls.length} уроков</span>`;
        if (ld === ls.length) st = `<span class="lt-state is-done"><i data-lucide="circle-check"></i>Пройден</span>`;
        else if (i === cur) st = `<span class="lt-state is-current"><i data-lucide="map-pin"></i>Вы здесь</span>`;
        return `<button type="button" role="tab" class="level-tab" data-level="${i}" aria-selected="${i === state.level && !state.query}">
            <span class="lt-top"><span class="lt-num">Уровень ${i}</span>${st}</span>
            <span class="lt-name">${lv.name}</span>
            <span class="lt-desc">${lv.desc} · ${nTopics} ${plural(nTopics, 'тема', 'темы', 'тем')}</span>
            <span class="bar ${ld === ls.length ? 'done' : ''}"><i style="width:${(ld / ls.length) * 100}%"></i></span>
        </button>`;
    }).join('');
}

function highlight(text) {
    const s = esc(text);
    if (!state.query) return s;
    const q = esc(state.query).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return s.replace(new RegExp(q, 'gi'), (m) => `<mark>${m}</mark>`);
}

const matches = (t) => {
    if (!state.query) return true;
    const q = state.query.toLowerCase();
    return (t.id + ' ' + t.name).toLowerCase().includes(q)
        || t.lessons.some((l) => (l.name + ' ' + l.note).toLowerCase().includes(q));
};

function topicHTML(t, next) {
    const st = statusOf(t);
    const d = doneIn(t), n = t.lessons.length;
    const isNext = next && next.topic === t;
    const cls = ['topic', `is-${st}`, isNext && 'is-next', state.open.has(t.id) && 'open'].filter(Boolean).join(' ');
    const step = st === 'done' ? '<i data-lucide="check"></i>' : isNext ? '<i data-lucide="play"></i>' : String(t.order).padStart(2, '0');
    const pill = isNext ? '<span class="pill next"><i data-lucide="sparkles"></i>Сейчас</span>'
        : st === 'done' ? '<span class="pill done">Завершена</span>' : '';
    const tasks = t.tasks.map((x) => `<span class="tag">№${x}</span>`).join('');
    const q = state.query.toLowerCase();

    const lessons = t.lessons.map((l) => {
        const ok = done.has(l.id);
        const isNextL = next === l;
        const hit = q && (l.name + ' ' + l.note).toLowerCase().includes(q);
        const ico = ok ? 'circle-check' : isNextL ? 'circle-play' : 'circle';
        const side = ok ? 'пройден' : isNextL ? 'следующий →' : `${l.minutes} мин`;
        return `<li><button type="button" class="lesson ${ok ? 'is-done' : ''} ${isNextL ? 'is-next' : ''}" data-lesson="${l.id}">
            <i data-lucide="${ico}" class="l-ico"></i>
            <span class="l-name"><span class="l-id">${l.id}</span>${highlight(l.name)}${l.note ? `<span class="l-note">${hit ? highlight(l.note) : esc(l.note)}</span>` : ''}</span>
            <span class="l-side">${side}</span>
        </button></li>`;
    }).join('');

    return `<li class="${cls}" id="topic-${t.id}" style="--p:${(d / n) * 100}%">
        <button type="button" class="topic-row" data-topic="${t.id}" aria-expanded="${state.open.has(t.id)}">
            <span class="step" aria-hidden="true">${step}</span>
            <span class="t-main">
                <span class="t-title"><span class="t-id">${t.id}</span>${highlight(t.name)}</span>
                <span class="t-meta">${pill}<span>Тема ${t.order} из ${TOPICS.length}</span><span>${n} ${plural(n, 'урок', 'урока', 'уроков')}</span>${tasks}</span>
            </span>
            <span class="t-prog"><span class="bar ${st === 'done' ? 'done' : ''}"><i style="width:${(d / n) * 100}%"></i></span><span class="num">${d}/${n}</span></span>
            <i data-lucide="chevron-down" class="chev"></i>
        </button>
        <ul class="lessons" ${state.open.has(t.id) ? '' : 'hidden'}>${lessons}</ul>
    </li>`;
}

function renderRoute() {
    const next = nextLesson();
    const pool = TOPICS.filter((t) => (state.query ? matches(t) : t.l === state.level))
        .filter((t) => state.status === 'all' || statusOf(t) === state.status);

    if (state.query) {
        $('filter-note').textContent = `По запросу «${state.query}»: ${pool.length} ${plural(pool.length, 'тема', 'темы', 'тем')} на всех уровнях`;
    } else {
        const lt = TOPICS.filter((t) => t.l === state.level);
        $('filter-note').textContent = `Уровень ${state.level}: ${lt.filter((t) => statusOf(t) === 'done').length} из ${lt.length} тем завершено`;
    }

    if (!pool.length) {
        $('route-list').innerHTML = '<div class="empty">Здесь пока пусто — попробуйте другой фильтр.</div>';
        return;
    }

    // При поиске группируем ещё и по уровню, чтобы порядок оставался читаемым
    const levels = [...new Set(pool.map((t) => t.l))];
    $('route-list').innerHTML = levels.map((li) => {
        const head = state.query ? `<h3 class="section-title" style="margin-top:12px">Уровень ${li} · ${LEVELS[li].name}</h3>` : '';
        return head + LEVELS[li].order.map((bi) => {
            const bname = BRANCHES[bi];
            const ts = pool.filter((t) => t.l === li && t.b === bi);
            if (!ts.length) return '';
            const all = TOPICS.filter((t) => t.l === li && t.b === bi);
            const bd = all.filter((t) => statusOf(t) === 'done').length;
            return `<div class="branch" style="--c:var(--b${bi + 1})">
                <div class="branch-head">
                    <span class="branch-dot"></span>
                    <span class="branch-name"><span>Ветка ${bi + 1}</span>${bname}</span>
                    <span class="branch-count">${bd}/${all.length} ${plural(all.length, 'тема', 'темы', 'тем')}</span>
                </div>
                <ol class="topics">${ts.map((t) => topicHTML(t, next)).join('')}</ol>
            </div>`;
        }).join('');
    }).join('');
}

function renderMap() {
    const next = nextLesson();
    let html = '<div></div>';
    BRANCHES.forEach((b, bi) => {
        const ls = LESSONS.filter((l) => l.topic.b === bi);
        const d = ls.filter((l) => done.has(l.id)).length;
        html += `<div class="m-bhead" style="--c:var(--b${bi + 1})"><span>Ветка ${bi + 1}</span><b>${b}</b>
            <div class="bar"><i style="width:${(d / ls.length) * 100}%"></i></div></div>`;
    });
    LEVELS.forEach((lv, li) => {
        html += `<div class="m-lab"><b>Уровень ${li}</b><span>${lv.name}</span></div>`;
        BRANCHES.forEach((_, bi) => {
            const ts = TOPICS.filter((t) => t.l === li && t.b === bi);
            const style = `--c:var(--b${bi + 1})`;
            if (!ts.length) { html += `<div class="m-cell none" style="${style}">нет уровня</div>`; return; }
            html += `<div class="m-cell" style="${style}">` + ts.map((t) => {
                const st = statusOf(t), d = doneIn(t), n = t.lessons.length;
                const isNext = next && next.topic === t;
                return `<button type="button" class="m-tile is-${st} ${isNext ? 'is-next' : ''}" data-goto="${t.id}" title="${esc(t.name)}">
                    <span class="mt-id">${t.id}</span><span>${esc(t.name)}</span>
                    ${st === 'done' ? '' : `<span class="bar"><i style="width:${(d / n) * 100}%"></i></span>`}
                </button>`;
            }).join('') + '</div>';
        });
    });
    $('map').innerHTML = html;
}

function render() {
    renderNext();
    renderProgress();
    renderLevelTabs();
    if (state.view === 'route') renderRoute(); else renderMap();
    lucide.createIcons();
}

// ------------------------------- урок -------------------------------

let current = null;
let lastFocus = null;

const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const flatText = (n) => n.t + (n.c ? ': ' + n.c.map(flatText).join('; ') : '');

// Конспект без ручного текста: «Подпись: формула» → карточка формулы, остальное → главное
function autoSummary(l) {
    const formulas = [], points = [];
    l.outline.forEach((n) => {
        const m = n.t.match(/^([^:]{2,60}):\s(.+)$/);
        if (!n.c && m && /[=<>≤≥√^·≠⋮≡]/.test(m[2])) formulas.push([m[1], m[2]]);
        else points.push(flatText(n));
    });
    const intro = l.note ? `${capitalize(l.note)}.` : `Урок из темы «${l.topic.name}».`;
    return { intro, formulas, points };
}

function conspectHTML(l) {
    const s = window.SUMMARIES?.[l.id] || autoSummary(l);
    let html = `<section class="c-block"><h3 class="c-title">Кратко</h3><p class="c-intro">${esc(s.intro)}</p></section>`;
    if (s.formulas?.length) {
        html += `<section class="c-block"><h3 class="c-title">Формулы и правила</h3><div class="c-formulas">${
            s.formulas.map(([label, f]) => `<div class="c-formula"><span>${esc(label)}</span><code>${esc(f)}</code></div>`).join('')
        }</div></section>`;
    }
    if (s.points?.length) {
        const tag = s.steps ? 'ol' : 'ul';
        html += `<section class="c-block"><h3 class="c-title">${s.steps ? 'Порядок действий' : 'Главное'}</h3>
            <${tag} class="c-points">${s.points.map((p) => `<li>${esc(p)}</li>`).join('')}</${tag}></section>`;
    }
    if (s.tip) {
        const warn = s.tip.kind === 'warn';
        html += `<div class="c-tip ${warn ? 'warn' : ''}"><i data-lucide="${warn ? 'triangle-alert' : 'lightbulb'}"></i>
            <p><b>${warn ? 'Частая ошибка' : 'Запомни'}.</b> ${esc(s.tip.text)}</p></div>`;
    }
    if (s.example) {
        html += `<section class="c-block c-example"><h3 class="c-title">Пример</h3>
            <p>${esc(s.example.q)}</p><code>${esc(s.example.a)}</code></section>`;
    }
    return html;
}

function openLesson(id) {
    current = lessonById[id];
    if (!current) return;
    const t = current.topic;
    lastFocus = document.activeElement;
    $('d-crumb').textContent = `Уровень ${t.l} · Ветка ${t.b + 1} · ${t.id}. ${t.name}`;
    $('d-title').textContent = `${current.id}. ${current.name}`;
    const status = done.has(current.id) ? 'Пройден' : nextLesson() === current ? 'Следующий урок' : 'Не пройден';
    $('d-meta').textContent = [`Урок ${current.index} из ${t.lessons.length}`, `≈ ${current.minutes} мин`,
        ...t.tasks.map((n) => `№${n}`), status].join(' · ');
    $('d-conspect').innerHTML = conspectHTML(current);
    $('d-conspect').parentElement.scrollTop = 0;
    lucide.createIcons();
    $('d-go').href = lessonUrl(current.id);
    $('drawer').classList.add('on');
    $('drawer').setAttribute('aria-hidden', 'false');
    $('backdrop').hidden = false;
    $('d-close').focus();
}

function closeLesson() {
    $('drawer').classList.remove('on');
    $('drawer').setAttribute('aria-hidden', 'true');
    $('backdrop').hidden = true;
    lastFocus?.focus();
}

$('d-close').addEventListener('click', closeLesson);
$('backdrop').addEventListener('click', closeLesson);
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && $('drawer').classList.contains('on')) closeLesson(); });

// ----------------------------- события -----------------------------

function goToTopic(id) {
    const t = topicById[id];
    state.view = 'route';
    state.query = '';
    $('search').value = '';
    state.status = 'all';
    state.level = t.l;
    state.open.add(id);
    syncControls();
    render();
    document.getElementById(`topic-${id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function syncControls() {
    document.querySelectorAll('.segmented button').forEach((b) => b.setAttribute('aria-selected', b.dataset.view === state.view));
    $('view-route').hidden = state.view !== 'route';
    $('view-map').hidden = state.view !== 'map';
    document.querySelectorAll('#status-chips .chip').forEach((c) => c.setAttribute('aria-pressed', c.dataset.status === state.status));
}

$('level-bars').addEventListener('click', (e) => {
    const b = e.target.closest('[data-level]');
    if (!b) return;
    state.level = +b.dataset.level;
    state.view = 'route';
    state.query = '';
    $('search').value = '';
    syncControls(); render();
    $('route-title').scrollIntoView({ behavior: 'smooth', block: 'start' });
});

$('level-tabs').addEventListener('click', (e) => {
    const b = e.target.closest('[data-level]');
    if (!b) return;
    state.level = +b.dataset.level;
    state.query = '';
    $('search').value = '';
    render();
});

$('status-chips').addEventListener('click', (e) => {
    const c = e.target.closest('.chip');
    if (!c) return;
    state.status = c.dataset.status;
    syncControls(); render();
});

$('route-list').addEventListener('click', (e) => {
    const lesson = e.target.closest('[data-lesson]');
    if (lesson) { openLesson(lesson.dataset.lesson); return; }
    const row = e.target.closest('[data-topic]');
    if (!row) return;
    const id = row.dataset.topic;
    state.open.has(id) ? state.open.delete(id) : state.open.add(id);
    const li = row.parentElement;
    li.classList.toggle('open', state.open.has(id));
    row.setAttribute('aria-expanded', state.open.has(id));
    li.querySelector('.lessons').hidden = !state.open.has(id);
});

$('map').addEventListener('click', (e) => {
    const tile = e.target.closest('[data-goto]');
    if (tile) goToTopic(tile.dataset.goto);
});

document.querySelector('.segmented').addEventListener('click', (e) => {
    const b = e.target.closest('[data-view]');
    if (!b) return;
    state.view = b.dataset.view;
    syncControls(); render();
});

let searchTimer;
$('search').addEventListener('input', (e) => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
        state.query = e.target.value.trim();
        if (state.query) {
            state.view = 'route';
            state.status = 'all'; // ищем по всей программе, а не только по начатым темам
            // раскрываем темы, где совпали уроки
            TOPICS.forEach((t) => {
                if (t.lessons.some((l) => (l.name + ' ' + l.note).toLowerCase().includes(state.query.toLowerCase()))) state.open.add(t.id);
            });
        }
        syncControls(); render();
    }, 150);
});

$('theme-toggle').addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('concept-theme', next); } catch { /* приватный режим */ }
});

syncControls();
render();
