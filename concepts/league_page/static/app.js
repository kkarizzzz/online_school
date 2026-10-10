// Вкладка «Лига»: итоги недели, задания, таблица лиги, клан, магазин.
// Данные — window.LEAGUE из data.js. Свои действия (забрать награду, покупка, взнос в банк)
// хранятся в localStorage `concept-league:state`, чтобы баланс переживал перезагрузку.

const L = window.LEAGUE;
const STATE_KEY = 'concept-league:state';

const $ = (sel) => document.querySelector(sel);
const icons = () => window.lucide?.createIcons();
const fmt = (n) => n.toLocaleString('ru-RU');
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

function plural(n, one, few, many) {
    const m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return one;
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
    return many;
}

// ----------------------------------- состояние -----------------------------------
// { spent, earned, claimed: [questId], owned: {itemId: count}, donated,
//   accepted: [id], declined: [id], sent: [ник], cheered: [id], challenged: [{ friend, template }], claimedDuels: [id] }

const EMPTY_STATE = () => ({
    spent: 0, earned: 0, claimed: [], owned: {}, donated: 0,
    accepted: [], declined: [], sent: [], cheered: [], challenged: [], claimedDuels: [],
});

function loadState() {
    try {
        const s = JSON.parse(localStorage.getItem(STATE_KEY));
        if (s && typeof s === 'object') return { ...EMPTY_STATE(), ...s };
    } catch { /* приватный режим */ }
    return EMPTY_STATE();
}

const state = loadState();
const save = () => { try { localStorage.setItem(STATE_KEY, JSON.stringify(state)); } catch { /* приватный режим */ } };

const balance = () => L.me.balance + state.earned - state.spent;
const isClaimed = (q) => q.claimed || state.claimed.includes(q.id);
const isDone = (q) => q.progress >= q.goal;

function toast(text) {
    const el = $('#toast');
    el.textContent = text;
    el.hidden = false;
    clearTimeout(toast.t);
    toast.t = setTimeout(() => { el.hidden = true; }, 2600);
}

const coin = (n, cls = '') => `<span class="reward ${cls}"><span class="coin coin-s" aria-hidden="true">С</span>${fmt(n)}</span>`;
const emblem = (c, size = '') => `<span class="emblem ${size}" style="--c:${c.color}"><i data-lucide="${c.icon}"></i></span>`;
const division = (id) => L.divisions.find((d) => d.id === id);

// ----------------------------------- итоги -----------------------------------

function renderSummary() {
    const clan = L.clan;
    const place = L.standings.findIndex((s) => s.mine) + 1;
    const div = division(clan.division);
    const clanPoints = L.standings.find((s) => s.mine).points;

    $('#eyebrow').textContent = `Сезон «${L.season.name}» · неделя ${L.season.week} из ${L.season.weeks}`;
    $('#clan-card').innerHTML = `
        ${emblem(clan, 'lg')}
        <span class="clan-info">
            <b>${esc(clan.name)} <span class="tag">${clan.tag}</span></b>
            <span class="muted">${esc(clan.motto)}</span>
            <span class="div-pill" style="--c:${div.color}"><i data-lucide="shield"></i>${div.name} лига · ${place} место</span>
        </span>`;

    $('#my-points').textContent = fmt(L.me.points);
    $('#my-share').textContent = `${Math.round((L.me.points / clanPoints) * 100)}% очков клана · серия ${L.me.streak} ${plural(L.me.streak, 'день', 'дня', 'дней')}`;
    renderBalance();
}

function renderBalance() {
    $('#balance').textContent = fmt(balance());
    $('#header-balance').textContent = fmt(balance());
    $('#earned').textContent = `+${fmt(L.me.earnedThisWeek + state.earned)} за неделю`;
}

function tickCountdown() {
    const left = Math.max(0, new Date(L.season.endsAt) - Date.now());
    const d = Math.floor(left / 864e5), h = Math.floor(left / 36e5) % 24, m = Math.floor(left / 6e4) % 60;
    // Концепт открывают и после даты окончания — тогда показываем «неделю» целиком
    $('#countdown').textContent = left ? (d ? `${d} д ${h} ч` : `${h} ч ${m} мин`) : '6 д 23 ч';
}

// ----------------------------------- задания -----------------------------------

