// Концепт «Выполнение ДЗ» — как решение варианта-отработки (variants_page/static/solve.js), но без таймера:
// вместо него срок сдачи и секундомер «в работе». Сверху — панель задач, «Сдать» -> подтверждение -> результаты.
//
// Адрес: solve.html?id=<ДЗ> — начать или продолжить (так открывает список);
//        solve.html?id=<ДЗ>&view=result — результаты сданного ДЗ.
// Начатое ДЗ хранится в localStorage (concept-homework:session:<id>), сданное — в concept-homework:attempts.

const params = new URLSearchParams(location.search);
const hw = homeworkById(params.get('id'));

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
const save = () => saveHwSession(hw.id, state.session);

/** 75 -> «1:15», 3725 -> «1:02:05» */
function clock(seconds) {
    const s = Math.max(0, seconds);
    const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
    const mm = h ? String(m).padStart(2, '0') : m;
    return `${h ? `${h}:` : ''}${mm}:${String(sec).padStart(2, '0')}`;
}

// ----------------------------------- выполнение -----------------------------------

function renderNav() {
    const cur = state.session.current;
    $('nav-strip').innerHTML = state.tasks.map((t, i) => `<button type="button"
        class="nav-task${isAnswered(i) ? ' is-answered' : ''}" data-index="${i}" ${i === cur ? 'aria-current="step"' : ''}
        aria-label="Задача ${i + 1}${isAnswered(i) ? ', есть ответ' : ''}">${i + 1}</button>`).join('');
    $('nav-progress').textContent = `Отвечено ${answeredCount()} из ${state.tasks.length}`;
}

function renderTask() {
    const i = state.session.current;
    const t = state.tasks[i];

    $('task-num').textContent = `Задача ${i + 1}`;
    $('task-meta').textContent = `№${t.number} ЕГЭ`;
    $('task-text').innerHTML = tex(t.text);
    $('answer').value = state.session.answers[i] ?? '';
    $('prev').disabled = i === 0;

    const last = i === state.tasks.length - 1;
    $('next').innerHTML = last ? 'К сдаче<i data-lucide="send"></i>' : 'Следующая<i data-lucide="arrow-right"></i>';
    renderNav();
    icons();
}

function goTo(i) {
    if (i < 0 || i >= state.tasks.length) return;
    state.session.current = i;
    save();
    renderTask();
    if (matchMedia('(hover: hover)').matches) $('answer').focus();
}

function next() {
    if (state.session.current === state.tasks.length - 1) openConfirm();
    else goTo(state.session.current + 1);
}

function onAnswer() {
    state.session.answers[state.session.current] = $('answer').value;
    save();
    renderNav();
}

// ----------------------------------- срок и секундомер -----------------------------------

function renderDeadline() {
    const overdue = hw.status === 'overdue';
    $('deadline-value').textContent = dayMonth(hw.deadline);
    $('deadline-label').textContent = overdue ? 'срок истёк' : 'срок · до 23:59';
    $('deadline').classList.toggle('is-danger', overdue);
}

function startTimer() {
    const tick = () => { $('timer-value').textContent = clock(elapsed()); };
    tick();
    state.timerId = setInterval(tick, 1000);
}

// ----------------------------------- сдача -----------------------------------

function openConfirm() {
    const left = state.tasks.length - answeredCount();
    const late = hw.status === 'overdue' ? ' Срок уже прошёл — преподаватель увидит, что ДЗ сдано после дедлайна.' : '';
    $('confirm-text').textContent = (left
        ? `Без ответа ${left} ${plural(left, 'задача', 'задачи', 'задач')} — они будут засчитаны как неверные.`
        : 'Ответы даны на все задачи. После сдачи изменить их будет нельзя.') + late;
    $('confirm').showModal();
}

function finish() {
    if (state.finished) return;
    state.finished = true;
    clearInterval(state.timerId);
    if ($('confirm').open) $('confirm').close();

    const answers = state.tasks.map((_, i) => state.session.answers[i] ?? '');
    const result = {
        points: state.tasks.map((t, i) => (isCorrect(answers[i], t.answer) ? 1 : 0)),
        answers,
        seconds: elapsed(),
        date: new Date().toISOString(),
        ...(hw.status === 'overdue' ? { late: true } : {}),
    };

    saveHwAttempt(hw.id, result);
    dropHwSession(hw.id);
    history.replaceState(null, '', `?id=${encodeURIComponent(hw.id)}&view=result`);
    showResults(result, true);
}

