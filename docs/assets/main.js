/* LumenHelix GitHub Pages launch template — interactions */

(function () {
  'use strict';

  // Tab switching for install commands
  const tabLists = document.querySelectorAll('[role="tablist"]');

  tabLists.forEach((list) => {
    const tabs = Array.from(list.querySelectorAll('[role="tab"]'));
    const panels = Array.from(
      document.querySelectorAll(`[role="tabpanel"][aria-labelledby^="${list.id ? list.id + '-' : ''}"]`)
    );

    // Build id mapping if list has id
    const listId = list.id || '';
    const getPanelId = (tab) => tab.getAttribute('aria-controls');

    function switchTab(targetTab) {
      tabs.forEach((tab) => {
        const selected = tab === targetTab;
        tab.setAttribute('aria-selected', selected);
        tab.setAttribute('tabindex', selected ? '0' : '-1');
      });

      const targetPanelId = getPanelId(targetTab);
      panels.forEach((panel) => {
        const isTarget = panel.id === targetPanelId;
        panel.setAttribute('aria-hidden', !isTarget);
      });
    }

    tabs.forEach((tab) => {
      tab.addEventListener('click', () => switchTab(tab));
      tab.addEventListener('keydown', (e) => {
        let index = tabs.indexOf(tab);
        if (e.key === 'ArrowRight') index = (index + 1) % tabs.length;
        else if (e.key === 'ArrowLeft') index = (index - 1 + tabs.length) % tabs.length;
        else if (e.key === 'Home') index = 0;
        else if (e.key === 'End') index = tabs.length - 1;
        else return;
        e.preventDefault();
        tabs[index].focus();
        switchTab(tabs[index]);
      });
    });
  });

  // Copy-to-clipboard for terminal blocks
  document.querySelectorAll('.terminal').forEach((term) => {
    const pre = term.querySelector('pre');
    if (!pre) return;

    const btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.setAttribute('aria-label', 'Copy command to clipboard');
    btn.textContent = 'Copy';

    btn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(pre.textContent.trim());
        const original = btn.textContent;
        btn.textContent = 'Copied';
        setTimeout(() => (btn.textContent = original), 1500);
      } catch (err) {
        btn.textContent = 'Failed';
        setTimeout(() => (btn.textContent = 'Copy'), 1500);
      }
    });

    term.appendChild(btn);
  });

  // Mobile menu toggle
  const menuBtn = document.querySelector('.mobile-menu-btn');
  const nav = document.querySelector('.site-header nav');
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', () => {
      const expanded = menuBtn.getAttribute('aria-expanded') === 'true';
      menuBtn.setAttribute('aria-expanded', String(!expanded));
      nav.style.display = expanded ? 'none' : 'flex';
      nav.style.flexDirection = 'column';
      nav.style.position = 'absolute';
      nav.style.top = '4rem';
      nav.style.left = '0';
      nav.style.right = '0';
      nav.style.background = 'var(--lh-bg)';
      nav.style.padding = '1rem 1.5rem';
      nav.style.borderBottom = '1px solid var(--lh-border)';
    });
  }
})();
