// Страница урока: короткие ролики → вопросы под каждым → блоки задач на закрепление → итог.
// Метаданные урока (тема, порядок, следующий урок) берутся из data.js страницы «Теория»,
// содержимое — из lesson.js. Прогресс хранится в localStorage (на бэкенде появится позже).

const DEMO_ID = '1.10.2';
const theoryUrl = '../../theory_page/static/index.html';
const lessonUrl = (id) => `index.html?id=${encodeURIComponent(id)}`;

const $ = (id) => document.getElementById(id);
const plural = (n, one, few, many) => {
    const m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return one;
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
    return many;
};
const mmss = (s) => `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`;
const LETTERS = 'АБВГДЕ';

// ------------------------------- модель -------------------------------

const { topics: TOPICS } = window.THEORY;
const LESSONS = TOPICS.flatMap((t) => t.lessons.map((l, i) => Object.assign(l, { topic: t, index: i + 1 })));

const requested = new URLSearchParams(location.search).get('id') || DEMO_ID;
const lesson = LESSONS.find((l) => l.id === requested) || LESSONS.find((l) => l.id === DEMO_ID);
const isDemo = !window.LESSON_CONTENT[lesson.id];
const content = window.LESSON_CONTENT[lesson.id] || window.LESSON_CONTENT[DEMO_ID];
const STEPS = content.steps;
const FINISH = STEPS.length; // виртуальный шаг «Итог»
const nextLesson = LESSONS[LESSONS.indexOf(lesson) + 1] || null;

const videos = STEPS.filter((s) => s.kind === 'video');
const itemsOf = (s) => (s.kind === 'video' ? s.questions : s.tasks);

const STORE_KEY = `concept-lesson:${lesson.id}`;
const fresh = () => ({ step: 0, max: 0, watched: {}, items: {} });
let state = fresh();
try { state = { ...fresh(), ...JSON.parse(localStorage.getItem(STORE_KEY)) }; } catch { /* нет сохранения */ }
const save = () => { try { localStorage.setItem(STORE_KEY, JSON.stringify(state)); } catch { /* приватный режим */ } };

// Ответ на вопрос/задачу: status — undefined (не решено) | 'ok' | 'shown' (решение открыто); tries — неверные попытки
const itemState = (si, ii) => (state.items[`${si}:${ii}`] ||= { tries: 0, wrong: [], hint: false });
const resolved = (it) => it.status === 'ok' || it.status === 'shown';
const stepDone = (si) => itemsOf(STEPS[si]).every((_, ii) => resolved(itemState(si, ii)));
const stepCounts = (si) => {
    const list = itemsOf(STEPS[si]).map((_, ii) => itemState(si, ii));
    return { total: list.length, done: list.filter(resolved).length };
};

// Ответы вида «1,5», «−2», «3/2» сравниваем как числа
function parseNumber(raw) {
    const s = raw.trim().replace(/\s+/g, '').replace(/,/g, '.').replace(/[−–]/g, '-');
    if (!s) return null;
    const frac = s.match(/^(-?\d+(?:\.\d+)?)\/(-?\d+(?:\.\d+)?)$/);
    if (frac) return +frac[2] === 0 ? null : +frac[1] / +frac[2];
    return /^-?\d+(?:\.\d+)?$/.test(s) ? +s : null;
}
const isCorrect = (task, value) => {
    const x = parseNumber(value);
    return x !== null && task.answer.some((a) => Math.abs(parseNumber(a) - x) < 1e-9);
};

// ------------------------------ шапка ------------------------------

