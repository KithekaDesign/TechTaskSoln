/**
 * TechTaskSoln — Shared API Utilities
 * JWT token management, fetch wrapper, auth guards.
 */

const API_BASE = '/api';

/* ── Token helpers ── */
function getAccessToken() {
    return localStorage.getItem('access_token');
}
function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}
function setTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    if (refresh) localStorage.setItem('refresh_token', refresh);
}
function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_info');
}
function isLoggedIn() {
    return !!getAccessToken();
}
function getUserInfo() {
    try { return JSON.parse(localStorage.getItem('user_info')); } catch { return null; }
}
function setUserInfo(info) {
    localStorage.setItem('user_info', JSON.stringify(info));
}

/* ── Fetch wrapper with JWT ── */
async function apiCall(url, method = 'GET', body = null) {
    const headers = { 'Content-Type': 'application/json' };
    const token = getAccessToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);

    let response = await fetch(`${API_BASE}${url}`, opts);

    // If 401, try to refresh token once
    if (response.status === 401 && getRefreshToken()) {
        const refreshRes = await fetch(`${API_BASE}/auth/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: getRefreshToken() })
        });
        if (refreshRes.ok) {
            const data = await refreshRes.json();
            // Store both access AND the new rotated refresh token
            setTokens(data.access, data.refresh);
            headers['Authorization'] = `Bearer ${data.access}`;
            response = await fetch(`${API_BASE}${url}`, { method, headers, body: opts.body });
        } else {
            clearTokens();
            window.location.href = '/login/';
            return null;
        }
    }

    if (response.status === 401) {
        clearTokens();
        window.location.href = '/login/';
        return null;
    }

    return response;
}

/* ── Auth guard — call at top of protected pages ── */
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = '/login/';
        return false;
    }
    return true;
}

/* ── Fetch and cache user info ── */
async function fetchUserInfo() {
    const cached = getUserInfo();
    if (cached) return cached;
    const res = await apiCall('/auth/me/');
    if (res && res.ok) {
        const info = await res.json();
        setUserInfo(info);
        return info;
    }
    return null;
}

/* ── Logout ── */
async function logout() {
    const refresh = getRefreshToken();
    try {
        await fetch(`${API_BASE}/auth/logout/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAccessToken()}`
            },
            body: JSON.stringify({ refresh: refresh })
        });
    } catch (err) {
        // Network failure — still clear local tokens
        console.warn('Logout API call failed:', err);
    } finally {
        // Always clear regardless of server response
        clearTokens();
        window.location.href = '/login/';
    }
}

/* ── Alert helper ── */
function showAlert(message, type = 'error') {
    document.querySelectorAll('.api-alert').forEach(el => el.remove());

    const div = document.createElement('div');
    div.className = 'api-alert';
    const bgColor = type === 'error' ? '#fee2e2' : type === 'success' ? '#dcfce7' : '#dbeafe';
    const textColor = type === 'error' ? '#991b1b' : type === 'success' ? '#166534' : '#1e40af';
    const borderColor = type === 'error' ? '#fca5a5' : type === 'success' ? '#86efac' : '#93c5fd';
    div.style.cssText = `position:fixed;top:20px;right:20px;z-index:9999;padding:16px 24px;border-radius:12px;background:${bgColor};color:${textColor};border:1px solid ${borderColor};font-family:'Manrope',sans-serif;font-weight:600;font-size:14px;box-shadow:0 4px 12px rgba(0,0,0,0.1);max-width:400px;animation:slideIn 0.3s ease;`;
    div.textContent = message;
    document.body.appendChild(div);
    setTimeout(() => div.remove(), 5000);
}

/* ── WebSocket protocol detection ── */
function getWSProtocol() {
    return window.location.protocol === 'https:' ? 'wss:' : 'ws:';
}