
(async function () {
  const res = await fetch('assets/reuse_locations.json');
  const LOCATIONS = await res.json();

  // ---------------------------------------------------------------
  // Shared marker-building logic (used by both the preview & full map)
  // ---------------------------------------------------------------
  function makeIcon(precision) {
    const cls = precision === 'city' ? 'reuse-marker-city' : 'reuse-marker-country';
    const size = precision === 'city' ? 10 : 12;
    return L.divIcon({
      className: cls,
      iconSize: [size, size],
    });
  }

  function buildMarkers(records, { withPopups }) {
    return records.map(function (rec) {
      const marker = L.marker([rec.lat, rec.lon], { icon: makeIcon(rec.precision) });
      marker.reuseRecord = rec;
      if (withPopups) {
        marker.bindPopup(
          '<p class="popup-org">' + escapeHtml(rec.name) + '</p>' +
          '<p class="popup-meta">' + escapeHtml(rec.country) +
            '<span class="sep">&middot;</span>' + escapeHtml(rec.category) + '</p>' +
          '<a class="popup-link" href="#" onclick="focusOrgInTable(\'' + rec.id + '\'); return false;">View in table &rarr;</a>'
        );
      }
      return marker;
    });
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str == null ? '' : String(str);
    return div.innerHTML;
  }

  // ---------------------------------------------------------------
  // Hook this up to whatever powers your existing Table/Card view.
  // Simplest approach: set the search box's value and dispatch an
  // input event so your existing filter logic picks it up.
  // ---------------------------------------------------------------
  function focusOrgInTable(id) {
    document.getElementById('map-modal').classList.remove('is-open');
    document.body.style.overflow = '';

    if (state.view === 'table') setView('cards');

    const record = LOCATIONS.find(function (r) { return r.id === id; });
    if (!record) return;

    const searchBox = document.getElementById('search');
    searchBox.value = record.name;
    searchBox.dispatchEvent(new Event('input'));

    const orgEntry = ORGS.find(function (o) { return o.name === record.name; });
    const cardEl = orgEntry ? document.querySelector('.card[data-slug="' + orgEntry.slug + '"]') : null;
    if (!cardEl) return;

    cardEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    cardEl.classList.add('card-highlight');
    setTimeout(function () { cardEl.classList.remove('card-highlight'); }, 2000);
  }
  window.focusOrgInTable = focusOrgInTable;

  // ---------------------------------------------------------------
  // PREVIEW MAP - static-feeling teaser, no interaction, cheap to draw
  // ---------------------------------------------------------------
  const previewMap = L.map('preview-map', {
    zoomControl: false,
    dragging: false,
    scrollWheelZoom: false,
    doubleClickZoom: false,
    boxZoom: false,
    keyboard: false,
    attributionControl: false,
    fadeAnimation: false,
  }).setView([15, 10], 2);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 18,
  }).addTo(previewMap);

  const previewCluster = L.markerClusterGroup({
    showCoverageOnHover: false,
    spiderfyOnMaxZoom: false,
    iconCreateFunction: clusterIcon,
  });
  previewCluster.addLayers(buildMarkers(LOCATIONS, { withPopups: false }));
  previewMap.addLayer(previewCluster);

  // ---------------------------------------------------------------
  // FULL MAP - built lazily, first time the modal opens
  // ---------------------------------------------------------------
  let fullMap = null;
  let fullClusterGroup = null;
  let allMarkers = [];

  function initFullMapIfNeeded() {
    if (fullMap) return;

    fullMap = L.map('full-map', { zoomControl: true }).setView([15, 10], 2);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap &copy; CARTO',
    }).addTo(fullMap);

    fullClusterGroup = L.markerClusterGroup({
      showCoverageOnHover: false,
      iconCreateFunction: clusterIcon,
      maxClusterRadius: 50,
    });

    allMarkers = buildMarkers(LOCATIONS, { withPopups: true });
    fullClusterGroup.addLayers(allMarkers);
    fullMap.addLayer(fullClusterGroup);
  }

  function clusterIcon(cluster) {
    const count = cluster.getChildCount();
    const size = count < 10 ? 32 : count < 50 ? 40 : 50;
    return L.divIcon({
      html: '<div style="width:' + size + 'px;height:' + size + 'px;border-radius:50%;' +
        'display:flex;align-items:center;justify-content:center;font-size:' +
        (count < 100 ? 13 : 11) + 'px;">' + count + '</div>',
      className: 'marker-cluster-reuse',
      iconSize: L.point(size, size),
    });
  }

  // ---------------------------------------------------------------
  // Modal open / close
  // ---------------------------------------------------------------
  const modal = document.getElementById('map-modal');
  const previewCard = document.getElementById('preview-card');
  const closeBtn = document.getElementById('modal-close');
  const backdrop = document.getElementById('modal-backdrop');
  const searchInput = document.getElementById('map-search');
  const visibleCount = document.getElementById('visible-count');

  function openModal() {
    modal.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    initFullMapIfNeeded();
    // Leaflet maps created while display:none render broken - fix on open.
    setTimeout(function () { fullMap.invalidateSize(); }, 50);
    searchInput.focus();
  }

  function closeModal() {
    modal.classList.remove('is-open');
    document.body.style.overflow = '';
    previewCard.focus();
  }

  previewCard.addEventListener('click', openModal);
  previewCard.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openModal(); }
  });
  closeBtn.addEventListener('click', closeModal);
  backdrop.addEventListener('click', closeModal);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && modal.classList.contains('is-open')) closeModal();
  });

  // ---------------------------------------------------------------
  // Live search/filter inside the expanded map
  // ---------------------------------------------------------------
  searchInput.addEventListener('input', function (e) {
    const q = e.target.value.trim().toLowerCase();
    fullClusterGroup.clearLayers();

    const matches = !q ? allMarkers : allMarkers.filter(function (m) {
      const r = m.reuseRecord;
      return r.name.toLowerCase().includes(q) ||
             r.country.toLowerCase().includes(q) ||
             r.category.toLowerCase().includes(q);
    });

    fullClusterGroup.addLayers(matches);
    visibleCount.textContent = matches.length;
  });
})();