function renderHeader() {
    const t = lesson.topic;
    $('crumb').innerHTML = `<a href="${theoryUrl}">Теория</a> · Уровень ${t.l} · ${t.id}. ${t.name}`;
    $('title').textContent = `${lesson.id}. ${isDemo ? lesson.name : content.title}`;
    $('goal').textContent = content.goal;
    const secs = videos.reduce((a, v) => a + v.duration, 0);
    const nTasks = STEPS.filter((s) => s.kind === 'practice').reduce((a, s) => a + s.tasks.length, 0);
    $('meta').innerHTML = [
        `<span><i data-lucide="circle-play"></i>${videos.length} ${plural(videos.length, 'ролик', 'ролика', 'роликов')} · ${mmss(secs)}</span>`,
        `<span><i data-lucide="pencil-line"></i>${nTasks} ${plural(nTasks, 'задача', 'задачи', 'задач')}</span>`,
        `<span><i data-lucide="list-ordered"></i>Урок ${lesson.index} из ${t.lessons.length}</span>`,
        ...t.tasks.map((n) => `<span class="tag">№${n} ЕГЭ</span>`),
    ].join('');
    $('demo-banner').hidden = !isDemo;
    document.title = `${content.title} — Из нуля в сотку`;
}

// ------------------------------ шаги ------------------------------

const stepIcon = (s) => (s.kind === 'video' ? 'circle-play' : 'pencil-line');
const stepLabel = (si) => {
    if (si === FINISH) return 'Итог';
    const s = STEPS[si];
    if (s.kind === 'video') return `Ролик ${videos.indexOf(s) + 1}`;
    return 'Практика';
};
const reachable = (si) => si <= state.max;

function renderTrack() {
    const nodes = [...STEPS.map((s, si) => si), FINISH].map((si) => {
        const done = si < FINISH ? stepDone(si) : state.max === FINISH;
        const cur = si === state.step;
        const kind = si === FINISH ? 'finish' : STEPS[si].kind;
        const ico = done && !cur ? 'check' : si === FINISH ? 'flag' : stepIcon(STEPS[si]);
        return `<li class="tr-step is-${kind} ${done ? 'is-done' : ''} ${cur ? 'is-current' : ''}">
            <button type="button" data-step="${si}" ${reachable(si) ? '' : 'disabled'} aria-current="${cur ? 'step' : 'false'}"
                title="${si === FINISH ? 'Итог урока' : STEPS[si].title}">
                <i data-lucide="${ico}"></i><span>${stepLabel(si)}</span>
            </button>
        </li>`;
    });
    $('track').innerHTML = nodes.join('');
}

function renderPlan() {
    $('plan').innerHTML = STEPS.map((s, si) => {
        const { total, done } = stepCounts(si);
        const ok = stepDone(si);
        const cur = si === state.step;
        const sub = s.kind === 'video'
            ? `${mmss(s.duration)} · ${done}/${total} ${plural(total, 'вопрос', 'вопроса', 'вопросов')}`
            : `${done}/${total} ${plural(total, 'задача', 'задачи', 'задач')}`;
        return `<li><button type="button" class="plan-item ${ok ? 'is-done' : ''} ${cur ? 'is-current' : ''} is-${s.kind}"
                data-step="${si}" ${reachable(si) ? '' : 'disabled'}>
            <span class="pi-ico"><i data-lucide="${ok ? 'check' : stepIcon(s)}"></i></span>
            <span class="pi-text"><span class="pi-title">${s.title}</span><span class="pi-sub">${sub}</span></span>
            ${reachable(si) ? '' : '<i data-lucide="lock" class="pi-lock"></i>'}
        </button></li>`;
    }).join('');
}

function stats() {
    let q = 0, qFirst = 0, t = 0, tSolved = 0, tShown = 0;
    STEPS.forEach((s, si) => itemsOf(s).forEach((_, ii) => {
        const it = itemState(si, ii);
        if (s.kind === 'video') { q++; if (it.status === 'ok' && it.tries === 0) qFirst++; }
        else { t++; if (it.status === 'ok') tSolved++; if (it.status === 'shown') tShown++; }
    }));
    const watched = videos.filter((v) => state.watched[STEPS.indexOf(v)]).length;
    return { q, qFirst, t, tSolved, tShown, watched };
}

