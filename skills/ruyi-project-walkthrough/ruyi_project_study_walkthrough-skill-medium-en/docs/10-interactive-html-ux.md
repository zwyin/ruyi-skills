# Interactive HTML: UX & Accessibility

The generated HTML files are self-contained interactive documents with sidebar navigation, theming, quiz interaction, and mobile responsiveness. All styling and behavior is embedded inline — no external dependencies.

## CSS Architecture

The HTML uses CSS custom properties for a two-theme system:

```css
// Simplified from: scripts/md_to_html.py:402-404
:root {
  --bg:#fff; --text:#1a1a2e; --sidebar-bg:#f0f0f5;
  --card-bg:#f8f8fc; --card-border:#e0e0e8;
  --accent:#4a6fa5; --code-bg:#f4f4f8;
}
[data-theme="dark"] {
  --bg:#1a1a2e; --text:#e0e0ea; --sidebar-bg:#16213e;
  --card-bg:#1e2744; --card-border:#2a3555;
}
```

Every color in the UI references a CSS variable, making the theme system automatic. Toggling between light and dark only requires setting `data-theme="dark"` on the `<html>` element.

## Theme Toggle

The toggle button persists the user's preference in `localStorage`:

```javascript
// Simplified from: scripts/md_to_html.py:441-442
function toggleTheme() {
  var d = document.documentElement,
      isDark = d.getAttribute('data-theme') === 'dark';
  d.setAttribute('data-theme', isDark ? 'light' : 'dark');
  localStorage.setItem('theme', isDark ? 'light' : 'dark');
  document.querySelector('.theme-toggle').textContent = isDark ? '☾' : '☀';
}
```

On page load, the saved theme is restored. If no preference exists, `prefers-color-scheme: dark` is respected:

```javascript
// Simplified from: scripts/md_to_html.py:443
(function() {
  var s = localStorage.getItem('theme');
  if (s) document.documentElement.setAttribute('data-theme', s);
  else if (window.matchMedia('(prefers-color-scheme:dark)').matches)
    document.documentElement.setAttribute('data-theme', 'dark');
})();
```

## Font Size Controls

Two floating buttons (A- and A+) adjust the base font size:

```javascript
// Simplified from: scripts/md_to_html.py:444-445
function adjustFontSize(d) {
  var b = document.body, s = parseFloat(getComputedStyle(b).fontSize);
  b.style.fontSize = Math.max(12, Math.min(24, s + d)) + 'px';
  localStorage.setItem('fs', b.style.fontSize);
}
(function() {
  var f = localStorage.getItem('fs');
  if (f) b.style.fontSize = f;
})();
```

Font size is clamped between 12px and 24px, persisted in `localStorage`.

## Sidebar Navigation

The sidebar is a fixed-position element on the left (280px wide) with chapter links:

```css
// Simplified from: scripts/md_to_html.py:405
.sidebar {
  width: 280px; background: var(--sidebar-bg);
  position: fixed; top: 0; left: 0;
  height: 100vh; overflow-y: auto;
  border-right: 1px solid var(--card-border);
}
```

Active chapter is highlighted with a left border accent:

```css
.sidebar a.active {
  background: var(--sidebar-active);
  border-left-color: var(--accent);
  font-weight: 600;
}
```

## Chapter Navigation

Previous/next buttons at the bottom of each chapter:

```javascript
// Simplified from: scripts/md_to_html.py:445
function showChapter(i) {
  document.querySelectorAll('.chapter').forEach(function(c) {
    c.classList.remove('active');
  });
  document.querySelectorAll('.sidebar a').forEach(function(a) {
    a.classList.remove('active');
  });
  document.querySelectorAll('.chapter')[i].classList.add('active');
  document.querySelectorAll('.sidebar a')[i].classList.add('active');
  window.scrollTo(0, 0);
}
```

Only the active chapter is visible; all others are hidden via CSS `display: none`.

## Quiz Interaction

Quiz questions are rendered as button groups with instant feedback:

```javascript
// Simplified from: scripts/md_to_html.py:296-309
btn.addEventListener('click', function() {
  var buttons = wrap.querySelectorAll('button');
  buttons.forEach(function(b) { b.disabled = true; b.style.cursor = 'default'; });
  if (oi === item.c) {
    btn.style.background = '#059669'; btn.style.color = '#fff';
  } else {
    btn.style.background = '#dc2626'; btn.style.color = '#fff';
    buttons[item.c].style.background = '#059669';
  }
  var fb = document.createElement('div');
  fb.textContent = item.e; // explanation
  wrap.appendChild(fb);
});
```

When clicked: all buttons are disabled, correct answer turns green, wrong selection turns red, and the explanation appears below.

## Mobile Responsive

At 768px or narrower, the sidebar collapses off-screen and a hamburger menu appears:

```css
// Simplified from: scripts/md_to_html.py:426
@media(max-width:768px) {
  .sidebar { transform: translateX(-100%); }
  .sidebar.open { transform: translateX(0); }
  .main { margin-left: 0; padding: 60px 20px 40px; }
  .topbar { display: flex; }
}
```

The topbar provides a toggle button and compact font size controls.

## Print-Friendly

Print styles hide interactive elements and show all chapters:

```css
// Simplified from: scripts/md_to_html.py:427
@media print {
  .sidebar, .topbar, .theme-toggle, .font-btn { display: none !important; }
  .main { margin-left: 0; padding: 20px; }
  .chapter { display: block !important; page-break-after: always; }
}
```

[Previous: Test Suite](09-test-suite.md) | [Next: Extensibility & Preferences](11-extensibility-preferences.md)
