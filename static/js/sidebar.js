/**
 * TechTaskSoln — Shared Sidebar Component
 * Handles: overlay sidebar, role-based nav rendering, toggle, badges.
 * 
 * Usage:
 *   1. Include <script src="/static/js/api.js"></script> BEFORE this file
 *   2. Include <script src="/static/js/sidebar.js"></script>
 *   3. The sidebar + overlay HTML is injected automatically on DOMContentLoaded
 *   4. Call `initSidebar()` after your page-specific init if needed
 *
 * Requires: api.js (isLoggedIn, fetchUserInfo, getUserInfo, logout)
 */

/* ══════════════════════════════════════════════════════
   ROLE-BASED MENU DEFINITIONS
   ══════════════════════════════════════════════════════ */

/**
 * Returns sidebar menu items for the given role.
 * Each item: { icon, label, href, badge? }
 * Use { divider: true } for separator lines.
 * @param {string} role - 'guest' | 'client' | 'freelancer' | 'admin'
 * @returns {Array}
 */
function getSidebarLinks(role) {
    const menus = {
        guest: [
            { icon: 'home', label: 'Home', href: '/' },
            { icon: 'search', label: 'Find Freelancers', href: '/client/freelancers/' },
            { icon: 'work', label: 'Find Projects', href: '/freelancer/projects/' },
            { icon: 'info', label: 'How it Works', href: '#how-it-works' },
            { icon: 'sell', label: 'Pricing', href: '/register/' },
            { divider: true },
            { icon: 'login', label: 'Log In', href: '/login/' },
            { icon: 'person_add', label: 'Sign Up', href: '/register/' },
        ],
        client: [
            { icon: 'dashboard', label: 'Dashboard', href: '/client/dashboard/' },
            { icon: 'work', label: 'My Projects', href: '/client/projects/' },
            { icon: 'description', label: 'Proposals', href: '/client/proposals/' },
            { icon: 'group', label: 'Freelancers', href: '/client/freelancers/' },
            { icon: 'payments', label: 'Payments', href: '/client/reports/' },
            { icon: 'bar_chart', label: 'Reports', href: '/client/reports/' },
            { icon: 'chat', label: 'Messages', href: '/chat/', badgeId: 'badge-messages' },
            { icon: 'notifications', label: 'Notifications', href: '/notifications/', badgeId: 'badge-notifications' },
            { divider: true },
            { icon: 'add_circle', label: 'New Project', href: '/client/projects/new/', highlight: true },
            { icon: 'settings', label: 'Settings', href: '/settings/' },
        ],
        freelancer: [
            { icon: 'dashboard', label: 'Dashboard', href: '/freelancer/dashboard/' },
            { icon: 'work', label: 'Projects', href: '/freelancer/projects/' },
            { icon: 'description', label: 'Proposals', href: '/freelancer/proposals/' },
            { icon: 'account_balance_wallet', label: 'Earnings', href: '/freelancer/earnings/' },
            { icon: 'bar_chart', label: 'Reports', href: '/freelancer/reports/' },
            { icon: 'chat', label: 'Messages', href: '/chat/', badgeId: 'badge-messages' },
            { icon: 'notifications', label: 'Notifications', href: '/notifications/', badgeId: 'badge-notifications' },
            { divider: true },
            { icon: 'manage_accounts', label: 'Edit Profile', href: '/freelancer/profile/edit/' },
            { icon: 'settings', label: 'Settings', href: '/settings/' },
        ],
        admin: [
            { icon: 'dashboard', label: 'Dashboard', href: '/admin-panel/' },
            { icon: 'people', label: 'User Management', href: '/admin-panel/users/' },
            { icon: 'work', label: 'Project Monitoring', href: '/admin-panel/projects/' },
            { icon: 'analytics', label: 'Reports & Analytics', href: '/admin-panel/reports/' },
            { icon: 'gpp_maybe', label: 'Fraud Monitoring', href: '/admin-panel/fraud/' },
            { divider: true },
            { icon: 'settings', label: 'Settings', href: '/settings/' },
        ],
    };
    return menus[role] || menus.guest;
}


/* ══════════════════════════════════════════════════════
   INJECT SIDEBAR HTML INTO PAGE
   ══════════════════════════════════════════════════════ */

/**
 * Injects the sidebar overlay + aside + hamburger into the DOM.
 * Should be called once on page load.
 */