function renderScore() {
    const s = stats();
    const row = (label, val, total) => `<div class="sc-row">
        <span class="sc-label">${label}</span><span class="sc-num">${val}/${total}</span>
        <span class="bar"><i style="width:${total ? (val / total) * 100 : 0}%"></i></span></div>`;
    $('score').innerHTML = row('Ролики просмотрены', s.watched, videos.length)
        + row('Вопросы с первой попытки', s.qFirst, s.q)
        + row('Задачи решены', s.tSolved, s.t);
}

// ------------------------------ вопросы ------------------------------

function feedbackHTML(item, it, si) {
    const practice = STEPS[si].kind === 'practice';
    if (it.status === 'ok') {
        const first = it.tries === 0 ? 'Верно с первой попытки!' : 'Верно!';
        return `<div class="fb ok"><i data-lucide="circle-check"></i><p><b>${first}</b> ${item.explain}</p></div>`;
    }
    if (it.status === 'shown') {
        const ans = item.type === 'choice' ? item.options[item.correct] : item.answer[0];
        return `<div class="fb shown"><i data-lucide="book-open-check"></i><p><b>Ответ: ${ans}.</b> ${item.explain}</p></div>`;
    }
    let html = '';
    if (it.error) html += `<div class="fb warn"><i data-lucide="info"></i><p>${it.error}</p></div>`;
    else if (it.tries) {
        const more = practice ? 'Попробуйте ещё раз.' : 'Попробуйте ещё раз или пересмотрите ролик.';
        html += `<div class="fb bad"><i data-lucide="circle-x"></i><p><b>Не совсем.</b> ${more}</p></div>`;
    }
    if (it.hint && item.hint) html += `<div class="fb hint"><i data-lucide="lightbulb"></i><p><b>Подсказка.</b> ${item.hint}</p></div>`;

    const actions = [];
    if (!practice && it.tries) actions.push(`<button type="button" class="chip-btn" data-act="rewatch"><i data-lucide="rotate-ccw"></i>Пересмотреть ролик</button>`);
    if (practice && item.hint && !it.hint) actions.push(`<button type="button" class="chip-btn" data-act="hint"><i data-lucide="lightbulb"></i>Подсказка</button>`);
    if (practice && it.tries) actions.push(`<button type="button" class="chip-btn" data-act="show"><i data-lucide="eye"></i>Показать решение</button>`);
    if (actions.length) html += `<div class="q-actions">${actions.join('')}</div>`;
    return html;
}

function itemHTML(si, ii) {
    const step = STEPS[si];
    const item = itemsOf(step)[ii];
    const it = itemState(si, ii);
    const locked = resolved(it);
    const practice = step.kind === 'practice';
    const cls = it.status === 'ok' ? 'is-ok' : it.status === 'shown' ? 'is-shown' : it.tries ? 'is-bad' : '';
    const pill = it.status === 'ok' ? '<span class="pill ok"><i data-lucide="check"></i>Решено</span>'
        : it.status === 'shown' ? '<span class="pill shown">Решение открыто</span>'
        : it.tries ? `<span class="pill bad">${it.tries} ${plural(it.tries, 'ошибка', 'ошибки', 'ошибок')}</span>` : '';
    const kind = item.type === 'input' ? 'Введите ответ' : 'Выберите ответ';

    let body;
    if (item.type === 'choice') {
        body = `<div class="options" role="group" aria-label="Варианты ответа">${item.options.map((o, oi) => {
            const right = locked && oi === item.correct;
            const wrong = it.wrong.includes(oi);
            return `<button type="button" class="option ${right ? 'is-right' : ''} ${wrong ? 'is-wrong' : ''}" data-opt="${oi}"
                ${locked || wrong ? 'disabled' : ''}><span class="opt-letter">${LETTERS[oi]}</span><span class="opt-text">${o}</span>
                ${right ? '<i data-lucide="check"></i>' : wrong ? '<i data-lucide="x"></i>' : ''}</button>`;
        }).join('')}</div>`;
    } else {
        const val = it.status === 'shown' ? item.answer[0] : (it.value || '');
        body = `<form class="answer" data-form>
            <label class="answer-field ${it.status === 'ok' ? 'is-right' : ''}">
                <span class="sr-only">Ваш ответ</span>
                <input type="text" inputmode="decimal" autocomplete="off" placeholder="Ответ, например 2 или 3/2"
                    value="${val.replace(/"/g, '&quot;')}" ${locked ? 'disabled' : ''}>
            </label>
            <button type="submit" class="btn btn-primary" ${locked ? 'disabled' : ''}>Проверить</button>
        </form>`;
    }

    return `<article class="glass q-card ${cls}" data-si="${si}" data-ii="${ii}">
        <div class="q-head"><span class="q-num">${practice ? 'Задача' : 'Вопрос'} ${ii + 1}</span>
            <span class="q-kind">${kind}</span>${pill}</div>
        <p class="q-text">${item.q}</p>
        ${body}
        <div class="q-feedback">${feedbackHTML(item, it, si)}</div>
    </article>`;
}

