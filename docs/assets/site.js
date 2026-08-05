
const state = { sortKey: 'name', sortDir: 1, view: 'cards' };

function escapeHtml(str) {
  return String(str ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
}

function uniqueSorted(values) {
  return Array.from(new Set(values.filter(Boolean))).sort();
}

function populateFilters() {
  const countrySel = document.getElementById('country-filter');
  const prioritySel = document.getElementById('priority-filter');
  const statusSel = document.getElementById('status-filter');
  uniqueSorted(ORGS.map(o => o.country)).forEach(c => {
    const opt = document.createElement('option');
    opt.value = c; opt.textContent = c;
    countrySel.appendChild(opt);
  });
  uniqueSorted(ORGS.map(o => o.priority)).forEach(p => {
    const opt = document.createElement('option');
    opt.value = p; opt.textContent = p;
    prioritySel.appendChild(opt);
  });
  uniqueSorted(ORGS.map(o => o.status)).forEach(s => {
    const opt = document.createElement('option');
    opt.value = s; opt.textContent = s;
    statusSel.appendChild(opt);
  });
}

function matches(org, q, country, priority, status) {
  if (country && org.country !== country) return false;
  if (priority && org.priority !== priority) return false;
  if (status && org.status !== status) return false;
  if (!q) return true;
  const hay = (org.name + ' ' + org.country + ' ' + org.categories + ' ' + org.summary).toLowerCase();
  return hay.includes(q);
}

function getFiltered() {
  const q = document.getElementById('search').value.trim().toLowerCase();
  const country = document.getElementById('country-filter').value;
  const priority = document.getElementById('priority-filter').value;
  const status = document.getElementById('status-filter').value;
  let rows = ORGS.filter(o => matches(o, q, country, priority, status));
  rows.sort((a, b) => {
    const av = (a[state.sortKey] || '').toString().toLowerCase();
    const bv = (b[state.sortKey] || '').toString().toLowerCase();
    if (av < bv) return -1 * state.sortDir;
    if (av > bv) return 1 * state.sortDir;
    return 0;
  });
  return rows;
}

function priorityClass(priority) {
  const p = String(priority || '');
  if (p.includes('Essential') || p.includes('★★★★★')) return 'pill score';
  if (p.includes('High') || p.includes('★★★★')) return 'pill score';
  if (p.includes('Low relevance') || p.includes('★')) {
    if (p.includes('Low relevance')) return 'pill bad';
    if (p.includes('★★')) return 'pill warn';
  }
  return 'pill';
}

function statusClass(status) {
  const s = String(status || '').toLowerCase();
  if (s.includes('inactive') || s.includes('closed') || s.includes('defunct') || s.includes('ceased') || s.includes('liquidation')) return 'pill bad';
  if (s.includes('uncertain') || s.includes('unclear') || s.includes('unverified')) return 'pill warn';
  return 'pill';
}

function renderSummary(rows) {
  const active = rows.filter(o => /active/i.test(o.status || '') && !/inactive/i.test(o.status || '')).length;
  const countries = new Set(rows.map(o => o.country).filter(c => c && c !== 'Not publicly available')).size;
  document.getElementById('summary').innerHTML = `
    <div class="metric"><div class="label">Organisations shown</div><div class="value">${rows.length}</div></div>
    <div class="metric"><div class="label">Confirmed active</div><div class="value">${active}</div></div>
    <div class="metric"><div class="label">Countries represented</div><div class="value">${countries}</div></div>
  `;
}

function renderCards(rows) {
  document.getElementById('cards').innerHTML = rows.map(o => `
    <article class="card">
      <div>
        <h2><a href="organisations/${o.slug}.html">${escapeHtml(o.name)}</a></h2>
        <div class="meta">
          <span class="${statusClass(o.status)}">${escapeHtml(o.status || 'Status unknown')}</span>
        </div>
      </div>
      <div class="small"><strong>${escapeHtml(o.country || 'Country unknown')}</strong>${o.year ? ' · ' + (/found/i.test(o.year) ? '' : 'Founded ') + escapeHtml(o.year) : ''}</div>
      <div class="field">
        <strong>Overview</strong>
        <span class="small">${escapeHtml(o.summary || 'Not publicly available')}</span>
      </div>
      <div class="field tags">
        <strong>Categories</strong>
        ${(o.categories || '').split(',').filter(Boolean).map(t => `<span class="tag-pill">${escapeHtml(t.trim())}</span>`).join('') || '<span class="small">Not publicly available</span>'}
      </div>
      <a class="view-link" href="organisations/${o.slug}.html">View full profile →</a>
    </article>
  `).join('');
}

function renderTable(rows) {
  const tbody = document.getElementById('org-table-body');
  tbody.innerHTML = rows.map(o => `
    <tr>
      <td><a href="organisations/${o.slug}.html">${escapeHtml(o.name)}</a></td>
      <td>${escapeHtml(o.country) || '—'}</td>
      <td>${(o.categories || '').split(',').filter(Boolean).map(t => `<span class="tag-pill">${escapeHtml(t.trim())}</span>`).join('')}</td>
      <td>${escapeHtml(o.year) || '—'}</td>
      <td><span class="${statusClass(o.status)}">${escapeHtml(o.status || '—')}</span></td>
    </tr>
  `).join('');
}

function render() {
  const rows = getFiltered();
  document.getElementById('result-count').textContent = `Showing ${rows.length} of ${ORGS.length} organisations`;
  renderSummary(rows);
  if (state.view === 'cards') renderCards(rows); else renderTable(rows);
}

function setView(view) {
  state.view = view;
  document.getElementById('cards').classList.toggle('hidden', view !== 'cards');
  document.getElementById('tableWrap').classList.toggle('hidden', view !== 'table');
  document.getElementById('cardBtn').classList.toggle('active', view === 'cards');
  document.getElementById('tableBtn').classList.toggle('active', view === 'table');
  render();
}

function resetFilters() {
  document.getElementById('search').value = '';
  document.getElementById('country-filter').value = '';
  document.getElementById('priority-filter').value = '';
  document.getElementById('status-filter').value = '';
  render();
}

document.getElementById('search').addEventListener('input', render);
document.getElementById('country-filter').addEventListener('change', render);
document.getElementById('priority-filter').addEventListener('change', render);
document.getElementById('status-filter').addEventListener('change', render);

document.querySelectorAll('th.sortable').forEach(th => {
  th.addEventListener('click', () => {
    const key = th.dataset.key;
    if (state.sortKey === key) { state.sortDir *= -1; } else { state.sortKey = key; state.sortDir = 1; }
    render();
  });
});

populateFilters();
render();
