// Концепт «Решение варианта»: стандартный вариант — на время (3 ч 55 мин), отработка — без ограничения.
// Сверху — панель для переключения между заданиями, «Завершить» -> подтверждение -> результаты.
//
// Адрес: solve.html?id=<вариант>&start=1 — новая попытка (так открывает каталог);
//        solve.html?id=<вариант> — продолжить начатую после перезагрузки;
//        solve.html?id=<вариант>&view=result — результаты последней попытки.
// Начатая попытка хранится в localStorage (concept-variants:session:<id>), итог — в concept-variants:attempts.

const params = new URLSearchParams(location.search);
const variant = variantById(params.get('id'));

const state = {
    tasks: [],
    session: null,   // { startedAt, answers: [], current }
    timerId: null,
    finished: false,
};

const elapsed = () => Math.floor((Date.now() - state.session.startedAt) / 1000);
const isAnswered = (i) => String(state.session.answers[i] ?? '').trim() !== '';
const answeredCount = () => state.tasks.filter((_, i) => isAnswered(i)).length;
const formatAnswer = (x) => String(x).replace('.', ',');

/** 14100 -> «3:55:00», 75 -> «1:15» */
function clock(seconds) {
    const s = Math.max(0, seconds);
    const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
    const mm = h ? String(m).padStart(2, '0') : m;
    return `${h ? `${h}:` : ''}${mm}:${String(sec).padStart(2, '0')}`;
}

// ----------------------------------- попытка -----------------------------------

function loadSession() {
    try {
        const s = JSON.parse(localStorage.getItem(sessionKey(variant.id)));
        return s && Array.isArray(s.answers) ? s : null;
    } catch {
        return null;
    }
}

function saveSession() {
    try { localStorage.setItem(sessionKey(variant.id), JSON.stringify(state.session)); } catch { /* приватный режим */ }
}

function newSession() {
    state.session = { startedAt: Date.now(), answers: [], current: 0 };
    saveSession();
}

// ----------------------------------- решение -----------------------------------

function renderNav() {
    const cur = state.session.current;
    const button = (t, i) => `<button type="button" class="nav-task${isAnswered(i) ? ' is-answered' : ''}"
        data-index="${i}" ${i === cur ? 'aria-current="step"' : ''}
        aria-label="Задание ${i + 1}${isAnswered(i) ? ', есть ответ' : ''}">${i + 1}</button>`;

    // У стандартного варианта — разделитель между частями
    $('nav-strip').innerHTML = state.tasks.map((t, i) =>
        (isStandard(variant) && i === EXAM.part1 ? '<span class="nav-sep" aria-hidden="true"></span>' : '') + button(t, i),
    ).join('');

    const n = answeredCount();
    $('nav-progress').textContent = `Отвечено ${n} из ${state.tasks.length}`;
}

function renderTask() {
    const i = state.session.current;
    const t = state.tasks[i];
    const part = isStandard(variant) ? ` · часть ${t.number <= EXAM.part1 ? 1 : 2}` : '';
    const points = isStandard(variant) ? ` · ${t.max} ${plural(t.max, 'балл', 'балла', 'баллов')}` : '';

    $('task-num').textContent = `Задание ${i + 1}`;
    $('task-meta').textContent = `№${t.number} ЕГЭ${points}${part}`;
    $('task-text').innerHTML = tex(t.text);
    $('answer').value = state.session.answers[i] ?? '';
    $('prev').disabled = i === 0;

    const last = i === state.tasks.length - 1;
    $('next').innerHTML = last ? 'К завершению<i data-lucide="flag"></i>' : 'Следующее<i data-lucide="arrow-right"></i>';
    renderNav();
    icons();
}

function goTo(i) {
    if (i < 0 || i >= state.tasks.length) return;
    state.session.current = i;
    saveSession();
    renderTask();
    if (matchMedia('(hover: hover)').matches) $('answer').focus();
}

function next() {
    if (state.session.current === state.tasks.length - 1) openConfirm();
    else goTo(state.session.current + 1);
}

function onAnswer() {
    state.session.answers[state.session.current] = $('answer').value;
    saveSession();
    renderNav();
}

// ----------------------------------- таймер -----------------------------------

function tick() {
    const limit = timeLimit(variant);
    if (!limit) {
        $('timer-value').textContent = clock(elapsed());
        return;
    }
    const left = limit - elapsed();
    $('timer-value').textContent = clock(left);
    $('timer').classList.toggle('is-warn', left <= 15 * 60 && left > 5 * 60);
    $('timer').classList.toggle('is-danger', left <= 5 * 60);
    if (left <= 0) finish(true);
}

function startTimer() {
    $('timer-label').textContent = timeLimit(variant) ? 'осталось' : 'без ограничения';
    $('timer').title = timeLimit(variant) ? `На вариант ${formatDuration(timeLimit(variant))}` : 'Отработка без ограничения времени';
    tick();
    state.timerId = setInterval(tick, 1000);
}

// ----------------------------------- завершение -----------------------------------

