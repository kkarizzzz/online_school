// Концепт «Нарешка», настройка персонального режима: номера ЕГЭ и подтемы с галочками.
// Галочка у номера отмечает или снимает все его подтемы; если отмечена часть — «частично».
// Сложность — чипы уровней (хотя бы один выбран), задания других уровней в ленту не попадают.
// Подборка сохраняется сразу (localStorage, concept-practice:personal), «Решать» открывает ленту ?scope=personal.

const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[c]));

/** Чипы сложности — без числа заданий */
function renderLevels() {
    $('levels').innerHTML = ALL_LEVELS.map((l) => `
        <button type="button" class="chip level-chip" data-level="${l}" aria-pressed="${personalLevels.has(l)}">
            ${levelMeter(l)}
        </button>`).join('');
}

function render() {
    renderLevels();
    $('numbers').innerHTML = BANK.map((b) => {
        const keys = keysOfNumber(b);
        const picked = keys.filter((k) => personal.has(k)).length;
        const tasks = byLevels(b.topics.flatMap((t) => t.tasks), personalLevels);
        return `
            <article class="num ${picked ? 'is-picked' : ''}">
                <label class="num-head pick-head">
                    <input type="checkbox" class="check" data-keys="${keys.join(' ')}"
                        ${picked === keys.length ? 'checked' : ''} ${picked && picked < keys.length ? 'data-mixed' : ''}>
                    <span class="num-badge">${b.n}</span>
                    <span class="num-text">
                        <span class="num-title">${escapeHtml(b.title)}</span>
                        <span class="num-meta">${picked === keys.length ? 'Весь номер'
                            : picked ? `Выбрано ${picked} из ${keys.length}`
                            : `${keys.length} ${plural(keys.length, 'подтема', 'подтемы', 'подтем')} · ${tasksWord(tasks.length)}`}</span>
                    </span>
                </label>
                <ul class="subs">
                    ${b.topics.map((t) => {
                        const key = keyOf(b.n, t.id);
                        return `
                            <li>
                                <label class="pick ${personal.has(key) ? 'is-selected' : ''}">
                                    <input type="checkbox" class="check" data-keys="${key}" ${personal.has(key) ? 'checked' : ''}>
                                    <span class="sub-name">${escapeHtml(t.name)}</span>
                                    <span class="sub-count">${byLevels(t.tasks, personalLevels).length}</span>
                                </label>
                            </li>`;
                    }).join('')}
                </ul>
            </article>`;
    }).join('');

    // «Частично» ставится только из JS
    $('numbers').querySelectorAll('[data-mixed]').forEach((el) => { el.indeterminate = true; });

    const parts = personalParts();
    const tasks = byLevels(tasksOfKeys(personal), personalLevels);
    const lv = levelsText(personalLevels);
    $('select-info').innerHTML = personal.size
        ? `Выбрано <b>${personal.size}</b> ${plural(personal.size, 'подтема', 'подтемы', 'подтем')}
            из <b>${parts.length}</b> ${plural(parts.length, 'номера', 'номеров', 'номеров')} · ${tasksWord(tasks.length)}${lv ? ` · ${escapeHtml(lv)}` : ''}`
        : 'Ничего не выбрано — отметьте номера или подтемы';
    $('clear').hidden = !personal.size;
    const off = !tasks.length;
    $('go').classList.toggle('is-disabled', off);
    $('go').setAttribute('aria-disabled', off);
    if (personal.size && off) $('select-info').innerHTML += ' — <b>нет заданий</b> такой сложности';
    icons();
}

$('numbers').addEventListener('change', (e) => {
    const box = e.target.closest('.check');
    if (!box) return;
    box.dataset.keys.split(' ').forEach((k) => (box.checked ? personal.add(k) : personal.delete(k)));
    savePersonal();
    render();
});

$('levels').addEventListener('click', (e) => {
    const chip = e.target.closest('[data-level]');
    if (!chip) return;
    const l = chip.dataset.level;
    if (personalLevels.has(l) && personalLevels.size === 1) return; // хотя бы один уровень остаётся
    if (personalLevels.has(l)) personalLevels.delete(l); else personalLevels.add(l);
    savePersonalLevels();
    render();
});

$('clear').addEventListener('click', () => {
    personal.clear();
    savePersonal();
    render();
});

initThemeToggle();
render();