function questItem(q, clan) {
    const pct = Math.min(100, Math.round((q.progress / q.goal) * 100));
    const done = isDone(q), claimed = isClaimed(q);
    const side = claimed
        ? '<span class="done-badge"><i data-lucide="check"></i>Получено</span>'
        : done
            ? `<button type="button" class="btn btn-primary" data-claim="${q.id}">Забрать ${coin(q.reward, 'on-primary')}</button>`
            : coin(q.reward);
    const extra = clan
        ? `<span class="muted small">Ваш вклад: ${q.mine} · в банк клана +${fmt(q.bank)}</span>`
        : '';
    return `
        <li class="glass quest ${done ? 'is-done' : ''} ${claimed ? 'is-claimed' : ''}">
            <span class="quest-icon"><i data-lucide="${q.icon}"></i></span>
            <div class="quest-body">
                <b>${esc(q.title)}</b>
                <span class="muted small">${esc(q.note)}</span>
                <div class="bar" role="progressbar" aria-valuenow="${q.progress}" aria-valuemax="${q.goal}"><span style="width:${pct}%"></span></div>
                <span class="quest-meta"><span>${fmt(Math.min(q.progress, q.goal))} / ${fmt(q.goal)}</span>${extra}</span>
            </div>
            <div class="quest-side">${side}</div>
        </li>`;
}

function renderQuests() {
    $('#personal-quests').innerHTML = L.personalQuests.map((q) => questItem(q, false)).join('');
    $('#clan-quests').innerHTML = L.clanQuests.map((q) => questItem(q, true)).join('');

    const doneCount = L.personalQuests.filter(isDone).length;
    const chestId = 'chest';
    const chestReady = doneCount === L.personalQuests.length;
    const chestClaimed = state.claimed.includes(chestId);
    $('#chest').innerHTML = `
        <span class="quest-icon"><i data-lucide="gift"></i></span>
        <div class="quest-body">
            <b>Сундук недели</b>
            <span class="muted small">Выполните все три личных задания: ${doneCount} из ${L.personalQuests.length}</span>
            <div class="pips">${L.personalQuests.map((q) => `<span class="${isDone(q) ? 'on' : ''}"></span>`).join('')}</div>
        </div>
        <div class="quest-side">${chestClaimed
            ? '<span class="done-badge"><i data-lucide="check"></i>Получено</span>'
            : chestReady ? `<button type="button" class="btn btn-primary" data-claim="${chestId}">Открыть</button>` : coin(L.personalChest)}</div>`;

    const ready = [...L.personalQuests, ...L.clanQuests].filter((q) => isDone(q) && !isClaimed(q)).length;
    $('#claim-badge').hidden = !ready;
    $('#claim-badge').textContent = ready;
    icons();
}

function claim(id) {
    const q = [...L.personalQuests, ...L.clanQuests].find((x) => x.id === id);
    const reward = id === 'chest' ? L.personalChest : q.reward;
    state.claimed.push(id);
    state.earned += reward;
    save();
    renderQuests();
    renderBalance();
    toast(`+${fmt(reward)} соток`);
}

// ----------------------------------- лига -----------------------------------

function renderLeague() {
    const current = L.divisions.findIndex((d) => d.id === L.clan.division);
    $('#ladder').innerHTML = L.divisions.map((d, i) => `
        <span class="rung ${i === current ? 'is-current' : ''} ${i < current ? 'is-passed' : ''}" style="--c:${d.color}">
            <i data-lucide="${i === L.divisions.length - 1 ? 'crown' : 'shield'}"></i>${d.name}
        </span>`).join('<i data-lucide="chevron-right" class="rung-sep"></i>');

    const n = L.standings.length;
    $('#standings').innerHTML = L.standings.map((c, i) => {
        const zone = i < 3 ? 'up' : i >= n - 3 ? 'down' : '';
        return `
        <li class="row ${zone ? `zone-${zone}` : ''} ${c.mine ? 'is-mine' : ''}">
            <span class="place">${i + 1}</span>
            <span class="row-clan">${emblem(c)}<span><b>${esc(c.name)}</b> <span class="tag">${c.tag}</span></span>
                ${zone === 'up' ? '<i data-lucide="arrow-up" class="zone-icon up"></i>' : ''}
                ${zone === 'down' ? '<i data-lucide="arrow-down" class="zone-icon down"></i>' : ''}</span>
            <span class="num muted">${c.members}</span>
            <span class="num"><b>${fmt(c.points)}</b></span>
            <span class="num">${coin(L.placeRewards[i])}</span>
        </li>`;
    }).join('');
}

