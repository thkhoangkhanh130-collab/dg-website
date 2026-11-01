/* Dương Gia — xnkduonggia.vn
   Giá niêm yết + tình trạng kho đọc trực tiếp từ hệ thống DG Đặt Hàng (cổng công khai, không có giá đại lý).
   Nội dung tĩnh trong trang là bản chụp lúc dựng — trang vẫn hiển thị đầy đủ khi không kết nối được hệ thống. */
(function () {
  'use strict';
  var API = 'https://script.google.com/macros/s/AKfycbw6S1jHEfsWmsyHwW3COmzDLawIWZWzG35yVnyuU_TujN0s7rDlRUZu50-E4Uxyp0lBzQ/exec';
  var HOTLINE = '0973 929 321';
  var TTL = 10 * 60 * 1000;

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function fmt(n) { n = Number(n); return (isFinite(n) && n > 0) ? n.toLocaleString('vi-VN') + ' đ' : 'Liên hệ'; }
  function key(s) { return String(s || '').toLowerCase().replace(/\s+/g, ' ').trim(); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function stKey(tt) {
    tt = String(tt || '');
    if (tt === 'Còn hàng') return 'ok';
    if (tt === 'Sắp hết') return 'warn';
    if (tt === 'Sắp về') return 'info';
    return 'off';
  }
  function stLabel(tt) { var k = stKey(tt); return k === 'ok' ? 'Còn hàng' : k === 'warn' ? 'Sắp hết hàng' : k === 'info' ? 'Sắp về hàng' : 'Tạm hết hàng'; }
  function setStatus(el, tt) { if (!el) return; var k = stKey(tt); el.className = el.className.replace(/\bst-\w+\b/g, '').trim() + ' st-' + k; el.textContent = stLabel(tt); }
  function store(k, v) { try { sessionStorage.setItem(k, JSON.stringify({ t: Date.now(), v: v })); } catch (e) { } }
  function load(k) { try { var o = JSON.parse(sessionStorage.getItem(k) || 'null'); return o && Date.now() - o.t < TTL ? o.v : null; } catch (e) { return null; } }

  function call(ten, args) {
    var ctl = ('AbortController' in window) ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) ctl.abort(); }, 15000);
    return fetch(API, { method: 'POST', body: JSON.stringify({ token: '', ten: ten, args: args || {} }), signal: ctl ? ctl.signal : undefined })
      .then(function (r) { return r.text(); })
      .then(function (txt) {
        clearTimeout(timer);
        var j = JSON.parse(txt);
        if (!j.ok) { var e = new Error(j.thongBao || 'Hệ thống chưa phản hồi.'); e.api = true; throw e; }
        return j.data;
      }, function (err) { clearTimeout(timer); throw err; });
  }
  function cached(ten) {
    var c = load('dg_' + ten); if (c) return Promise.resolve(c);
    return call(ten, { lang: 'vi' }).then(function (d) { store('dg_' + ten, d); return d; });
  }

  /* ---------- menu điện thoại ---------- */
  var burger = $('.burger'), drawer = $('#drawer');
  if (burger && drawer) burger.addEventListener('click', function () {
    var open = drawer.hidden; drawer.hidden = !open; burger.setAttribute('aria-expanded', String(open));
  });

  /* ---------- ưu đãi có thời hạn ---------- */
  $$('[data-until]').forEach(function (el) {
    var d = new Date(el.getAttribute('data-until') + 'T23:59:59+07:00');
    if (!isNaN(d) && Date.now() > d.getTime()) el.hidden = true;
  });

  /* ---------- trang mẫu gai: chọn cỡ ---------- */
  var pdEl = $('#pdata'), PD = null;
  if (pdEl) { try { PD = JSON.parse(pdEl.textContent); } catch (e) { PD = null; } }
  var showPrice = true;
  function renderSel() {
    if (!PD) return;
    var s = PD.skus[PD.sel] || PD.skus[0]; if (!s) return;
    $$('.sz').forEach(function (b) { b.setAttribute('aria-pressed', String(Number(b.getAttribute('data-i')) === PD.sel)); });
    ['li', 'od', 'sw', 'td', 'rim', 'single', 'dual'].forEach(function (k) { var el = $('#kv-' + k); if (el) el.textContent = s[k] || '—'; });
    var pl = $('#p-pl'); if (pl) pl.textContent = 'Giá niêm yết · ' + s.size + ' ' + s.pr;
    var pr = $('#p-price'); if (pr) pr.textContent = showPrice ? fmt(s.price) : 'Liên hệ';
    setStatus($('#p-status'), s.status);
    var q = $('#p-quote'); if (q) q.href = q.getAttribute('data-base') + '?ma=' + encodeURIComponent(s.label);
  }
  $$('.sz').forEach(function (b) { b.addEventListener('click', function () { PD.sel = Number(b.getAttribute('data-i')); renderSel(); }); });
  if (PD) { var h0 = location.hash.slice(1); PD.skus.forEach(function (s, i) { if (h0 && s.anchor === h0) PD.sel = i; }); if (h0) renderSel(); }

  /* ---------- danh mục: lọc ---------- */
  var list = $('#sp-list'), F = { route: '', size: '', type: '', avail: false };
  function applyFilter(push) {
    if (!list) return;
    var cards = $$('.pc', list), n = 0;
    cards.forEach(function (c) {
      var st = c.getAttribute('data-status');
      var ok = (!F.route || c.getAttribute('data-route') === F.route) && (!F.size || c.getAttribute('data-size') === F.size) &&
        (!F.type || c.getAttribute('data-type') === F.type) && (!F.avail || st === 'ok' || st === 'warn');
      c.hidden = !ok; if (ok) n++;
    });
    var cnt = $('#f-count'); if (cnt) cnt.textContent = n + ' quy cách';
    var em = $('#f-empty'); if (em) em.hidden = n > 0;
    $$('.chip[data-route]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-route') === F.route)); });
    if (push && window.history && history.replaceState) {
      var p = []; if (F.size) p.push('size=' + encodeURIComponent(F.size)); if (F.route) p.push('route=' + F.route); if (F.type) p.push('type=' + F.type); if (F.avail) p.push('avail=1');
      try { history.replaceState(null, '', location.pathname + (p.length ? '?' + p.join('&') : '')); } catch (e) { }
    }
  }
  function sortList() {
    if (!list) return;
    var rank = { ok: 0, warn: 0, info: 1, off: 2 };
    $$('.pc', list).sort(function (a, b) {
      return (rank[a.getAttribute('data-status')] - rank[b.getAttribute('data-status')]) || (Number(a.getAttribute('data-idx')) - Number(b.getAttribute('data-idx')));
    }).forEach(function (c) { list.appendChild(c); });
  }
  if (list) {
    var qs = {}; location.search.replace(/^\?/, '').split('&').forEach(function (kv) { var p = kv.split('='); if (p[0]) qs[p[0]] = decodeURIComponent((p[1] || '').replace(/\+/g, ' ')); });
    F.size = qs.size || ''; F.route = qs.route || ''; F.type = qs.type || ''; F.avail = qs.avail === '1';
    var fs = $('#f-size'), ft = $('#f-type'), fa = $('#f-avail');
    if (fs) { fs.value = F.size; fs.addEventListener('change', function () { F.size = fs.value; applyFilter(true); }); }
    if (ft) { ft.value = F.type; ft.addEventListener('change', function () { F.type = ft.value; applyFilter(true); }); }
    if (fa) { fa.checked = F.avail; fa.addEventListener('change', function () { F.avail = fa.checked; applyFilter(true); }); }
    $$('.chip[data-route]').forEach(function (b) { b.addEventListener('click', function () { F.route = b.getAttribute('data-route'); applyFilter(true); }); });
    var fr = $('#f-reset'); if (fr) fr.addEventListener('click', function () { F = { route: '', size: '', type: '', avail: false }; if (fs) fs.value = ''; if (ft) ft.value = ''; if (fa) fa.checked = false; applyFilter(true); });
    applyFilter(false);
  }

  /* ---------- trang chủ: hàng có sẵn ---------- */
  function applyFeatured() {
    $$('[data-featured]').forEach(function (box) {
      var lim = Number(box.getAttribute('data-limit')) || 8, n = 0;
      $$('.pc', box).forEach(function (c) { var st = c.getAttribute('data-status'), show = (st === 'ok' || st === 'warn') && n < lim; c.hidden = !show; if (show) n++; });
      var em = $('[data-featured-empty]'); if (em) em.hidden = n > 0;
    });
  }

  /* ---------- dữ liệu sống từ hệ thống ---------- */
  function stamp() {
    var d = new Date(), p = function (x) { return (x < 10 ? '0' : '') + x; };
    $$('.js-stamp').forEach(function (el) { el.textContent = 'Giá và tình trạng hàng cập nhật từ hệ thống lúc ' + p(d.getHours()) + ':' + p(d.getMinutes()) + ' ' + p(d.getDate()) + '/' + p(d.getMonth() + 1) + '/' + d.getFullYear() + '.'; });
  }
  var needCat = $$('[data-sku]').length > 0 || !!PD;
  if (needCat) cached('catalog').then(function (data) {
    var map = {}; (data.san_pham || []).forEach(function (p) { map[key(p.ma_sp)] = p; });
    showPrice = data.hien_niem_yet !== false;
    $$('[data-sku]').forEach(function (el) {
      var p = map[el.getAttribute('data-sku')]; if (!p) return;
      var pe = $('.js-price', el); if (pe) pe.textContent = showPrice ? fmt(p.gia_niem_yet) : 'Liên hệ';
      setStatus($('.js-status', el), p.tinh_trang);
      el.setAttribute('data-status', stKey(p.tinh_trang));
    });
    if (PD) { PD.skus.forEach(function (s) { var p = map[s.sku]; if (p) { s.price = p.gia_niem_yet; s.status = p.tinh_trang; } }); renderSel(); }
    sortList(); applyFilter(false); applyFeatured(); stamp();
  })['catch'](function () { /* giữ dữ liệu đã dựng sẵn */ });

  var tiers = $('[data-tiers]');
  if (tiers) cached('thongTin').then(function (d) {
    (d.hang_ds || []).forEach(function (h) {
      var box = $('.tier[data-tier="' + String(h.ten).replace(/"/g, '') + '"] .js-ql', tiers); if (!box || !h.quyen_loi) return;
      box.innerHTML = String(h.quyen_loi).split(/\s*·\s*|\n+/).filter(Boolean).map(function (x) { return '<li>' + esc(x.charAt(0).toUpperCase() + x.slice(1)) + '</li>'; }).join('');
    });
  })['catch'](function () { });

  /* ---------- form: yêu cầu báo giá / đăng ký đại lý → hệ thống DG Đặt Hàng ---------- */
  function phone(v) { v = String(v || '').replace(/[^\d+]/g, ''); if (v.indexOf('+84') === 0) v = '0' + v.slice(3); else if (/^84\d{9,10}$/.test(v)) v = '0' + v.slice(2); return v; }
  function val(f, n) { var el = f.elements[n]; return el ? String(el.value || '').trim() : ''; }
  $$('form[data-form]').forEach(function (f) {
    var kind = f.getAttribute('data-form'), msg = $('.msg', f), btn = $('button[type=submit]', f);
    function say(cls, html) { if (!msg) return; msg.className = 'msg full ' + cls; msg.innerHTML = html; msg.hidden = false; }
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (val(f, 'website')) { say('ok', 'Dương Gia đã nhận thông tin.'); f.reset(); return; }
      var sdt = phone(val(f, 'dien_thoai')), ten = val(f, 'ten') || val(f, 'nguoi_lien_he');
      if (!ten) { say('err', 'Vui lòng nhập tên cửa hàng, đơn vị hoặc họ tên.'); return; }
      if (!/^0\d{9,10}$/.test(sdt)) { say('err', 'Số điện thoại chưa đúng — cần 10–11 số, bắt đầu bằng 0.'); return; }
      if (f.elements.consent && !f.elements.consent.checked) { say('err', 'Vui lòng đồng ý để Dương Gia dùng thông tin này liên hệ với bạn.'); return; }
      var parts = kind === 'dai-ly'
        ? ['[Website · Đăng ký đại lý]', val(f, 'loai_hinh'), val(f, 'mst') ? 'MST: ' + val(f, 'mst') : '', val(f, 'ghi_chu')]
        : ['[Website · Yêu cầu báo giá]', val(f, 'ma') ? 'Lốp: ' + val(f, 'ma') : '', val(f, 'so_luong') ? 'SL: ' + val(f, 'so_luong') : '', val(f, 'ghi_chu')];
      parts.splice(1, 0, 'Đã đồng ý CS bảo mật');
      var args = { ten: ten, nguoi_lien_he: val(f, 'nguoi_lien_he'), dien_thoai: sdt, tinh_thanh: val(f, 'tinh_thanh'), loai_xe: val(f, 'loai_xe'), ghi_chu: parts.filter(Boolean).join(' · ').slice(0, 300), lang: 'vi' };
      if (btn) btn.disabled = true; say('', 'Đang gửi…');
      call('dangKyDaiLy', args).then(function () {
        say('ok', '<b>Dương Gia đã nhận thông tin.</b> Chúng tôi sẽ liên hệ số ' + esc(sdt) + ' trong giờ làm việc. Cần gấp, vui lòng gọi hoặc Zalo ' + HOTLINE + '.');
        f.reset();
      })['catch'](function (err) {
        if (err && err.api) say('err', esc(err.message));
        else say('err', 'Chưa gửi được do lỗi kết nối. Vui lòng gọi hoặc Zalo <b>' + HOTLINE + '</b> — Dương Gia sẽ hỗ trợ ngay.');
      }).then(function () { if (btn) btn.disabled = false; });
    });
  });
  var qma = $('#q-ma');
  if (qma) { var m = /[?&]ma=([^&]+)/.exec(location.search); if (m) qma.value = decodeURIComponent(m[1].replace(/\+/g, ' ')); }
})();