function injectSidebarHTML() {
    // Don't inject if sidebar already exists
    if (document.getElementById('sidebar')) return;

    // --- Overlay ---
    const overlay = document.createElement('div');
    overlay.id = 'sidebar-overlay';
    overlay.className = 'fixed inset-0 bg-black/50 z-40 hidden';
    overlay.style.transition = 'opacity 0.3s ease';
    overlay.addEventListener('click', closeSidebar);
    document.body.insertBefore(overlay, document.body.firstChild);

    // --- Sidebar ---
    const aside = document.createElement('aside');
    aside.id = 'sidebar';
    aside.className = 'fixed top-0 left-0 z-50 h-full w-64 flex flex-col -translate-x-full transition-transform duration-300 ease-in-out overflow-y-auto overflow-x-hidden shadow-2xl';
    aside.style.cssText = 'background: linear-gradient(160deg, #1e1b4b 0%, #1e2a5e 45%, #0f172a 100%);';
    aside.innerHTML = `
        <!-- Sidebar Header -->
        <div class="flex items-center justify-between px-5 py-4" style="border-bottom: 1px solid rgba(255,255,255,0.1);">
            <a href="/" class="flex items-center gap-3 no-underline min-w-0">
                <div class="rounded-xl p-2 shrink-0" style="background:linear-gradient(135deg,#6366f1,#818cf8);">
                    <span class="material-symbols-outlined text-white">rocket_launch</span>
                </div>
                <div class="overflow-hidden">
                    <h1 class="text-white text-lg font-bold leading-none whitespace-nowrap tracking-tight">TechTaskSoln</h1>
                    <p class="text-indigo-300 text-xs font-medium" id="sidebar-role-label">Platform</p>
                </div>
            </a>
            <button onclick="closeSidebar()" class="flex items-center justify-center size-8 rounded-lg transition-colors text-indigo-300 hover:text-white hover:bg-white/10" aria-label="Close sidebar">
                <span class="material-symbols-outlined text-xl">close</span>
            </button>
        </div>

        <!-- Navigation (populated by JS) -->
        <nav class="flex-1 flex flex-col gap-1 px-3 py-4" id="sidebar-nav">
        </nav>
        <!-- Decorative gradient accent -->
        <div style="position:absolute;top:0;right:0;width:3px;height:100%;background:linear-gradient(180deg,#6366f1,#818cf8,#6366f1);opacity:0.6;"></div>

        <!-- User Info Footer (hidden until login) -->
        <div class="px-3 pb-4" id="sidebar-user-info" style="display:none;">
            <div class="pt-4" style="border-top: 1px solid rgba(255,255,255,0.1);">
                <div class="flex items-center gap-3 p-3 rounded-xl" style="background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);">
                    <div id="sidebar-avatar" class="size-10 rounded-full flex items-center justify-center font-bold text-sm shrink-0 overflow-hidden" style="background:linear-gradient(135deg,#6366f1,#818cf8);color:white;border:2px solid rgba(255,255,255,0.3);"></div>
                    <div class="flex flex-col overflow-hidden min-w-0">
                        <span class="text-sm font-bold truncate text-white" id="sidebar-username">User</span>
                        <span class="text-xs truncate text-indigo-300" id="sidebar-email">user@email.com</span>
                    </div>
                </div>
                <button onclick="logout()" class="mt-3 w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-colors" style="color:#fca5a5;border:1px solid rgba(252,165,165,0.2);background:rgba(239,68,68,0.1);" onmouseover="this.style.background='rgba(239,68,68,0.2)'" onmouseout="this.style.background='rgba(239,68,68,0.1)'">
                    <span class="material-symbols-outlined text-lg">logout</span>
                    Log Out
                </button>
            </div>
        </div>
    `;
    document.body.insertBefore(aside, overlay.nextSibling);
}

/**
 * Ensures the current page's header has a hamburger button.
 * Finds the first <header> and prepends a ☰ button if missing.
 */
function ensureHamburgerButton() {
    if (document.getElementById('hamburger-btn')) return;

    const header = document.querySelector('header');
    if (!header) return;

    // Find the first child flex container, or the header itself
    const target = header.querySelector('.flex') || header;

    const btn = document.createElement('button');
    btn.id = 'hamburger-btn';
    btn.className = 'flex items-center justify-center size-10 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-700 dark:text-slate-300';
    btn.setAttribute('aria-label', 'Toggle sidebar');
    btn.onclick = toggleSidebar;
    btn.innerHTML = '<span class="material-symbols-outlined text-2xl">menu</span>';

    target.insertBefore(btn, target.firstChild);
}


/* ══════════════════════════════════════════════════════
   RENDER SIDEBAR NAVIGATION
   ══════════════════════════════════════════════════════ */

/**
 * Renders the sidebar nav links based on role.
 * Highlights the active page link.
 * @param {string} role
 */
