<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Newton — Платформа управления</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', sans-serif; background: #f0f2f5; color: #1a1a2e; display: flex; height: 100vh; overflow: hidden; }

/* ===== LOGIN SCREEN ===== */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes floatDot {
  0%,100% { transform: translateY(0) scale(1); opacity:.18; }
  50%      { transform: translateY(-18px) scale(1.12); opacity:.32; }
}
@keyframes spinRing {
  to { transform: rotate(360deg); }
}
.login-screen {
  position: fixed; inset: 0; z-index: 9999;
  display: flex; align-items: stretch;
  background: #0b0e1a;
  font-family: 'Inter', sans-serif;
}
.login-left {
  flex: 1;
  background: linear-gradient(145deg, #0f1525 0%, #141d38 60%, #0f1525 100%);
  display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
  padding: 48px;
}
.login-dots {
  position: absolute; inset: 0; pointer-events: none;
}
.login-dot {
  position: absolute; border-radius: 50%;
  background: #4f8ef7;
  animation: floatDot var(--d,6s) ease-in-out infinite;
  animation-delay: var(--dl,0s);
}
.login-left-content {
  position: relative; z-index: 1;
  animation: fadeInUp .7s ease both;
}
.login-brand {
  display: flex; align-items: center; gap: 14px;
  margin-bottom: 48px;
}
.login-brand-icon {
  width: 52px; height: 52px; border-radius: 14px;
  background: linear-gradient(135deg,#4f8ef7,#7c5cfc);
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; font-weight: 900; color: #fff;
  box-shadow: 0 8px 32px rgba(79,142,247,.35);
}
.login-brand-name {
  font-size: 28px; font-weight: 800; color: #fff; letter-spacing: -.5px;
}
.login-tagline {
  font-size: 15px; color: #5a6a9a; margin-top: 2px; font-weight: 400;
}
.login-hero-title {
  font-size: 38px; font-weight: 800; color: #fff;
  line-height: 1.15; letter-spacing: -.8px; margin-bottom: 18px;
  max-width: 420px;
}
.login-hero-title span { color: #4f8ef7; }
.login-hero-sub {
  font-size: 15px; color: #5a6a9a; line-height: 1.6; max-width: 360px;
}
.login-stats {
  display: flex; gap: 32px; margin-top: 48px;
}
.login-stat-val {
  font-size: 24px; font-weight: 800; color: #fff;
}
.login-stat-label {
  font-size: 12px; color: #4a5a80; margin-top: 2px;
}

/* Ring decoration */
.login-ring {
  position: absolute; border-radius: 50%;
  border: 1px solid rgba(79,142,247,.1);
  pointer-events: none;
}
.login-ring-spin {
  position: absolute; border-radius: 50%;
  border: 1.5px dashed rgba(79,142,247,.15);
  animation: spinRing 18s linear infinite;
  pointer-events: none;
}

/* Right side — form */
.login-right {
  width: 460px; flex-shrink: 0;
  background: #fff;
  display: flex; align-items: center; justify-content: center;
  padding: 48px 44px;
}
.login-form-wrap {
  width: 100%;
  animation: fadeInUp .55s .1s ease both;
}
.login-form-title {
  font-size: 24px; font-weight: 800; color: #0d1117; margin-bottom: 6px;
}
.login-form-sub {
  font-size: 14px; color: #8891b0; margin-bottom: 36px;
}
.lf-group { margin-bottom: 20px; }
.lf-label {
  display: block; font-size: 12px; font-weight: 700;
  color: #4a5578; letter-spacing: .4px; text-transform: uppercase;
  margin-bottom: 7px;
}
.lf-input-wrap { position: relative; }
.lf-input-icon {
  position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
  color: #b0b8d0; display: flex; pointer-events: none;
}
.lf-input {
  width: 100%; padding: 13px 14px 13px 42px;
  border: 2px solid #e8eaf2; border-radius: 10px;
  font-size: 14px; font-family: inherit; color: #0d1117;
  background: #f8f9fc; outline: none;
  transition: border-color .2s, background .2s, box-shadow .2s;
  letter-spacing: .3px;
}
.lf-input:focus {
  border-color: #4f8ef7; background: #fff;
  box-shadow: 0 0 0 3px rgba(79,142,247,.12);
}
.lf-input.error { border-color: #ef4444; background: #fff8f8; }
.lf-input::placeholder { color: #c0c8de; }
.lf-eye {
  position: absolute; right: 13px; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer; color: #b0b8d0; padding: 4px;
  display: flex; border-radius: 6px; transition: color .15s;
}
.lf-eye:hover { color: #4f8ef7; }
.lf-hint { font-size: 11px; color: #a0a8c0; margin-top: 5px; }
.lf-hint.error-msg { color: #ef4444; display: none; }
.lf-hint.error-msg.show { display: block; }
.lf-submit {
  width: 100%; padding: 14px;
  background: linear-gradient(135deg, #4f8ef7 0%, #7c5cfc 100%);
  color: #fff; border: none; border-radius: 10px;
  font-size: 15px; font-weight: 700; letter-spacing: .2px;
  cursor: pointer; margin-top: 8px;
  transition: opacity .2s, transform .15s, box-shadow .2s;
  box-shadow: 0 4px 20px rgba(79,142,247,.3);
}
.lf-submit:hover { opacity: .92; transform: translateY(-1px); box-shadow: 0 6px 28px rgba(79,142,247,.4); }
.lf-submit:active { transform: translateY(0); }
.lf-submit.loading { opacity: .7; pointer-events: none; }
.lf-divider {
  display: flex; align-items: center; gap: 12px;
  margin: 24px 0; color: #c8cfe0; font-size: 12px;
}
.lf-divider::before, .lf-divider::after {
  content: ''; flex: 1; height: 1px; background: #e8eaf2;
}
.lf-accounts {
  display: flex; flex-direction: column; gap: 8px;
}
.lf-account-btn {
  width: 100%; padding: 10px 14px;
  border: 1.5px solid #e8eaf2; border-radius: 8px;
  background: #f8f9fc; cursor: pointer; text-align: left;
  display: flex; align-items: center; gap: 10px;
  transition: border-color .15s, background .15s;
  font-family: inherit;
}
.lf-account-btn:hover { border-color: #4f8ef7; background: #f0f5ff; }
.lf-account-role {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .4px; color: #4f8ef7;
}
.lf-account-name { font-size: 13px; color: #333; font-weight: 500; }
.lf-account-iin { font-size: 11px; color: #a0a8c0; font-family: monospace; }
.lf-account-avatar {
  width: 32px; height: 32px; border-radius: 8px;
  background: linear-gradient(135deg, #4f8ef7, #7c5cfc);
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-weight: 700; font-size: 12px; flex-shrink: 0;
}
.login-screen.hidden { display: none; }

/* SIDEBAR */
.sidebar {
  width: 260px;
  background: #fff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  flex-shrink: 0;
  z-index: 10;
}
.sidebar-logo {
  padding: 18px 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 10px;
}
.logo-icon {
  width: 40px; height: 40px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-weight: 800; font-size: 18px;
}
.logo-text { font-size: 20px; font-weight: 700; color: #111; }
.nav { flex: 1; padding: 10px 0; }
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px;
  cursor: pointer;
  color: #555;
  font-size: 13.5px;
  font-weight: 500;
  border-radius: 0;
  transition: all 0.15s;
  position: relative;
}
.nav-item:hover { background: #f5f6ff; color: #6366f1; }
.nav-item.active { background: #eef0ff; color: #6366f1; font-weight: 600; }
.nav-item.active::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: #6366f1; border-radius: 0 2px 2px 0; }
.nav-item svg { width: 18px; height: 18px; flex-shrink: 0; }
.nav-group-header {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px;
  cursor: pointer;
  color: #555;
  font-size: 13.5px;
  font-weight: 500;
  transition: all 0.15s;
  user-select: none;
}
.nav-group-header:hover { background: #f5f6ff; color: #6366f1; }
.nav-group-header svg { width: 18px; height: 18px; flex-shrink: 0; }
.nav-group-header .chevron { margin-left: auto; width: 14px; height: 14px; transition: transform 0.2s; }
.nav-group-header.open .chevron { transform: rotate(180deg); }
.nav-sub { display: none; }
.nav-sub.open { display: block; }
.nav-sub-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 16px 8px 44px;
  cursor: pointer;
  color: #666;
  font-size: 13px;
  font-weight: 400;
  transition: all 0.15s;
}
.nav-sub-item:hover { background: #f5f6ff; color: #6366f1; }
.nav-sub-item.active { background: #eef0ff; color: #6366f1; font-weight: 600; }
.nav-sub-item svg { width: 15px; height: 15px; flex-shrink: 0; }
.nav-divider { height: 1px; background: #f0f0f0; margin: 6px 0; }
.sidebar-user {
  padding: 14px 16px;
  border-top: 1px solid #e5e7eb;
  display: flex; align-items: center; gap: 10px;
}
.user-avatar {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-weight: 700; font-size: 13px;
  flex-shrink: 0;
}
.user-info { flex: 1; min-width: 0; }
.user-name { font-size: 12px; font-weight: 600; color: #111; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-meta { font-size: 11px; color: #888; }
.logout-btn {
  background: none; border: none; cursor: pointer; color: #999;
  padding: 4px; border-radius: 6px;
  transition: color 0.15s;
  display: flex;
}
.logout-btn:hover { color: #ef4444; }

/* ROLE SWITCHER */
.role-bar {
  padding: 8px 12px;
  border-bottom: 1px solid #e5e7eb;
  display: flex; gap: 6px;
}
.role-btn {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  border: 1.5px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.15s;
  background: #fff;
  color: #666;
}
.role-btn.active { background: #6366f1; border-color: #6366f1; color: #fff; }

/* MAIN */
.main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.page { display: none; flex-direction: column; flex: 1; overflow: hidden; }
.page.active { display: flex; }
.page-header {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 16px 24px;
  display: flex; align-items: center; justify-content: space-between;
  flex-shrink: 0;
}
.page-title { font-size: 20px; font-weight: 700; color: #111; }
.page-actions { display: flex; gap: 8px; align-items: center; }
.page-body { flex: 1; overflow-y: auto; padding: 20px 24px; }

/* BUTTONS */
.btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 16px; border-radius: 8px;
  font-size: 13px; font-weight: 600;
  cursor: pointer; border: none; transition: all 0.15s;
}
.btn-primary { background: #6366f1; color: #fff; }
.btn-primary:hover { background: #5558e8; }
.btn-outline { background: #fff; color: #6366f1; border: 1.5px solid #6366f1; }
.btn-outline:hover { background: #eef0ff; }
.btn-danger { background: #ef4444; color: #fff; }
.btn-danger:hover { background: #dc2626; }
.btn-sm { padding: 5px 10px; font-size: 12px; }
.btn-icon { padding: 6px; border-radius: 6px; background: none; border: 1px solid #e5e7eb; color: #666; cursor: pointer; }
.btn-icon:hover { background: #f5f5f5; }

/* SEARCH BAR */
.search-bar {
  display: flex; gap: 10px; margin-bottom: 16px;
}
.search-input {
  flex: 1;
  padding: 10px 14px 10px 38px;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  background: #fff;
  outline: none;
  position: relative;
}
.search-wrap { position: relative; flex: 1; }
.search-wrap svg { position: absolute; left: 11px; top: 50%; transform: translateY(-50%); color: #aaa; width: 16px; height: 16px; }
.search-input:focus { border-color: #6366f1; }

/* TABLE */
.table-wrap { background: #fff; border-radius: 10px; border: 1px solid #e5e7eb; overflow: hidden; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
thead th {
  background: #f9fafb;
  padding: 11px 14px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #666;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
}
tbody tr { border-bottom: 1px solid #f3f4f6; transition: background 0.1s; }
tbody tr:last-child { border-bottom: none; }
tbody tr:hover { background: #fafbff; }
tbody td { padding: 11px 14px; color: #333; }
.td-truncate { max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* BADGES */
.badge {
  display: inline-flex; align-items: center;
  padding: 3px 9px; border-radius: 20px;
  font-size: 11px; font-weight: 600;
}
.badge-active { background: #dcfce7; color: #16a34a; }
.badge-inactive { background: #f3f4f6; color: #6b7280; }
.badge-started { background: #dbeafe; color: #2563eb; }
.badge-not-started { background: #f3f4f6; color: #6b7280; }
.badge-return { background: #fee2e2; color: #dc2626; }
.badge-kaz { background: #fef3c7; color: #d97706; }
.badge-rus { background: #dbeafe; color: #2563eb; }

/* ACTION MENU */
.action-menu { position: relative; display: inline-block; }
.action-dots {
  background: none; border: none; cursor: pointer;
  padding: 4px 8px; border-radius: 6px; color: #666; font-size: 18px; line-height: 1;
}
.action-dots:hover { background: #f3f4f6; }
.action-dropdown {
  position: absolute; right: 0; top: 100%; z-index: 100;
  background: #fff; border: 1px solid #e5e7eb; border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  min-width: 160px; display: none;
}
.action-dropdown.open { display: block; }
.action-dropdown-item {
  padding: 9px 14px; font-size: 13px; cursor: pointer; color: #333;
  display: flex; align-items: center; gap: 8px;
  transition: background 0.1s;
}
.action-dropdown-item:hover { background: #f9fafb; }
.action-dropdown-item.danger { color: #ef4444; }

/* MODAL */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  z-index: 1000; display: none; align-items: center; justify-content: center;
}
.modal-overlay.open { display: flex; }
.modal {
  background: #fff; border-radius: 12px;
  padding: 24px; width: 500px; max-width: 95vw;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  max-height: 90vh; overflow-y: auto;
}
.modal-lg { width: 700px; }
.modal-title { font-size: 16px; font-weight: 700; margin-bottom: 18px; color: #111; }
.modal-footer { display: flex; gap: 8px; justify-content: flex-end; margin-top: 20px; }

/* FORM */
.form-row { display: flex; gap: 12px; margin-bottom: 14px; }
.form-group { flex: 1; display: flex; flex-direction: column; gap: 5px; }
.form-label { font-size: 12px; font-weight: 600; color: #555; }
.form-input, .form-select, .form-textarea {
  padding: 9px 12px;
  border: 1.5px solid #e5e7eb;
  border-radius: 7px;
  font-size: 13px;
  font-family: inherit;
  outline: none;
  background: #fff;
  transition: border-color 0.15s;
}
.form-input:focus, .form-select:focus, .form-textarea:focus { border-color: #6366f1; }
.form-textarea { resize: vertical; min-height: 80px; }
.form-section-title { font-size: 14px; font-weight: 700; color: #111; margin: 16px 0 10px; border-bottom: 1px solid #f0f0f0; padding-bottom: 6px; }

/* SCHEDULE */
.schedule-grid { background: #fff; border-radius: 10px; border: 1px solid #e5e7eb; overflow: auto; }
.schedule-table { border-collapse: collapse; min-width: 900px; }
.schedule-table th, .schedule-table td { border: 1px solid #e5e7eb; padding: 0; }
.sched-header { background: #f9fafb; font-size: 12px; font-weight: 700; color: #555; padding: 10px 14px; text-align: center; white-space: nowrap; }
.sched-day { background: #f9fafb; font-size: 12px; font-weight: 700; color: #444; padding: 8px 12px; white-space: nowrap; }
.sched-time { font-size: 11px; color: #888; padding: 6px 10px; white-space: nowrap; background: #fafafa; text-align: right; }
.sched-cell { min-height: 50px; padding: 4px; vertical-align: top; }
.sched-lesson {
  border-radius: 6px; padding: 6px 8px; margin: 2px;
  font-size: 11px; cursor: pointer; transition: opacity 0.15s;
}
.sched-lesson:hover { opacity: 0.85; }
.sched-lesson .lesson-name { font-weight: 700; margin-bottom: 2px; }
.sched-lesson .lesson-teacher { color: rgba(0,0,0,0.65); }
.sched-lesson .lesson-room { color: rgba(0,0,0,0.5); margin-top: 1px; }
.lesson-color-1 { background: #dcfce7; color: #166534; }
.lesson-color-2 { background: #dbeafe; color: #1e40af; }
.lesson-color-3 { background: #fef3c7; color: #92400e; }
.lesson-color-4 { background: #fce7f3; color: #9d174d; }
.lesson-color-5 { background: #ede9fe; color: #5b21b6; }
.lesson-count {
  width: 20px; height: 20px; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 700; color: #fff;
  float: right; margin-left: 4px;
}

/* ANALYTICS */
.chart-bars { display: flex; align-items: flex-end; gap: 6px; height: 200px; padding: 10px 0; }
.chart-bar-wrap { display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 1; }
.chart-bar { width: 100%; background: #6366f1; border-radius: 4px 4px 0 0; min-height: 4px; transition: background 0.15s; cursor: pointer; }
.chart-bar:hover { background: #4f46e5; }
.chart-bar-label { font-size: 10px; color: #888; }
.chart-bar-val { font-size: 10px; color: #555; font-weight: 600; }

/* TASKS */
.task-card {
  background: #fff; border-radius: 10px; border: 1px solid #e5e7eb;
  padding: 14px 18px; margin-bottom: 8px;
  display: flex; align-items: center; gap: 14px;
  transition: border-color 0.15s;
}
.task-card:hover { border-color: #c7d2fe; }
.task-info { flex: 1; }
.task-name { font-size: 14px; font-weight: 600; color: #111; margin-bottom: 4px; }
.task-type { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 500; background: #f3f4f6; color: #555; margin-bottom: 6px; }
.task-meta { font-size: 12px; color: #888; }
.task-meta span { color: #6366f1; }
.task-deadline {
  display: flex; align-items: center; gap: 5px;
  background: #fee2e2; color: #dc2626;
  padding: 4px 10px; border-radius: 20px;
  font-size: 12px; font-weight: 600;
  white-space: nowrap;
}

/* SLOTS */
.slots-table td { text-align: center; font-size: 12px; font-weight: 600; }
.slot-green { background: #dcfce7; color: #16a34a; }
.slot-red { background: #fee2e2; color: #dc2626; }
.slot-blue { background: #dbeafe; color: #2563eb; }
.slot-gray { background: #f3f4f6; color: #6b7280; }

/* MY GROUPS */
.group-card {
  background: #fff; border-radius: 10px; border: 1px solid #e5e7eb;
  margin-bottom: 10px; overflow: hidden;
}
.group-card-header {
  padding: 14px 18px; display: flex; align-items: center; gap: 14px;
  cursor: pointer; transition: background 0.1s;
}
.group-card-header:hover { background: #fafbff; }
.group-name { font-size: 14px; font-weight: 700; color: #111; }
.group-sub { font-size: 12px; color: #888; margin-top: 2px; }
.group-body { padding: 0 18px 14px; border-top: 1px solid #f3f4f6; display: none; }
.group-body.open { display: block; }
.report-table th { font-size: 11px; }
.report-table td { font-size: 12px; padding: 8px 10px; }
.attendance-btn {
  width: 28px; height: 28px; border-radius: 6px; border: 1.5px solid #e5e7eb;
  cursor: pointer; font-size: 11px; font-weight: 700;
  transition: all 0.15s; display: inline-flex; align-items: center; justify-content: center;
}
.att-present { background: #dcfce7; border-color: #86efac; color: #16a34a; }
.att-absent { background: #fee2e2; border-color: #fca5a5; color: #dc2626; }
.att-none { background: #fff; color: #ccc; }
.score-input {
  width: 50px; padding: 4px 6px; border: 1.5px solid #e5e7eb;
  border-radius: 5px; font-size: 12px; text-align: center;
}

/* TABS */
.tabs { display: flex; gap: 0; border-bottom: 2px solid #e5e7eb; margin-bottom: 16px; }
.tab-btn {
  padding: 10px 18px; font-size: 13px; font-weight: 600;
  cursor: pointer; border: none; background: none;
  color: #888; border-bottom: 2px solid transparent; margin-bottom: -2px;
  transition: all 0.15s;
}
.tab-btn.active { color: #6366f1; border-bottom-color: #6366f1; }
.tab-btn:hover { color: #6366f1; }

/* STAT CARDS */
.stat-row { display: flex; gap: 14px; margin-bottom: 20px; }
.stat-card {
  flex: 1; background: #fff; border-radius: 10px; border: 1px solid #e5e7eb;
  padding: 16px 20px;
}
.stat-label { font-size: 12px; color: #888; font-weight: 500; margin-bottom: 6px; }
.stat-value { font-size: 26px; font-weight: 800; color: #111; }
.stat-sub { font-size: 12px; color: #6366f1; margin-top: 4px; }

/* TRANSFER */
.transfer-box {
  display: flex; align-items: center; gap: 20px;
  background: #fff; border-radius: 12px; border: 1px solid #e5e7eb;
  padding: 30px;
}
.transfer-side { flex: 1; }
.transfer-arrow { font-size: 28px; color: #6366f1; flex-shrink: 0; }

/* DATE LIST */
.date-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px; background: #fff;
  border-bottom: 1px solid #f3f4f6;
}
.date-item:last-child { border-bottom: none; }

/* RETURNS */
.return-card {
  background: #fff; border-radius: 10px; border: 1px solid #e5e7eb;
  margin-bottom: 8px; overflow: hidden;
}
.return-card-row {
  display: grid; grid-template-columns: 120px 140px 100px 160px 70px 1fr;
  gap: 10px; padding: 12px 16px; align-items: start;
}
.return-label { font-size: 11px; color: #888; }
.return-val { font-size: 13px; color: #111; font-weight: 500; }
.return-reason { font-size: 12px; color: #555; line-height: 1.5; }

/* FORM HISTORY */
.history-tags { display: flex; gap: 4px; flex-wrap: wrap; }

/* EMPTY STATE */
.empty-state { text-align: center; padding: 60px 20px; color: #aaa; }
.empty-state svg { width: 48px; height: 48px; margin-bottom: 12px; opacity: 0.3; }
.empty-state p { font-size: 14px; }

/* MENTOR ASSIGN */
.mentor-select {
  padding: 6px 10px; border: 1.5px solid #e5e7eb; border-radius: 6px;
  font-size: 12px; outline: none; background: #fff; min-width: 100px;
}
.assign-btn {
  padding: 6px 12px; background: #6366f1; color: #fff;
  border: none; border-radius: 6px; font-size: 12px; font-weight: 600;
  cursor: pointer;
}
.assign-btn:hover { background: #5558e8; }
.assign-btn:disabled { background: #d1d5db; cursor: default; }

/* SCROLLBAR */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 10px; }

/* ENT PROGRESS */
.progress-bar { height: 6px; background: #e5e7eb; border-radius: 10px; overflow: hidden; }
.progress-fill { height: 100%; background: #6366f1; border-radius: 10px; }

/* FILTER TAG */
.filter-tag {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 10px; background: #eef0ff; color: #6366f1;
  border-radius: 20px; font-size: 12px; font-weight: 500;
}
</style>
</head>
<body>

<!-- ===== LOGIN SCREEN ===== -->
<div class="login-screen" id="login-screen">

  <div class="login-left">
    <div class="login-ring" style="width:320px;height:320px;bottom:-80px;left:-80px"></div>
    <div class="login-ring" style="width:200px;height:200px;top:60px;right:60px"></div>
    <div class="login-ring-spin" style="width:440px;height:440px;bottom:-140px;left:-140px"></div>
    <div class="login-dots">
      <div class="login-dot" style="width:8px;height:8px;top:18%;left:22%;--d:7s;--dl:0s"></div>
      <div class="login-dot" style="width:5px;height:5px;top:55%;left:65%;--d:9s;--dl:1.2s"></div>
      <div class="login-dot" style="width:6px;height:6px;top:75%;left:38%;--d:6s;--dl:.5s"></div>
      <div class="login-dot" style="width:10px;height:10px;top:30%;left:78%;--d:8s;--dl:2s"></div>
    </div>
    <div class="login-left-content">
      <div class="login-brand">
        <div><div class="login-brand-icon">Z</div></div>
        <div><div class="login-brand-name">ZEIN</div><div class="login-tagline">Образовательный центр</div></div>
      </div>
      <div class="login-hero-title">Платформа<br>управления<br><span>образованием</span></div>
      <div class="login-hero-sub">Единое пространство для учителей, менторов и администрации. Журнал посещений, отчёты, расписание — всё в одном месте.</div>
      <div class="login-stats">
      </div>
    </div>
  </div>

  <div class="login-right">
    <div class="login-form-wrap">
      <div class="login-form-title">Добро пожаловать</div>
      <div class="login-form-sub">Войдите используя ваш ИИН и пароль</div>
      <div class="lf-group">
        <label class="lf-label">ИИН</label>
        <div class="lf-input-wrap">
          <span class="lf-input-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="17" height="17"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg></span>
          <input class="lf-input" id="iin-input" type="text" maxlength="12" placeholder="000000000000">
        </div>
        <div class="lf-hint">12-значный индивидуальный идентификационный номер</div>
        <div class="lf-hint error-msg" id="iin-error">Введите корректный ИИН (12 цифр)</div>
      </div>
      <div class="lf-group">
        <label class="lf-label">Пароль</label>
        <div class="lf-input-wrap">
          <span class="lf-input-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="17" height="17"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg></span>
          <input class="lf-input" id="pass-input" type="password" placeholder="Введите пароль">
          <button class="lf-eye" id="eye-btn" onclick="togglePass()" type="button"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="17" height="17"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg></button>
        </div>
        <div class="lf-hint error-msg" id="pass-error">Неверный ИИН или пароль</div>
      </div>
      <button class="lf-submit" id="login-btn" onclick="doLogin()">Войти в систему</button>
      <div class="lf-divider">или войдите как</div>
      <div class="lf-accounts">
        <button class="lf-account-btn" onclick="quickLogin('admin')">
          <div class="lf-account-avatar">СТ</div>
          <div><div class="lf-account-role">Ст. тренер</div><div class="lf-account-name">Туран Сыганак Кенесары Е.</div><div class="lf-account-iin">ИИН: 900101350123</div></div>
        </button>
        <button class="lf-account-btn" onclick="quickLogin('teacher')">
          <div class="lf-account-avatar" style="background:linear-gradient(135deg,#00c896,#0099cc)">МА</div>
          <div><div class="lf-account-role" style="color:#00b386">Преподаватель</div><div class="lf-account-name">Мухамеди Айман</div><div class="lf-account-iin">ИИН: 950215450234</div></div>
        </button>
      </div>
    </div>
  </div>

</div> <!-- /login-screen -->

<!-- SIDEBAR -->
<div class="sidebar" id="sidebar" style="display:none">
  <div class="sidebar-logo">
    <div class="logo-icon">N</div>
    <div class="logo-text">newton</div>
  </div>

  <!-- Role switcher -->
  <div class="role-bar">
    <button class="role-btn active" onclick="setRole('admin')">Ст. тренер</button>
    <button class="role-btn" onclick="setRole('teacher')">Учитель</button>
  </div>

  <nav class="nav" id="nav">
    <!-- populated by JS -->
  </nav>

  <div class="sidebar-user">
    <div class="user-avatar">ТЕ</div>
    <div class="user-info">
      <div class="user-name">Туран Сыганак Кенесары Е...</div>
      <div class="user-meta">77757339394 · ID: 3361</div>
    </div>
    <button class="logout-btn" title="Выйти">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/></svg>
    </button>
  </div>
</div>

<!-- MAIN -->
<div class="main" id="main-app" style="display:none">

  <!-- ============ PAGES ============ -->

  <!-- STUDENTS -->
  <div class="page active" id="page-students">
    <div class="page-header">
      <div class="page-title">Ученики</div>
    </div>
    <div class="page-body">
      <div class="search-bar">
        <div class="search-wrap" style="flex:1">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
          <input class="search-input" placeholder="Поиск по имени, телефону...">
        </div>
        <button class="btn btn-outline" onclick="openModal('filter-modal')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="12" y1="18" x2="12" y2="18"/></svg>
          Фильтр
        </button>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Фамилия + имя</th><th>Телефон</th>
              <th>Имя родителя</th><th>Тел. родителя</th>
              <th>Филиал</th><th>Ментор</th><th>Класс</th>
              <th>Язык</th><th>Статус</th><th>Групп</th>
            </tr>
          </thead>
          <tbody id="students-tbody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- MENTORS -->
  <div class="page" id="page-mentors">
    <div class="page-header">
      <div class="page-title">Менторы</div>
      <div class="page-actions">
        <button class="btn btn-primary" onclick="openModal('add-staff-modal')">+ Добавить</button>
      </div>
    </div>
    <div class="page-body">
      <div class="search-bar">
        <div class="search-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg><input class="search-input" placeholder="Поиск..."></div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>ID</th><th>Фамилия</th><th>Имя</th><th>Телефон</th><th>Статус</th><th>Действия</th></tr></thead>
          <tbody id="mentors-tbody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- TEACHERS -->
  <div class="page" id="page-teachers">
    <div class="page-header">
      <div class="page-title">Преподаватели</div>
      <div class="page-actions"><button class="btn btn-primary" onclick="openModal('add-staff-modal')">+ Добавить</button></div>
    </div>
    <div class="page-body">
      <div class="search-bar">
        <div class="search-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg><input class="search-input" placeholder="Поиск..."></div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>ID</th><th>Фамилия</th><th>Имя</th><th>Телефон</th><th>Ставка/час</th><th>Статус</th><th>Действия</th></tr></thead>
          <tbody id="teachers-tbody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- LIDORUBY -->
  <div class="page" id="page-lidoruby">
    <div class="page-header">
      <div class="page-title">Лидорубы</div>
      <div class="page-actions"><button class="btn btn-primary" onclick="openModal('add-staff-modal')">+ Добавить</button></div>
    </div>
    <div class="page-body">
      <div class="search-bar"><div class="search-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg><input class="search-input" placeholder="Поиск..."></div></div>
      <div class="table-wrap">
        <table><thead><tr><th>ID</th><th>Фамилия</th><th>Имя</th><th>Телефон</th><th>Статус</th><th>Действия</th></tr></thead>
        <tbody id="lidoruby-tbody"></tbody></table>
      </div>
    </div>
  </div>

  <!-- MANAGERS -->
  <div class="page" id="page-managers">
    <div class="page-header">
      <div class="page-title">Менеджеры</div>
      <div class="page-actions"><button class="btn btn-primary" onclick="openModal('add-staff-modal')">+ Добавить</button></div>
    </div>
    <div class="page-body">
      <div class="search-bar"><div class="search-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg><input class="search-input" placeholder="Поиск..."></div></div>
      <div class="table-wrap">
        <table><thead><tr><th>ID</th><th>Фамилия</th><th>Имя</th><th>Телефон</th><th>Статус</th><th>Действия</th></tr></thead>
        <tbody id="managers-tbody"></tbody></table>
      </div>
    </div>
  </div>

  <!-- MENTOR ASSIGNMENT -->
  <div class="page" id="page-mentor-assign">
    <div class="page-header"><div class="page-title">Назначение менторов</div></div>
    <div class="page-body">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Фамилия + имя</th><th>Имя родителя</th><th>Класс</th><th>Язык</th><th>Филиал</th><th>Статус</th><th>Ментор</th><th>Действия</th></tr></thead>
          <tbody id="mentor-assign-tbody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- SCHEDULE -->
  <div class="page" id="page-schedule">
    <div class="page-header">
      <div class="page-title">Расписание</div>
      <div class="page-actions">
        <select class="form-select" style="font-size:13px;padding:7px 12px;min-width:150px">
          <option>Кенесары 47</option>
        </select>
        <button class="btn btn-outline">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="12" y1="18" x2="12" y2="18"/></svg>
          Фильтр
        </button>
        <button class="btn btn-primary" onclick="openModal('add-schedule-modal')">+ Добавить</button>
      </div>
    </div>
    <div class="page-body" style="padding:0">
      <div class="schedule-grid" id="schedule-grid"></div>
    </div>
  </div>

  <!-- GROUPS -->
  <div class="page" id="page-groups">
    <div class="page-header">
      <div class="page-title">Группы</div>
      <div class="page-actions">
        <button class="btn btn-outline">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="12" y1="18" x2="12" y2="18"/></svg>
          Фильтр
        </button>
        <button class="btn btn-primary" onclick="openModal('add-group-modal')">+ Добавить</button>
      </div>
    </div>
    <div class="page-body">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Название группы</th><th>ФИ преподавателя</th><th>Предмет</th><th>Филиал – Кабинет</th><th>Начало – Окончание</th><th>Дни обучения</th><th>Уч-ки</th></tr></thead>
          <tbody id="groups-tbody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- CLASSROOMS -->
  <div class="page" id="page-classrooms">
    <div class="page-header">
      <div class="page-title">Кабинеты</div>
      <div class="page-actions">
        <button class="btn btn-outline"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="12" y1="18" x2="12" y2="18"/></svg> Фильтр</button>
        <button class="btn btn-primary" onclick="openModal('add-classroom-modal')">+ Добавить</button>
      </div>
    </div>
    <div class="page-body">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Название кабинета</th><th>Филиал</th><th>Действия</th></tr></thead>
          <tbody id="classrooms-tbody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- MY TASKS -->
  <div class="page" id="page-my-tasks">
    <div class="page-header">
      <div class="page-title">Мои задачи</div>
      <div class="page-actions"><button class="btn btn-primary" onclick="openModal('add-task-modal')">+ Добавить</button></div>
    </div>
    <div class="page-body" id="my-tasks-body"></div>
  </div>

  <!-- ALL TASKS -->
  <div class="page" id="page-all-tasks">
    <div class="page-header">
      <div class="page-title">Все задачи</div>
      <div class="page-actions">
        <button class="btn btn-outline"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="12" y1="18" x2="12" y2="18"/></svg> Фильтр</button>
        <button class="btn btn-primary" onclick="openModal('add-task-modal')">+ Добавить</button>
      </div>
    </div>
    <div class="page-body" id="all-tasks-body"></div>
  </div>

  <!-- RETURNS MARK -->
  <div class="page" id="page-returns-mark">
    <div class="page-header">
      <div class="page-title">Пометка возвратов</div>
      <div class="page-actions"><button class="btn btn-outline" onclick="showPage('page-all-tasks')">Назад</button></div>
    </div>
    <div class="page-body">
      <div style="background:#fff;border-radius:10px;border:1px solid #e5e7eb;padding:24px;max-width:600px">
        <div class="form-group" style="margin-bottom:16px">
          <label class="form-label">Студент</label>
          <div class="search-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
            <input class="search-input" placeholder="Поиск студента...">
          </div>
        </div>
        <div style="text-align:right">
          <button class="btn btn-danger" disabled>Пометить как возврат</button>
        </div>
      </div>
    </div>
  </div>

  <!-- MY GROUPS (TEACHER) -->
  <div class="page" id="page-my-groups">
    <div class="page-header"><div class="page-title">Мои группы</div></div>
    <div class="page-body">
      <div class="tabs">
        <button class="tab-btn active" onclick="switchTab(this,'today')">Сегодня</button>
        <button class="tab-btn" onclick="switchTab(this,'all')">Все</button>
      </div>
      <div id="my-groups-body"></div>
    </div>
  </div>

  <!-- MY REPORTS -->
  <div class="page" id="page-my-reports">
    <div class="page-header"><div class="page-title">Мои отчеты</div></div>
    <div class="page-body">
      <div style="background:#fff;border-radius:10px;border:1px solid #e5e7eb;padding:16px;margin-bottom:16px;display:flex;gap:10px;align-items:center">
        <div class="form-group" style="margin:0">
          <label class="form-label">Дата от</label>
          <input type="date" class="form-input">
        </div>
        <div class="form-group" style="margin:0">
          <label class="form-label">Дата до</label>
          <input type="date" class="form-input">
        </div>
        <div style="display:flex;gap:8px;margin-top:18px">
          <button class="btn btn-primary"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="12" y1="18" x2="12" y2="18"/></svg> Фильтр</button>
          <button class="btn btn-outline">Очистить</button>
        </div>
      </div>
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 17H7A5 5 0 017 7h2"/><path d="M15 7h2a5 5 0 010 10h-2"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
        <p>Отчетов не найдено</p>
      </div>
    </div>
  </div>

  <!-- RETURNS LIST -->
  <div class="page" id="page-returns">
    <div class="page-header"><div class="page-title">Возвраты</div></div>
    <div class="page-body">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Создано</th><th>Ученик</th><th>Родитель</th><th>Телефон родителя</th><th>Язык</th><th>Причина</th></tr></thead>
          <tbody id="returns-tbody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- RETURN FORM -->
  <div class="page" id="page-return-form">
    <div class="page-header"><div class="page-title">Форма для передачи возврата</div></div>
    <div class="page-body">
      <div style="background:#fff;border-radius:10px;border:1px solid #e5e7eb;padding:24px;max-width:800px;margin:0 auto">
        <div class="form-section-title">Выбор ученика</div>
        <div class="form-group" style="margin-bottom:14px">
          <label class="form-label">Поиск ученика</label>
          <div class="search-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg><input class="search-input" placeholder="Поиск..."></div>
        </div>
        <div class="form-section-title">Данные родителя</div>
        <div class="form-row">
          <div class="form-group"><label class="form-label">Имя родителя *</label><input class="form-input" placeholder="Имя родителя"></div>
          <div class="form-group"><label class="form-label">WhatsApp номер родителя *</label><input class="form-input" placeholder="+77770000000"></div>
        </div>
        <div class="form-group" style="margin-bottom:14px">
          <label class="form-label">Язык общения родителя *</label>
          <select class="form-select"><option>KAZ</option><option>RUS</option></select>
        </div>
        <div class="form-section-title">Причина возврата</div>
        <div class="form-group" style="margin-bottom:14px">
          <label class="form-label">Причина *</label>
          <textarea class="form-textarea" placeholder="Опишите причину возврата..."></textarea>
        </div>
        <div style="text-align:right"><button class="btn btn-primary">Отправить форму</button></div>
      </div>
    </div>
  </div>

  <!-- FORM HISTORY -->
  <div class="page" id="page-form-history">
    <div class="page-header"><div class="page-title">История заполнения формы</div></div>
    <div class="page-body">
      <div class="table-wrap" style="overflow-x:auto">
        <table>
          <thead><tr><th>Создано</th><th>Менеджер</th><th>Ученик</th><th>Класс</th><th>Язык</th><th>Тел. ученика</th><th>Родитель</th><th>Тел. родителя</th><th>Филиал</th><th>Старт</th><th>Платн./Подар.</th></tr></thead>
          <tbody id="form-history-tbody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- NEW STUDENT -->
  <div class="page" id="page-new-student">
    <div class="page-header"><div class="page-title">Запись ученика</div></div>
    <div class="page-body">
      <div style="background:#fff;border-radius:10px;border:1px solid #e5e7eb;padding:28px;max-width:800px;margin:0 auto">
        <div class="form-section-title">Данные ученика</div>
        <div class="form-group" style="margin-bottom:14px">
          <label class="form-label">Менеджер клиента *</label>
          <select class="form-select"><option>Выберите менеджера</option><option>Калымова Еркежан</option><option>Тазабеков Олжас</option></select>
        </div>
        <div class="form-row">
          <div class="form-group"><label class="form-label">Язык обучения *</label><select class="form-select"><option>KAZ</option><option>RUS</option></select></div>
          <div class="form-group"><label class="form-label">Фамилия ученика *</label><input class="form-input" placeholder="Фамилия"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label class="form-label">Имя ученика *</label><input class="form-input" placeholder="Имя"></div>
          <div class="form-group"><label class="form-label">WhatsApp ученика</label><input class="form-input" placeholder="+7..."></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label class="form-label">WhatsApp родителя</label><input class="form-input" placeholder="+7..."></div>
          <div class="form-group"><label class="form-label">Имя родителя *</label><input class="form-input" placeholder="Имя родителя"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label class="form-label">Класс *</label><select class="form-select"><option>0</option><option>1</option><option>2</option><option>3</option><option>4</option><option>5</option><option>6</option><option>7</option><option>8</option><option>9</option><option>10</option><option>11</option></select></div>
          <div class="form-group"><label class="form-label">Филиал *</label><select class="form-select"><option>Кенесары 47</option></select></div>
        </div>
        <div class="form-section-title">Параметры обучения</div>
        <div class="form-row">
          <div class="form-group"><label class="form-label">Купил, мес. *</label><input class="form-input" type="number" placeholder="0"></div>
          <div class="form-group"><label class="form-label">Подарок, мес.</label><input class="form-input" type="number" placeholder="0"></div>
          <div class="form-group"><label class="form-label">Дата начала *</label><input class="form-input" type="date"></div>
        </div>
        <div class="form-group" style="margin-bottom:14px">
          <label class="form-label">Группы</label>
          <select class="form-select"><option>Выберите группу</option></select>
        </div>
        <div style="text-align:right"><button class="btn btn-primary">Записать ученика</button></div>
      </div>
    </div>
  </div>

  <!-- EXTENSION -->
  <div class="page" id="page-extension">
    <div class="page-header"><div class="page-title">Продление обучения</div></div>
    <div class="page-body">
      <div style="background:#fff;border-radius:10px;border:1px solid #e5e7eb;padding:28px;max-width:700px;margin:0 auto">
        <div class="form-section-title">Выбор ученика</div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Менеджер клиента *</label>
            <select class="form-select"><option>Выберите менеджера</option></select>
          </div>
        </div>
        <div class="form-group" style="margin-bottom:14px">
          <label class="form-label">Поиск пользователя</label>
          <div class="search-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg><input class="search-input" placeholder="Поиск..."></div>
        </div>
        <div class="form-section-title">Параметры обучения</div>
        <div class="form-row">
          <div class="form-group"><label class="form-label">Купил, мес. *</label><input class="form-input" type="number" placeholder="0"></div>
          <div class="form-group"><label class="form-label">Подарок, мес.</label><input class="form-input" type="number" placeholder="0"></div>
        </div>
        <div style="text-align:right;margin-top:16px"><button class="btn btn-primary">Продлить</button></div>
      </div>
    </div>
  </div>

  <!-- ANALYTICS -->
  <div class="page" id="page-analytics">
    <div class="page-header"><div class="page-title">Аналитика</div></div>
    <div class="page-body">
      <div style="background:#fff;border-radius:10px;border:1px solid #e5e7eb;padding:20px;">
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px;flex-wrap:wrap">
          <div style="font-weight:700;font-size:15px">Распределение по количеству учеников</div>
          <span style="font-size:13px;color:#666">Всего групп: <b>992</b></span>
          <span style="font-size:13px;color:#666">Средний размер: <b>6.9</b></span>
          <div style="margin-left:auto;display:flex;gap:6px">
            <button class="btn btn-primary btn-sm">Штуки</button>
            <button class="btn btn-outline btn-sm">%</button>
          </div>
        </div>
        <div id="analytics-chart"></div>
        <div style="font-size:11px;color:#aaa;margin-top:12px">Оси: по горизонтали — «Количество учеников» (0..20+), по вертикали — «Количество групп».</div>
      </div>
    </div>
  </div>

  <!-- ENT TESTS -->
  <div class="page" id="page-ent">
    <div class="page-header">
      <div class="page-title">Тесты ЕНТ</div>
      <div class="page-actions"><button class="btn btn-primary" onclick="openModal('add-ent-modal')">+ Добавить</button></div>
    </div>
    <div class="page-body">
      <div class="table-wrap">
        <table>
          <thead><tr><th>ID</th><th>Название</th><th>Статус</th><th>Прогресс</th><th>Действия</th></tr></thead>
          <tbody id="ent-tbody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- FORBIDDEN DATES -->
  <div class="page" id="page-forbidden-dates">
    <div class="page-header">
      <div class="page-title">Недоступные даты начала</div>
      <div class="page-actions"><button class="btn btn-primary" onclick="openModal('add-date-modal')">Добавить</button></div>
    </div>
    <div class="page-body">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Дата (нельзя начать)</th><th>Добавлено</th><th>Действия</th></tr></thead>
          <tbody id="forbidden-dates-tbody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- MENTOR TRANSFER -->
  <div class="page" id="page-mentor-transfer">
    <div class="page-header"><div class="page-title">Передача учеников и задач ментора</div></div>
    <div class="page-body">
      <div class="transfer-box">
        <div class="transfer-side">
          <div class="form-label" style="margin-bottom:8px">От:</div>
          <select class="form-select" style="width:100%"><option>Выберите ментора</option><option>Абди Динара</option><option>Амангелди Шуғыла</option><option>Асетова Асем</option></select>
        </div>
        <div class="transfer-arrow">→</div>
        <div class="transfer-side">
          <div class="form-label" style="margin-bottom:8px">К:</div>
          <select class="form-select" style="width:100%"><option>Выберите ментора</option><option>Абди Динара</option><option>Амангелди Шуғыла</option><option>Асетова Асем</option></select>
        </div>
      </div>
      <div style="text-align:center;margin-top:16px">
        <button class="btn btn-primary">Отправить →</button>
      </div>
    </div>
  </div>

  <!-- SLOTS -->
  <div class="page" id="page-slots">
    <div class="page-header">
      <div class="page-title">Слоты</div>
      <div class="page-actions">
        <button class="btn btn-outline"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="12" y1="18" x2="12" y2="18"/></svg> Фильтр</button>
        <button class="btn btn-primary">Управлять</button>
      </div>
    </div>
    <div class="page-body" style="padding:0">
      <div style="overflow:auto;background:#fff">
        <table class="slots-table" style="border-collapse:collapse;min-width:900px">
          <thead>
            <tr>
              <th style="padding:10px 16px;text-align:left;font-size:12px;border:1px solid #e5e7eb;background:#f9fafb">Продукт</th>
              <th style="padding:10px 16px;text-align:left;font-size:12px;border:1px solid #e5e7eb;background:#f9fafb">Язык</th>
              <th colspan="5" style="padding:10px 16px;text-align:center;font-size:12px;border:1px solid #e5e7eb;background:#f9fafb">Кенесары 47</th>
            </tr>
            <tr>
              <th style="border:1px solid #e5e7eb;padding:8px 16px;background:#f9fafb"></th>
              <th style="border:1px solid #e5e7eb;padding:8px 16px;background:#f9fafb"></th>
              <th style="border:1px solid #e5e7eb;padding:8px 16px;font-size:11px;background:#f9fafb">09:00–12:00</th>
              <th style="border:1px solid #e5e7eb;padding:8px 16px;font-size:11px;background:#f9fafb">14:30–17:30</th>
              <th style="border:1px solid #e5e7eb;padding:8px 16px;font-size:11px;background:#f9fafb">17:30–20:30</th>
              <th style="border:1px solid #e5e7eb;padding:8px 16px;font-size:11px;background:#f9fafb">ЕНТ 14:30–16:30</th>
              <th style="border:1px solid #e5e7eb;padding:8px 16px;font-size:11px;background:#f9fafb">ЕНТ 15:30–17:30</th>
            </tr>
          </thead>
          <tbody id="slots-tbody"></tbody>
        </table>
      </div>
    </div>
  </div>

</div><!-- /main -->

<!-- ============ MODALS ============ -->

<!-- ADD STAFF MODAL -->
<div class="modal-overlay" id="add-staff-modal">
  <div class="modal">
    <div class="modal-title">Добавить сотрудника</div>
    <div class="form-row">
      <div class="form-group"><label class="form-label">Фамилия *</label><input class="form-input" placeholder="Фамилия"></div>
      <div class="form-group"><label class="form-label">Имя *</label><input class="form-input" placeholder="Имя"></div>
    </div>
    <div class="form-group" style="margin-bottom:14px">
      <label class="form-label">Телефон *</label>
      <input class="form-input" placeholder="+7...">
    </div>
    <div class="form-group" style="margin-bottom:14px">
      <label class="form-label">Статус</label>
      <select class="form-select"><option>ACTIVE</option><option>INACTIVE</option></select>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" onclick="closeModal('add-staff-modal')">Отмена</button>
      <button class="btn btn-primary" onclick="closeModal('add-staff-modal')">Добавить</button>
    </div>
  </div>
</div>

<!-- ADD TASK MODAL -->
<div class="modal-overlay" id="add-task-modal">
  <div class="modal">
    <div class="modal-title">Добавить задачу</div>
    <div class="form-group" style="margin-bottom:14px">
      <label class="form-label">Ученик</label>
      <input class="form-input" placeholder="Поиск ученика...">
    </div>
    <div class="form-group" style="margin-bottom:14px">
      <label class="form-label">Тип задачи</label>
      <select class="form-select"><option>Дать регулярную ОС</option><option>Отправить на продление</option><option>Связаться с родителем</option></select>
    </div>
    <div class="form-row">
      <div class="form-group"><label class="form-label">От</label><input class="form-input" placeholder="Отправитель"></div>
      <div class="form-group"><label class="form-label">Для</label><input class="form-input" placeholder="Исполнитель"></div>
    </div>
    <div class="form-group" style="margin-bottom:14px">
      <label class="form-label">Дедлайн</label>
      <input type="date" class="form-input">
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" onclick="closeModal('add-task-modal')">Отмена</button>
      <button class="btn btn-primary" onclick="closeModal('add-task-modal')">Создать</button>
    </div>
  </div>
</div>

<!-- ADD GROUP MODAL -->
<div class="modal-overlay" id="add-group-modal">
  <div class="modal modal-lg">
    <div class="modal-title">Добавить группу</div>
    <div class="form-row">
      <div class="form-group"><label class="form-label">Название группы *</label><input class="form-input" placeholder="5 коу A1"></div>
      <div class="form-group"><label class="form-label">Предмет *</label><select class="form-select"><option>Математика и логика</option><option>Русский язык</option><option>Английский язык</option><option>Физика</option><option>Алгебра и геометрия</option></select></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label class="form-label">Преподаватель *</label><select class="form-select"><option>Выберите преподавателя</option></select></div>
      <div class="form-group"><label class="form-label">Филиал *</label><select class="form-select"><option>Кенесары 47</option></select></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label class="form-label">Кабинет *</label><select class="form-select"><option>101</option><option>102</option><option>103</option></select></div>
      <div class="form-group"><label class="form-label">Начало</label><input type="time" class="form-input" value="09:00"></div>
      <div class="form-group"><label class="form-label">Окончание</label><input type="time" class="form-input" value="10:00"></div>
    </div>
    <div class="form-group" style="margin-bottom:14px">
      <label class="form-label">Дни обучения</label>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:4px">
        <label style="display:flex;align-items:center;gap:4px;font-size:13px"><input type="checkbox"> ПН</label>
        <label style="display:flex;align-items:center;gap:4px;font-size:13px"><input type="checkbox"> ВТ</label>
        <label style="display:flex;align-items:center;gap:4px;font-size:13px"><input type="checkbox"> СР</label>
        <label style="display:flex;align-items:center;gap:4px;font-size:13px"><input type="checkbox"> ЧТ</label>
        <label style="display:flex;align-items:center;gap:4px;font-size:13px"><input type="checkbox"> ПТ</label>
        <label style="display:flex;align-items:center;gap:4px;font-size:13px"><input type="checkbox"> СБ</label>
        <label style="display:flex;align-items:center;gap:4px;font-size:13px"><input type="checkbox"> ВС</label>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" onclick="closeModal('add-group-modal')">Отмена</button>
      <button class="btn btn-primary" onclick="closeModal('add-group-modal')">Создать группу</button>
    </div>
  </div>
</div>

<!-- ADD CLASSROOM MODAL -->
<div class="modal-overlay" id="add-classroom-modal">
  <div class="modal">
    <div class="modal-title">Добавить кабинет</div>
    <div class="form-group" style="margin-bottom:14px"><label class="form-label">Название кабинета *</label><input class="form-input" placeholder="101"></div>
    <div class="form-group" style="margin-bottom:14px"><label class="form-label">Филиал *</label><select class="form-select"><option>Кенесары 47</option></select></div>
    <div class="modal-footer">
      <button class="btn btn-outline" onclick="closeModal('add-classroom-modal')">Отмена</button>
      <button class="btn btn-primary" onclick="closeModal('add-classroom-modal')">Добавить</button>
    </div>
  </div>
</div>

<!-- ADD SCHEDULE MODAL -->
<div class="modal-overlay" id="add-schedule-modal">
  <div class="modal">
    <div class="modal-title">Добавить урок в расписание</div>
    <div class="form-row">
      <div class="form-group"><label class="form-label">День *</label>
        <select class="form-select"><option>ПН</option><option>ВТ</option><option>СР</option><option>ЧТ</option><option>ПТ</option><option>СБ</option><option>ВС</option></select>
      </div>
      <div class="form-group"><label class="form-label">Время *</label><input type="time" class="form-input" value="09:00"></div>
    </div>
    <div class="form-group" style="margin-bottom:14px"><label class="form-label">Группа *</label><select class="form-select"><option>5 коу A1</option><option>2–3 коу C1</option></select></div>
    <div class="form-group" style="margin-bottom:14px"><label class="form-label">Кабинет *</label><select class="form-select"><option>101</option><option>102</option><option>103</option></select></div>
    <div class="modal-footer">
      <button class="btn btn-outline" onclick="closeModal('add-schedule-modal')">Отмена</button>
      <button class="btn btn-primary" onclick="closeModal('add-schedule-modal')">Добавить</button>
    </div>
  </div>
</div>

<!-- FILTER MODAL -->
<div class="modal-overlay" id="filter-modal">
  <div class="modal">
    <div class="modal-title">Фильтр учеников</div>
    <div class="form-row">
      <div class="form-group"><label class="form-label">Филиал</label><select class="form-select"><option>Все</option><option>Кенесары 47</option></select></div>
      <div class="form-group"><label class="form-label">Ментор</label><select class="form-select"><option>Все</option></select></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label class="form-label">Класс</label><select class="form-select"><option>Все</option><option>1</option><option>2</option><option>3</option><option>4</option><option>5</option><option>6</option><option>7</option><option>8</option><option>9</option><option>10</option><option>11</option></select></div>
      <div class="form-group"><label class="form-label">Язык</label><select class="form-select"><option>Все</option><option>KAZ</option><option>RUS</option></select></div>
    </div>
    <div class="form-group" style="margin-bottom:14px"><label class="form-label">Статус</label><select class="form-select"><option>Все</option><option>ACTIVE</option><option>INACTIVE</option><option>NOT_STARTED</option></select></div>
    <div class="modal-footer">
      <button class="btn btn-outline" onclick="closeModal('filter-modal')">Очистить</button>
      <button class="btn btn-primary" onclick="closeModal('filter-modal')">Применить</button>
    </div>
  </div>
</div>

<!-- ADD DATE MODAL -->
<div class="modal-overlay" id="add-date-modal">
  <div class="modal">
    <div class="modal-title">Добавить недоступную дату</div>
    <div class="form-group" style="margin-bottom:14px"><label class="form-label">Дата *</label><input type="date" class="form-input"></div>
    <div class="modal-footer">
      <button class="btn btn-outline" onclick="closeModal('add-date-modal')">Отмена</button>
      <button class="btn btn-primary" onclick="closeModal('add-date-modal')">Добавить</button>
    </div>
  </div>
</div>

<!-- ADD ENT MODAL -->
<div class="modal-overlay" id="add-ent-modal">
  <div class="modal">
    <div class="modal-title">Добавить тест ЕНТ</div>
    <div class="form-group" style="margin-bottom:14px"><label class="form-label">Название *</label><input class="form-input" placeholder="Вариант 1 КО"></div>
    <div class="form-group" style="margin-bottom:14px"><label class="form-label">Статус</label><select class="form-select"><option>ACTIVE</option><option>INACTIVE</option></select></div>
    <div class="modal-footer">
      <button class="btn btn-outline" onclick="closeModal('add-ent-modal')">Отмена</button>
      <button class="btn btn-primary" onclick="closeModal('add-ent-modal')">Добавить</button>
    </div>
  </div>
</div>

<!-- REPORT MODAL -->
<div class="modal-overlay" id="report-modal">
  <div class="modal modal-lg">
    <div class="modal-title" id="report-modal-title">Отчет — 5 коу A1 — Понедельник 09:00</div>
    <div class="table-wrap">
      <table class="report-table">
        <thead><tr><th>Ученик</th><th>Присутствие</th><th>Балл за урок</th><th>Балл за д/з</th></tr></thead>
        <tbody>
          <tr>
            <td>Иванов Алексей</td>
            <td>
              <button class="attendance-btn att-present" onclick="toggleAttendance(this)">✓</button>
            </td>
            <td><input class="score-input" type="number" min="0" max="10" placeholder="—"></td>
            <td><input class="score-input" type="number" min="0" max="10" placeholder="—"></td>
          </tr>
          <tr>
            <td>Петрова Мария</td>
            <td><button class="attendance-btn att-absent" onclick="toggleAttendance(this)">✗</button></td>
            <td><input class="score-input" type="number" min="0" max="10" placeholder="—"></td>
            <td><input class="score-input" type="number" min="0" max="10" placeholder="—"></td>
          </tr>
          <tr>
            <td>Сидоров Дмитрий</td>
            <td><button class="attendance-btn att-none" onclick="toggleAttendance(this)">?</button></td>
            <td><input class="score-input" type="number" min="0" max="10" placeholder="—"></td>
            <td><input class="score-input" type="number" min="0" max="10" placeholder="—"></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="form-group" style="margin:14px 0 0">
      <label class="form-label">Комментарий к уроку</label>
      <textarea class="form-textarea" placeholder="Тема урока, замечания..."></textarea>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" onclick="closeModal('report-modal')">Отмена</button>
      <button class="btn btn-primary" onclick="closeModal('report-modal')">Сохранить отчет</button>
    </div>
  </div>
</div>

<script>
// ===================== DATA =====================
const students = [
  {id:'3...',name:'? Ангелина',phone:'+8778779...',parent:'Руслан',parentPhone:'+8778779...',branch:'Сыгана...',mentor:'Елубай...',grade:11,lang:'RUS',status:'INACTIVE',groups:0},
  {id:'3...',name:'+77477034635...',phone:'+7747703...',parent:'Мархаба',parentPhone:'+7747703...',branch:'Керей ...',mentor:'Серікба...',grade:10,lang:'KAZ',status:'ACTIVE',groups:2},
  {id:41,name:'PRODUCTION',phone:'+7747592*...',parent:'—',parentPhone:'+7747592...',branch:'Мангил...',mentor:'Еденба...',grade:8,lang:'KAZ',status:'INACTIVE',groups:0},
  {id:'1...',name:'PRODUCTION A...',phone:'+000000...',parent:'Parent #2',parentPhone:'+7777309...',branch:'Сыгана...',mentor:'Асетов...',grade:6,lang:'KAZ',status:'INACTIVE',groups:0},
  {id:76,name:'Student #1 Testi...',phone:'+000000...',parent:'Родитель',parentPhone:'+7747592...',branch:'Туран 16',mentor:'Маряк ...',grade:8,lang:'KAZ',status:'INACTIVE',groups:0},
  {id:77,name:'Student #2 Test...',phone:'+000000...',parent:'Родитель ...',parentPhone:'+7777309...',branch:'Мангил...',mentor:'Дворни...',grade:8,lang:'RUS',status:'ACTIVE',groups:0},
  {id:'2...',name:'Test Test',phone:'+7747592...',parent:'TestParent',parentPhone:'+7705392...',branch:'Керей ...',mentor:'Серікба...',grade:7,lang:'KAZ',status:'INACTIVE',groups:0},
  {id:'3...',name:'Testing Test',phone:'+7747592...',parent:'TestParent',parentPhone:'+7705392...',branch:'Сыгана...',mentor:'Асетов...',grade:3,lang:'KAZ',status:'INACTIVE',groups:0},
];

const mentors = [
  {id:3147,lastName:'Абди',firstName:'Динара',phone:'+77051186574',status:'ACTIVE'},
  {id:3449,lastName:'Амангелді',firstName:'Шуғыла',phone:'+77766149564',status:'ACTIVE'},
  {id:2990,lastName:'Асетова',firstName:'Асем',phone:'+77779795816',status:'ACTIVE'},
  {id:2051,lastName:'Аханова',firstName:'Дильнур',phone:'+77713651455',status:'INACTIVE'},
  {id:1638,lastName:'Ахмедова',firstName:'Балжан',phone:'+77018387104',status:'INACTIVE'},
  {id:17,lastName:'Әлімхан',firstName:'Саулехан',phone:'+77072668131',status:'INACTIVE'},
  {id:2728,lastName:'Галиева',firstName:'Адэля',phone:'+77001888033',status:'ACTIVE'},
  {id:16,lastName:'Дворниченко',firstName:'Лаура',phone:'+77472220142',status:'ACTIVE'},
];

const teachers = [
  {id:201,lastName:'Бердбеков',firstName:'Арыстан',phone:'+77051111111',rate:1500,status:'ACTIVE'},
  {id:202,lastName:'Өтеген',firstName:'Әлішер',phone:'+77052222222',rate:1800,status:'ACTIVE'},
  {id:203,lastName:'Мараткызы',firstName:'Акбота',phone:'+77053333333',rate:1500,status:'ACTIVE'},
  {id:204,lastName:'Сабырова',firstName:'Аружан',phone:'+77054444444',rate:1600,status:'ACTIVE'},
  {id:205,lastName:'Куат',firstName:'Дина',phone:'+77055555555',rate:1700,status:'INACTIVE'},
  {id:206,lastName:'Багиткалиева',firstName:'Альбина',phone:'+77056666666',rate:1500,status:'ACTIVE'},
];

const lidoruby = [
  {id:301,lastName:'Нурланова',firstName:'Айгерим',phone:'+77061111111',status:'ACTIVE'},
  {id:302,lastName:'Сейткали',firstName:'Ербол',phone:'+77062222222',status:'ACTIVE'},
];

const managers = [
  {id:401,lastName:'Калымова',firstName:'Еркежан',phone:'+77071111111',status:'ACTIVE'},
  {id:402,lastName:'Тазабеков',firstName:'Олжас',phone:'+77072222222',status:'ACTIVE'},
  {id:403,lastName:'Имангазиев',firstName:'Искандер',phone:'+77073333333',status:'ACTIVE'},
];

const groups = [
  {name:'8 роу C1',teacher:'Бердбеков Арыстан',subject:'Физика',branch:'Туран 16',room:'3036',start:'09:00',end:'10:00',days:'ПН, СР, ПТ',students:2},
  {name:'8 роу C1',teacher:'Өтеген Әлішер',subject:'Алгебра и геометрия',branch:'Туран 16',room:'3036',start:'10:00',end:'11:00',days:'ПН, СР, ПТ',students:2},
  {name:'8 роу C1',teacher:'Мараткызы Акбота',subject:'Английский язык',branch:'Туран 16',room:'3036',start:'11:00',end:'12:00',days:'ПН, СР, ПТ',students:2},
  {name:'7 роу C1',teacher:'Сабырова Аружан',subject:'Английский язык',branch:'Туран 16',room:'401а',start:'09:00',end:'10:00',days:'ПН, СР, ПТ',students:7},
  {name:'7 роу C1',teacher:'Куат Дина',subject:'Алгебра и геометрия',branch:'Туран 16',room:'401а',start:'10:00',end:'11:00',days:'ПН, СР, ПТ',students:8},
  {name:'7 роу C1',teacher:'Багиткалиева Альбина',subject:'Физика',branch:'Туран 16',room:'401а',start:'11:00',end:'12:00',days:'ПН, СР, ПТ',students:8},
  {name:'5 коу A1',teacher:'Мухамеди Айман',subject:'Математика и логика',branch:'Кенесары 47',room:'101',start:'09:00',end:'10:00',days:'ПН, СР, ПТ',students:11},
  {name:'2–3 коу C1',teacher:'Амангелдиева Салтанат',subject:'Русский язык',branch:'Кенесары 47',room:'102',start:'09:00',end:'10:00',days:'ПН, СР, ПТ',students:9},
];

const classrooms = [
  {name:'200-А',branch:'Туран 16'},{name:'201а',branch:'Туран 16'},
  {name:'201б',branch:'Туран 16'},{name:'202',branch:'Туран 16'},
  {name:'202а',branch:'Туран 16'},{name:'202б',branch:'Туран 16'},
  {name:'203а',branch:'Туран 16'},{name:'203б',branch:'Туран 16'},
  {name:'205а',branch:'Туран 16'},{name:'205б',branch:'Туран 16'},
  {name:'101',branch:'Кенесары 47'},{name:'102',branch:'Кенесары 47'},
  {name:'103',branch:'Кенесары 47'},{name:'104',branch:'Кенесары 47'},
];

const tasks = [
  {student:'Айболат Айдан',type:'Дать регулярную ОС',from:'Маликова Томирис',to:'Абди Динара',deadline:'18.03.2026',done:false},
  {student:'Матенов Алтаир',type:'Дать регулярную ОС',from:'Маликова Томирис',to:'Маликова Томирис',deadline:'19.03.2026',done:false},
  {student:'Әбдіжүсіп Бейбіт',type:'Отправить на продление',from:'Асылхан (БОТ)',to:'Абди Динара',deadline:'21.03.2026',done:false},
  {student:'Уалихан Улан',type:'Связаться с родителем',from:'Система',to:'Дворниченко Лаура',deadline:'24.03.2026',done:false},
];

const returns = [
  {created:'26.03.2026 16:15',student:'Русланкызы Аяннур',parent:'Гульмира',parentPhone:'+77072495937',lang:'KAZ',reason:'заболели на кенесары из-за холода'},
  {created:'26.03.2026 15:52',student:'Османов Аслан',parent:'Нурсултан',parentPhone:'+77083312074',lang:'RUS',reason:'Отец говорит семейные обстоятельства, больше ничего не сказал и сразу твердо решили возврат'},
  {created:'26.03.2026 15:50',student:'Куанышев Самир',parent:'Алия',parentPhone:'+77028296601',lang:'RUS',reason:'Заявление написала 20го марта. Они были один день на Туране, один день на Мангилик. В итоге не понравилось'},
];

const formHistory = [
  {created:'29.03.2026 14:50',manager:'Калымова Еркежан',student:'Ибрашев Абдулъуаххаб',grade:7,lang:'KAZ',studentPhone:'+87477775153',parent:'Акмоншак',parentPhone:'+87476033790',branch:'Кенесары 47',start:'01.04.2026',payment:'10/4'},
  {created:'29.03.2026 14:19',manager:'Калымова Еркежан',student:'Ибрашев Ибрахим',grade:4,lang:'RUS',studentPhone:'+87476033790',parent:'Акмоншак',parentPhone:'+87476033790',branch:'Кенесары 47',start:'01.04.2026',payment:'7/7'},
  {created:'28.03.2026 18:25',manager:'Калымова Еркежан',student:'Талапулы Рахат',grade:9,lang:'KAZ',studentPhone:'+870066554 29',parent:'Индира',parentPhone:'+87778853130',branch:'Сыганак 17ф',start:'13.04.2026',payment:'2/1'},
  {created:'28.03.2026 18:22',manager:'Тазабеков Олжас',student:'Хамитов Нурали',grade:5,lang:'RUS',studentPhone:'+777866140 86',parent:'Бауыржан',parentPhone:'+77017749409',branch:'Сыганак 17ф',start:'01.04.2026',payment:'4/3'},
];

const entTests = [
  {id:2,name:'Вариант 1 КО (демо)',status:'ACTIVE',progress:100},
  {id:1,name:'Вариант 1 РО (демо)',status:'INACTIVE',progress:9},
  {id:3,name:'Вариант 2 КО',status:'ACTIVE',progress:100},
  {id:4,name:'Вариант 2 РО',status:'ACTIVE',progress:100},
  {id:6,name:'Вариант 3 КО',status:'ACTIVE',progress:100},
  {id:5,name:'Вариант 3 РО',status:'ACTIVE',progress:100},
  {id:7,name:'Вариант 4 РО',status:'ACTIVE',progress:100},
  {id:8,name:'Вариант 4КО',status:'ACTIVE',progress:100},
];

const forbiddenDates = [
  {date:'2026-03-25',added:'02.03.2026, 18:33:33'},
  {date:'2026-03-24',added:'02.03.2026, 18:33:33'},
  {date:'2026-03-23',added:'02.03.2026, 18:33:33'},
  {date:'2026-03-22',added:'02.03.2026, 18:33:33'},
  {date:'2026-03-21',added:'02.03.2026, 18:33:33'},
  {date:'2026-03-09',added:'23.02.2026, 15:31:51'},
  {date:'2026-01-07',added:'27.10.2025, 11:51:52'},
  {date:'2026-01-03',added:'27.10.2025, 11:51:10'},
  {date:'2026-01-02',added:'27.10.2025, 11:51:10'},
  {date:'2026-01-01',added:'27.10.2025, 11:51:10'},
];

const assignStudents = [
  {name:'Береген Амина',parent:'Айгуль',grade:5,lang:'RUS',branch:'Кенесары 47',status:'NOT_STARTED'},
  {name:'Ибрашев Абдулъуаххаб',parent:'Акмоншак',grade:7,lang:'KAZ',branch:'Кенесары 47',status:'NOT_STARTED'},
  {name:'Ибрашев Ибрахим',parent:'Акмоншак',grade:4,lang:'RUS',branch:'Кенесары 47',status:'NOT_STARTED'},
  {name:'Куанышбек Али',parent:'Индира',grade:10,lang:'KAZ',branch:'Керей Жанибек хандар 28',status:'NOT_STARTED'},
  {name:'Кулантай Аружан',parent:'Лязаат',grade:5,lang:'KAZ',branch:'Туран 16',status:'NOT_STARTED'},
  {name:'Муканова Мерей',parent:'Динара',grade:10,lang:'RUS',branch:'Сыганак 17ф',status:'NOT_STARTED'},
];

const slotsData = [
  {grade:0,kaz:['3/6','0/0','0/0','0/0','0/0'],rus:['0/0','0/6','0/0','0/0','0/0']},
  {grade:1,kaz:['0/6','0/0','0/0','0/0','0/0'],rus:['0/0','2/6','0/0','0/0','0/0']},
  {grade:2,kaz:['1/6','0/6','0/0','0/0','0/0'],rus:['1/6','1/12','0/0','0/0','0/0']},
  {grade:3,kaz:['7/6','2/6','0/0','0/0','0/0'],rus:['3/6','3/0','0/0','0/0','0/0']},
  {grade:4,kaz:['1/12','5/0','0/0','0/0','0/0'],rus:['5/12','7/12','0/0','0/0','0/0']},
  {grade:5,kaz:['24/24','5/12','0/0','0/0','0/0'],rus:['26/24','7/6','0/0','0/0','0/0']},
  {grade:6,kaz:['29/24','0/24','0/0','0/0','0/0'],rus:['18/24','3/12','0/0','0/0','0/0']},
];

// ===================== NAV CONFIG =====================
const adminNav = [
  {id:'students',label:'Ученики',icon:'users'},
  {id:'staff',label:'Сотрудники',icon:'briefcase',children:[
    {id:'mentors',label:'Менторы',icon:'shield'},
    {id:'teachers',label:'Преподаватели',icon:'book-open'},
    {id:'lidoruby',label:'Лидорубы',icon:'zap'},
    {id:'managers',label:'Менеджеры',icon:'bar-chart'},
  ]},
  {id:'mentor-assign',label:'Назначение менторов',icon:'user-check'},
  {id:'schedule',label:'Расписание',icon:'calendar'},
  {id:'groups',label:'Группы',icon:'users-2'},
  {id:'classrooms',label:'Кабинеты',icon:'door-open'},
  {id:'my-tasks',label:'Мои задачи',icon:'check-circle'},
  {id:'all-tasks',label:'Все задачи',icon:'list-checks'},
  {id:'returns-mark',label:'Пометка возвратов',icon:'arrow-left-circle'},
  {divider:true},
  {id:'my-groups',label:'Мои группы',icon:'users-round'},
  {id:'my-reports',label:'Мои отчеты',icon:'file-text'},
  {id:'returns',label:'Возвраты',icon:'rotate-ccw'},
  {id:'return-form',label:'Форма возврата',icon:'clipboard'},
  {id:'form-history',label:'История заполнения формы',icon:'history'},
  {id:'new-student',label:'Новый ученик',icon:'user-plus'},
  {id:'extension',label:'Продление обучения',icon:'refresh-cw'},
  {id:'analytics',label:'Аналитика',icon:'trending-up'},
  {id:'ent',label:'Тесты ЕНТ',icon:'help-circle'},
  {id:'forbidden-dates',label:'Недоступные даты',icon:'calendar-x'},
  {id:'mentor-transfer',label:'Передача работы',icon:'arrow-right-left'},
  {id:'slots',label:'Слоты',icon:'grid'},
];

const teacherNav = [
  {id:'my-groups',label:'Мои группы',icon:'users-round'},
  {id:'my-reports',label:'Мои отчеты',icon:'file-text'},
];

// ===================== ICONS =====================
function icon(name) {
  const icons = {
    'users':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>',
    'briefcase':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/><line x1="12" y1="12" x2="12" y2="12"/></svg>',
    'shield':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="15" height="15"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    'book-open':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="15" height="15"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>',
    'zap':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="15" height="15"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    'bar-chart':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="15" height="15"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>',
    'user-check':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/></svg>',
    'calendar':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    'users-2':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M14 19a6 6 0 00-12 0"/><circle cx="8" cy="9" r="4"/><path d="M22 19a6 6 0 00-6-6 4 4 0 000-8"/></svg>',
    'door-open':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M13 4h3a2 2 0 012 2v14"/><path d="M2 20h3"/><path d="M13 20h9"/><path d="M10 12v.01"/><path d="M13 4l-6 2v14l6 2V4z"/></svg>',
    'check-circle':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    'list-checks':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><line x1="10" y1="6" x2="21" y2="6"/><line x1="10" y1="12" x2="21" y2="12"/><line x1="10" y1="18" x2="21" y2="18"/><polyline points="3 6 4 7 6 5"/><polyline points="3 12 4 13 6 11"/><polyline points="3 18 4 19 6 17"/></svg>',
    'arrow-left-circle':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><circle cx="12" cy="12" r="10"/><polyline points="12 8 8 12 12 16"/><line x1="16" y1="12" x2="8" y2="12"/></svg>',
    'users-round':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M18 21a8 8 0 10-16 0"/><circle cx="10" cy="8" r="5"/><path d="M22 21a8 8 0 00-4.3-7.1"/><circle cx="20" cy="7" r="3"/></svg>',
    'file-text':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
    'rotate-ccw':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 102.13-9.36L1 10"/></svg>',
    'clipboard':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>',
    'history':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 102.13-9.36L1 10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="12" x2="16" y2="14"/></svg>',
    'user-plus':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>',
    'refresh-cw':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg>',
    'trending-up':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    'help-circle':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    'calendar-x':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><line x1="10" y1="14" x2="14" y2="18"/><line x1="14" y1="14" x2="10" y2="18"/></svg>',
    'arrow-right-left':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 014-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 01-4 4H3"/></svg>',
    'grid':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
    'trash':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>',
    'edit':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
  };
  return icons[name] || '';
}

// ===================== RENDER =====================
function renderNav(role) {
  const nav = document.getElementById('nav');
  const items = role === 'admin' ? adminNav : teacherNav;
  nav.innerHTML = '';
  items.forEach(item => {
    if (item.divider) {
      nav.innerHTML += '<div class="nav-divider"></div>';
      return;
    }
    if (item.children) {
      nav.innerHTML += `
        <div class="nav-group-header" onclick="toggleGroup(this)" id="group-${item.id}">
          ${icon(item.icon)}<span>${item.label}</span>
          <svg class="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
        </div>
        <div class="nav-sub" id="sub-${item.id}">
          ${item.children.map(c=>`<div class="nav-sub-item" onclick="showPage('page-${c.id}')" id="nav-${c.id}">${icon(c.icon)}<span>${c.label}</span></div>`).join('')}
        </div>`;
    } else {
      nav.innerHTML += `<div class="nav-item" onclick="showPage('page-${item.id}')" id="nav-${item.id}">${icon(item.icon)}<span>${item.label}</span></div>`;
    }
  });
}

function populateStudents() {
  document.getElementById('students-tbody').innerHTML = students.map(s=>`
    <tr>
      <td class="td-truncate">${s.id}</td>
      <td class="td-truncate">${s.name}</td>
      <td class="td-truncate">${s.phone}</td>
      <td>${s.parent}</td>
      <td class="td-truncate">${s.parentPhone}</td>
      <td class="td-truncate">${s.branch}</td>
      <td class="td-truncate">${s.mentor}</td>
      <td>${s.grade}</td>
      <td><span class="badge ${s.lang==='KAZ'?'badge-kaz':'badge-rus'}">${s.lang}</span></td>
      <td><span class="badge ${s.status==='ACTIVE'?'badge-active':'badge-inactive'}">${s.status.substring(0,2)}...</span></td>
      <td>${s.groups}</td>
    </tr>`).join('');
}

function populateStaff(tbodyId, data, extraCol) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  tbody.innerHTML = data.map(s=>`
    <tr>
      <td>${s.id}</td>
      <td>${s.lastName}</td>
      <td>${s.firstName}</td>
      <td>${s.phone}</td>
      ${extraCol ? `<td>${s.rate?.toLocaleString()} ₸/ч</td>` : ''}
      <td><span class="badge ${s.status==='ACTIVE'?'badge-active':'badge-inactive'}">${s.status}</span></td>
      <td>
        <div class="action-menu">
          <button class="action-dots" onclick="toggleMenu(this)">⋮</button>
          <div class="action-dropdown">
            <div class="action-dropdown-item">${icon('edit')} Редактировать</div>
            ${extraCol ? '<div class="action-dropdown-item">💰 Изменить ставку</div>' : ''}
            <div class="action-dropdown-item danger">${icon('trash')} Деактивировать</div>
          </div>
        </div>
      </td>
    </tr>`).join('');
}

function populateMentorAssign() {
  document.getElementById('mentor-assign-tbody').innerHTML = assignStudents.map(s=>`
    <tr>
      <td>${s.name}</td>
      <td>${s.parent}</td>
      <td>${s.grade}</td>
      <td><span class="badge ${s.lang==='KAZ'?'badge-kaz':'badge-rus'}">${s.lang}</span></td>
      <td class="td-truncate">${s.branch}</td>
      <td><span class="badge badge-not-started">${s.status}</span></td>
      <td>
        <select class="mentor-select">
          <option>Мент...</option>
          ${mentors.map(m=>`<option>${m.lastName} ${m.firstName}</option>`).join('')}
        </select>
      </td>
      <td><button class="assign-btn">Назначить</button></td>
    </tr>`).join('');
}

function buildSchedule() {
  const days = ['ПН','ВТ','СР','ЧТ','ПТ','СБ'];
  const times = [];
  for(let h=7;h<=20;h++){times.push(`${String(h).padStart(2,'0')}:00`);times.push(`${String(h).padStart(2,'0')}:30`);}
  const rooms = ['101','102','103','104','105','106'];
  const colors = ['lesson-color-1','lesson-color-2','lesson-color-3','lesson-color-4','lesson-color-5'];
  const lessons = [
    {day:'ПН',time:'09:00',room:'101',name:'5 коу A1',teacher:'Мухамеди Айман',subject:'Математика и логика',count:11,color:0},
    {day:'ПН',time:'09:00',room:'102',name:'2–3 коу C1',teacher:'Амангелдиева Салтанат',subject:'Русский язык',count:9,color:1},
    {day:'ПН',time:'09:00',room:'103',name:'0–1 коу C1',teacher:'Турар Нурзада',subject:'Грамотность чтения',count:4,color:2},
    {day:'ПН',time:'09:00',room:'104',name:'5 коу B1',teacher:'Бекбаева Аружан',subject:'Русский язык',count:12,color:3},
    {day:'ПН',time:'09:00',room:'105',name:'6 коу A1',teacher:'Кожанова Улжан',subject:'Английский язык',count:8,color:4},
    {day:'ПН',time:'10:00',room:'101',name:'5 коу A1',teacher:'Бекбаева Аружан',subject:'Русский язык',count:11,color:0},
    {day:'ПН',time:'10:00',room:'102',name:'2–3 коу C1',teacher:'Орынбекова Алтынай',subject:'Математика и логика',count:9,color:1},
    {day:'ПН',time:'10:00',room:'103',name:'0–1 коу C1',teacher:'Турар Нурзада',subject:'Каллиграфия',count:4,color:2},
    {day:'ВТ',time:'09:00',room:'101',name:'7 роу C1',teacher:'Куат Дина',subject:'Алгебра',count:8,color:1},
    {day:'ВТ',time:'10:00',room:'102',name:'8 роу C1',teacher:'Бердбеков Арыстан',subject:'Физика',count:5,color:3},
    {day:'СР',time:'09:00',room:'101',name:'5 коу A1',teacher:'Фаизуллина Камилла',subject:'Английский язык',count:11,color:4},
    {day:'СР',time:'11:00',room:'103',name:'0–1 коу C1',teacher:'Турар Нурзада',subject:'Математика и логика',count:4,color:2},
  ];

  let html = `<table class="schedule-table"><thead><tr>
    <th class="sched-header" style="min-width:50px">ДЕНЬ</th>
    <th class="sched-header" style="min-width:60px">ВРЕМЯ</th>
    ${rooms.map(r=>`<th class="sched-header" style="min-width:140px">${r}</th>`).join('')}
  </tr></thead><tbody>`;

  days.forEach(day=>{
    const dayTimes = times.filter(t=>{
      return lessons.some(l=>l.day===day&&l.time<=t&&t<addHour(l.time));
    });
    const allTimes = times.filter(t=>{
      const h=parseInt(t.split(':')[0]);
      return h>=8&&h<=15;
    });
    let firstOfDay = true;
    allTimes.forEach(time=>{
      html += '<tr>';
      if(firstOfDay){
        html += `<td class="sched-day" rowspan="${allTimes.length}">${day}</td>`;
        firstOfDay=false;
      }
      html += `<td class="sched-time">${time}</td>`;
      rooms.forEach(room=>{
        const lesson = lessons.find(l=>l.day===day&&l.time===time&&l.room===room);
        if(lesson){
          html+=`<td class="sched-cell"><div class="sched-lesson ${colors[lesson.color]}" onclick="openModal('report-modal')">
            <span class="lesson-count" style="background:${['#16a34a','#2563eb','#d97706','#9d174d','#5b21b6'][lesson.color]}">${lesson.count}</span>
            <div class="lesson-name">${lesson.name}</div>
            <div class="lesson-teacher">${lesson.teacher}</div>
            <div class="lesson-room">${lesson.subject} • ${room}</div>
          </div></td>`;
        } else {
          html += `<td class="sched-cell"></td>`;
        }
      });
      html += '</tr>';
    });
  });
  html += '</tbody></table>';
  document.getElementById('schedule-grid').innerHTML = html;
}

function addHour(t){
  const [h,m]=t.split(':').map(Number);
  return `${String(h+1).padStart(2,'0')}:${String(m).padStart(2,'0')}`;
}

function populateGroups() {
  document.getElementById('groups-tbody').innerHTML = groups.map(g=>`
    <tr>
      <td><b>${g.name}</b></td>
      <td>${g.teacher}</td>
      <td>${g.subject}</td>
      <td>${g.branch} — ${g.room}</td>
      <td>${g.start} — ${g.end}</td>
      <td>${g.days}</td>
      <td><b>${g.students}</b></td>
    </tr>`).join('');
}

function populateClassrooms() {
  document.getElementById('classrooms-tbody').innerHTML = classrooms.map(c=>`
    <tr>
      <td>${c.name}</td>
      <td><span class="filter-tag">${c.branch}</span></td>
      <td>
        <div class="action-menu">
          <button class="action-dots" onclick="toggleMenu(this)">⋮</button>
          <div class="action-dropdown">
            <div class="action-dropdown-item">${icon('edit')} Редактировать</div>
            <div class="action-dropdown-item danger">${icon('trash')} Удалить</div>
          </div>
        </div>
      </td>
    </tr>`).join('');
}

function populateTasks(bodyId, data) {
  const el = document.getElementById(bodyId);
  if (!el) return;
  el.innerHTML = data.map(t=>`
    <div class="task-card">
      <div class="task-info">
        <div class="task-name">${t.student}</div>
        <span class="task-type">${t.type}</span>
        <div class="task-meta">От: <span>${t.from}</span> · Для: <span>${t.to}</span> · Выполнено: —</div>
      </div>
      <div class="task-deadline">
        <svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12" stroke="#fff" stroke-width="2"/><line x1="12" y1="16" x2="12" y2="16" stroke="#fff" stroke-width="2"/></svg>
        Дедлайн: ${t.deadline}
      </div>
      <button class="btn btn-primary btn-sm">Выполнить</button>
    </div>`).join('');
}

function populateMyGroups() {
  const el = document.getElementById('my-groups-body');
  const myGroups = groups.slice(0,3);
  el.innerHTML = myGroups.map((g,i)=>`
    <div class="group-card">
      <div class="group-card-header" onclick="toggleGroupCard(this)">
        <div style="flex:1">
          <div class="group-name">${g.name} · ${g.subject}</div>
          <div class="group-sub">${g.teacher} · ${g.start}–${g.end} · ${g.days}</div>
        </div>
        <span class="badge badge-active">${g.students} учеников</span>
        <button class="btn btn-primary btn-sm" style="margin-left:8px" onclick="event.stopPropagation();openModal('report-modal')">Сделать отчет</button>
      </div>
      <div class="group-body" id="group-body-${i}">
        <div style="padding-top:12px">
          <table class="report-table" style="width:100%">
            <thead><tr><th style="text-align:left;padding:8px 10px">Ученик</th><th>Присутствие</th><th>Балл/урок</th><th>Балл/д/з</th></tr></thead>
            <tbody>
              ${['Иванов Алексей','Петрова Мария','Сидоров Дмитрий'].map(name=>`
                <tr>
                  <td style="padding:8px 10px">${name}</td>
                  <td style="text-align:center"><button class="attendance-btn att-none" onclick="toggleAttendance(this)">?</button></td>
                  <td style="text-align:center"><input class="score-input" type="number" min="0" max="10" placeholder="—"></td>
                  <td style="text-align:center"><input class="score-input" type="number" min="0" max="10" placeholder="—"></td>
                </tr>`).join('')}
            </tbody>
          </table>
          <div style="text-align:right;margin-top:10px">
            <button class="btn btn-primary btn-sm">Сохранить отчет</button>
          </div>
        </div>
      </div>
    </div>`).join('');
}

function populateReturns() {
  document.getElementById('returns-tbody').innerHTML = returns.map(r=>`
    <tr>
      <td style="white-space:nowrap;font-size:12px">${r.created}</td>
      <td><b>${r.student}</b></td>
      <td>${r.parent}</td>
      <td>${r.parentPhone}</td>
      <td><span class="badge ${r.lang==='KAZ'?'badge-kaz':'badge-rus'}">${r.lang}</span></td>
      <td style="font-size:12px;color:#555;max-width:300px">${r.reason}</td>
    </tr>`).join('');
}

function populateFormHistory() {
  document.getElementById('form-history-tbody').innerHTML = formHistory.map(f=>`
    <tr>
      <td style="font-size:12px;white-space:nowrap">${f.created}</td>
      <td>${f.manager}</td>
      <td>${f.student}</td>
      <td>${f.grade}</td>
      <td><span class="badge ${f.lang==='KAZ'?'badge-kaz':'badge-rus'}">${f.lang}</span></td>
      <td>${f.studentPhone}</td>
      <td>${f.parent}</td>
      <td>${f.parentPhone}</td>
      <td>${f.branch}</td>
      <td>${f.start}</td>
      <td><span class="filter-tag">${f.payment}</span></td>
    </tr>`).join('');
}

function populateAnalytics() {
  const data = [{x:0,y:12},{x:1,y:128},{x:2,y:29},{x:3,y:55},{x:4,y:50},{x:5,y:64},{x:6,y:64},{x:7,y:106},{x:8,y:84},{x:9,y:62},{x:10,y:62},{x:11,y:97},{x:12,y:64},{x:13,y:33},{x:14,y:11},{x:15,y:5},{x:16,y:2}];
  const max = Math.max(...data.map(d=>d.y));
  document.getElementById('analytics-chart').innerHTML = `
    <div style="display:flex;align-items:flex-end;gap:4px;height:220px;padding:10px 0">
      ${data.map(d=>`
        <div class="chart-bar-wrap">
          <div class="chart-bar-val">${d.y}</div>
          <div class="chart-bar" style="height:${Math.round((d.y/max)*180)}px" title="${d.x} учеников: ${d.y} групп"></div>
          <div class="chart-bar-label">${d.x}</div>
        </div>`).join('')}
    </div>`;
}

function populateEnt() {
  document.getElementById('ent-tbody').innerHTML = entTests.map(e=>`
    <tr>
      <td>${e.id}</td>
      <td><b>${e.name}</b></td>
      <td><span class="badge ${e.status==='ACTIVE'?'badge-active':'badge-inactive'}">${e.status}</span></td>
      <td style="min-width:150px">
        <div class="progress-bar" style="margin-bottom:3px"><div class="progress-fill" style="width:${e.progress}%"></div></div>
        <div style="font-size:11px;color:#888">${e.progress}%</div>
      </td>
      <td>
        <div class="action-menu">
          <button class="action-dots" onclick="toggleMenu(this)">⋮</button>
          <div class="action-dropdown">
            <div class="action-dropdown-item">${icon('edit')} Редактировать</div>
            <div class="action-dropdown-item danger">${icon('trash')} Удалить</div>
          </div>
        </div>
      </td>
    </tr>`).join('');
}

function populateForbiddenDates() {
  document.getElementById('forbidden-dates-tbody').innerHTML = forbiddenDates.map(d=>`
    <tr>
      <td><b>${d.date}</b></td>
      <td style="color:#888;font-size:13px">${d.added}</td>
      <td>
        <button style="background:none;border:none;cursor:pointer;color:#ef4444">${icon('trash')}</button>
      </td>
    </tr>`).join('');
}

function populateSlots() {
  const slotColors = (val) => {
    const [a,b] = val.split('/').map(Number);
    if(b===0) return 'slot-gray';
    if(a>b) return 'slot-red';
    if(a===b) return 'slot-green';
    if(a>b*0.7) return 'slot-blue';
    return '';
  };
  document.getElementById('slots-tbody').innerHTML = slotsData.map(row=>`
    <tr>
      <td rowspan="2" style="border:1px solid #e5e7eb;padding:8px 16px;font-weight:700;background:#f9fafb">${row.grade}</td>
      <td style="border:1px solid #e5e7eb;padding:8px 16px;font-size:12px;font-weight:600">KAZ</td>
      ${row.kaz.map(v=>`<td class="${slotColors(v)}" style="border:1px solid #e5e7eb;padding:8px;text-align:center;font-size:12px;font-weight:600">${v}</td>`).join('')}
    </tr>
    <tr>
      <td style="border:1px solid #e5e7eb;padding:8px 16px;font-size:12px;font-weight:600">RUS</td>
      ${row.rus.map(v=>`<td class="${slotColors(v)}" style="border:1px solid #e5e7eb;padding:8px;text-align:center;font-size:12px;font-weight:600">${v}</td>`).join('')}
    </tr>`).join('');
}

// ===================== INTERACTIONS =====================
let currentRole = 'admin';

function setRole(role) {
  currentRole = role;
  document.querySelectorAll('.role-btn').forEach(b=>b.classList.remove('active'));
  event.target.classList.add('active');
  renderNav(role);
  if(role==='teacher') showPage('page-my-groups');
  else showPage('page-students');
}

function showPage(pageId) {
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-item, .nav-sub-item').forEach(n=>n.classList.remove('active'));
  const page = document.getElementById(pageId);
  if(page) page.classList.add('active');
  const navId = pageId.replace('page-','nav-');
  const navEl = document.getElementById(navId);
  if(navEl) navEl.classList.add('active');
  // Close all dropdowns
  document.querySelectorAll('.action-dropdown').forEach(d=>d.classList.remove('open'));
}

function toggleGroup(el) {
  el.classList.toggle('open');
  const id = el.id.replace('group-','sub-');
  const sub = document.getElementById(id);
  if(sub) sub.classList.toggle('open');
}

function openModal(id) {
  document.getElementById(id).classList.add('open');
}
function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}

document.querySelectorAll('.modal-overlay').forEach(o=>{
  o.addEventListener('click', e=>{
    if(e.target===o) o.classList.remove('open');
  });
});

function toggleMenu(btn) {
  const dropdown = btn.nextElementSibling;
  const isOpen = dropdown.classList.contains('open');
  document.querySelectorAll('.action-dropdown').forEach(d=>d.classList.remove('open'));
  if(!isOpen) dropdown.classList.add('open');
  event.stopPropagation();
}
document.addEventListener('click', ()=>document.querySelectorAll('.action-dropdown').forEach(d=>d.classList.remove('open')));

function toggleAttendance(btn) {
  if(btn.classList.contains('att-none')) {
    btn.classList.remove('att-none'); btn.classList.add('att-present'); btn.textContent='✓';
  } else if(btn.classList.contains('att-present')) {
    btn.classList.remove('att-present'); btn.classList.add('att-absent'); btn.textContent='✗';
  } else {
    btn.classList.remove('att-absent'); btn.classList.add('att-none'); btn.textContent='?';
  }
}

function toggleGroupCard(el) {
  const body = el.nextElementSibling;
  body.classList.toggle('open');
}

function switchTab(btn, tab) {
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
}

// Open staff submenu by default
document.addEventListener('DOMContentLoaded', ()=>{
  const grpEl = document.getElementById('group-staff');
  if(grpEl) { grpEl.classList.add('open'); }
  const subEl = document.getElementById('sub-staff');
  if(subEl) subEl.classList.add('open');
});

// ===================== INIT =====================
renderNav('admin');
populateStudents();
populateStaff('mentors-tbody', mentors, false);
populateStaff('teachers-tbody', teachers, true);
populateStaff('lidoruby-tbody', lidoruby, false);
populateStaff('managers-tbody', managers, false);
populateMentorAssign();
buildSchedule();
populateGroups();
populateClassrooms();
populateTasks('my-tasks-body', tasks.slice(0,2));
populateTasks('all-tasks-body', tasks);
populateMyGroups();
populateReturns();
populateFormHistory();
populateAnalytics();
populateEnt();
populateForbiddenDates();
populateSlots();

// Open staff sub by default
setTimeout(()=>{
  const g = document.getElementById('group-staff');
  const s = document.getElementById('sub-staff');
  if(g&&s){g.classList.add('open');s.classList.add('open');}
},50);
</script>
</body>
</html>
<script>
// ===== LOGIN LOGIC =====
const ACCOUNTS = {
  '900101350123': { pass: 'newton123', role: 'admin',   name: 'Туран Сыганак', initials: 'СТ' },
  '950215450234': { pass: 'teacher1',  role: 'teacher', name: 'Мухамеди Айман', initials: 'МА' },
};

function formatIin(inp) {
  inp.value = inp.value.replace(/\D/g,'').slice(0,12);
}

function togglePass() {
  const inp = document.getElementById('pass-input');
  inp.type = inp.type === 'password' ? 'text' : 'password';
}

function doLogin() {
  const iin  = document.getElementById('iin-input').value.trim();
  const pass = document.getElementById('pass-input').value;
  const iinErr  = document.getElementById('iin-error');
  const passErr = document.getElementById('pass-error');
  const iinInp  = document.getElementById('iin-input');
  const passInp = document.getElementById('pass-input');

  // Reset
  iinErr.classList.remove('show'); iinInp.classList.remove('error');
  passErr.classList.remove('show'); passInp.classList.remove('error');

  if (!/^\d{12}$/.test(iin)) {
    iinErr.classList.add('show'); iinInp.classList.add('error'); return;
  }
  const acc = ACCOUNTS[iin];
  if (!acc || acc.pass !== pass) {
    passErr.classList.add('show'); passInp.classList.add('error'); return;
  }
  enterApp(acc.role);
}

function quickLogin(role) {
  enterApp(role);
}

function enterApp(role) {
  const btn = document.getElementById('login-btn');
  btn.classList.add('loading'); btn.textContent = 'Вход...';
  setTimeout(() => {
    document.getElementById('login-screen').classList.add('hidden');
    document.getElementById('sidebar').style.display = '';
    document.getElementById('main-app').style.display = '';
    // set role
    currentRole = role;
    document.querySelectorAll('.role-btn').forEach(b => {
      b.classList.toggle('active', (role === 'admin' && b.textContent.trim() === 'Ст. тренер') || (role === 'teacher' && b.textContent.trim() === 'Учитель'));
    });
    renderNav(role);
    if (role === 'teacher') showPage('page-my-groups');
    else showPage('page-students');
    setTimeout(()=>{
      const g = document.getElementById('group-staff');
      const s = document.getElementById('sub-staff');
      if(g&&s){g.classList.add('open');s.classList.add('open');}
    },60);
    btn.classList.remove('loading'); btn.textContent = 'Войти в систему';
  }, 700);
}

// Enter key support
document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !document.getElementById('login-screen').classList.contains('hidden')) doLogin();
});
</script>