// ----------------------------------- результаты -----------------------------------

function statsHtml(result) {
    const total = state.tasks.length;
    const correct = result.points.filter((p) => p > 0).length;
    const percent = Math.round((correct / total) * 100);

    const cells = state.tasks.map((t, i) => {
        const ok = (result.points[i] ?? 0) > 0;
        return `<span class="cell ${ok ? 'is-full' : 'is-zero'}" title="Задача ${i + 1} (№${t.number} ЕГЭ): ${ok ? 'верно' : 'неверно'}">
            <b>${i + 1}</b><small>№${t.number}</small></span>`;
    }).join('');

    return `<div class="stats">
        <div class="score">
            ${progressRing(percent, `${percent}%`, 'решено верно')}
            ${ringLegend([[`Верно — ${correct}`, true], [`Неверно — ${total - correct}`, false]])}
        </div>
        <dl class="facts">
            <div><dt>Сдано</dt><dd>${formatDate(result.date)}</dd></div>
            <div><dt>Время</dt><dd>${formatDuration(result.seconds)}</dd></div>
            <div class="facts-wide"><dt>Срок</dt><dd>до ${dayMonth(hw.deadline)}, 23:59${result.late ? ' · сдано после срока' : ''}</dd></div>
        </dl>
        <div class="cells-wrap">
            <p class="cells-title">По задачам</p>
            <div class="cells">${cells}</div>
            <p class="cells-legend">
                <span><i class="is-full"></i>верно</span>
                <span><i class="is-zero"></i>неверно или без ответа</span>
            </p>
        </div>
    </div>`;
}

function showResults(result, justFinished = false) {
    $('work').hidden = true;
    $('timer').hidden = true;
    $('deadline').hidden = true;
    $('finish-btn').hidden = true;
    $('results').hidden = false;
    $('back-link').href = 'index.html?tab=done';
    document.querySelector('.solve-top').classList.add('is-results');

    $('results-kicker').textContent = justFinished ? 'Домашнее задание сдано' : `Сдано ${dayMonth(result.date)}`;
    $('results-stats').innerHTML = statsHtml(result);

    $('review').innerHTML = state.tasks.map((t, i) => {
        const ok = (result.points[i] ?? 0) > 0;
        // У заглушки ответов нет — показываем только верный
        const given = result.answers?.[i];
        const yours = given === undefined ? '<em>—</em>' : given.trim() ? escapeHtml(given) : '<em>нет ответа</em>';
        return `<details name="review" class="review-row ${ok ? 'is-full' : 'is-zero'}">
            <summary>
                <span class="review-num">${i + 1}</span>
                <span class="review-ege">№${t.number}</span>
                <span class="review-answers">
                    <span><small>Ваш ответ</small>${yours}</span>
                    <span><small>Верный</small>${formatAnswer(t.answer)}</span>
                </span>
                <span class="review-points">${ok ? 1 : 0}/1</span>
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
    if (!hw) {
        $('missing').hidden = false;
        $('timer').hidden = true;
        $('deadline').hidden = true;
        $('finish-btn').hidden = true;
        icons();
        return;
    }

    state.tasks = homeworkTasks(hw);
    document.title = `${hw.title} — Из нуля в сотку`;
    $('title').textContent = hw.title;
    $('kicker').textContent = `Домашнее задание · ${hw.topic} · ${state.tasks.length} ${plural(state.tasks.length, 'задача', 'задачи', 'задач')}`;

    // Сданное ДЗ — только результаты, переписать нельзя
    const result = hwResultOf(hw);
    if (result) {
        if (params.get('view') !== 'result') history.replaceState(null, '', `?id=${encodeURIComponent(hw.id)}&view=result`);
        showResults(result);
        return;
    }

    state.session = hwSessionOf(hw) ?? { startedAt: Date.now(), answers: [], current: 0 };
    save();
    history.replaceState(null, '', `?id=${encodeURIComponent(hw.id)}`);

    $('work').hidden = false;
    renderDeadline();
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
$('confirm-ok').addEventListener('click', finish);

// Стрелки переключают задачи, когда фокус не в поле ответа
document.addEventListener('keydown', (e) => {
    if ($('work').hidden || e.target.matches('input, textarea') || $('confirm').open) return;
    if (e.key === 'ArrowLeft') goTo(state.session.current - 1);
    if (e.key === 'ArrowRight') goTo(state.session.current + 1);
});

init();