// ------------------------------ сцена ------------------------------

function navHTML() {
    const si = state.step;
    const { total, done } = stepCounts(si);
    const ok = stepDone(si);
    const prev = si > 0 ? `<button type="button" class="btn btn-ghost" data-go="${si - 1}"><i data-lucide="arrow-left"></i>Назад</button>` : '<span></span>';
    const nextName = si + 1 === FINISH ? 'Завершить урок' : `Дальше: ${STEPS[si + 1].title}`;
    const left = total - done;
    const what = STEPS[si].kind === 'video' ? plural(left, 'вопрос', 'вопроса', 'вопросов') : plural(left, 'задача', 'задачи', 'задач');
    const note = ok ? '<span class="nav-note ok"><i data-lucide="circle-check"></i>Шаг пройден</span>'
        : `<span class="nav-note">Осталось: ${left} ${what} из ${total}</span>`;
    return `${prev}${note}<button type="button" class="btn btn-primary" data-go="${si + 1}" ${ok ? '' : 'disabled'}>${nextName}<i data-lucide="arrow-right"></i></button>`;
}

function videoHTML(si) {
    const s = STEPS[si];
    const n = videos.indexOf(s) + 1;
    const watched = state.watched[si];
    return `<article class="glass card video-card">
        <div class="step-head">
            <div>
                <p class="kicker">Ролик ${n} из ${videos.length} · ${mmss(s.duration)}</p>
                <h2 class="step-title">${s.title}</h2>
            </div>
            <span class="pill ${watched ? 'ok' : ''}" id="watched-pill">${watched ? '<i data-lucide="check"></i>Просмотрено' : '<i data-lucide="eye"></i>Не просмотрено'}</span>
        </div>
        <div class="player">
            <video id="video" controls playsinline preload="metadata" poster="${s.poster}" src="${s.src}"></video>
        </div>
        <details class="transcript">
            <summary><i data-lucide="captions"></i>Текст ролика</summary>
            <ul>${s.transcript.map((p) => `<li>${p}</li>`).join('')}</ul>
        </details>
    </article>
    <section class="checks">
        <div class="checks-head">
            <h3 class="section-title">Проверь себя</h3>
            <p class="muted">Ответьте на ${plural(s.questions.length, 'вопрос', 'вопросы', 'вопросы')} по ролику — после этого откроется следующий шаг.</p>
        </div>
        ${s.questions.map((_, ii) => itemHTML(si, ii)).join('')}
    </section>`;
}

function practiceHTML(si) {
    const s = STEPS[si];
    return `<article class="glass card practice-head">
        <span class="practice-ico"><i data-lucide="pencil-line"></i></span>
        <div>
            <p class="kicker">Практика · ${s.tasks.length} ${plural(s.tasks.length, 'задача', 'задачи', 'задач')}</p>
            <h2 class="step-title">${s.title}</h2>
            <p class="muted">${s.intro}</p>
        </div>
    </article>
    <section class="checks">${s.tasks.map((_, ii) => itemHTML(si, ii)).join('')}</section>`;
}

