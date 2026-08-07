import json, os

with open('/opt/data/vienna-map/places.json') as f:
    places = json.load(f)

cat_colors = {
    'Appartamento': '#e74c3c',
    'Attività': '#ff6b35',
    'Café': '#e67e22',
    'Dolci': '#e91e63',
    'Eventi': '#9b59b6',
    'Giro Tram 1/2': '#f59e0b',
    'Gite fuori Vienna': '#1abc9c',
    'Mercati': '#f1c40f',
    'Monumenti': '#7f8c8d',
    'Musei': '#3498db',
    'Panificio': '#a0522d',
    'Parchi': '#27ae60',
    'Spiaggia': '#0ea5e9',
    'Divertimenti': '#ef4444',
    'Avventura': '#f97316',
    'Parchi avventura': '#f97316',
    'Parchi giochi': '#06b6d4',
    'Parchi e giardini': '#22c55e',
    'Ristorante': '#d35400',
    'Shopping': '#8e44ad',
    'Tè': '#d4a574',
    'Vintage': '#c8a2c8',
    'Souvenir': '#f59e0b',
    'Trasporti': '#3b82f6',
    'Vegano / Vegetariano': '#27ae60',
}

cat_emoji = {
    'Appartamento': '\U0001F3E0',
    'Attività': '\U0001F3AF',
    'Café': '\u2615',
    'Dolci': '\U0001F370',
    'Eventi': '\U0001F3AA',
    'Giro Tram 1/2': '\U0001F68B',
    'Gite fuori Vienna': '\U0001F697',
    'Mercati': '\U0001F6D2',
    'Monumenti': '\U0001F3DB',
    'Musei': '\U0001F3DB',
    'Panificio': '\U0001F96F',
    'Parchi': '\U0001F3DE',
    'Spiaggia': '\U0001F3D6',
    'Divertimenti': '\U0001F3A2',
    'Avventura': '\U0001F9CF',
    'Parchi avventura': '\U0001F9CF',
    'Parchi giochi': '\U0001F3A1',
    'Parchi e giardini': '\U0001F333',
    'Ristorante': '\U0001F35C',
    'Shopping': '\U0001F6CD',
    'Tè': '\u2618',
    'Vintage': '\U0001F45C',
    'Souvenir': '\U0001F9F7',
    'Trasporti': '\U0001F687',
    'Vegano / Vegetariano': '\U0001F37D',
}

# Ristorazione macro: subcategories
RISTO_CATS = {'Café', 'Dolci', 'Ristorante', 'Panificio', 'Vegano / Vegetariano'}

# Shopping macro: subcategories
SHOP_CATS = {'Tè', 'Vintage', 'Souvenir'}

# Parchi macro: subcategories
PARK_CATS = {'Spiaggia', 'Avventura', 'Parchi avventura', 'Parchi giochi', 'Parchi e giardini'}

# Build categories
cats = {}
for p in places:
    c = p.get('cat', 'Altro')
    if c not in cats:
        cats[c] = []
    cats[c].append(p)

# Build places JS
places_js_lines = []
for p in places:
    name = p['name'].replace("'", "\\'").replace("\u2019", "\\'").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    metro = p.get('metro', '')
    note = p.get('note', '').replace("'", "\\'").replace("\u2019", "\\'").replace("\n", " ").replace("&", "&amp;")
    desc = p.get('desc', '').replace("'", "\\'").replace("\u2019", "\\'").replace("\n", " ").replace("&", "&amp;")
    ptype = p.get('type', 'default')
    emoji = cat_emoji.get(p['cat'], '\U0001F4CD')
    cat2 = p.get('cat2', '')
    line = "  {name: '%s', lat: %s, lng: %s, cat: '%s', type: '%s', emoji: '%s'" % (name, p['lat'], p['lng'], p['cat'].replace("'", "\\'").replace("\u2019", "\\'"), ptype, emoji)
    if cat2:
        line += ", cat2: '%s'" % cat2.replace("'", "\\'").replace("\u2019", "\\'")
    if metro:
        line += ", metro: '%s'" % metro.replace("'", "\\'")
    if note:
        line += ", note: '%s'" % note
    line += "}"
    places_js_lines.append(line)
places_data = ",\n".join(places_js_lines)

# Build catColors JS
cat_keys = sorted(cats.keys())
cat_colors_js_lines = []
for cat_name in cat_keys:
    color = cat_colors.get(cat_name, '#95a5a6')
    cat_colors_js_lines.append("  '%s': '%s'" % (cat_name.replace("'", "\\'"), color))
cat_colors_js = ",\n".join(cat_colors_js_lines)

# Build filter HTML
RISTO_CATS_ORDERED = ['Café', 'Dolci', 'Ristorante', 'Panificio', 'Vegano / Vegetariano']
RISTO_SET = set(RISTO_CATS_ORDERED)

