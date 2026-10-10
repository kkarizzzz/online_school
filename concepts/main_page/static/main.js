// Общее для трёх страниц: шапка, подвал, призыв, тема, появление блоков, бегущие строки, отсчёт до ЕГЭ.
// Страница говорит, кто она, через <body data-page="home|graduates|parents">.
// Скрипт страницы (graduates.js, parents.js) подключается раньше: он дорисовывает свои блоки, а этот файл потом
// расставляет иконки и включает появление.

(() => {
const LOGO = '../../../frontend/src/shared/assets/icons/logo.svg';

// Вкладки кабинета — ведут в соседние концепты
const CABINET = {
    theory: '../../theory_page/static/index.html',
    lesson: '../../lesson_page/static/index.html?id=1.10.2',
    homework: '../../homework_page/static/index.html',
    bank: '../../bank_page/static/index.html',
    practice: 'http://localhost:8100',
    variants: '../../variants_page/static/index.html',
    review: '../../review_page/static/index.html',
};

// Меню шапки: «Преподаватели» и «Психологи» убраны, вместо них — «Обучение»
const MENU = [
    { id: 'learning', href: 'index.html#learning', label: 'Обучение' },
    { id: 'graduates', href: 'graduates.html', label: 'Выпускникам' },
    { id: 'parents', href: 'parents.html', label: 'Родителям' },
    { id: 'pricing', href: 'index.html#pricing', label: 'Тарифы' },
];

// Ориентировочное начало основного периода ЕГЭ: по расписанию прошлых лет — начало июня
const EXAM_DATE = new Date('2027-06-01T10:00:00+03:00');

// Куда ведут кнопки «7 дней бесплатно»: на главной — к блоку пробной недели
const TRIAL = 'index.html#trial-week';

const page = document.body.dataset.page;

function renderHeader() {
    const links = MENU.map((m) =>
        `<a href="${m.href}"${m.id === page ? ' aria-current="page"' : ''}>${m.label}</a>`).join('');

    document.getElementById('header').outerHTML = `
    <header class="header" id="header">
        <div class="container header-inner">
            <a href="index.html" class="logo" aria-label="Из нуля в сотку — на главную">
                <img src="${LOGO}" alt=""><span>Из нуля в сотку</span>
            </a>
            <nav class="nav" aria-label="Основное меню">${links}</nav>
            <div class="header-actions">
                <button type="button" class="icon-btn" id="theme-toggle" aria-label="Сменить тему">
                    <i data-lucide="moon" class="theme-dark-hidden"></i>
                    <i data-lucide="sun" class="theme-light-hidden"></i>
                </button>
                <a class="icon-btn header-login" href="${CABINET.theory}" aria-label="Войти" title="Войти"><i data-lucide="log-in"></i></a>
                <a class="btn btn-primary btn-s header-login" href="${TRIAL}">7 дней бесплатно</a>
                <button type="button" class="icon-btn burger" id="burger" aria-label="Открыть меню" aria-expanded="false" aria-controls="mobile-menu">
                    <i data-lucide="menu"></i>
                </button>
            </div>
        </div>
        <div class="mobile-menu" id="mobile-menu">
            <nav aria-label="Меню">${links}<a class="btn btn-primary" href="${TRIAL}">7 дней бесплатно</a><a class="btn btn-outline" href="${CABINET.theory}">Войти</a></nav>
        </div>
    </header>`;
}

function renderTrial() {
    const el = document.getElementById('trial');
    if (!el) return;
    el.outerHTML = `
    <section class="trial" id="trial">
        <div class="container">
            <p class="eyebrow">Пробная неделя</p>
            <h2>7 дней<br>бесплатно<span class="dot">.</span></h2>
            <p>Полный доступ ко всем четырём предметам: математика, русский, информатика, физика. Входной тест, уроки,
                домашка, нарешка и пробник на время. Без карты и автосписаний — продолжать или нет, решите по результату.</p>
            <a class="btn btn-primary btn-xl" href="${CABINET.theory}">Начать бесплатную неделю<i data-lucide="arrow-right"></i></a>
            <p class="trial-phone">Или позвони <a href="tel:+78000000000">8 (800) 000-00-00</a> — подберём программу</p>
        </div>
        <div class="marquee" style="--speed:50s"><div class="marquee-track" data-marquee>
            <span class="marquee-item">7 ДНЕЙ БЕСПЛАТНО</span>
            <span class="marquee-item">БЕЗ КАРТЫ</span>
            <span class="marquee-item">МАТЕМАТИКА · РУССКИЙ · ИНФОРМАТИКА · ФИЗИКА</span>
            <span class="marquee-item">СТАРТ В ЛЮБОЙ МОМЕНТ</span>
        </div></div>
    </section>`;
}

function renderFooter() {
    document.getElementById('footer').outerHTML = `
    <footer class="footer" id="footer">
        <div class="container">
            <div class="footer-hero">
                <h2>Путь<span class="serif-i">к сотке.</span></h2>
                <a class="btn btn-primary btn-xl" href="${CABINET.theory}">Начать обучение<i data-lucide="arrow-up-right"></i></a>
            </div>
            <div class="footer-grid">
                <div class="footer-col">
                    <a href="index.html" class="logo"><img src="${LOGO}" alt=""><span>Из нуля в сотку</span></a>
                    <p style="margin-top:12px;color:var(--text-secondary)">Онлайн-школа ЕГЭ — 2027</p>
                </div>
                <div class="footer-col">
                    <h3>Меню</h3>
                    <ul>${MENU.map((m) => `<li><a href="${m.href}">${m.label}</a></li>`).join('')}</ul>
                </div>
                <div class="footer-col">
                    <h3>Контакты</h3>
                    <ul>
                        <li>Москва, ул. Академическая, 1</li>
                        <li><a href="tel:+78000000000">8 (800) 000-00-00</a></li>
                        <li><a href="mailto:support@zero-to-hundred.ru">support@zero-to-hundred.ru</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Режим работы</h3>
                    <ul class="footer-hours">
                        <li><span>Пн–Пт</span><span>09:00 — 21:00</span></li>
                        <li><span>Сб–Вс</span><span>10:00 — 18:00</span></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <span>© ${new Date().getFullYear()} Из нуля в сотку. Все права защищены.</span>
                <span><a href="#">Политика конфиденциальности</a> · <a href="#">Оферта</a></span>
            </div>
        </div>
        <div class="footer-mark" aria-hidden="true">100</div>
    </footer>
    <p class="demo-note">Концепт главной: данные на странице — заглушки, цены — пример, кнопки «Войти» и вкладки ведут в соседние концепты.</p>`;
}

function initTheme() {
    document.getElementById('theme-toggle').addEventListener('click', () => {
        const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
        document.documentElement.dataset.theme = next;
        try { localStorage.setItem('concept-theme', next); } catch { /* приватный режим */ }
    });
}

function initHeader() {
    const header = document.getElementById('header');
    const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 20);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });

    const burger = document.getElementById('burger');
    const menu = document.getElementById('mobile-menu');
    const setOpen = (open) => {
        menu.classList.toggle('is-open', open);
        burger.setAttribute('aria-expanded', String(open));
        burger.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
    };
    burger.addEventListener('click', () => setOpen(!menu.classList.contains('is-open')));
    menu.addEventListener('click', (e) => { if (e.target.closest('a')) setOpen(false); });
}