function finishHTML() {
    const s = stats();
    const qPc = s.q ? Math.round((s.qFirst / s.q) * 100) : 0;
    const tPc = s.t ? Math.round((s.tSolved / s.t) * 100) : 0;
    const total = Math.round(((s.qFirst + s.tSolved) / (s.q + s.t)) * 100);
    const verdict = total >= 85 ? 'Отлично! Тема усвоена.' : total >= 60 ? 'Хорошо, но пару моментов стоит повторить.' : 'Урок пройден, но тему лучше закрепить.';
    // задачи, где открыли решение, — кандидаты на повторение
    const weak = [];
    STEPS.forEach((st, si) => itemsOf(st).forEach((item, ii) => {
        const it = itemState(si, ii);
        if (it.status === 'shown' || (st.kind === 'video' && it.tries)) weak.push({ si, ii, st, item });
    }));
    const next = nextLesson
        ? `<a class="btn btn-primary" href="${lessonUrl(nextLesson.id)}">Следующий урок: ${nextLesson.name}<i data-lucide="arrow-right"></i></a>`
        : '';
    return `<article class="glass card finish">
        <div class="finish-top">
            <svg class="ring" viewBox="0 0 36 36" aria-hidden="true">
                <circle cx="18" cy="18" r="15.9" pathLength="100" class="ring-track"/>
                <circle cx="18" cy="18" r="15.9" pathLength="100" class="ring-arc" stroke-dasharray="${total} 100"/>
                <text x="18" y="18" class="ring-text">${total}%</text>
            </svg>
            <div>
                <p class="kicker">Урок пройден</p>
                <h2 class="step-title">${verdict}</h2>
                <p class="muted">Процент — доля вопросов, решённых с первой попытки, и задач, решённых без открытого решения.</p>
            </div>
        </div>
        <div class="finish-stats">
            <div><b>${s.watched}/${videos.length}</b><span>роликов просмотрено</span></div>
            <div><b>${qPc}%</b><span>вопросов с первой попытки</span></div>
            <div><b>${tPc}%</b><span>задач решено самостоятельно</span></div>
        </div>
        ${weak.length ? `<div class="weak">
            <h3 class="c-title">Стоит повторить</h3>
            <ul>${weak.map((w) => `<li><button type="button" class="weak-item" data-go="${w.si}">
                <i data-lucide="${stepIcon(w.st)}"></i><span>${w.st.title}: ${w.item.q}</span><i data-lucide="chevron-right"></i></button></li>`).join('')}</ul>
        </div>` : ''}
        <div class="finish-actions">
            ${next}
            <a class="btn btn-ghost" href="${theoryUrl}"><i data-lucide="map"></i>К маршруту</a>
        </div>
    </article>`;
}

function renderStage() {
    const si = state.step;
    let html;
    if (si === FINISH) html = finishHTML();
    else html = (STEPS[si].kind === 'video' ? videoHTML(si) : practiceHTML(si)) + `<nav class="step-nav" id="step-nav">${navHTML()}</nav>`;
    $('stage').innerHTML = html;
    bindVideo();
}

// Точечные обновления — чтобы не сбрасывать воспроизведение ролика
function refresh(si, ii) {
    const card = document.querySelector(`.q-card[data-si="${si}"][data-ii="${ii}"]`);
    if (card) card.outerHTML = itemHTML(si, ii);
    if ($('step-nav')) $('step-nav').innerHTML = navHTML();
    renderTrack(); renderPlan(); renderScore();
    lucide.createIcons();
    save();
}

function render() {
    renderTrack(); renderPlan(); renderScore(); renderStage();
    lucide.createIcons();
}