// ----------------------------------- клан -----------------------------------

const ROLES = { leader: 'Глава', officer: 'Офицер', member: '' };

function renderClan() {
    const top = 10;
    const max = L.members[0].points || 1;
    $('#members-count').textContent = `${L.members.length} из ${L.clan.limit} · в зачёт идут ${top} лучших`;
    $('#members').innerHTML = L.members.map((m, i) => `
        <li class="member ${m.id === L.me.id ? 'is-me' : ''} ${i >= top ? 'is-out' : ''}">
            <span class="place">${i + 1}</span>
            <span class="m-avatar">${esc(m.name[0])}</span>
            <span class="m-name"><b>${esc(m.name)}${m.id === L.me.id ? ' · вы' : ''}</b>
                ${ROLES[m.role] ? `<span class="role">${ROLES[m.role]}</span>` : ''}
                ${m.streak ? `<span class="streak"><i data-lucide="flame"></i>${m.streak}</span>` : ''}</span>
            <span class="m-bar"><span style="width:${Math.round((m.points / max) * 100)}%"></span></span>
            <span class="num"><b>${fmt(m.points)}</b></span>
        </li>`).join('');

    $('#bank').textContent = fmt(L.clan.bank + state.donated);
    $('#invite').textContent = L.clan.invite;
    $('#seats').textContent = `Свободно ${L.clan.limit - L.members.length} ${plural(L.clan.limit - L.members.length, 'место', 'места', 'мест')}`;

    $('#feed').innerHTML = L.feed.map((f) => `
        <li><span class="m-avatar sm">${esc(f.who[0])}</span>
            <span><b>${esc(f.who)}</b> ${esc(f.text)}${f.points ? ` <span class="plus">+${f.points}</span>` : ''}
            <span class="muted small">· ${f.ago}</span></span></li>`).join('');
}

function donate() {
    if (balance() < 100) return toast('Не хватает соток');
    state.spent += 100;
    state.donated += 100;
    save();
    renderBalance();
    renderClan();
    icons();
    toast('100 соток в банке клана');
}

// ----------------------------------- магазин -----------------------------------

const SHOP_KINDS = [
    { id: 'all', label: 'Всё' },
    { id: 'use', label: 'Полезное' },
    { id: 'look', label: 'Оформление' },
    { id: 'clan', label: 'Для клана' },
    { id: 'real', label: 'С преподавателем' },
];
let shopKind = 'all';

function renderShop() {
    $('#shop-filters').innerHTML = SHOP_KINDS.map((k) =>
        `<button type="button" class="chip ${k.id === shopKind ? 'is-active' : ''}" data-kind="${k.id}">${k.label}</button>`).join('');

    const items = L.shop.filter((it) => shopKind === 'all' || it.kind === shopKind);
    $('#shop').innerHTML = items.map((it) => {
        const owned = state.owned[it.id] || 0;
        const fromBank = it.kind === 'clan';
        const wallet = fromBank ? L.clan.bank + state.donated : balance();
        const lacks = wallet < it.price;
        return `
        <li class="glass item kind-${it.kind}">
            <span class="item-icon"><i data-lucide="${it.icon}"></i></span>
            <b>${esc(it.title)}</b>
            <span class="muted small">${esc(it.note)}</span>
            <div class="item-foot">
                ${coin(it.price)}${fromBank ? '<span class="muted small">из банка</span>' : ''}
                ${owned ? `<span class="owned">есть: ${owned}</span>` : ''}
                <button type="button" class="btn ${lacks ? 'btn-ghost' : 'btn-primary'}" data-buy="${it.id}" ${lacks ? 'disabled' : ''}>
                    ${lacks ? `Нужно ещё ${fmt(it.price - wallet)}` : 'Купить'}</button>
            </div>
        </li>`;
    }).join('');
    icons();
}

