// «Родителям»: заглушки кабинета родителя — занятия за неделю, пробники, номера.
// Подключается перед main.js: рисует блоки, а иконки и появление включает main.js.

(() => {
// Минуты в кабинете по дням недели
const WEEK = [
    { day: 'Пн', min: 45 }, { day: 'Вт', min: 62 }, { day: 'Ср', min: 30 }, { day: 'Чт', min: 74 },
    { day: 'Пт', min: 0 }, { day: 'Сб', min: 52 }, { day: 'Вс', min: 21 },
];

// Пробники: дата и тестовый балл
const MOCKS = [
    { label: '14.09', score: 48 }, { label: '28.09', score: 55 }, { label: '05.10', score: 58 },
    { label: '19.10', score: 66 }, { label: '02.11', score: 72 },
];

// Номера ЕГЭ по предметам: доля верных ответов за месяц
const TOPICS = [
    { title: 'Математика · № 1 Планиметрия', p: 92 },
    { title: 'Русский · № 9–12 Орфография', p: 85 },
    { title: 'Информатика · № 5 Алгоритмы', p: 74 },
    { title: 'Русский · № 16–21 Пунктуация', p: 58 },
    { title: 'Математика · № 8 Производная', p: 40 },
]

function renderWeek() {
    const max = Math.max(...WEEK.map((d) => d.min));
    document.getElementById('week').innerHTML = WEEK.map((d) => `
        <div title="${d.min} мин">
            <i class="${d.min ? '' : 'zero'}" style="--h:${d.min ? Math.round(d.min / max * 100) : 4}%"></i>
            <span>${d.day}</span>
        </div>`).join('');

    const total = WEEK.reduce((s, d) => s + d.min, 0);
    const days = WEEK.filter((d) => d.min).length;
    document.getElementById('week-total').textContent =
        `${Math.floor(total / 60)} ч ${total % 60} мин · ${days} дней из 7`;
}

function renderChart() {
    const W = 400, H = 170, padX = 18, top = 22, bottom = 26;
    const min = 40, max = 100;
    const x = (i) => padX + i * (W - padX * 2) / (MOCKS.length - 1);
    const y = (v) => top + (1 - (v - min) / (max - min)) * (H - top - bottom);

    const pts = MOCKS.map((m, i) => [x(i), y(m.score)]);
    const line = pts.map(([px, py], i) => `${i ? 'L' : 'M'}${px.toFixed(1)} ${py.toFixed(1)}`).join(' ');
    const area = `${line} L${pts.at(-1)[0].toFixed(1)} ${H - bottom} L${pts[0][0].toFixed(1)} ${H - bottom} Z`;

    const grid = [50, 70, 90].map((v) =>
        `<line class="grid-l" x1="0" x2="${W}" y1="${y(v)}" y2="${y(v)}"/><text x="${W}" y="${y(v) - 4}" text-anchor="end">${v}</text>`).join('');

    document.getElementById('chart').innerHTML = `
        ${grid}
        <path class="area" d="${area}"/>
        <path class="line" d="${line}"/>
        ${pts.map(([px, py], i) => `
            <circle class="pt" cx="${px}" cy="${py}" r="4.5"/>
            <text class="val" x="${px}" y="${py - 10}" text-anchor="middle">${MOCKS[i].score}</text>
            <text x="${px}" y="${H - 6}" text-anchor="middle">${MOCKS[i].label}</text>`).join('')}`;
}

function renderTopics() {
    const color = (p) => (p >= 80 ? 'var(--done)' : p >= 60 ? 'var(--warn)' : 'var(--bad)');
    document.getElementById('topics').innerHTML = TOPICS.map((t) => `
        <div class="topic">
            <span>${t.title}</span><b style="color:${color(t.p)}">${t.p}%</b>
            <span class="bar"><span style="--p:${t.p}%;--c:${color(t.p)}"></span></span>
        </div>`).join('');
}

renderWeek();
renderChart();
renderTopics();
})();
