// --- Theme menu (gear icon → Light / Dark / System) ---

document.addEventListener("DOMContentLoaded", function () {
    const htmlEl = document.documentElement;
    const gear = document.getElementById('theme-gear');
    const menu = document.getElementById('theme-menu');

    function systemPrefersDark() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    // Apply a theme choice. `choice` is 'light', 'dark', or 'system'.
    function applyTheme(choice) {
        let effective = choice;
        if (choice === 'system') {
            effective = systemPrefersDark() ? 'dark' : 'light';
        }
        htmlEl.classList.toggle('dark-mode', effective === 'dark');
        localStorage.setItem('theme', choice);
        updateActiveOption();
    }

    function updateActiveOption() {
        if (!menu) return;
        const current = localStorage.getItem('theme') || 'system';
        menu.querySelectorAll('.theme-option').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === current);
        });
    }

    function closeMenu() {
        if (!menu || menu.hidden) return;
        menu.hidden = true;
        if (gear) gear.setAttribute('aria-expanded', 'false');
    }

    // Apply saved choice (default to 'system' for new users)
    const savedTheme = localStorage.getItem('theme') || 'system';
    applyTheme(savedTheme);

    if (gear && menu) {
        gear.addEventListener('click', (e) => {
            e.stopPropagation();
            menu.hidden = !menu.hidden;
            gear.setAttribute('aria-expanded', String(!menu.hidden));
        });

        menu.querySelectorAll('.theme-option').forEach(btn => {
            btn.addEventListener('click', () => {
                applyTheme(btn.dataset.theme);
                closeMenu();
            });
        });

        document.addEventListener('click', (e) => {
            if (menu.hidden) return;
            if (!menu.contains(e.target) && e.target !== gear) {
                closeMenu();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeMenu();
        });
    }

    // Live-update when OS theme changes — only if user picked 'system'
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (localStorage.getItem('theme') === 'system') {
            applyTheme('system');
        }
    });
});