function buy(id) {
    const it = L.shop.find((x) => x.id === id);
    const where = it.kind === 'clan' ? 'из банка клана' : 'с вашего баланса';
    if (!confirm(`Купить «${it.title}» за ${fmt(it.price)} соток ${where}?`)) return;
    if (it.kind === 'clan') state.donated -= it.price;
    else state.spent += it.price;
    state.owned[id] = (state.owned[id] || 0) + 1;
    save();
    renderBalance();
    renderShop();
    renderClan();
    toast(`Куплено: ${it.title}`);
}

// ----------------------------------- друзья -----------------------------------

const MAX_CHALLENGES = 3;
const FRIEND_ACTIONS = '[data-accept],[data-decline],[data-cheer],[data-challenge],[data-template],[data-invite-clan],[data-duel]';
let challengeFriend = null;

/** Друзья с учётом принятых в этом браузере заявок */
function friendsList() {
    const accepted = L.requests.incoming
        .filter((r) => state.accepted.includes(r.id))
        .map((r) => ({ id: r.id, name: r.name, clan: r.clan, points: 0, streak: 0, together: 0, online: false, last: 'только что добавлен' }));
    return [...L.friends, ...accepted];
}

const pendingIncoming = () => L.requests.incoming.filter((r) => !state.accepted.includes(r.id) && !state.declined.includes(r.id));

/** Вызовы: заглушка + отправленные в этом браузере (ждут ответа друга) */
function challengesList() {
    const own = state.challenged.map((c, i) => {
        const tpl = L.challengeTemplates.find((t) => t.id === c.template);
        return { id: `own${i}`, friend: c.friend, title: tpl.title, me: 0, them: 0, pending: true };
    });
    return [...L.challenges, ...own];
}

function renderRequests() {
    const incoming = pendingIncoming();
    const outgoing = [...L.requests.outgoing.map((r) => r.name), ...state.sent];
    $('#friends-badge').hidden = !incoming.length;
    $('#friends-badge').textContent = incoming.length;
    if (!incoming.length && !outgoing.length) return '';
    return `
        <div class="glass card requests">
            ${incoming.map((r) => `
                <div class="request">
                    <span class="m-avatar">${esc(r.name[0])}</span>
                    <span class="f-info">
                        <span class="m-name"><b>${esc(r.name)}</b>${r.clan ? `<span class="tag">${r.clan}</span>` : ''}</span>
                        <span class="muted small">хочет добавить вас · ${r.mutual} ${plural(r.mutual, 'общий друг', 'общих друга', 'общих друзей')}</span>
                    </span>
                    <span class="f-actions">
                        <button type="button" class="btn btn-primary btn-sm" data-accept="${r.id}">Принять</button>
                        <button type="button" class="icon-btn" data-decline="${r.id}" aria-label="Отклонить"><i data-lucide="x"></i></button>
                    </span>
                </div>`).join('')}
            ${outgoing.length ? `<span class="muted small">Ждут ответа: ${outgoing.map(esc).join(', ')}</span>` : ''}
        </div>`;
}

function duelItem(d) {
    const total = d.me + d.them;
    const lead = d.me > d.them ? 'is-win' : d.me < d.them ? 'is-lose' : '';
    let side = `<span class="muted small"><i data-lucide="timer" class="inline-icon"></i>${d.endsIn}</span>`;
    if (d.pending) side = '<span class="muted small">ждём ответа</span>';
    else if (d.done) side = state.claimedDuels.includes(d.id)
        ? '<span class="done-badge"><i data-lucide="check"></i>Получено</span>'
        : `<button type="button" class="btn btn-primary btn-sm" data-duel="${d.id}">Забрать ${coin(d.reward, 'on-primary')}</button>`;
    return `
        <li class="glass duel ${lead}">
            <div class="duel-head"><span><b>${esc(d.title)}</b> <span class="muted small">· с ${esc(d.friend)}</span></span>${side}</div>
            <div class="duel-score">
                <span class="duel-name">Вы <b>${d.me}</b></span>
                <div class="duel-bar"><span style="width:${total ? Math.round((d.me / total) * 100) : 50}%"></span></div>
                <span class="duel-name right"><b>${d.them}</b> ${esc(d.friend.split(' ')[0])}</span>
            </div>
        </li>`;
}