function openConfirm() {
    const left = state.tasks.length - answeredCount();
    $('confirm-text').innerHTML = left
        ? `Без ответа ${left} ${plural(left, 'задание', 'задания', 'заданий')} — они будут засчитаны как неверные.`
        : 'Ответы даны на все задания. После завершения изменить их будет нельзя.';
    $('confirm').showModal();
}

function finish(timeUp = false) {
    if (state.finished) return;
    state.finished = true;
    clearInterval(state.timerId);
    if ($('confirm').open) $('confirm').close();

    const limit = timeLimit(variant);
    const answers = state.tasks.map((_, i) => state.session.answers[i] ?? '');
    const result = {
        points: state.tasks.map((t, i) => (isCorrect(answers[i], t.answer) ? t.max : 0)),
        answers,
        seconds: limit ? Math.min(elapsed(), limit) : elapsed(),
        date: new Date().toISOString(),
        ...(timeUp ? { timeUp: true } : {}),
    };

    saveAttempt(variant.id, result);
    try { localStorage.removeItem(sessionKey(variant.id)); } catch { /* приватный режим */ }
    history.replaceState(null, '', `?id=${encodeURIComponent(variant.id)}&view=result`);
    showResults(result);
}

// ----------------------------------- результаты -----------------------------------

function showResults(result) {
    $('work').hidden = true;
    $('timer').hidden = true;
    $('finish-btn').hidden = true;
    $('results').hidden = false;
    $('back-link').href = `index.html?open=${encodeURIComponent(variant.id)}`;
    $('back-link').querySelector('span').textContent = 'В каталог';
    document.querySelector('.solve-top').classList.add('is-results');

    $('results-kicker').textContent = result.timeUp ? 'Время вышло — вариант завершён автоматически' : 'Вариант завершён';
    $('results-stats').innerHTML = statsHtml(variant, result);
    $('retry').href = `solve.html?id=${encodeURIComponent(variant.id)}&start=1`;
    $('to-catalog').href = `index.html?open=${encodeURIComponent(variant.id)}`;

    $('review').innerHTML = state.tasks.map((t, i) => {
        const p = result.points[i] ?? 0;
        const given = result.answers?.[i] ?? '';
        const cls = p >= t.max ? 'is-full' : p > 0 ? 'is-part' : 'is-zero';
        return `<details name="review" class="review-row ${cls}">
            <summary>
                <span class="review-num">${i + 1}</span>
                <span class="review-ege">№${t.number}</span>
                <span class="review-answers">
                    <span><small>Ваш ответ</small>${given.trim() ? escapeHtml(given) : '<em>нет ответа</em>'}</span>
                    <span><small>Верный</small>${formatAnswer(t.answer)}</span>
                </span>
                <span class="review-points">${p}/${t.max}</span>
                <i data-lucide="chevron-down" class="review-chevron"></i>
            </summary>
            ${taskReviewHtml(t)}
        </details>`;
    }).join('');

    icons();
    window.scrollTo(0, 0);
}

// ----------------------------------- запуск -----------------------------------

function init() {
    if (!variant) {
        $('missing').hidden = false;
        $('timer').hidden = true;
        $('finish-btn').hidden = true;
        icons();
        return;
    }

    state.tasks = tasksOf(variant);
    document.title = `${variant.title} — Из нуля в сотку`;
    $('title').textContent = variant.title;
    $('kicker').textContent = isStandard(variant)
        ? `Стандартный · ${state.tasks.length} заданий · ${formatDuration(EXAM.minutes * 60)}`
        : `Отработка · ${state.tasks.length} ${plural(state.tasks.length, 'задание', 'задания', 'заданий')} · без таймера`;

    if (params.get('view') === 'result') {
        const result = loadAttempts()[variant.id];
        if (result) {
            showResults(result);
            return;
        }
    }

    // start=1 — новая попытка; иначе продолжаем начатую (перезагрузка страницы)
    state.session = params.get('start') ? null : loadSession();
    if (!state.session) newSession();
    history.replaceState(null, '', `?id=${encodeURIComponent(variant.id)}`);

    $('work').hidden = false;
    startTimer();
    renderTask();
}

$('nav-strip').addEventListener('click', (e) => {
    const btn = e.target.closest('.nav-task');
    if (btn) goTo(Number(btn.dataset.index));
});
$('answer').addEventListener('input', onAnswer);
$('answer').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); next(); }
});
$('prev').addEventListener('click', () => goTo(state.session.current - 1));
$('next').addEventListener('click', next);
$('finish-btn').addEventListener('click', openConfirm);
$('confirm-cancel').addEventListener('click', () => $('confirm').close());
$('confirm-ok').addEventListener('click', () => finish());

// Стрелки переключают задания, когда фокус не в поле ответа
document.addEventListener('keydown', (e) => {
    if ($('work').hidden || e.target.matches('input, textarea') || $('confirm').open) return;
    if (e.key === 'ArrowLeft') goTo(state.session.current - 1);
    if (e.key === 'ArrowRight') goTo(state.session.current + 1);
});

// Не потерять попытку случайным закрытием вкладки
window.addEventListener('beforeunload', (e) => {
    if (state.session && !state.finished && !$('work').hidden) e.preventDefault();
});

init();