SHOP_CATS_ORDERED = ['Tè', 'Vintage', 'Souvenir']
SHOP_SET = set(SHOP_CATS_ORDERED)

PARK_CATS_ORDERED = ['Spiaggia', 'Parchi avventura', 'Parchi giochi', 'Parchi e giardini']
PARK_SET = set(PARK_CATS_ORDERED)

filter_lines = []
filter_lines.append('  <div id="filter-panel">')
filter_lines.append('    <div class="filter-title" id="filter-toggle" onclick="toggleFilterPanel()">Filtra categorie <span id="filter-chevron">&#9660;</span></div>')
filter_lines.append('    <div id="filter-collapsible">')

risto_output = False
shop_output = False
park_output = False
for cat_name in sorted(cats.keys()):
    if cat_name in RISTO_SET and not risto_output:
        risto_total = sum(len(cats[c]) for c in RISTO_CATS_ORDERED if c in cats)
        filter_lines.append('    <label class="filter-item macro-parent"><input type="checkbox" id="macro-risto" checked><span style="font-size:14px">\U0001F37D</span> <b>Ristorazione</b> <span class="cat-count">(%d)</span></label>' % risto_total)
        for rc in RISTO_CATS_ORDERED:
            if rc in cats:
                color = cat_colors.get(rc, '#95a5a6')
                count = len(cats[rc])
                filter_lines.append('    <label class="filter-item macro-child"><input type="checkbox" class="cat-filter risto-sub" data-cat="%s" checked><span class="place-dot" style="background:%s"></span> %s <span class="cat-count">(%d)</span></label>' % (rc.replace('"', '&quot;'), color, rc.replace("&", "&amp;"), count))
        risto_output = True
    elif cat_name in SHOP_SET and not shop_output:
        shop_total = sum(len(cats[c]) for c in SHOP_CATS_ORDERED if c in cats)
        filter_lines.append('    <label class="filter-item macro-parent"><input type="checkbox" id="macro-shop" checked><span style="font-size:14px">\U0001F6CD</span> <b>Shopping</b> <span class="cat-count">(%d)</span></label>' % shop_total)
        for sc in SHOP_CATS_ORDERED:
            if sc in cats:
                color = cat_colors.get(sc, '#95a5a6')
                count = len(cats[sc])
                filter_lines.append('    <label class="filter-item macro-child"><input type="checkbox" class="cat-filter shop-sub" data-cat="%s" checked><span class="place-dot" style="background:%s"></span> %s <span class="cat-count">(%d)</span></label>' % (sc.replace('"', '&quot;'), color, sc.replace("&", "&amp;"), count))
        shop_output = True
    elif cat_name in PARK_SET and not park_output:
        park_total = sum(len(cats[c]) for c in PARK_CATS_ORDERED if c in cats)
        filter_lines.append('    <label class="filter-item macro-parent"><input type="checkbox" id="macro-park" checked><span style="font-size:14px">\U0001F3DE</span> <b>Parchi</b> <span class="cat-count">(%d)</span></label>' % park_total)
        for pc in PARK_CATS_ORDERED:
            if pc in cats:
                color = cat_colors.get(pc, '#95a5a6')
                count = len(cats[pc])
                filter_lines.append('    <label class="filter-item macro-child"><input type="checkbox" class="cat-filter park-sub" data-cat="%s" checked><span class="place-dot" style="background:%s"></span> %s <span class="cat-count">(%d)</span></label>' % (pc.replace('"', '&quot;'), color, pc.replace("&", "&amp;"), count))
        park_output = True
    elif cat_name not in RISTO_SET and cat_name not in SHOP_SET and cat_name not in PARK_SET:
        color = cat_colors.get(cat_name, '#95a5a6')
        count = len(cats[cat_name])
        filter_lines.append('    <label class="filter-item"><input type="checkbox" class="cat-filter" data-cat="%s" checked><span class="place-dot" style="background:%s"></span> %s <span class="cat-count">(%d)</span></label>' % (cat_name.replace('"', '&quot;'), color, cat_name.replace("&", "&amp;"), count))