function friendRow(f, i, max) {
    const busy = challengesList().some((d) => !d.done && d.friend === f.name);
    const cheered = state.cheered.includes(f.id);
    const actions = f.me ? '' : `
        <button type="button" class="icon-btn" data-cheer="${f.id}" title="Подбодрить" aria-label="Подбодрить" ${cheered ? 'disabled' : ''}>
            <i data-lucide="${cheered ? 'check' : 'hand-heart'}"></i></button>
        <button type="button" class="icon-btn" data-challenge="${esc(f.name)}" title="Бросить вызов" aria-label="Бросить вызов" ${busy ? 'disabled' : ''}>
            <i data-lucide="swords"></i></button>
        ${f.clan ? '' : `<button type="button" class="icon-btn" data-invite-clan="${esc(f.name)}" title="Позвать в клан" aria-label="Позвать в клан"><i data-lucide="user-plus"></i></button>`}`;
    return `
        <li class="friend ${f.me ? 'is-me' : ''}">
            <span class="place">${i + 1}</span>
            <span class="m-avatar ${f.online ? 'is-online' : ''}">${esc(f.name[0])}</span>
            <span class="f-info">
                <span class="m-name"><b>${esc(f.name)}${f.me ? ' · вы' : ''}</b>
                    ${f.clan ? `<span class="tag">${f.clan}</span>` : ''}
                    ${f.together ? `<span class="streak" title="Общая серия: дней подряд, когда занимались оба"><i data-lucide="flame"></i>${f.together} вместе</span>` : ''}</span>
                ${f.me ? '' : `<span class="muted small">${esc(f.last)}</span>`}
            </span>
            <span class="m-bar"><span style="width:${Math.round((f.points / max) * 100)}%"></span></span>
            <span class="num"><b>${fmt(f.points)}</b></span>
            <span class="f-actions">${actions}</span>
        </li>`;
}

function renderFriends() {
    $('#friend-code').textContent = L.friendCode;
    $('#invite-reward').innerHTML = `${coin(L.inviteReward)} за каждого друга`;
    $('#requests').innerHTML = renderRequests();
    $('#challenges').innerHTML = challengesList().map(duelItem).join('');

    const me = { id: L.me.id, name: L.me.name, clan: L.clan.tag, points: L.me.points, online: true, me: true };
    const rows = [...friendsList(), me].sort((a, b) => b.points - a.points);
    const n = rows.length - 1;
    $('#friends-count').textContent = `${n} ${plural(n, 'друг', 'друга', 'друзей')} · ${rows.findIndex((r) => r.me) + 1} место среди друзей`;
    $('#friends').innerHTML = rows.map((f, i) => friendRow(f, i, rows[0].points || 1)).join('');
    icons();
}

function openChallenge(name) {
    if (challengesList().filter((d) => !d.done).length >= MAX_CHALLENGES) {
        return toast(`Не больше ${MAX_CHALLENGES} вызовов одновременно`);
    }
    challengeFriend = name;
    $('#challenge-title').textContent = `Вызов: ${name}`;
    $('#templates').innerHTML = L.challengeTemplates.map((t) => `
        <button type="button" class="template" data-template="${t.id}">
            <span class="quest-icon"><i data-lucide="${t.icon}"></i></span>
            <span class="f-info"><b>${esc(t.title)}</b><span class="muted small">${esc(t.note)}</span></span>
        </button>`).join('');
    icons();
    $('#challenge-dialog').showModal();
}

function friendAction(t) {
    const d = t.dataset;
    if (d.challenge) return openChallenge(d.challenge);
    if (d.inviteClan) return toast(`${d.inviteClan} получит приглашение в «${L.clan.name}»`);

    if (d.accept) {
        state.accepted.push(Number(d.accept));
        toast('Заявка принята');
    } else if (d.decline) {
        state.declined.push(Number(d.decline));
    } else if (d.cheer) {
        state.cheered.push(Number(d.cheer));
        toast('Друг получит уведомление «Так держать!»');
    } else if (d.template) {
        state.challenged.push({ friend: challengeFriend, template: d.template });
        $('#challenge-dialog').close();
        toast(`Вызов отправлен: ${challengeFriend}`);
    } else if (d.duel) {
        const duel = L.challenges.find((x) => x.id === d.duel);
        state.claimedDuels.push(duel.id);
        state.earned += duel.reward;
        renderBalance();
        toast(`+${duel.reward} соток`);
    }
    save();
    renderFriends();
}