function renderSidebar(role) {
    const navEl = document.getElementById('sidebar-nav');
    if (!navEl) return;

    const items = getSidebarLinks(role);
    const currentPath = window.location.pathname;
    navEl.innerHTML = '';

    items.forEach(item => {
        if (item.divider) {
            const hr = document.createElement('div');
            hr.className = 'my-3';
            hr.style.cssText = 'border-top: 1px solid rgba(255,255,255,0.1);';
            navEl.appendChild(hr);
            return;
        }

        const a = document.createElement('a');
        a.href = item.href;
        a.title = item.label;

        const isActive = item.href === currentPath;

        if (item.highlight) {
            // Special highlight style
            a.className = 'flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold transition-all';
            a.style.cssText = 'background:linear-gradient(135deg,#6366f1,#818cf8);color:white;';
        } else if (isActive) {
            a.className = 'flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold';
            a.style.cssText = 'background:rgba(99,102,241,0.3);color:white;border:1px solid rgba(129,140,248,0.4);';
        } else {
            a.className = 'flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all';
            a.style.cssText = 'color:rgba(199,210,254,0.85);';
            a.onmouseover = function() { this.style.background='rgba(255,255,255,0.08)'; this.style.color='white'; };
            a.onmouseout  = function() { this.style.background=''; this.style.color='rgba(199,210,254,0.85)'; };
        }

        // Build inner HTML
        let badgeHTML = '';
        if (item.badgeId) {
            badgeHTML = `<span id="${item.badgeId}" class="ml-auto hidden px-2 py-0.5 rounded-full bg-rose-500 text-white text-[10px] font-bold leading-tight"></span>`;
        }

        a.innerHTML = `
            <span class="material-symbols-outlined shrink-0 text-xl">${item.icon}</span>
            <span class="text-sm font-semibold tracking-tight">${item.label}</span>
            ${badgeHTML}
        `;

        navEl.appendChild(a);
    });
}


/* ══════════════════════════════════════════════════════
   SIDEBAR TOGGLE (Pure Overlay — No Margin Push)
   ══════════════════════════════════════════════════════ */

function openSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (sidebar) sidebar.classList.remove('-translate-x-full');
    if (overlay) overlay.classList.remove('hidden');
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (sidebar) sidebar.classList.add('-translate-x-full');
    if (overlay) overlay.classList.add('hidden');
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;
    if (sidebar.classList.contains('-translate-x-full')) {
        openSidebar();
    } else {
        closeSidebar();
    }
}

// Close sidebar on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeSidebar();
});


/* ══════════════════════════════════════════════════════
   BADGE API (for future notification/message counts)
   ══════════════════════════════════════════════════════ */

/**
 * Set a badge count on a sidebar item.
 * @param {string} badgeId - e.g. 'badge-messages'
 * @param {number} count
 */
function setSidebarBadge(badgeId, count) {
    const badge = document.getElementById(badgeId);
    if (!badge) return;
    if (count > 0) {
        badge.textContent = count > 99 ? '99+' : count;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}


/* ══════════════════════════════════════════════════════
   USER INFO HELPERS
   ══════════════════════════════════════════════════════ */

function populateSidebarUserInfo(info) {
    if (!info) return;

    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;

    // Role label
    const roleLabel = document.getElementById('sidebar-role-label');
    if (roleLabel) {
        roleLabel.textContent = info.is_staff ? '⚙ Admin Panel' : info.is_client ? '💼 Client Dashboard' : '🚀 Freelancer Hub';
    }

    // Avatar
    const initial = (info.username || 'U')[0].toUpperCase();
    const avatarHTML = info.profile_image
        ? `<img src="${info.profile_image}" alt="Profile" class="h-full w-full object-cover"/>`
        : `<span class="text-base font-bold">${initial}</span>`;

    const sidebarAvatar = document.getElementById('sidebar-avatar');
    if (sidebarAvatar) sidebarAvatar.innerHTML = avatarHTML;

    // User info text
    const nameEl = document.getElementById('sidebar-username');
    if (nameEl) nameEl.textContent = info.username || 'User';

    const emailEl = document.getElementById('sidebar-email');
    if (emailEl) emailEl.textContent = info.email || '';

    // Show user info section
    const userInfoSection = document.getElementById('sidebar-user-info');
    if (userInfoSection) userInfoSection.style.display = '';
}


/* ══════════════════════════════════════════════════════
   INITIALIZATION
   ══════════════════════════════════════════════════════ */

/**
 * Main init function. Call this on page load.
 * Injects HTML, determines role, renders nav, populates user info.
 */
async function initSidebar() {
    // 1. Inject sidebar + overlay HTML
    injectSidebarHTML();

    // 2. Ensure hamburger exists in header
    ensureHamburgerButton();

    // 3. Determine role and render
    if (typeof isLoggedIn === 'function' && isLoggedIn()) {
        // Fetch user info (uses cache from api.js)
        const info = typeof fetchUserInfo === 'function' ? await fetchUserInfo() : null;

        if (info) {
            const role = info.is_staff ? 'admin' : info.is_client ? 'client' : 'freelancer';
            renderSidebar(role);
            populateSidebarUserInfo(info);
        } else {
            // Fallback: try localStorage role
            const storedRole = localStorage.getItem('role') || 'guest';
            renderSidebar(storedRole);
        }
    } else {
        renderSidebar('guest');
    }

    // Fetch notification badge count
    if (typeof isLoggedIn === 'function' && isLoggedIn()) {
        try {
            const res = await apiCall('/notifications/unread-count/');
            if (res && res.ok) {
                const data = await res.json();
                setSidebarBadge('badge-notifications', data.unread_count || 0);
            }
        } catch (e) {
            // Silently fail — badge just stays hidden
        }
    }
}

// Auto-init when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSidebar);
} else {
    // DOM already loaded (script at bottom of body)
    initSidebar();
}