function go(si) {
    if (si < 0 || si > FINISH) return;
    // вперёд — только через пройденный шаг
    if (si > state.max) {
        if (si !== state.max + 1 || !stepDone(state.max)) return;
        state.max = si;
    }
    state.step = si;
    save();
    render();
    $('track').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ------------------------------ видео ------------------------------

function markWatched(si) {
    if (state.watched[si]) return;
    state.watched[si] = true;
    const pill = $('watched-pill');
    if (pill) { pill.classList.add('ok'); pill.innerHTML = '<i data-lucide="check"></i>Просмотрено'; }
    renderScore();
    lucide.createIcons();
    save();
}

function bindVideo() {
    const v = $('video');
    if (!v) return;
    const si = state.step;
    // засчитываем просмотр с 90% — финальная шпаргалка часто стоит на паузе
    v.addEventListener('timeupdate', () => { if (v.duration && v.currentTime / v.duration > 0.9) markWatched(si); });
    v.addEventListener('ended', () => markWatched(si));
}

// ------------------------------ ответы ------------------------------

function answerChoice(si, ii, oi) {
    const item = itemsOf(STEPS[si])[ii];
    const it = itemState(si, ii);
    if (resolved(it)) return;
    if (oi === item.correct) it.status = 'ok';
    else { it.tries++; it.wrong.push(oi); }
    refresh(si, ii);
    // после верного ответа фокус — на следующий нерешённый вопрос
    if (it.status === 'ok') focusNext(si, ii);
}

function answerInput(si, ii, value) {
    const item = itemsOf(STEPS[si])[ii];
    const it = itemState(si, ii);
    if (resolved(it)) return;
    it.value = value;
    it.error = null;
    if (parseNumber(value) === null) it.error = value.trim() ? 'Ответ должен быть числом: целым, десятичным (2,5) или дробью (5/2).' : 'Введите ответ.';
    else if (isCorrect(item, value)) it.status = 'ok';
    else it.tries++;
    refresh(si, ii);
    if (it.status === 'ok') focusNext(si, ii);
    else document.querySelector(`.q-card[data-si="${si}"][data-ii="${ii}"] input`)?.focus();
}

function focusNext(si, ii) {
    const list = itemsOf(STEPS[si]);
    for (let j = ii + 1; j < list.length; j++) {
        if (!resolved(itemState(si, j))) {
            const card = document.querySelector(`.q-card[data-si="${si}"][data-ii="${j}"]`);
            card?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            card?.querySelector('input, .option:not([disabled])')?.focus({ preventScroll: true });
            return;
        }
    }
    if (stepDone(si)) document.querySelector('#step-nav [data-go]:last-child')?.focus({ preventScroll: true });
}

// ------------------------------ события ------------------------------

$('stage').addEventListener('click', (e) => {
    const goBtn = e.target.closest('[data-go]');
    if (goBtn) { go(+goBtn.dataset.go); return; }
    const card = e.target.closest('.q-card');
    if (!card) return;
    const si = +card.dataset.si, ii = +card.dataset.ii;
    const opt = e.target.closest('[data-opt]');
    if (opt) { answerChoice(si, ii, +opt.dataset.opt); return; }
    const act = e.target.closest('[data-act]')?.dataset.act;
    if (act === 'hint') { itemState(si, ii).hint = true; refresh(si, ii); }
    if (act === 'show') { itemState(si, ii).status = 'shown'; refresh(si, ii); }
    if (act === 'rewatch') {
        const v = $('video');
        v.currentTime = 0;
        v.play().catch(() => {});
        v.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
});

$('stage').addEventListener('submit', (e) => {
    e.preventDefault();
    const card = e.target.closest('.q-card');
    answerInput(+card.dataset.si, +card.dataset.ii, e.target.querySelector('input').value);
});

for (const id of ['track', 'plan']) {
    $(id).addEventListener('click', (e) => {
        const b = e.target.closest('[data-step]');
        if (b && !b.disabled) go(+b.dataset.step);
    });
}

$('reset').addEventListener('click', () => {
    state = fresh();
    save();
    render();
});

$('theme-toggle').addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('concept-theme', next); } catch { /* приватный режим */ }
});

renderHeader();
render();