filter_lines.append('    <div class="filter-buttons">')
filter_lines.append('      <button id="filter-all" class="filter-btn">Tutti</button>')
filter_lines.append('      <button id="filter-none" class="filter-btn">Nessuno</button>')
filter_lines.append('    </div>')
filter_lines.append('    <label class="filter-item" style="margin-top:8px;border-top:1px solid #0f3460;padding-top:8px"><input type="checkbox" id="toggle-labels"><span style="font-size:12px">Mostra etichette sulla mappa</span></label>')
filter_lines.append('    <div style="font-size:10px;color:#64748b;margin-top:2px;padding-left:20px">Automatiche quando zoomi (max 8 luoghi)</div>')
filter_lines.append('    <label class="filter-item"><input type="checkbox" id="toggle-tram-cw"><span class="place-dot" style="background:#1b5e20"></span><span style="font-size:12px">\U0001F68B Tram oraria</span></label>')
filter_lines.append('    <label class="filter-item"><input type="checkbox" id="toggle-tram-ccw"><span class="place-dot" style="background:#1565c0"></span><span style="font-size:12px">\U0001F68B Tram antioraria</span></label>')
filter_lines.append('    <div style="text-align:center;padding:8px 0"><a href="vienna-itinerario.html" style="color:#94a3b8;font-size:12px;text-decoration:none;border:1px solid #0f3460;padding:4px 10px;border-radius:4px">📋 Itinerario 6 giorni</a></div>')
filter_lines.append('    </div>')  # close filter-collapsible
filter_lines.append('  </div>')
filter_html = "\n".join(filter_lines)

# Build sidebar HTML - with data-cat2 attribute for cross-category
sidebar_lines = []
for cat_name in sorted(cats.keys()):
    color = cat_colors.get(cat_name, '#95a5a6')
    sidebar_lines.append('    <div class="cat-header" data-cat="%s" style="color:%s">%s</div>' % (cat_name.replace('"', '&quot;'), color, cat_name.replace("&", "&amp;")))
    for p in cats[cat_name]:
        name = p['name'].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        ring_tag = ' <span style="color:#f59e0b">\U0001F68B</span>' if p.get('type') == 'ring_tram' else ''
        cat2_attr = ' data-cat2="%s"' % p.get('cat2', '').replace('"', '&quot;') if p.get('cat2') else ''
        sidebar_lines.append('    <div class="place-item" data-name="%s" data-cat="%s"%s><span class="place-dot" style="background:%s"></span> %s%s</div>' % (name, cat_name.replace('"', '&quot;'), cat2_attr, color, name, ring_tag))
sidebar_html = "\n".join(sidebar_lines)

