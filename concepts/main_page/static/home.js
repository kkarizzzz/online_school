// Главная: переключатель «Помесячно / До экзамена» в тарифах.
// Цены лежат в data-month и data-year у каждой цены.

(() => {
const billing = document.getElementById('billing');
const prices = document.querySelectorAll('.price b');

billing.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-period]');
    if (!btn) return;
    billing.querySelectorAll('[data-period]').forEach((b) => b.setAttribute('aria-checked', String(b === btn)));
    prices.forEach((p) => { p.textContent = p.dataset[btn.dataset.period]; });
});
})();
