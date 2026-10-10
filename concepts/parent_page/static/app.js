/* Кабинет родителя: три варианта главной (A — четыре ответа, B — отчёт недели, C — светофор) и настройки отчётов.
   Данные — data.js (window.PARENT), выбор ребёнка и настройки — localStorage concept-parent:* */
(function () {
    const D = window.PARENT;
    const view = document.getElementById('view');
    const tip = document.getElementById('tip');

    const store = {
        get(k, def) { try { const v = localStorage.getItem('concept-parent:' + k); return v == null ? def : JSON.parse(v); } catch { return def; } },
        set(k, v) { try { localStorage.setItem('concept-parent:' + k, JSON.stringify(v)); } catch {} },
    };

    const DEFAULT_SETTINGS = { email: true, telegram: false, weekday: 0, idleDays: 3, lateAlert: true, mockDrop: 5 };
    const settings = () => ({ ...DEFAULT_SETTINGS, ...store.get('settings', {}) });

    let childId = store.get('child', D.children[0].id);
    const child = () => D.children.find((c) => c.id === childId) || D.children[0];

    // ------------------------------ утилиты ------------------------------

    const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const parse = (s) => { const [y, m, d] = s.split('-').map(Number); return new Date(y, m - 1, d); };
    const TODAY = parse(D.today);
    const daysBetween = (a, b) => Math.round((parse(b) - parse(a)) / 864e5);
    const MONTHS = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
    const MONTHS_S = ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'];
    const WD = ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб'];
    const WD_FULL = ['воскресенье', 'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота'];
    const fmtDate = (s) => { const d = parse(s); return `${d.getDate()} ${MONTHS[d.getMonth()]}`; };
    const fmtShort = (s) => { const d = parse(s); return `${d.getDate()} ${MONTHS_S[d.getMonth()]}`; };
    const fmtMin = (m) => (m >= 60 ? `${Math.floor(m / 60)} ч ${m % 60 ? (m % 60) + ' мин' : ''}`.trim() : `${m} мин`);
    const plural = (n, a, b, c) => { const m = n % 10, h = n % 100; return m === 1 && h !== 11 ? a : m >= 2 && m <= 4 && (h < 12 || h > 14) ? b : c; };
    const signed = (n) => (n > 0 ? '+' + n : n < 0 ? '−' + Math.abs(n) : '0');
    const SUBJ_ICON = { math: 'sigma', rus: 'book-open-text', inf: 'code-xml' };
    const subjTitle = (c, id) => c.subjects.find((s) => s.id === id)?.title || id;

    function toast(text) {
        const t = document.getElementById('toast');
        t.textContent = text; t.classList.add('is-on');
        clearTimeout(toast.t); toast.t = setTimeout(() => t.classList.remove('is-on'), 2400);
    }

    // ------------------------------ сводка по ребёнку ------------------------------

    function weekSlice(c, weeksAgo) {
        const end = c.days.length - weeksAgo * 7;
        return c.days.slice(Math.max(0, end - 7), end);
    }

    function stats(c) {
        const s = settings();
        const week = weekSlice(c, 0), prev = weekSlice(c, 1);
        const sum = (a, k) => a.reduce((x, d) => x + d[k], 0);
        const activeDays = week.filter((d) => d.minutes > 0).length;
        const lastActive = [...c.days].reverse().find((d) => d.minutes > 0);
        const idle = lastActive ? daysBetween(lastActive.date, D.today) : 99;
        const month = c.homework.filter((h) => daysBetween(h.due, D.today) <= 30);
        const hw = {
            done: month.filter((h) => h.status === 'done').length,
            work: c.homework.filter((h) => h.status === 'work').length,
            late: c.homework.filter((h) => h.status === 'late').length,
            total: month.length,
        };
        const mocks = c.subjects.map((sub) => {
            const m = sub.mocks, last = m[m.length - 1], prevM = m[m.length - 2], first = m[Math.max(0, m.length - 5)];
            return { id: sub.id, title: sub.title, last: last.score, delta: last.score - prevM.score, month: last.score - first.score, goal: sub.goal };
        });
        const weak = c.subjects.flatMap((sub) => sub.numbers.filter((n) => n.acc < 0.5 && n.n <= 12).map((n) => ({ ...n, subject: sub.id, title: sub.title })))
            .sort((a, b) => a.acc - b.acc);
        const behind = c.subjects.filter((sub) => sub.planBehind > 0);

        // сигналы — то, о чём кабинет говорит первым
        const signals = [];
        if (idle >= s.idleDays) signals.push({ level: 'bad', icon: 'moon', title: `${idle} ${plural(idle, 'день', 'дня', 'дней')} без занятий`, text: `Последний раз ${c.f ? 'занималась' : 'занимался'} ` + fmtDate(lastActive.date) + '.', action: 'Спросить, что мешает' });
        if (s.lateAlert && hw.late) signals.push({ level: hw.late > 1 ? 'bad' : 'mid', icon: 'clock-alert', title: `${hw.late} ${plural(hw.late, 'просроченная домашка', 'просроченные домашки', 'просроченных домашек')}`, text: hw.late > 1 ? 'Досдать можно — они лежат во вкладке «Просроченные».' : 'Досдать можно — она лежит во вкладке «Просроченные».', action: 'Напомнить ребёнку' });
        mocks.filter((m) => m.delta <= -s.mockDrop).forEach((m) => signals.push({ level: 'mid', icon: 'trending-down', title: `${m.title}: пробник ${signed(m.delta)}`, text: 'Разовое падение — не повод для паники, смотрим следующий.', action: 'Написать куратору' }));
        behind.filter((b) => b.planBehind >= 3).forEach((b) => signals.push({ level: 'mid', icon: 'calendar-clock', title: `${b.title}: отстаёт на ${b.planBehind} ${plural(b.planBehind, 'урок', 'урока', 'уроков')}`, text: 'План сдвинулся. Наверстать — примерно ' + Math.ceil(b.planBehind / 2) + ' доп. занятия.', action: 'Предложить план' }));

        const level = signals.some((x) => x.level === 'bad') ? 'bad' : signals.length ? 'mid' : 'good';
        return {
            week, prev, activeDays, idle, lastActive,
            minutes: sum(week, 'minutes'), prevMinutes: sum(prev, 'minutes'),
            lessons: sum(week, 'lessons'), tasks: sum(week, 'tasks'),
            today: c.days[c.days.length - 1], hw, mocks, weak, behind, signals, level,
            examIn: daysBetween(D.today, c.examDate),
        };
    }

    const LEVEL = {
        good: { icon: 'circle-check', label: 'Всё по плану', cls: 'good' },
        mid: { icon: 'circle-alert', label: 'Есть на что взглянуть', cls: 'mid' },
        bad: { icon: 'octagon-alert', label: 'Пора поговорить', cls: 'bad' },
    };
    const pill = (lvl, text) => `<span class="verdict v-${lvl}"><i data-lucide="${LEVEL[lvl].icon}"></i>${esc(text)}</span>`;
    const accLvl = (a) => (a >= 0.75 ? 'good' : a >= 0.5 ? 'mid' : 'bad');

    // ------------------------------ графики ------------------------------

    // Тепловая карта занятий: 8 недель × 7 дней, один оттенок от светлого к тёмному
    function heatmap(c) {
        const days = c.days;
        const first = parse(days[0].date);
        const pad = (first.getDay() + 6) % 7; // понедельник — первая строка
        const cells = Array(pad).fill(null).concat(days);
        const cols = Math.ceil(cells.length / 7);
        const step = (m) => (m === 0 ? 0 : m < 25 ? 1 : m < 45 ? 2 : m < 70 ? 3 : 4);
        let html = '<div class="heat-wrap"><div class="heat-days">' + ['пн', '', 'ср', '', 'пт', '', 'вс'].map((d) => `<span>${d}</span>`).join('') + '</div>';
        html += `<div class="heat" style="--cols:${cols}">`;
        for (let col = 0; col < cols; col++) for (let row = 0; row < 7; row++) {
            const d = cells[col * 7 + row];
            if (!d) { html += '<span class="hc is-empty"></span>'; continue; }
            const label = `${WD[parse(d.date).getDay()]}, ${fmtDate(d.date)} — ${d.minutes ? fmtMin(d.minutes) + `, ${d.tasks} задач` : `не ${c.f ? 'занималась' : 'занимался'}`}`;
            html += `<span class="hc s${step(d.minutes)}${d.date === D.today ? ' is-today' : ''}" style="grid-column:${col + 1};grid-row:${row + 1}" data-tip="${esc(label)}"></span>`;
        }
        html += '</div></div>';
        html += '<div class="heat-legend"><span>меньше</span>' + [0, 1, 2, 3, 4].map((s) => `<span class="hc s${s}"></span>`).join('') + '<span>больше</span></div>';
        return html;
    }

    // Линия пробников по одному предмету + пунктир цели
    function mockChart(sub) {
        const W = 560, H = 200, L = 34, R = 16, T = 16, B = 28;
        const pts = sub.mocks;
        const lo = Math.max(0, Math.floor((Math.min(...pts.map((p) => p.score), sub.goal) - 10) / 10) * 10);
        const hi = Math.min(100, Math.ceil((Math.max(...pts.map((p) => p.score), sub.goal) + 5) / 10) * 10);
        const x = (i) => L + (pts.length === 1 ? 0 : (i * (W - L - R)) / (pts.length - 1));
        const y = (v) => T + ((hi - v) * (H - T - B)) / (hi - lo);
        let g = '';
        for (let v = lo; v <= hi; v += 10) g += `<line class="grid" x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}"/><text class="axis" x="${L - 8}" y="${y(v) + 4}" text-anchor="end">${v}</text>`;
        const path = pts.map((p, i) => `${i ? 'L' : 'M'}${x(i)},${y(p.score)}`).join('');
        const goal = `<line class="goal" x1="${L}" x2="${W - R}" y1="${y(sub.goal)}" y2="${y(sub.goal)}"/><text class="goal-label" x="${L + 6}" y="${y(sub.goal) - 6}">цель ${sub.goal}</text>`;
        const dots = pts.map((p, i) => {
            const d = i ? p.score - pts[i - 1].score : null;
            const t = `${fmtDate(p.date)}: ${p.score} баллов${d == null ? '' : ` (${signed(d)})`}`;
            return `<circle class="dot" cx="${x(i)}" cy="${y(p.score)}" r="4.5"/><rect class="hit" x="${x(i) - 18}" y="${T}" width="36" height="${H - T - B}" data-tip="${esc(t)}"/>`;
        }).join('');
        const xl = pts.map((p, i) => (i % 2 === pts.length % 2 || i === pts.length - 1 ? `<text class="axis" x="${x(i)}" y="${H - 8}" text-anchor="middle">${fmtShort(p.date)}</text>` : '')).join('');
        const last = pts[pts.length - 1];
        return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="Пробники по предмету ${esc(sub.title)}: последний ${last.score}, цель ${sub.goal}">
            ${g}${goal}<path class="line" d="${path}"/>${dots}${xl}
            <text class="end-label" x="${x(pts.length - 1) - 8}" y="${y(last.score) - 10}" text-anchor="end">${last.score}</text></svg>`;
    }

    // Номера ЕГЭ клетками: цвет — статус точности, внутри — номер, под ним — процент
    function numberGrid(sub) {
        return `<div class="nums">${sub.numbers.map((n) => `<span class="num n-${accLvl(n.acc)}" data-tip="${esc(`№${n.n} · ${n.topic}: ${Math.round(n.acc * 100)}% верно из ${n.tries} попыток`)}">
            <b>${n.n}</b><small>${Math.round(n.acc * 100)}%</small></span>`).join('')}</div>`;
    }

    // ------------------------------ шапка страницы ------------------------------

    function head(c, st, eyebrow, extra = '') {
        return `<div class="page-header"><div>
            <p class="eyebrow">${eyebrow}</p>
            <h1 class="title">${esc(c.name)}, ${c.grade}</h1>
            <p class="description">До ЕГЭ ${st.examIn} ${plural(st.examIn, 'день', 'дня', 'дней')} · ${c.subjects.map((s) => s.title).join(', ')}</p>
        </div>${extra}</div>`;
    }

    // ------------------------------ A · Четыре ответа ------------------------------

    function viewA() {
        const c = child(), st = stats(c);
        const todayMin = st.today.minutes;
        const actLvl = st.activeDays >= 4 ? 'good' : st.activeDays >= 2 ? 'mid' : 'bad';
        const hwLvl = st.hw.late === 0 ? 'good' : st.hw.late === 1 ? 'mid' : 'bad';
        const avgMonth = Math.round(st.mocks.reduce((a, m) => a + m.month, 0) / st.mocks.length);
        const mockLvl = avgMonth >= 3 ? 'good' : avgMonth >= 0 ? 'mid' : 'bad';
        const weakLvl = st.weak.length <= 2 ? 'good' : st.weak.length <= 5 ? 'mid' : 'bad';
        const subTab = store.get('a-subject', c.subjects[0].id);
        const sub = c.subjects.find((s) => s.id === subTab) || c.subjects[0];

        const card = (anchor, q, lvl, verdict, value, note) => `<a class="glass answer" href="#/a" data-scroll="${anchor}">
            <span class="answer-q">${q}</span>${pill(lvl, verdict)}
            <span class="answer-value">${value}</span><span class="answer-note">${note}</span></a>`;

        view.innerHTML = head(c, st, 'Вариант A · дашборд «четыре вопроса — четыре ответа»',
            `<div class="today glass"><i data-lucide="${todayMin ? 'flame' : 'moon'}"></i><span>${todayMin ? `Сегодня ${c.f ? 'занималась' : 'занимался'} <b>${fmtMin(todayMin)}</b>` : `Сегодня ещё не ${c.f ? 'занималась' : 'занимался'}`}</span></div>`) + `
        <div class="answers">
            ${card('act', 'Занимается ли?', actLvl, st.activeDays >= 4 ? 'Да, регулярно' : st.activeDays ? 'С перерывами' : 'Нет', `${st.activeDays}<small> из 7 дней</small>`, `${fmtMin(st.minutes)} за неделю · ${st.minutes >= st.prevMinutes ? 'больше' : 'меньше'}, чем неделей раньше`)}
            ${card('hw', 'Делает ли домашку?', hwLvl, st.hw.late ? `${st.hw.late} ${plural(st.hw.late, 'просрочка', 'просрочки', 'просрочек')}` : 'Всё в срок', `${st.hw.done}<small> из ${st.hw.total} сдано</small>`, `${st.hw.work} в работе · за 30 дней`)}
            ${card('mock', 'Растёт ли балл?', mockLvl, avgMonth >= 3 ? 'Растёт' : avgMonth >= 0 ? 'Держится' : 'Снижается', `${signed(avgMonth)}<small> за месяц</small>`, st.mocks.map((m) => `${m.title.slice(0, 3)}. ${m.last}`).join(' · '))}
            ${card('weak', 'Где проседает?', weakLvl, st.weak.length ? `${st.weak.length} ${plural(st.weak.length, 'тема', 'темы', 'тем')}` : 'Пробелов нет', st.weak[0] ? `№${st.weak[0].n}<small> ${esc(st.weak[0].title.toLowerCase())}</small>` : '—', st.weak[0] ? esc(st.weak[0].topic) + ` · ${Math.round(st.weak[0].acc * 100)}% верно` : 'Первая часть ровная')}
        </div>

        <section class="glass panel" id="act">
            <div class="panel-head"><h2>Занятия за 8 недель</h2><span class="muted small">Наведите на день — минуты и задачи</span></div>
            ${heatmap(c)}
            <div class="facts">
                <div><span class="fact-v">${fmtMin(st.minutes)}</span><span class="fact-l">за 7 дней</span></div>
                <div><span class="fact-v">${st.lessons}</span><span class="fact-l">${plural(st.lessons, 'урок', 'урока', 'уроков')}</span></div>
                <div><span class="fact-v">${st.tasks}</span><span class="fact-l">задач решено</span></div>
                <div><span class="fact-v">${c.subjects.map((s) => Math.round((s.planDone / s.planTotal) * 100) + '%').join(' / ')}</span><span class="fact-l">программы пройдено</span></div>
            </div>
        </section>

        <div class="grid-2">
            <section class="glass panel" id="hw">
                <div class="panel-head"><h2>Домашние задания</h2>
                    <span class="chips"><span class="chip c-good">${st.hw.done} сдано</span><span class="chip c-mid">${st.hw.work} в работе</span>${st.hw.late ? `<span class="chip c-bad">${st.hw.late} просрочено</span>` : ''}</span></div>
                <ul class="rows">${[...c.homework].sort((a, b) => ({ late: 0, work: 1, done: 2 }[a.status] - { late: 0, work: 1, done: 2 }[b.status]) || b.due.localeCompare(a.due)).slice(0, 7).map((h) => `
                    <li class="row"><i data-lucide="${SUBJ_ICON[h.subject]}" class="muted"></i>
                        <span class="row-main"><span>${esc(h.title)}</span><span class="muted">${subjTitle(c, h.subject)}</span></span>
                        ${h.status === 'done' ? `<span class="pill p-good">${h.score} из ${h.total}</span>` : h.status === 'late' ? `<span class="pill p-bad">просрочено ${fmtShort(h.due)}</span>` : `<span class="pill p-mid">до ${fmtShort(h.due)}</span>`}
                    </li>`).join('')}</ul>
            </section>

            <section class="glass panel" id="mock">
                <div class="panel-head"><h2>Пробники в формате ЕГЭ</h2>
                    <div class="seg" role="tablist">${c.subjects.map((s) => `<button type="button" role="tab" data-subj="${s.id}" aria-selected="${s.id === sub.id}">${s.title}</button>`).join('')}</div></div>
                ${mockChart(sub)}
                <p class="muted small">Тестовый балл по шкале ФИПИ. Последний — ${sub.mocks.at(-1).score}, до цели ${Math.max(0, sub.goal - sub.mocks.at(-1).score)}.</p>
            </section>
        </div>

        <section class="glass panel" id="weak">
            <div class="panel-head"><h2>Доля верных по номерам · ${sub.title}</h2>
                <span class="legend"><span class="lg n-good">от 75%</span><span class="lg n-mid">50–74%</span><span class="lg n-bad">меньше 50%</span></span></div>
            ${numberGrid(sub)}
            ${st.weak.length ? `<div class="note"><i data-lucide="sparkles"></i><span>Слабые темы первой части уже добавлены в быстрое повторение: ${st.weak.slice(0, 3).map((w) => `${w.title.toLowerCase()} №${w.n} (${esc(w.topic.toLowerCase())})`).join(', ')}.</span></div>` : ''}
        </section>`;

        view.querySelectorAll('[data-subj]').forEach((b) => b.addEventListener('click', () => { store.set('a-subject', b.dataset.subj); render(); document.getElementById('mock').scrollIntoView({ block: 'nearest' }); }));
        view.querySelectorAll('[data-scroll]').forEach((a) => a.addEventListener('click', (e) => { e.preventDefault(); document.getElementById(a.dataset.scroll).scrollIntoView({ behavior: 'smooth', block: 'start' }); }));
    }

    // ------------------------------ B · Отчёт недели ------------------------------

    function viewB() {
        const c = child();
        const weeks = Math.floor(c.days.length / 7);
        let w = Math.min(store.get('b-week', 0), weeks - 2);
        const cur = weekSlice(c, w), prev = weekSlice(c, w + 1);
        const from = cur[0].date, to = cur[cur.length - 1].date;
        const sum = (a, k) => a.reduce((x, d) => x + d[k], 0);
        const act = (a) => a.filter((d) => d.minutes > 0).length;
        const inRange = (d, a, b) => d >= a && d <= b;
        const hwIn = (a, b) => c.homework.filter((h) => inRange(h.due, a, b));
        const hwCur = hwIn(from, to), hwPrev = hwIn(prev[0].date, prev[prev.length - 1].date);
        const okCnt = (l) => l.filter((h) => h.status === 'done').length;
        const mockAt = (date) => { const all = c.subjects[0].mocks.filter((m) => m.date <= date); return all.at(-1)?.score; };
        const mCur = mockAt(to), mPrev = mockAt(prev[prev.length - 1].date);
        const st = stats(c);

        const days = act(cur);
        const mood = days >= 5 ? ['good', 'Хорошая неделя'] : days >= 3 ? ['mid', 'Обычная неделя'] : ['bad', 'Тихая неделя'];
        const lead = `${mood[1]}: ${c.name} ${c.f ? 'занималась' : 'занимался'} ${days} ${plural(days, 'день', 'дня', 'дней')} из 7`;

        const rowsData = [
            ['Время в кабинете', fmtMin(sum(prev, 'minutes')), fmtMin(sum(cur, 'minutes')), sum(cur, 'minutes') - sum(prev, 'minutes')],
            ['Дней с занятиями', act(prev), days, days - act(prev)],
            ['Уроков пройдено', sum(prev, 'lessons'), sum(cur, 'lessons'), sum(cur, 'lessons') - sum(prev, 'lessons')],
            ['Задач решено', sum(prev, 'tasks'), sum(cur, 'tasks'), sum(cur, 'tasks') - sum(prev, 'tasks')],
            ['ДЗ в срок', `${okCnt(hwPrev)} / ${hwPrev.length}`, `${okCnt(hwCur)} / ${hwCur.length}`, null],
            [`Пробник · ${c.subjects[0].title.toLowerCase()}`, mPrev ?? '—', mCur ?? '—', mCur != null && mPrev != null ? mCur - mPrev : null],
        ];
        const delta = (d) => (d == null || d === 0 ? '<span class="muted">—</span>' : `<span class="${d > 0 ? 'tone-good' : 'tone-bad'}">${d > 0 ? '▲' : '▼'} ${Math.abs(d)}</span>`);

        const feed = c.events.filter((e) => inRange(e.date, from, to));
        const byDay = {};
        feed.forEach((e) => (byDay[e.date] = byDay[e.date] || []).push(e));
        const EV_ICON = { lesson: 'play-circle', review: 'zap', hw: 'clipboard-check', late: 'clock-alert', mock: 'file-chart-column' };

        const weak = st.weak.slice(0, 2);
        const talk = [
            days < 3 ? `Спросите не «почему не ${c.f ? 'занималась' : 'занимался'}», а «что сейчас мешает» — неделя вышла тихой.` : `Отметьте, что ${c.name} ${c.f ? 'занималась' : 'занимался'} ${days} ${plural(days, 'день', 'дня', 'дней')} — регулярность важнее рекордов.`,
            weak[0] ? `${weak[0].title}, №${weak[0].n} (${weak[0].topic.toLowerCase()}) — можно попросить объяснить вам одну задачу: пересказ закрепляет.` : 'Слабых тем в первой части нет — можно спросить, что из второй части даётся тяжелее.',
            st.hw.late ? 'Есть просрочка: договоритесь о дне, когда она будет досдана, — без наказаний.' : 'Домашки сданы — хороший повод ничего не проверять на этой неделе.',
        ];

        view.innerHTML = `
        <div class="page-header"><div>
            <p class="eyebrow">Вариант B · главная — это письмо-отчёт, только живое</p>
            <h1 class="title">Отчёт за ${fmtDate(from)} — ${fmtDate(to)}</h1>
            <p class="description">${esc(c.name)}, ${c.grade}. Такая же сводка приходит ${settings().telegram ? 'в Telegram' : 'на почту'} в ${WD_FULL[settings().weekday]}.</p></div>
            <div class="head-actions">
                <button class="btn btn-outline btn-s" data-week="1" ${w >= weeks - 2 ? 'disabled' : ''}><i data-lucide="chevron-left"></i>Раньше</button>
                <button class="btn btn-outline btn-s" data-week="-1" ${w === 0 ? 'disabled' : ''}>Позже<i data-lucide="chevron-right"></i></button>
            </div></div>

        <article class="glass report">
            <p class="report-lead">${pill(mood[0], mood[1])}</p>
            <h2 class="report-title">${esc(lead)}</h2>
            <div class="week-dots" aria-label="Дни недели">${cur.map((d) => `<span class="wd${d.minutes ? ' is-on' : ''}" data-tip="${esc(`${WD_FULL[parse(d.date).getDay()]}: ${d.minutes ? fmtMin(d.minutes) : `не ${c.f ? 'занималась' : 'занимался'}`}`)}"><b>${WD[parse(d.date).getDay()]}</b><i></i></span>`).join('')}</div>

            <table class="bs">
                <thead><tr><th>Показатель</th><th>Неделей раньше</th><th>Эта неделя</th><th></th></tr></thead>
                <tbody>${rowsData.map((r) => `<tr><td>${r[0]}</td><td class="muted">${r[1]}</td><td><b>${r[2]}</b></td><td>${delta(r[3])}</td></tr>`).join('')}</tbody>
            </table>

            ${weak.length || st.hw.late ? `<div class="callout c-mid"><i data-lucide="eye"></i><div><b>Обратите внимание.</b>
                ${weak.map((x) => `${x.title.toLowerCase()}, номер ${x.n} (${esc(x.topic.toLowerCase())}) — ${Math.round(x.acc * 100)}% верно`).join('; ')}${weak.length && st.hw.late ? '; ' : ''}${st.hw.late ? `${st.hw.late} ${plural(st.hw.late, 'домашка просрочена', 'домашки просрочены', 'домашек просрочено')}` : ''}.
                <span class="muted">Темы уже добавлены в быстрое повторение и в домашку на следующую неделю — вам ничего делать не нужно.</span></div></div>` : ''}

            <div class="callout c-primary"><i data-lucide="message-circle-heart"></i><div><b>О чём можно поговорить за ужином</b><ul>${talk.map((t) => `<li>${esc(t)}</li>`).join('')}</ul></div></div>
        </article>

        <section class="glass panel">
            <div class="panel-head"><h2>Что происходило по дням</h2><span class="muted small">${feed.length ? `${feed.length} ${plural(feed.length, 'событие', 'события', 'событий')}` : ''}</span></div>
            ${feed.length ? Object.keys(byDay).map((d) => `<div class="day"><p class="day-h">${WD_FULL[parse(d).getDay()]}, ${fmtDate(d)}</p>
                <ul class="feed">${byDay[d].map((e) => `<li class="ev ev-${e.kind}"><i data-lucide="${EV_ICON[e.kind]}"></i><span class="mono muted">${e.time}</span><span>${esc(e.text)}</span><span class="chip">${subjTitle(c, e.subject)}</span></li>`).join('')}</ul></div>`).join('')
                : '<p class="empty-s">Подробная лента хранится за последние две недели — для более ранних недель остаётся только сводка выше.</p>'}
        </section>`;

        view.querySelectorAll('[data-week]').forEach((b) => b.addEventListener('click', () => { store.set('b-week', Math.max(0, w + Number(b.dataset.week))); render(); }));
    }

    // ------------------------------ C · Светофор ------------------------------

    function viewC() {
        const c = child(), st = stats(c);
        const L = LEVEL[st.level];
        const subjLevel = (sub) => {
            const m = st.mocks.find((x) => x.id === sub.id);
            if (sub.planBehind >= 5 || m.month < -3) return 'bad';
            if (sub.planBehind > 0 || m.delta < 0) return 'mid';
            return 'good';
        };
        const headline = { good: `${c.name} идёт по плану. Можно не вмешиваться.`, mid: `В целом нормально, но ${st.signals.length} ${plural(st.signals.length, 'момент', 'момента', 'моментов')} стоит заметить.`, bad: 'Подготовка буксует — лучше обсудить это на этой неделе.' }[st.level];

        view.innerHTML = `
        <div class="solo">
            <p class="eyebrow">Вариант C · один экран, ответ за 10 секунд — под телефон</p>
            <section class="glass hero h-${L.cls}">
                <span class="lamp"><i data-lucide="${L.icon}"></i></span>
                <div><p class="hero-label">${L.label}</p><h1 class="hero-title">${esc(headline)}</h1></div>
            </section>

            <div class="week-strip glass">${st.week.map((d) => `<span class="wd${d.minutes ? ' is-on' : ''}" data-tip="${esc(`${WD_FULL[parse(d.date).getDay()]}: ${d.minutes ? fmtMin(d.minutes) : `не ${c.f ? 'занималась' : 'занимался'}`}`)}"><b>${WD[parse(d.date).getDay()]}</b><i></i></span>`).join('')}
                <span class="ws-total"><b>${st.activeDays}/7</b><small>${fmtMin(st.minutes)}</small></span></div>

            <ul class="lights">${c.subjects.map((sub) => {
                const lv = subjLevel(sub), m = st.mocks.find((x) => x.id === sub.id);
                return `<li class="glass light"><span class="bulb b-${lv}" aria-label="${LEVEL[lv].label}"><i data-lucide="${LEVEL[lv].icon}"></i></span>
                    <span class="light-main"><b>${sub.title}</b><span class="muted">${sub.planBehind ? `отстаёт на ${sub.planBehind} ${plural(sub.planBehind, 'урок', 'урока', 'уроков')}` : 'по плану'} · пройдено ${Math.round((sub.planDone / sub.planTotal) * 100)}%</span></span>
                    <span class="light-score"><b>${m.last}</b><small class="${m.delta >= 0 ? 'tone-good' : 'tone-bad'}">${signed(m.delta)}</small></span></li>`;
            }).join('')}</ul>

            <section class="signals">
                <h2 class="h-s">${st.signals.length ? 'Что заметила система' : 'Сигналов нет'}</h2>
                ${st.signals.length ? st.signals.map((s, i) => `<div class="glass signal s-${s.level}">
                    <i data-lucide="${s.icon}"></i><div class="signal-main"><b>${esc(s.title)}</b><span class="muted">${esc(s.text)}</span></div>
                    <button class="btn btn-outline btn-s" data-act="${i}">${esc(s.action)}</button></div>`).join('')
                    : `<p class="empty-s glass">Занятия регулярные, домашки в срок, балл не падает. Следующий отчёт — в ${WD_FULL[settings().weekday]}.</p>`}
            </section>

            <div class="solo-foot">
                <a class="btn btn-ghost btn-s" href="#/a"><i data-lucide="layout-dashboard"></i>Подробнее</a>
                <a class="btn btn-ghost btn-s" href="#/settings"><i data-lucide="sliders-horizontal"></i>Когда тревожить</a>
            </div>
        </div>`;

        view.querySelectorAll('[data-act]').forEach((b) => b.addEventListener('click', () => {
            const s = st.signals[b.dataset.act];
            toast(s.action === 'Написать куратору' ? 'Откроется чат с куратором (заглушка)' : s.action === 'Напомнить ребёнку' ? `${c.name} получит мягкое напоминание в кабинете` : 'Подсказка для разговора — в варианте B, блок «О чём поговорить»');
        }));
    }

    // ------------------------------ Отчёты и сигналы ------------------------------

    function viewSettings() {
        const s = settings();
        const c = child();
        view.innerHTML = `
        <div class="page-header"><div>
            <p class="eyebrow">Общее для всех вариантов</p>
            <h1 class="title">Отчёты и сигналы</h1>
            <p class="description">Когда и куда присылать сводку и о чём сообщать сразу. Кабинет — только для просмотра: решить задачу за ребёнка или поменять ответы нельзя.</p></div></div>

        <div class="grid-2">
            <section class="glass panel">
                <h2>Еженедельный отчёт</h2>
                <label class="sw"><input type="checkbox" data-k="email" ${s.email ? 'checked' : ''}><span>На почту</span></label>
                <label class="sw"><input type="checkbox" data-k="telegram" ${s.telegram ? 'checked' : ''}><span>В Telegram</span></label>
                <label class="field"><span>День отправки</span>
                    <select data-k="weekday">${[1, 2, 3, 4, 5, 6, 0].map((d) => `<option value="${d}" ${d === s.weekday ? 'selected' : ''}>${WD_FULL[d]}</option>`).join('')}</select></label>
                <a class="link" href="#/b">Посмотреть, как выглядит отчёт →</a>
            </section>

            <section class="glass panel">
                <h2>Сообщать сразу, если…</h2>
                <label class="field"><span>Нет занятий подряд</span>
                    <select data-k="idleDays">${[2, 3, 5, 7].map((d) => `<option value="${d}" ${d === s.idleDays ? 'selected' : ''}>${d} ${plural(d, 'день', 'дня', 'дней')}</option>`).join('')}</select></label>
                <label class="sw"><input type="checkbox" data-k="lateAlert" ${s.lateAlert ? 'checked' : ''}><span>Домашка просрочена</span></label>
                <label class="field"><span>Пробник упал больше чем на</span>
                    <select data-k="mockDrop">${[3, 5, 10].map((d) => `<option value="${d}" ${d === s.mockDrop ? 'selected' : ''}>${d} баллов</option>`).join('')}</select></label>
                <p class="muted small">Пороги влияют на «Светофор» и блок «Обратите внимание» — переключитесь на вариант C, чтобы увидеть разницу.</p>
            </section>
        </div>

        <section class="glass panel">
            <h2>Прозрачность</h2>
            <div class="note"><i data-lucide="eye"></i><span>${esc(c.name)} видит в своём профиле, что кабинет родителя подключён, и какие сигналы вам приходят. Так меньше поводов для конфликтов.</span></div>
            <ul class="rows">${D.children.map((k) => `<li class="row"><i data-lucide="user-round"></i><span class="row-main"><span>${esc(k.name)}</span><span class="muted">${k.grade} · ${k.subjects.map((x) => x.title).join(', ')}</span></span><span class="pill p-good">подключён</span></li>`).join('')}
                <li class="row"><i data-lucide="user-round-plus"></i><span class="row-main"><span>Добавить ребёнка</span><span class="muted">Ссылка-приглашение придёт ребёнку в профиль</span></span><button class="btn btn-outline btn-s" id="invite">Пригласить</button></li></ul>
        </section>`;

        view.querySelectorAll('[data-k]').forEach((el) => el.addEventListener('change', () => {
            const next = settings();
            next[el.dataset.k] = el.type === 'checkbox' ? el.checked : Number(el.value);
            store.set('settings', next); toast('Сохранено');
        }));
        document.getElementById('invite').addEventListener('click', () => toast('Приглашение отправлено (заглушка)'));
    }

    // ------------------------------ оболочка ------------------------------

    function renderKids() {
        document.getElementById('kids').innerHTML = D.children.map((k) => {
            const lv = stats(k).level;
            return `<button type="button" role="tab" class="kid" aria-selected="${k.id === childId}" data-kid="${k.id}">
                <span class="kid-dot b-${lv}" aria-label="${LEVEL[lv].label}"></span>${esc(k.name)}<small>${k.grade}</small></button>`;
        }).join('');
        document.querySelectorAll('[data-kid]').forEach((b) => b.addEventListener('click', () => { childId = b.dataset.kid; store.set('child', childId); render(); }));
    }

    const ROUTES = { a: viewA, b: viewB, c: viewC, settings: viewSettings };

    function render() {
        const route = (location.hash.replace('#/', '') || store.get('route', 'a')).split('?')[0];
        const r = ROUTES[route] ? route : 'a';
        store.set('route', r);
        document.querySelectorAll('[data-route]').forEach((a) => a.classList.toggle(a.closest('.mnav') ? 'is-on' : 'active', a.dataset.route === r));
        renderKids();
        ROUTES[r]();
        window.lucide?.createIcons();
    }

    // Подсказки по наведению и по тапу
    function showTip(el) {
        tip.textContent = el.dataset.tip; tip.hidden = false;
        const r = el.getBoundingClientRect(), t = tip.getBoundingClientRect();
        tip.style.left = Math.max(8, Math.min(innerWidth - t.width - 8, r.left + r.width / 2 - t.width / 2)) + 'px';
        tip.style.top = (r.top - t.height - 8 < 8 ? r.bottom + 8 : r.top - t.height - 8) + 'px';
    }
    document.addEventListener('pointerover', (e) => { const el = e.target.closest('[data-tip]'); if (el) showTip(el); else tip.hidden = true; });
    document.addEventListener('scroll', () => { tip.hidden = true; }, true);

    document.getElementById('theme-toggle').addEventListener('click', () => {
        const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
        document.documentElement.dataset.theme = next;
        try { localStorage.setItem('concept-theme', next); } catch {}
    });

    window.addEventListener('hashchange', () => { render(); scrollTo(0, 0); });
    render();
})();
