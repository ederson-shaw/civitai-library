
(() => {
  const page = document.body.dataset.page;
  document.querySelectorAll('.stage-link').forEach((link) => {
    if (link.dataset.stage === page) link.setAttribute('aria-current', 'page');
  });

  const selected = {base: null, layer: [], motion: null, voice: null};
  const exactVersion = (url) => typeof url === 'string' && (/modelVersionId=/.test(url) || /\/model-versions\//.test(url));
  const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const formatSize = (value) => `${Math.round(Number(value) || 0)} MB`;

  const cards = [...document.querySelectorAll('.entry-card')];
  const filterChips = [...document.querySelectorAll('.filter-chip')];
  const searchInput = document.querySelector('#entry-search');
  let activeFacet = '';
  const syncUrl = () => {
    const url = new URL(window.location.href);
    const query = (searchInput?.value || '').trim();
    if (query) url.searchParams.set('q', query); else url.searchParams.delete('q');
    if (activeFacet) url.searchParams.set('filter', activeFacet); else url.searchParams.delete('filter');
    window.history.replaceState(null, '', url);
  };
  const cardFacets = (card) => {
    try { return JSON.parse(card.dataset.facets || '[]'); } catch (error) { return []; }
  };
  const updateStyleVisibility = () => {
    const animeMode = page === 'persona' && activeFacet === 'style: anime';
    document.querySelectorAll('.persona-anime-option').forEach((option) => { option.hidden = !animeMode; });
  };
  const matches = (card, query, facet = '') => {
    const textMatch = !query || (card.dataset.search || '').includes(query);
    const animeMode = page === 'persona' && (activeFacet === 'style: anime' || facet === 'style: anime');
    const isAnime = card.dataset.style === 'anime-illustration';
    const styleMatch = page !== 'persona' || (animeMode ? isAnime : !isAnime);
    const facetMatch = !facet || (facet === 'style: anime' ? isAnime : cardFacets(card).includes(facet));
    return textMatch && styleMatch && facetMatch;
  };
  const updateFilters = () => {
    const query = (searchInput?.value || '').trim().toLowerCase();
    cards.forEach((card) => { card.hidden = !matches(card, query, activeFacet); });
    const animeCluster = document.querySelector('[data-anime-cluster]');
    if (animeCluster) animeCluster.hidden = !(page === 'persona' && activeFacet === 'style: anime');
    const allCount = cards.filter((card) => matches(card, query)).length;
    const allNode = document.querySelector('[data-all-count]');
    if (allNode) allNode.textContent = allCount;
    filterChips.forEach((chip) => {
      const facet = chip.dataset.filterFacet || '';
      if (!facet) return;
      const count = cards.filter((card) => matches(card, query, facet)).length;
      const countNode = chip.querySelector('b');
      if (countNode) countNode.textContent = count;
      chip.disabled = count === 0 && activeFacet !== facet;
    });
    filterChips.forEach((chip) => chip.setAttribute('aria-pressed', String((chip.dataset.filterFacet || '') === activeFacet)));
    updateStyleVisibility();
  };
  filterChips.forEach((chip) => chip.addEventListener('click', () => {
    activeFacet = chip.dataset.filterFacet || '';
    updateFilters();
    syncUrl();
  }));
  if (searchInput) searchInput.addEventListener('input', () => { updateFilters(); syncUrl(); });

  const initialUrl = new URL(window.location.href);
  if (searchInput) searchInput.value = initialUrl.searchParams.get('q') || '';
  const initialFacet = initialUrl.searchParams.get('filter') || '';
  if (initialFacet && filterChips.some((chip) => chip.dataset.filterFacet === initialFacet)) activeFacet = initialFacet;
  updateFilters();

  document.querySelectorAll('.score-button').forEach((button) => {
    button.addEventListener('click', (event) => {
      event.stopPropagation();
      const popover = button.parentElement?.querySelector('.score-popover');
      if (!popover) return;
      document.querySelectorAll('.score-popover').forEach((other) => { if (other !== popover) other.hidden = true; });
      document.querySelectorAll('.score-button').forEach((other) => { if (other !== button) other.setAttribute('aria-expanded', 'false'); });
      const open = button.getAttribute('aria-expanded') === 'true';
      if (open) {
        popover.hidden = true;
        button.setAttribute('aria-expanded', 'false');
        return;
      }
      let score;
      try { score = JSON.parse(button.dataset.scorePayload || '{}'); } catch (error) { score = {}; }
      const axes = Object.entries(score.axes || {}).map(([key, value]) => `<li><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></li>`).join('');
      const scoreMarkup = score.score ? `<strong>score ${escapeHtml(score.score)}</strong>` : '';
      const communityMarkup = score.community ? `<p>Community anchors: ${Object.entries(score.community).map(([key, value]) => `${escapeHtml(value)} ${escapeHtml(key)}`).join(' · ')}</p>` : '';
      const axesMarkup = axes ? `<ul>${axes}</ul>` : '';
      const verdictMarkup = score.verdict ? `<p>${escapeHtml(score.verdict)}</p>` : '';
      const dateMarkup = score.pulled_at ? `<span class="score-date">pulled ${escapeHtml(score.pulled_at)}</span>` : '';
      popover.innerHTML = `${scoreMarkup}${communityMarkup}${axesMarkup}${verdictMarkup}${dateMarkup}`;
      popover.hidden = false;
      button.setAttribute('aria-expanded', 'true');
    });
  });

  const roleLabel = (role) => ({base: 'base', layer: 'layer', motion: 'motion', voice: 'voice'}[role] || role);
  const selectedItems = () => [selected.base, ...selected.layer, selected.motion, selected.voice].filter(Boolean);
  const isSelected = (item) => {
    if (!item || !item.role) return false;
    return item.role === 'layer' ? selected.layer.some((entry) => entry.id === item.id) : selected[item.role]?.id === item.id;
  };
  const toggleSelected = (item) => {
    if (!item || !item.id || !Object.prototype.hasOwnProperty.call(selected, item.role)) return;
    if (item.role === 'layer') {
      const index = selected.layer.findIndex((entry) => entry.id === item.id);
      if (index >= 0) selected.layer.splice(index, 1); else selected.layer.push(item);
      return;
    }
    selected[item.role] = selected[item.role]?.id === item.id ? null : item;
  };
  const updateSelectionVisuals = () => {
    document.querySelectorAll('.stack-option[data-stack-entry]').forEach((option) => {
      let item;
      try { item = JSON.parse(option.dataset.stackEntry || '{}'); } catch (error) { item = {}; }
      const active = isSelected(item);
      option.setAttribute('aria-pressed', String(active));
      const action = option.querySelector('.stack-option-action');
      if (action) action.textContent = active ? 'remove' : 'add';
    });
    document.querySelectorAll('.entry-card[data-stack-payload]').forEach((card) => {
      let item;
      try { item = JSON.parse(card.dataset.stackPayload || '{}'); } catch (error) { item = {}; }
      const active = isSelected(item);
      card.classList.toggle('is-stack-selected', active);
      const addButton = card.querySelector('[data-card-add]');
      if (addButton) {
        addButton.setAttribute('aria-pressed', String(active));
        addButton.textContent = active ? 'remove from stack' : 'add to stack';
      }
    });
  };
  const updatePlan = () => {
    const items = selectedItems();
    const hasStack = items.length > 0;
    const empty = document.querySelector('[data-stack-empty]');
    const plan = document.querySelector('[data-stack-plan]');
    const live = document.querySelector('[data-stack-live]');
    if (empty) empty.hidden = hasStack;
    if (plan) plan.hidden = !hasStack;
    if (live) live.hidden = !hasStack;
    const selectedSummary = document.querySelector('[data-stack-selected]');
    if (selectedSummary) {
      selectedSummary.innerHTML = items.map((item) => `<div class="stack-selected-item"><span>${escapeHtml(roleLabel(item.role))}</span><strong>${escapeHtml(item.name)}</strong></div>`).join('');
    }
    document.querySelectorAll('[data-plan-slot]').forEach((slot) => {
      const role = slot.dataset.planSlot;
      const values = role === 'layer' ? selected.layer : (selected[role] ? [selected[role]] : []);
      const target = slot.querySelector('[data-plan-selection]');
      if (target) target.innerHTML = values.map((item) => `<span class="plan-selection-item">${escapeHtml(item.name)}</span>`).join('');
    });
  };
  const manifestRows = () => {
    const rows = [];
    const seen = new Set();
    selectedItems().forEach((item) => {
      const models = Array.isArray(item.models) ? item.models : [];
      models.forEach((model) => {
        if (!model.name || !model.folder || model.size_mb == null || !exactVersion(model.url)) return;
        const key = `${model.name}|${model.url}`;
        if (seen.has(key)) return;
        seen.add(key);
        rows.push({name: model.name, folder: model.folder, size: model.size_mb, url: model.url});
      });
    });
    return rows;
  };

  const updateStack = () => {
    const items = selectedItems();
    const vram = items.reduce((sum, item) => sum + (Number(item.vram) || 0), 0);
    const disk = items.reduce((sum, item) => sum + (Number(item.disk) || 0), 0);
    updatePlan();
    updateSelectionVisuals();
    const vramNode = document.querySelector('[data-stack-vram]');
    const diskNode = document.querySelector('[data-stack-disk]');
    if (vramNode) vramNode.textContent = `${vram} GB`;
    if (diskNode) diskNode.textContent = formatSize(disk);
    const rows = manifestRows();
    const manifest = document.querySelector('[data-stack-manifest]');
    const copyButton = document.querySelector('[data-copy-all]');
    if (manifest) {
      manifest.innerHTML = rows.map((row) => `<div class="manifest-row"><strong>${escapeHtml(row.name)}</strong><span>${escapeHtml(row.folder)} · ${formatSize(row.size)}</span><a href="${escapeHtml(row.url)}" target="_blank" rel="noreferrer">exact version ↗</a></div>`).join('');
    }
    if (copyButton) copyButton.disabled = rows.length === 0;
  };

  document.querySelectorAll('.stack-option').forEach((option) => {
    option.addEventListener('click', () => {
      let item;
      try { item = JSON.parse(option.dataset.stackEntry || '{}'); } catch (error) { return; }
      toggleSelected(item);
      updateStack();
    });
  });

  document.querySelectorAll('[data-card-add]').forEach((button) => {
    button.addEventListener('click', (event) => {
      event.stopPropagation();
      const card = button.closest('.entry-card');
      if (!card) return;
      let item;
      try { item = JSON.parse(card.dataset.stackPayload || '{}'); } catch (error) { return; }
      toggleSelected(item);
      updateStack();
    });
  });

  const copyButton = document.querySelector('[data-copy-all]');
  if (copyButton) copyButton.addEventListener('click', async () => {
    const rows = manifestRows();
    const status = document.querySelector('[data-copy-status]');
    try {
      await navigator.clipboard.writeText(rows.map((row) => row.url).join('\n'));
      if (status) status.textContent = `${rows.length} exact links copied`;
    } catch (error) {
      if (status) status.textContent = 'Clipboard unavailable; copy links from the rows.';
    }
  });

  document.querySelectorAll('.entry-card').forEach((card) => {
    const detail = card.querySelector('.card-detail');
    const toggleDetail = () => {
      if (!detail) return;
      const open = card.getAttribute('aria-expanded') === 'true';
      card.setAttribute('aria-expanded', String(!open));
      detail.hidden = open;
    };
    card.addEventListener('click', (event) => {
      if (event.target.closest('a, button')) return;
      toggleDetail();
    });
    card.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        toggleDetail();
      }
    });
  });

  document.querySelectorAll('[data-gallery-surface]').forEach((surface) => {
    const image = surface.querySelector('img[data-gallery]');
    if (!image) return;
    let gallery;
    try { gallery = JSON.parse(image.dataset.gallery || '[]'); } catch (error) { gallery = []; }
    if (gallery.length < 2) return;
    surface.addEventListener('mousemove', (event) => {
      const bounds = surface.getBoundingClientRect();
      const ratio = Math.max(0, Math.min(0.999, (event.clientX - bounds.left) / bounds.width));
      image.src = gallery[Math.floor(ratio * gallery.length)];
    });
    surface.addEventListener('mouseleave', () => { image.src = gallery[0]; });
  });

  document.querySelectorAll('[data-hover-video]').forEach((video) => {
    video.addEventListener('mouseenter', () => { video.play().catch(() => {}); });
    video.addEventListener('mouseleave', () => { video.pause(); video.currentTime = 0; });
  });

  updateStack();
})();