function addFriend(e) {
    e.preventDefault();
    const input = $('#friend-input');
    const value = input.value.trim();
    if (!value) return;
    if (value.toUpperCase() === L.friendCode) return toast('Это ваш код');
    state.sent.push(value);
    save();
    input.value = '';
    renderFriends();
    toast('Заявка отправлена');
}

// ----------------------------------- без клана -----------------------------------

function renderNoClan() {
    $('#open-clans').innerHTML = L.openClans.map((c) => {
        const div = division(c.division);
        return `
        <li class="glass open-clan">
            ${emblem(c, 'lg')}
            <div class="quest-body">
                <b>${esc(c.name)} <span class="tag">${c.tag}</span></b>
                <span class="muted small">${esc(c.subject)} · цель ${c.target} · ${c.members} из 20</span>
                <span class="div-pill" style="--c:${div.color}"><i data-lucide="shield"></i>${div.name} лига</span>
            </div>
            <button type="button" class="btn ${c.open ? 'btn-primary' : 'btn-ghost'}">${c.open ? 'Вступить' : 'Подать заявку'}</button>
        </li>`;
    }).join('');
}

// ----------------------------------- вкладки -----------------------------------

const TABS = ['quests', 'league', 'clan', 'friends', 'shop', 'rules'];

function openTab(tab, push = true) {
    if (!TABS.includes(tab)) tab = 'quests';
    document.querySelectorAll('.tab').forEach((b) => {
        b.classList.toggle('is-active', b.dataset.tab === tab);
        b.setAttribute('aria-selected', b.dataset.tab === tab);
    });
    document.querySelectorAll('.panel').forEach((p) => { p.hidden = p.dataset.panel !== tab; });
    if (push) {
        const url = new URL(location.href);
        url.searchParams.set('tab', tab);
        history.replaceState(null, '', url);
    }
}

// ----------------------------------- запуск -----------------------------------

function init() {
    const params = new URLSearchParams(location.search);
    const noClan = params.get('clan') === 'none';

    $('#header-balance').textContent = fmt(balance());
    $('#with-clan').hidden = noClan;
    $('#no-clan').hidden = !noClan;
    $('#demo-switch').textContent = noClan ? 'Посмотреть экран с кланом' : 'Посмотреть экран без клана';
    $('#demo-switch').href = noClan ? '?' : '?clan=none';

    if (noClan) {
        renderNoClan();
    } else {
        renderSummary();
        renderQuests();
        renderLeague();
        renderClan();
        renderFriends();
        renderShop();
        tickCountdown();
        setInterval(tickCountdown, 30_000);
        openTab(params.get('tab'), false);
    }

    document.addEventListener('click', (e) => {
        const t = e.target.closest('[data-tab],[data-go],[data-claim],[data-kind],[data-buy],#donate,#copy-invite,#theme-toggle,'
            + `${FRIEND_ACTIONS},#copy-friend-code,#copy-invite-link`);
        if (!t) return;
        if (t.matches(FRIEND_ACTIONS)) friendAction(t);
        else if (t.id === 'copy-friend-code' || t.id === 'copy-invite-link') {
            const text = t.id === 'copy-friend-code' ? L.friendCode : `${location.origin}/?invite=${L.friendCode}`;
            navigator.clipboard?.writeText(text).catch(() => {});
            toast(t.id === 'copy-friend-code' ? 'Код скопирован' : 'Ссылка скопирована');
        } else if (t.dataset.tab) openTab(t.dataset.tab);
        else if (t.dataset.go) { e.preventDefault(); openTab(t.dataset.go); }
        else if (t.dataset.claim) claim(t.dataset.claim);
        else if (t.dataset.kind) { shopKind = t.dataset.kind; renderShop(); }
        else if (t.dataset.buy) buy(t.dataset.buy);
        else if (t.id === 'donate') donate();
        else if (t.id === 'copy-invite') {
            navigator.clipboard?.writeText(L.clan.invite).catch(() => {});
            toast('Код скопирован');
        } else if (t.id === 'theme-toggle') {
            const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
            document.documentElement.dataset.theme = next;
            try { localStorage.setItem('concept-theme', next); } catch { /* приватный режим */ }
        }
    });

    $('#add-friend')?.addEventListener('submit', addFriend);

    icons();
}

init();