# HTML template
html_content = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vienna 2026 — Mappa Interattiva</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background:#1a1a2e; color:#cbd5e1; display:flex; height:100vh; }
#sidebar { width:300px; background:#1a1a2e; overflow-y:auto; padding:12px; flex-shrink:0; }
#map { flex:1; }
#search { width:100%; padding:8px 12px; margin-bottom:10px; background:#16213e; border:1px solid #0f3460; border-radius:6px; color:#f1f5f9; font-size:16px; }
#search::placeholder { color:#64748b; }
#filter-panel { background:#16213e; border:1px solid #0f3460; border-radius:6px; padding:8px 10px; margin-bottom:10px; }
.filter-title { font-size:11px; text-transform:uppercase; letter-spacing:1px; font-weight:700; color:#94a3b8; margin-bottom:6px; cursor:pointer; user-select:none; display:flex; justify-content:space-between; align-items:center; }
#filter-chevron { font-size:10px; transition:transform .2s; }
#filter-chevron.collapsed { transform:rotate(-90deg); }
#filter-collapsible { overflow:hidden; transition:max-height .3s ease-out, opacity .2s; max-height:2000px; opacity:1; }
#filter-collapsible.collapsed { max-height:0; opacity:0; }
.filter-item { display:flex; align-items:center; gap:6px; padding:3px 0; font-size:12px; cursor:pointer; color:#cbd5e1; }
.filter-item input { accent-color:#f59e0b; }
.cat-count { color:#64748b; font-size:11px; }
.filter-buttons { display:flex; gap:6px; margin-top:8px; }
.filter-btn { background:#0f3460; border:none; border-radius:4px; color:#cbd5e1; padding:4px 8px; font-size:11px; cursor:pointer; }
.filter-btn:hover { background:#1a4a7a; }
.macro-parent { font-size:13px; padding-top:4px; border-top:1px solid #0f3460; margin-top:4px; }
.macro-child { padding-left:20px; font-size:12px; }
.cat-header { font-size:11px; text-transform:uppercase; letter-spacing:1px; padding:8px 4px 4px; font-weight:700; }
.place-item { padding:6px 4px 6px 8px; cursor:pointer; font-size:13px; border-radius:4px; display:flex; align-items:center; gap:6px; line-height:1.3; }
.place-item:hover { background:#16213e; }
.place-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.place-item.highlight { background:#0f3460; }
.richiamo-tag { font-size:10px; color:#94a3b8; margin-left:4px; font-style:italic; }
.marker-icon { background:none !important; border:none !important; }
.marker-label { background:rgba(26,26,46,0.92); color:#e2e8f0; padding:4px 8px; border-radius:6px; font-size:11px; white-space:nowrap; border:1px solid #0f3460; line-height:1.4; box-shadow:0 2px 8px rgba(0,0,0,0.3); }
.leaflet-popup-content-wrapper { background:#1a1a2e; color:#cbd5e1; border-radius:8px; }
.leaflet-popup-tip { background:#1a1a2e; }
.leaflet-popup-content { margin:10px 14px; font-size:13px; }
.leaflet-popup-content b { color:#e2e8f0; }
.metro-badge { background:#f59e0b; color:#1a1a2e; padding:1px 6px; border-radius:3px; font-size:11px; font-weight:700; margin-left:4px; }
.ring-badge { background:#f59e0b; color:#1a1a2e; padding:2px 6px; border-radius:10px; font-size:11px; font-weight:600; }
#mobile-toggle { display:none; position:fixed; top:10px; right:10px; z-index:1001; background:#1a1a2e; color:#f1f5f9; border:1px solid #0f3460; border-radius:6px; padding:6px 10px; font-size:18px; cursor:pointer; }
@media (max-width:768px) {
  body { flex-direction:column; }
  #sidebar { width:100%; max-height:40vh; border-top:2px solid #0f3460; }
  #mobile-toggle { display:block; }
  #sidebar.collapsed { display:none; }
  .leaflet-control-zoom { top:10px !important; left:10px !important; }
}
</style>
</head>
<body>
<button id="mobile-toggle" aria-label="Menu">&#9776;</button>
<div id="sidebar">
  <input type="text" id="search" placeholder="Cerca luogo...">
FILTER_PLACEHOLDER
  <div id="place-list">
SIDEBAR_PLACEHOLDER
  </div>
</div>
<div id="map"></div>
<script>
var places = [
PLACES_PLACEHOLDER
];

var catColors = {
CATCOLORS_PLACEHOLDER
};

var map = L.map('map',{zoomControl:true}).setView([48.2082,16.3738],13);

// Geolocation button
var locBtn = L.control({position:'topright'});
locBtn.onAdd = function(m) {
  var d = L.DomUtil.create('div','leaflet-bar');
  var a = L.DomUtil.create('a','loc-btn',d);
  a.href='#'; a.title='Mostra la mia posizione'; a.innerHTML='📍';
  a.style.cssText='font-size:18px;line-height:34px;text-align:center;display:block;width:34px;height:34px;';
  L.DomEvent.disableClickPropagation(d);
  L.DomEvent.on(a,'click',function(e){
    e.preventDefault();
    if (!navigator.geolocation) { alert('Geolocalizzazione non disponibile'); return; }
    // Toggle tracking
    if (window._locWatchId != null) {
      navigator.geolocation.clearWatch(window._locWatchId);
      window._locWatchId = null;
      if (window._locCircle) { map.removeLayer(window._locCircle); window._locCircle = null; }
      if (window._locMarker) { map.removeLayer(window._locMarker); window._locMarker = null; }
      a.innerHTML = '📍';
      a.style.backgroundColor = '';
      return;
    }
    a.innerHTML = '⏳';
    window._locWatchId = navigator.geolocation.watchPosition(function(pos){
      var lat=pos.coords.latitude, lng=pos.coords.longitude, acc=pos.coords.accuracy;
      if (window._locCircle) window._locCircle.setLatLng([lat,lng]).setRadius(acc);
      else window._locCircle = L.circle([lat,lng],{radius:acc,fillOpacity:0.1,color:'#3b82f6',weight:1}).addTo(map);
      if (window._locMarker) window._locMarker.setLatLng([lat,lng]);
      else window._locMarker = L.circleMarker([lat,lng],{radius:6,fillColor:'#3b82f6',fillOpacity:1,color:'#fff',weight:2}).addTo(map);
      map.setView([lat,lng],15);
      a.innerHTML = '🔵';
      a.style.backgroundColor = '#1e40af';
    },function(err){
      if (err.code !== 1) a.innerHTML = '📍';
      else { navigator.geolocation.clearWatch(window._locWatchId); window._locWatchId = null; }
    },{enableHighAccuracy:true,maxAge:5000});
  });
  return d;
};
locBtn.addTo(map);
L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',{
  attribution:'&copy; <a href="https://carto.com/">CARTO</a>',
  maxZoom:19
}).addTo(map);

var markers = L.layerGroup().addTo(map);

function popupContent(place) {
  var metro = place.metro ? ' <span class="metro-badge">🚇 ' + place.metro + '</span>' : '';
  var ring = place.type === 'ring_tram' ? ' <span class="ring-badge">Giro Tram 1/2</span>' : '';
  var note = place.note ? '<br><small>' + place.note + '</small>' : '';
  return (place.emoji ? place.emoji + ' ' : '') + '<b>' + place.name + '</b>' + metro + ring + note;
}

function createMarker(place) {
  var color = catColors[place.cat] || '#95a5a6';

  if (place.type === 'ring_tram') {
    var size = 30, half = size/2;
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'" viewBox="0 0 '+size+' '+size+'">'
      + '<polygon points="'+half+',2 '+(size-2)+','+half+' '+half+','+(size-2)+' 2,'+half+'" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/>'
      + '<text x="'+half+'" y="'+(half+1)+'" text-anchor="middle" dominant-baseline="middle" font-size="14">' + (place.emoji || '\U0001F68B') + '</text>'
      + '</svg>';
    var icon = L.divIcon({html:svg, className:'marker-icon', iconSize:[size,size], iconAnchor:[half,half]});
    return L.marker([place.lat,place.lng],{icon:icon}).bindPopup(popupContent(place));
  }

  if (place.type === 'home') {
    var s = 32;
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="'+s+'" height="'+s+'" viewBox="0 0 '+s+' '+s+'">'
      + '<rect x="2" y="2" width="'+(s-4)+'" height="'+(s-4)+'" rx="4" fill="#e74c3c" stroke="#fff" stroke-width="1.5"/>'
      + '<text x="'+(s/2)+'" y="'+(s/2+1)+'" text-anchor="middle" dominant-baseline="middle" font-size="18">' + (place.emoji || '\U0001F3E0') + '</text>'
      + '</svg>';
    var icon = L.divIcon({html:svg, className:'marker-icon', iconSize:[s,s], iconAnchor:[s/2,s/2]});
    return L.marker([place.lat,place.lng],{icon:icon}).bindPopup(popupContent(place));
  }

  if (place.type === 'transport') {
    var s = 24;
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="'+s+'" height="'+s+'" viewBox="0 0 '+s+' '+s+'">'
      + '<circle cx="'+(s/2)+'" cy="'+(s/2)+'" r="'+(s/2-2)+'" fill="#3498db" stroke="#fff" stroke-width="1.5"/>'
      + '<text x="'+(s/2)+'" y="'+(s/2+1)+'" text-anchor="middle" dominant-baseline="middle" fill="#fff" font-size="11" font-weight="bold">M</text>'
      + '</svg>';
    var icon = L.divIcon({html:svg, className:'marker-icon', iconSize:[s,s], iconAnchor:[s/2,s/2]});
    return L.marker([place.lat,place.lng],{icon:icon}).bindPopup(popupContent(place));
  }

  var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="34" viewBox="0 0 28 34">'
    + '<path d="M14 0C7.4 0 2 5.4 2 12c0 9 12 22 12 22s12-13 12-22C26 5.4 20.6 0 14 0z" fill="'+color+'" stroke="#fff" stroke-width="1.5"/>'
    + '<text x="14" y="16" text-anchor="middle" dominant-baseline="middle" font-size="13">' + (place.emoji || '\U0001F4CD') + '</text>'
    + '</svg>';
  var icon = L.divIcon({html:svg, className:'marker-icon', iconSize:[28,34], iconAnchor:[14,34]});
  return L.marker([place.lat,place.lng],{icon:icon}).bindPopup(popupContent(place));
}

places.forEach(function(place) {
  var marker = createMarker(place);
  marker.place = place;
  marker.on('click', function() {
    document.querySelectorAll('.place-item').forEach(function(el) { el.classList.remove('highlight'); });
    var items = document.querySelectorAll('.place-item');
    items.forEach(function(el) {
      if (el.dataset.name === place.name) el.classList.add('highlight');
    });
  });
  markers.addLayer(marker);
});

// Smart labels
var labelsVisible = false;
var labelMarkers = [];

function updateSmartLabels() {
  labelMarkers.forEach(function(lm) { map.removeLayer(lm); });
  labelMarkers = [];
  if (!labelsVisible) return;
  var visibleMarkers = [];
  markers.eachLayer(function(m) {
    if (m.place && map.hasLayer(m) && map.getBounds().contains(m.getLatLng())) {
      visibleMarkers.push(m);
    }
  });
  if (visibleMarkers.length > 8) return;
  visibleMarkers.forEach(function(m) {
    var p = m.place;
    var html = '<div class="marker-label"><b>' + p.name + '</b>';
    html += '<br><span style="font-size:10px;opacity:0.8">' + (p.emoji ? p.emoji + ' ' : '') + p.cat + '</span>';
    if (p.note && p.note.indexOf('VCC') !== -1) {
      var vccMatch = p.note.match(/VCC[\\s\\u2013\\-]+([^|]+)/);
      if (vccMatch) html += '<br><span style="font-size:10px;color:#4ade80">🔑 VCC ' + vccMatch[1].trim() + '</span>';
    }
    html += '</div>';
    var labelIcon = L.divIcon({html: html, className: 'marker-icon', iconSize: [160, 50], iconAnchor: [0, -20]});
    var lm = L.marker(m.getLatLng(), {icon: labelIcon, interactive: false, keyboard: false});
    labelMarkers.push(lm);
    map.addLayer(lm);
  });
}

map.on('zoomend moveend', updateSmartLabels);

function toggleFilterPanel() {
  var c = document.getElementById('filter-collapsible');
  var ch = document.getElementById('filter-chevron');
  c.classList.toggle('collapsed');
  ch.classList.toggle('collapsed');
}

document.getElementById('toggle-labels').addEventListener('change', function() {
  labelsVisible = this.checked;
  updateSmartLabels();
});

document.querySelectorAll('.place-item').forEach(function(el) {
  el.addEventListener('click', function() {
    var name = this.dataset.name;
    markers.eachLayer(function(m) {
      if (m.place.name === name) {
        map.flyTo(m.getLatLng(), 16);
        m.openPopup();
      }
    });
  });
});

function normalizeStr(s) {
  return s.toLowerCase()
    .replace(/\u00e4/g,'a').replace(/\u00f6/g,'o').replace(/\u00fc/g,'u').replace(/\u00df/g,'ss')
    .replace(/\u00e9/g,'e').replace(/\u00e8/g,'e').replace(/\u00ea/g,'e')
    .replace(/\u00e1/g,'a').replace(/\u00e0/g,'a')
    .replace(/\u00f3/g,'o').replace(/\u00f2/g,'o')
    .replace(/\u00ed/g,'i').replace(/\u00ec/g,'i')
    .replace(/\u00fa/g,'u').replace(/\u00f9/g,'u')
    .replace(/\u00f1/g,'n').replace(/\u00e7/g,'c')
    .replace(/[^a-z0-9\\s]/g,'');
}
document.getElementById('search').addEventListener('input', function() {
  var q = normalizeStr(this.value);
  var checkedCats = getCheckedCats();
  document.querySelectorAll('.place-item').forEach(function(el) {
    var nameNorm = normalizeStr(el.dataset.name);
    var searchMatch = !q || nameNorm.indexOf(q) >= 0;
    var cat = el.dataset.cat;
    var cat2 = el.dataset.cat2;
    var catVisible = checkedCats[cat] !== false;
    if (!catVisible && cat2 && checkedCats[cat2] !== false) catVisible = true;
    el.style.display = (searchMatch && catVisible) ? '' : 'none';
  });
  document.querySelectorAll('.cat-header').forEach(function(el) {
    var next = el.nextElementSibling;
    var anyVisible = false;
    while (next && !next.classList.contains('cat-header')) {
      if (next.style.display !== 'none') anyVisible = true;
      next = next.nextElementSibling;
    }
    el.style.display = anyVisible ? '' : 'none';
  });
});

document.getElementById('mobile-toggle').addEventListener('click', function() {
  document.getElementById('sidebar').classList.toggle('collapsed');
});

// Category filter logic — with cat2 cross-category support
var markerByPlace = {};
markers.eachLayer(function(m) {
  if (m.place) markerByPlace[m.place.name] = m;
});

function getCheckedCats() {
  var checkedCats = {};
  // Start: mark all known categories as false (unchecked)
  document.querySelectorAll('.cat-filter').forEach(function(cb) {
    checkedCats[cb.dataset.cat] = cb.checked;
  });
  // When any subcategory of a macro is checked, the macro name is also "checked"
  var ristoAny = false;
  document.querySelectorAll('.risto-sub').forEach(function(cb) { if (cb.checked) ristoAny = true; });
  checkedCats['Ristorazione'] = ristoAny;
  var shopAny = false;
  document.querySelectorAll('.shop-sub').forEach(function(cb) { if (cb.checked) shopAny = true; });
  checkedCats['Shopping'] = shopAny;
  var parkAny = false;
  document.querySelectorAll('.park-sub').forEach(function(cb) { if (cb.checked) parkAny = true; });
  checkedCats['Parchi'] = parkAny;
  return checkedCats;
}

function isPlaceVisible(place, checkedCats) {
  // Visible if primary category is checked
  if (checkedCats[place.cat]) return true;
  // Visible if secondary category is checked
  if (place.cat2 && checkedCats[place.cat2]) return true;
  return false;
}

function applyFilters() {
  var checkedCats = getCheckedCats();
  var activeCats = {};
  for (var c in checkedCats) { if (checkedCats[c]) activeCats[c] = true; }
  var hasActiveCat = Object.keys(activeCats).length > 0;
  
  markers.eachLayer(function(m) {
    if (m.place) {
      var visible = isPlaceVisible(m.place, checkedCats);
      if (visible && !map.hasLayer(m)) map.addLayer(m);
      if (!visible && map.hasLayer(m)) map.removeLayer(m);
    }
  });
  
  updateSmartLabels();
  
  // Update sidebar — hide items whose primary cat is off and no cat2 is active
  document.querySelectorAll('.place-item').forEach(function(el) {
    var cat = el.dataset.cat;
    var cat2 = el.dataset.cat2;
    var visible = checkedCats[cat] !== false;
    var viaCat2 = false;
    if (!visible && cat2 && checkedCats[cat2] !== false) {
      visible = true;
      viaCat2 = true;
    }
    el.style.display = visible ? '' : 'none';
    // Update richiamo tag
    var existingTag = el.querySelector('.richiamo-tag');
    if (viaCat2) {
      if (!existingTag) {
        var tag = document.createElement('span');
        tag.className = 'richiamo-tag';
        tag.textContent = '(via ' + cat2 + ')';
        el.appendChild(tag);
      }
    } else if (existingTag) {
      existingTag.remove();
    }
  });
  
  // Update cat headers — only show if there's a visible child AND
  // the cat itself is checked OR some child is shown via cat2 from elsewhere
  document.querySelectorAll('.cat-header').forEach(function(el) {
    var headerCat = el.dataset.cat;
    var anyVisible = false;
    var next = el.nextElementSibling;
    while (next && !next.classList.contains('cat-header')) {
      if (next.style.display !== 'none' && next.classList.contains('place-item')) {
        anyVisible = true;
        // Hide the header if this cat is NOT checked and child is only visible via cat2
        if (checkedCats[headerCat] === false) {
          anyVisible = false;
          break;
        }
      }
      next = next.nextElementSibling;
    }
    el.style.display = anyVisible ? '' : 'none';
  });
}

document.querySelectorAll('.cat-filter').forEach(function(cb) {
  cb.addEventListener('change', applyFilters);
});

document.getElementById('filter-all').addEventListener('click', function() {
  document.querySelectorAll('.cat-filter').forEach(function(cb) { cb.checked = true; });
  var mr = document.getElementById('macro-risto');
  if (mr) { mr.checked = true; mr.indeterminate = false; }
  var ms = document.getElementById('macro-shop');
  if (ms) { ms.checked = true; ms.indeterminate = false; }
  var mp = document.getElementById('macro-park');
  if (mp) { mp.checked = true; mp.indeterminate = false; }
  applyFilters();
});

document.getElementById('filter-none').addEventListener('click', function() {
  document.querySelectorAll('.cat-filter').forEach(function(cb) { cb.checked = false; });
  var mr = document.getElementById('macro-risto');
  if (mr) { mr.checked = false; mr.indeterminate = false; }
  var ms = document.getElementById('macro-shop');
  if (ms) { ms.checked = false; ms.indeterminate = false; }
  var mp = document.getElementById('macro-park');
  if (mp) { mp.checked = false; mp.indeterminate = false; }
  applyFilters();
});

// Macro Ristorazione
document.getElementById('macro-risto').addEventListener('change', function() {
  document.querySelectorAll('.risto-sub').forEach(function(cb) {
    cb.checked = this.checked;
  }.bind(this));
  applyFilters();
});

document.querySelectorAll('.risto-sub').forEach(function(cb) {
  cb.addEventListener('change', function() {
    var subs = document.querySelectorAll('.risto-sub');
    var checked = 0;
    subs.forEach(function(s) { if (s.checked) checked++; });
    var parent = document.getElementById('macro-risto');
    if (checked === subs.length) {
      parent.checked = true;
      parent.indeterminate = false;
    } else if (checked === 0) {
      parent.checked = false;
      parent.indeterminate = false;
    } else {
      parent.indeterminate = true;
    }
    applyFilters();
  });
});

// Macro Shopping
document.getElementById('macro-shop').addEventListener('change', function() {
  document.querySelectorAll('.shop-sub').forEach(function(cb) {
    cb.checked = this.checked;
  }.bind(this));
  applyFilters();
});

document.querySelectorAll('.shop-sub').forEach(function(cb) {
  cb.addEventListener('change', function() {
    var subs = document.querySelectorAll('.shop-sub');
    var checked = 0;
    subs.forEach(function(s) { if (s.checked) checked++; });
    var parent = document.getElementById('macro-shop');
    if (checked === subs.length) {
      parent.checked = true;
      parent.indeterminate = false;
    } else if (checked === 0) {
      parent.checked = false;
      parent.indeterminate = false;
    } else {
      parent.indeterminate = true;
    }
    applyFilters();
  });
});

// Macro Parchi
document.getElementById('macro-park').addEventListener('change', function() {
  document.querySelectorAll('.park-sub').forEach(function(cb) {
    cb.checked = this.checked;
  }.bind(this));
  applyFilters();
});

document.querySelectorAll('.park-sub').forEach(function(cb) {
  cb.addEventListener('change', function() {
    var subs = document.querySelectorAll('.park-sub');
    var checked = 0;
    subs.forEach(function(s) { if (s.checked) checked++; });
    var parent = document.getElementById('macro-park');
    if (checked === subs.length) {
      parent.checked = true;
      parent.indeterminate = false;
    } else if (checked === 0) {
      parent.checked = false;
      parent.indeterminate = false;
    } else {
      parent.indeterminate = true;
    }
    applyFilters();
  });
});

// Tram 1/2 routes — two independent directions with real road paths
var tramRouteCW = null;
var tramRouteCCW = null;
var tramStopsCW = [];
var tramStopsCCW = [];
var tramRouteCoordsCW = TRAM_ROUTE_CW_PLACEHOLDER;
var tramRouteCoordsCCW = TRAM_ROUTE_CCW_PLACEHOLDER;
var tramStopCoordsCW = TRAM_STOPS_CW_PLACEHOLDER;
var tramStopCoordsCCW = TRAM_STOPS_CCW_PLACEHOLDER;

function toggleTramLayer(routeVar, stopsVar, addFn, removeFn) {
  return function() {
    if (this.checked) {
      addFn();
    } else {
      removeFn();
    }
  };
}

document.getElementById('toggle-tram-cw').addEventListener('change', function() {
  if (this.checked) {
    tramRouteCW = L.polyline(tramRouteCoordsCW, {color: '#1b5e20', weight: 5, opacity: 0.8}).addTo(map);
    tramStopCoordsCW.forEach(function(s) {
      var stop = L.circleMarker(s, {radius: 5, color: '#1b5e20', fillColor: '#ffffff', fillOpacity: 1, weight: 2}).addTo(map);
      tramStopsCW.push(stop);
    });
  } else {
    if (tramRouteCW) { map.removeLayer(tramRouteCW); tramRouteCW = null; }
    tramStopsCW.forEach(function(s) { map.removeLayer(s); });
    tramStopsCW = [];
  }
});

document.getElementById('toggle-tram-ccw').addEventListener('change', function() {
  if (this.checked) {
    tramRouteCCW = L.polyline(tramRouteCoordsCCW, {color: '#1565c0', weight: 5, opacity: 0.8, dashArray: '8 6'}).addTo(map);
    tramStopCoordsCCW.forEach(function(s) {
      var stop = L.circleMarker(s, {radius: 5, color: '#1565c0', fillColor: '#ffffff', fillOpacity: 1, weight: 2}).addTo(map);
      tramStopsCCW.push(stop);
    });
  } else {
    if (tramRouteCCW) { map.removeLayer(tramRouteCCW); tramRouteCCW = null; }
    tramStopsCCW.forEach(function(s) { map.removeLayer(s); });
    tramStopsCCW = [];
  }
});
</script>
</body>
<script>if('serviceWorker'in navigator)navigator.serviceWorker.register('sw.js');</script>
</html>"""

# Substitute placeholders
html_content = html_content.replace("SIDEBAR_PLACEHOLDER", sidebar_html)
html_content = html_content.replace("FILTER_PLACEHOLDER", filter_html)
html_content = html_content.replace("PLACES_PLACEHOLDER", places_data)
html_content = html_content.replace("CATCOLORS_PLACEHOLDER", cat_colors_js)

# Load tram route data
with open('/opt/data/vienna-map/tram-route-cw.json') as f:
    cw_coords = json.load(f)
with open('/opt/data/vienna-map/tram-route-ccw.json') as f:
    ccw_coords = json.load(f)
with open('/opt/data/vienna-map/tram-stops-cw.json') as f:
    cw_stops = json.load(f)
with open('/opt/data/vienna-map/tram-stops-ccw.json') as f:
    ccw_stops = json.load(f)

html_content = html_content.replace("TRAM_ROUTE_CW_PLACEHOLDER", json.dumps(cw_coords))
html_content = html_content.replace("TRAM_ROUTE_CCW_PLACEHOLDER", json.dumps(ccw_coords))
html_content = html_content.replace("TRAM_STOPS_CW_PLACEHOLDER", json.dumps(cw_stops))
html_content = html_content.replace("TRAM_STOPS_CCW_PLACEHOLDER", json.dumps(ccw_stops))

with open('/opt/data/vienna-map/vienna-tutti-luoghi.html', 'w') as f:
    f.write(html_content)

size = os.path.getsize('/opt/data/vienna-map/vienna-tutti-luoghi.html')
print("HTML generato: %d bytes (%.1f KB)" % (size, size/1024))
print("Luoghi: %d" % len(places))
print("Categorie: %d" % len(cats))
ring_count = sum(1 for p in places if p.get('type') == 'ring_tram')
print("Giro Tram: %d" % ring_count)