// Бегущая строка: содержимое удваивается, анимация сдвигает на половину
function initMarquees() {
    document.querySelectorAll('[data-marquee]').forEach((track) => {
        const items = track.innerHTML;
        track.innerHTML = items.repeat(4);
    });
}

function initReveal() {
    const items = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window)) { items.forEach((el) => el.classList.add('is-visible')); return; }
    const io = new IntersectionObserver((entries) => {
        entries.forEach((e) => {
            if (!e.isIntersecting) return;
            e.target.classList.add('is-visible');
            io.unobserve(e.target);
        });
    }, { threshold: 0.12 });
    items.forEach((el) => io.observe(el));
}

const DAY = 24 * 60 * 60 * 1000;

function plural(n, one, few, many) {
    const m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return one;
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
    return many;
}

// [data-countdown="days"] — число дней; [data-countdown-label] — «дней/дня/день»
function initCountdown() {
    const days = Math.max(0, Math.ceil((EXAM_DATE - Date.now()) / DAY));
    document.querySelectorAll('[data-countdown="days"]').forEach((el) => { el.textContent = days; });
    document.querySelectorAll('[data-countdown-label]').forEach((el) => {
        el.textContent = `${plural(days, 'день', 'дня', 'дней')} до ЕГЭ`;
    });
}

renderHeader();
renderTrial();
renderFooter();
initTheme();
initHeader();
initMarquees();
initCountdown();
window.lucide?.createIcons();
initReveal();
})();
