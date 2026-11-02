# -*- coding: utf-8 -*-
"""Dựng website xnkduonggia.vn.   python3 build.py site     → thư mục site/ (đưa lên GitHub Pages)
                                   python3 build.py preview  → thư mục preview/ (CSS/JS nhúng thẳng, để xem thử)"""
import json, html, os, re, shutil, sys
from collections import OrderedDict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import SKUS, IMAGES, ROUTE, ROUTE_LABEL, ROAD_VI, CTY, TIERS, PROMO, SNAPSHOT_AT

B = os.path.dirname(os.path.abspath(__file__))
MODE = sys.argv[1] if len(sys.argv) > 1 else 'site'
OUT = os.path.join(B, MODE)
_sp = os.path.join(B, 'catalog_specs.json')
SPECS = json.load(open(_sp if os.path.exists(_sp) else os.path.join(B, '..', 'catalog_specs.json'), encoding='utf-8'))
IMG_SRC = os.path.join(B, 'src', 'img') if os.path.isdir(os.path.join(B, 'src', 'img')) else os.path.join(B, '..', 'img')
CSS = open(os.path.join(B, 'src', 'site.css'), encoding='utf-8').read()
JS = open(os.path.join(B, 'src', 'site.js'), encoding='utf-8').read()
e = lambda s: html.escape(str(s), quote=True)
TODAY = '2026-11-02'

# ------------------------------------------------------------------ dữ liệu
def key(s): return re.sub(r'\s+', ' ', str(s)).strip().lower()
def pat(g): return str(g).upper()
def slug(g): return pat(g).lower().replace('+', '-plus')
def prd(s): return re.sub(r'\D', '', str(s))
def num(n): return '{:,}'.format(int(n)).replace(',', '.')
def vnd(n): return num(n) + ' đ' if n else 'Liên hệ'
def dec(s):
    s = str(s).strip()
    if not s: return ''
    if re.match(r'^\d+\.0+$', s): s = s.split('.')[0]
    return s.replace('.', ',')
def rim(m):
    m = str(m).strip()
    d = re.match(r'^\d{4}-05-(\d{2})$', m)          # lỗi Sheets: "7.5" → 07/05
    if d: return '%d.50' % int(d.group(1))
    if re.match(r'^\d+$', m): return m + '.00'
    return m
def load_txt(s):
    if not s or '/' not in s: return ''
    kg, kpa = s.split('/')[:2]
    return '%s kg · %s kPa' % (num(kg), kpa)
def st_key(t): return {'Còn hàng': 'ok', 'Sắp hết': 'warn', 'Sắp về': 'info'}.get(t, 'off')
def st_label(t): return {'ok': 'Còn hàng', 'warn': 'Sắp hết hàng', 'info': 'Sắp về hàng'}.get(st_key(t), 'Tạm hết hàng')
def size_sort(s):
    lt = 'LT' in s
    m = re.match(r'^([\d.]+)(?:/(\d+))?R([\d.]+)', s)
    w, r = float(m.group(1)), float(m.group(3))
    return (lt, r, w if w < 30 else w / 25.4)
def anchor(it): return 'c-' + re.sub(r'[^a-z0-9]+', '-', (it['size'] + '-' + it['pr']).lower()).strip('-')

def cat_row(P, size, pr, ss):
    rows = [r for r in SPECS.get(P, {}).get('rows', []) if r[0] == size and prd(r[1]) == prd(pr)]
    if not rows: return None
    for r in rows:
        if r[3] == ss: return r
    return rows[0]

ITEMS = []
for i, (ma, qc, g, pr, li, ss, mam, tt, gia) in enumerate(SKUS):
    P = pat(g); r = cat_row(P, qc, pr, ss)
    star = ('★' in r[1]) if r else ('*' in pr)
    it = {'i': i, 'ma': ma, 'k': key(ma), 'size': qc, 'g': P, 'pr': prd(pr) + 'PR' + ('★' if star else ''),
          'li': (r[2] if r else li), 'ss': (r[3] if r else ss), 'rim': (r[7] if r else rim(mam)),
          'od': (num(r[4]) + ' mm') if r else '', 'sw': (r[5] + ' mm') if r else '', 'td': (dec(r[6]) + ' mm') if r else '',
          'single': load_txt(r[8]) if r else '', 'dual': load_txt(r[9]) if r else '',
          'status': tt, 'price': gia, 'route': ROUTE.get(P, ''), 'type': 'lt' if 'LT' in qc else 'tbr', 'img': P in IMAGES, 'cat': bool(r)}
    it['label'] = '%s · %s %s' % (P, qc, it['pr'])
    it['anchor'] = anchor(it)
    it['li_full'] = (it['li'] + ' ' + it['ss']).strip()
    ITEMS.append(it)

PATTERNS = OrderedDict()
for it in sorted(ITEMS, key=lambda x: (x['type'] == 'lt', ['cao-toc', 'hon-hop', 'cong-trinh', ''].index(x['route']), not x['img'], x['g'])):
    PATTERNS.setdefault(it['g'], []).append(it)
for P in PATTERNS: PATTERNS[P].sort(key=lambda x: size_sort(x['size']))
SIZES = sorted({it['size'] for it in ITEMS}, key=size_sort)
N_PAT, N_SKU = len(PATTERNS), len(ITEMS)

def road_txt(P):
    road = SPECS.get(P, {}).get('road') or []
    out = []
    for x in road:
        v = ROAD_VI.get(x.strip().lower())
        if v and v not in out: out.append(v)
    return ', '.join(out)

def pattern_sub(P, items):
    rt = ROUTE.get(P, '')
    if items[0]['type'] == 'lt': return 'Lốp tải nhẹ radial WYNSTAR cho xe tải nhẹ, cỡ vành 16 inch.'
    return {
        'cao-toc': 'Lốp tải radial toàn thép cho tuyến cao tốc và quốc lộ: chịu tải nặng, sinh nhiệt thấp, chống mòn và chống nứt rãnh gai khi chạy đường dài.',
        'hon-hop': 'Lốp tải radial toàn thép cho tuyến hỗn hợp, đường nhựa và đường xấu: chịu tải nặng, chống cắt, chống mòn, đáy rãnh chống kẹt đá.',
        'cong-trinh': 'Lốp tải radial toàn thép cho đường mỏ, công trường và đường hỗn hợp: chống cắt, chống kẹt đá, chịu va đập.',
    }.get(rt, 'Lốp tải radial toàn thép WYNSTAR. Liên hệ Dương Gia để được tư vấn điều kiện sử dụng phù hợp.')

# ------------------------------------------------------------------ khung trang
FONTS = 'https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap'
NAV = [('san-pham', 'Sản phẩm', 'san-pham/'), ('wynstar', 'Thương hiệu WYNSTAR', 'thuong-hieu-wynstar.html'), ('dai-ly', 'Dành cho đại lý', 'dai-ly.html'),
       ('bao-hanh', 'Bảo hành & Kỹ thuật', 'bao-hanh.html'), ('gioi-thieu', 'Về Dương Gia', 'gioi-thieu.html'), ('lien-he', 'Liên hệ', 'lien-he.html')]

def href(r, path):
    """path dạng 'san-pham/' | 'dai-ly.html' | '' (trang chủ)"""
    if MODE == 'preview':
        if path == '': return r + 'index.html'
        if path.endswith('/'): return r + path + 'index.html'
    else:
        if path == '': return r or './'
    return r + path

PHONE_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>'
NOIMG = '<div class="noimg"><div><svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="26" fill="none" stroke="currentColor" stroke-width="7"/><circle cx="32" cy="32" r="10" fill="none" stroke="currentColor" stroke-width="3"/></svg>Ảnh đang cập nhật</div></div>'

TAB = {'': 'Dương Gia', 'san-pham/': 'Sản phẩm', 'dai-ly.html': 'Đại lý', 'thuong-hieu-wynstar.html': 'WYNSTAR', 'bao-hanh.html': 'Bảo hành', 'gioi-thieu.html': 'Về chúng tôi', 'lien-he.html': 'Liên hệ', 'chinh-sach.html': 'Chính sách', '404.html': 'Không tìm thấy trang'}
def tab_title(path, title):
    if path == '': return 'Dương Gia'
    if path in TAB: return 'Dương Gia · ' + TAB[path]
    m = re.match(r'san-pham/(.+)\.html$', path)
    return 'Dương Gia · ' + (m.group(1).upper() if m else title)
def page(path, depth, title, desc, active, body, ld=None, og_title=None):
    r = '../' * depth
    canon = CTY['domain'] + '/' + path
    style = '<style>' + CSS + '</style>' if MODE == 'preview' else '<link rel="stylesheet" href="%sassets/site.css?v=%s">' % (r, TODAY.replace('-', ''))
    script = '<script>' + JS + '</script>' if MODE == 'preview' else '<script src="%sassets/site.js?v=%s" defer></script>' % (r, TODAY.replace('-', ''))
    lds = ''.join('<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False).replace('</', '<\\/') for x in (ld or []))
    menu = ''.join('<li><a href="%s"%s>%s</a></li>' % (href(r, p), ' aria-current="page"' if k == active else '', e(t)) for k, t, p in NAV)
    return f'''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(tab_title(path, title))}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="vi_VN">
<meta property="og:site_name" content="Dương Gia">
<meta property="og:title" content="{e(og_title or title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canon)}">
<meta property="og:image" content="{CTY['domain']}/img/og.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#232220">
<link rel="icon" href="{r}img/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="{r}img/favicon-32.png">
<link rel="apple-touch-icon" href="{r}img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
{style}
{lds}
</head>
<body>
<a class="skip" href="#main">Bỏ qua menu</a>
<div class="topbar"><div class="wrap">
  <span>Nhà phân phối <b>WYNSTAR</b> tại Việt Nam · Lốp tải radial toàn thép</span>
  <span class="r">Hotline · Zalo <a href="tel:{CTY['tel']}"><b>{CTY['hotline']}</b></a></span>
</div></div>
<header class="nav"><div class="wrap">
  <a class="logo" href="{href(r, '')}" aria-label="Dương Gia — trang chủ"><img src="{r}img/logo-dg-trang.png" alt="Dương Gia" width="97" height="40"></a>
  <nav aria-label="Menu chính"><ul class="menu">{menu}</ul></nav>
  <a class="btn btn-pri cta" href="{CTY['app']}" rel="noopener">Đặt hàng đại lý</a>
  <button class="burger" type="button" aria-label="Mở menu" aria-expanded="false" aria-controls="drawer"><svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
</div>
<div class="drawer" id="drawer" hidden><div class="wrap"><ul>{menu}</ul><a class="btn btn-pri" href="{CTY['app']}" rel="noopener">Đặt hàng đại lý</a></div></div>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
  <div class="wrap">
    <div><img src="{r}img/logo-dg-trang.png" alt="Dương Gia" width="83" height="34" style="height:34px;width:auto;margin-bottom:14px">
      <p class="co"><b>{CTY['ten']}</b><br>MST/ĐKDN {CTY['mst']} · cấp lần đầu 13/01/2025, Sở KH&amp;ĐT tỉnh Đắk Lắk<br>Trụ sở: {CTY['dia_chi']}<br>Hotline · Zalo: <a href="tel:{CTY['tel']}">{CTY['hotline']}</a> · Email: <a href="mailto:{CTY['email']}">{CTY['email']}</a></p></div>
    <div><h2>Sản phẩm &amp; đại lý</h2><ul><li><a href="{href(r, 'san-pham/')}">Lốp WYNSTAR</a></li><li><a href="{href(r, 'dai-ly.html')}">Chương trình đại lý</a></li><li><a href="{CTY['app']}" rel="noopener">Ứng dụng DG Đặt Hàng ↗</a></li><li><a href="{href(r, 'bao-hanh.html')}">Bảo hành &amp; kỹ thuật</a></li></ul></div>
    <div><h2>Công ty</h2><ul><li><a href="{href(r, 'gioi-thieu.html')}">Về Dương Gia</a></li><li><a href="{href(r, 'thuong-hieu-wynstar.html')}">Thương hiệu WYNSTAR</a></li><li><a href="{href(r, 'lien-he.html')}">Liên hệ</a></li><li><a href="{href(r, 'chinh-sach.html')}">Chính sách &amp; điều khoản</a></li></ul></div>
  </div>
  <div class="legal"><div class="wrap"><span>© 2026 Dương Gia · Nhà phân phối WYNSTAR tại Việt Nam</span><span>{CTY['slogan']}</span></div></div>
</footer>
<div class="fab" aria-label="Liên hệ nhanh"><a class="z" href="{CTY['zalo']}" rel="noopener" aria-label="Nhắn Zalo Dương Gia">Zalo</a><a class="p" href="tel:{CTY['tel']}" aria-label="Gọi {CTY['hotline']}">{PHONE_SVG}</a></div>
<nav class="callbar" aria-label="Liên hệ nhanh"><a class="c1" href="tel:{CTY['tel']}">{PHONE_SVG} Gọi {CTY['hotline']}</a><a class="c2" href="{CTY['zalo']}" rel="noopener">Chat Zalo</a></nav>
{script}
</body>
</html>
'''

def crumbs(r, trail, light=False):
    parts = ['<a href="%s">Trang chủ</a>' % href(r, '')]
    for t, p in trail[:-1]: parts.append('<a href="%s">%s</a>' % (href(r, p), e(t)))
    parts.append('<b>%s</b>' % e(trail[-1][0]))
    return '<p class="crumb%s">%s</p>' % (' light' if light else '', ' › '.join(parts))

def ld_crumbs(trail):
    items = [{'@type': 'ListItem', 'position': 1, 'name': 'Trang chủ', 'item': CTY['domain'] + '/'}]
    for n, (t, p) in enumerate(trail, 2): items.append({'@type': 'ListItem', 'position': n, 'name': t, 'item': CTY['domain'] + '/' + p})
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': items}

def pagehead(r, trail, eyebrow, h1, lead, extra='', h1_html=None):
    return f'''<section class="pagehead"><div class="wrap">{crumbs(r, trail)}<p class="eyebrow">{e(eyebrow)}</p><h1 class="disp">{h1_html or e(h1)}</h1><p class="lead">{lead}</p>{extra}</div></section>'''

def card(it, r, hidden=False):
    img = ('<img src="%simg/lop/%s.jpg" alt="Mẫu gai WYNSTAR %s" loading="lazy" width="600" height="600">' % (r, slug(it['g']), e(it['g']))) if it['img'] else NOIMG
    rl = ROUTE_LABEL.get(it['route']) or ('Lốp tải nhẹ' if it['type'] == 'lt' else 'Lốp tải radial')
    spec = ['<span>Chỉ số <b>%s</b></span>' % e(it['li_full'] or '—')]
    if it['td']: spec.append('<span>Sâu gai <b>%s</b></span>' % e(it['td']))
    if it['single']: spec.append('<span>Tải đơn <b>%s</b></span>' % e(it['single'].split(' · ')[0]))
    if it['rim']: spec.append('<span>Mâm <b>%s</b></span>' % e(it['rim']))
    return (f'<a class="pc" href="{r}san-pham/{slug(it["g"])}.html#{it["anchor"]}" data-sku="{e(it["k"])}" data-route="{it["route"]}" data-size="{e(it["size"])}" '
            f'data-type="{it["type"]}" data-status="{st_key(it["status"])}" data-idx="{it["i"]}"{" hidden" if hidden else ""}>'
            f'<div class="img">{img}<span class="st js-status st-{st_key(it["status"])}">{st_label(it["status"])}</span></div>'
            f'<div class="route">{e(rl)}</div><div class="code disp">{e(it["g"])}</div><div class="size">{e(it["size"])} · {e(it["pr"])}</div>'
            f'<div class="spec">{"".join(spec)}</div><div class="pl">Giá niêm yết</div><div class="price js-price">{vnd(it["price"])}</div>'
            f'<div class="vat">đã gồm VAT · 1 lốp</div><div class="more"><span>Chi tiết</span><span aria-hidden="true">→</span></div></a>')

def tiers_html(r):
    out = []
    for n, (t, sub, ql) in enumerate(TIERS):
        li = ''.join('<li>%s</li>' % e(x[0].upper() + x[1:]) for x in re.split(r'\s*·\s*', ql) if x)
        out.append(f'<div class="tier{" hl" if n == 1 else ""}" data-tier="{e(t)}"><div class="nm disp">{e(t)}</div><div class="sub">{e(sub)}</div><ul class="js-ql">{li}</ul></div>')
    return '<div class="tiers" data-tiers>' + ''.join(out) + '</div>'

def form_bao_gia(r, light=False, prefill=''):
    dl = ''.join('<option value="%s"></option>' % e(it['label']) for it in sorted(ITEMS, key=lambda x: (x['g'], size_sort(x['size']))))
    return f'''<form class="form{' light' if light else ''}" data-form="bao-gia" novalidate>
  <div class="full"><h3 class="disp" style="font-size:28px;margin:0 0 4px">Yêu cầu báo giá</h3><p class="note">Dương Gia gọi lại trong giờ làm việc. Trường có dấu * là bắt buộc.</p></div>
  <div><label class="lb" for="q-ten">Cửa hàng / đơn vị *</label><input id="q-ten" name="ten" type="text" autocomplete="organization" placeholder="Vận tải Minh An"></div>
  <div><label class="lb" for="q-lh">Người liên hệ</label><input id="q-lh" name="nguoi_lien_he" type="text" autocomplete="name" placeholder="Anh Minh"></div>
  <div><label class="lb" for="q-sdt">Số điện thoại / Zalo *</label><input id="q-sdt" name="dien_thoai" type="tel" inputmode="tel" autocomplete="tel" placeholder="09xx xxx xxx"></div>
  <div><label class="lb" for="q-tinh">Tỉnh / thành</label><input id="q-tinh" name="tinh_thanh" type="text" placeholder="Đắk Lắk"></div>
  <div><label class="lb" for="q-ma">Lốp quan tâm</label><input id="q-ma" name="ma" type="text" list="dl-lop" value="{e(prefill)}" placeholder="VD: D303 · 11R22.5 18PR"><datalist id="dl-lop">{dl}</datalist></div>
  <div><label class="lb" for="q-sl">Số lượng (lốp)</label><input id="q-sl" name="so_luong" type="number" min="1" inputmode="numeric" placeholder="10"></div>
  <div class="full"><label class="lb" for="q-xe">Loại xe / vị trí lắp</label><input id="q-xe" name="loai_xe" type="text" placeholder="VD: sơ mi rơ moóc 3 trục"></div>
  <div class="full"><label class="lb" for="q-gc">Ghi chú</label><textarea id="q-gc" name="ghi_chu" maxlength="200" placeholder="Tuyến đường, thời gian cần hàng…"></textarea></div>
  <div class="hp" aria-hidden="true"><label for="q-web">Website</label><input id="q-web" name="website" type="text" tabindex="-1" autocomplete="off"></div>
  <label class="consent full"><input type="checkbox" name="consent" required> <span>Tôi đồng ý để Dương Gia dùng thông tin này để liên hệ tư vấn, theo <a href="{href(r, 'chinh-sach.html')}#bao-mat">Chính sách bảo mật</a>.</span></label>
  <div class="msg full" role="status" aria-live="polite" hidden></div>
  <div class="full"><button class="btn btn-pri" type="submit" style="width:100%">Gửi yêu cầu</button></div>
</form>'''

def form_dai_ly(r):
    return f'''<form class="form" data-form="dai-ly" novalidate>
  <div><label class="lb" for="d-ten">Tên cửa hàng / công ty *</label><input id="d-ten" name="ten" type="text" autocomplete="organization" placeholder="Lốp xe Minh An"></div>
  <div><label class="lb" for="d-lh">Người liên hệ</label><input id="d-lh" name="nguoi_lien_he" type="text" autocomplete="name" placeholder="Anh Minh"></div>
  <div><label class="lb" for="d-sdt">Số điện thoại / Zalo *</label><input id="d-sdt" name="dien_thoai" type="tel" inputmode="tel" autocomplete="tel" placeholder="09xx xxx xxx"></div>
  <div><label class="lb" for="d-tinh">Tỉnh / thành *</label><input id="d-tinh" name="tinh_thanh" type="text" placeholder="Gia Lai"></div>
  <div><label class="lb" for="d-lhinh">Loại hình</label><select id="d-lhinh" name="loai_hinh"><option>Đại lý / cửa hàng lốp</option><option>Garage sửa chữa</option><option>Đội xe / doanh nghiệp vận tải</option><option>Khác</option></select></div>
  <div><label class="lb" for="d-mst">Mã số thuế (nếu có)</label><input id="d-mst" name="mst" type="text" inputmode="numeric" placeholder="Để xuất hóa đơn"></div>
  <div class="full"><label class="lb" for="d-xe">Loại xe đang phục vụ</label><input id="d-xe" name="loai_xe" type="text" placeholder="VD: đầu kéo, sơ mi rơ moóc, xe ben"></div>
  <div class="hp" aria-hidden="true"><label for="d-web">Website</label><input id="d-web" name="website" type="text" tabindex="-1" autocomplete="off"></div>
  <label class="consent full"><input type="checkbox" name="consent" required> <span>Tôi đồng ý để Dương Gia dùng thông tin này để liên hệ và mở tài khoản đại lý, theo <a href="{href(r, 'chinh-sach.html')}#bao-mat">Chính sách bảo mật</a>.</span></label>
  <div class="msg full" role="status" aria-live="polite" hidden></div>
  <div class="full"><button class="btn btn-pri" type="submit" style="width:100%">Gửi đăng ký</button></div>
</form>'''

def stores_html(r, light=True):
    maps = 'https://www.google.com/maps/search/?api=1&query=' + CTY['dia_chi'].replace(' ', '+').replace(',', '%2C')
    return f'''<div class="loc">
  <div class="lc"><span class="tag">Cửa hàng · Đắk Lắk</span><h3 class="disp">Cửa hàng Dương Gia</h3><p>{CTY['dia_chi']}</p><p>Thứ Hai – Thứ Bảy, 7:00 – 17:00 (nghỉ trưa) · Nghỉ Chủ nhật</p><p>Lốp xe · mâm xe · ắc quy · dầu nhớt · dịch vụ lốp</p><p style="margin-top:14px"><a class="link-more" href="{maps}" rel="noopener">Chỉ đường trên Google Maps →</a></p></div>
  <div class="lc"><span class="tag">Giao hàng · Toàn quốc</span><h3 class="disp">Giao đến tận nơi</h3><p>Giao hàng toàn quốc theo địa chỉ, phí theo địa chỉ giao và báo trước khi xác nhận đơn.</p><p>Miễn phí giao hàng trong TP.HCM (địa bàn cũ).</p><p>Đại lý đặt hàng trên ứng dụng DG Đặt Hàng; Dương Gia xác nhận đơn và giao hàng.</p><p style="margin-top:14px"><a class="link-more" href="{CTY['app']}" rel="noopener">Mở ứng dụng DG Đặt Hàng →</a></p></div>
</div>'''

PILL_ICONS = {
    'nk': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 17l2 3h14l2-3M3 17h18M5 17V9h14v8M9 9V5h6v4M2 21h20"/></svg>',
    'qc': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5 4.5-5"/></svg>',
    'gh': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 7h11v9H2zM13 10h4l3 3v3h-7"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/></svg>',
    'cs': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h11l3 3v13H5zM9 12h6M9 16h6M9 8h3"/></svg>',
}

def write(path, content):
    fp = os.path.join(OUT, path); os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, 'w', encoding='utf-8').write(content)

# ------------------------------------------------------------------ TRANG CHỦ
def build_home():
    r = ''
    size_opts = ''.join('<option value="%s">%s</option>' % (e(s), e(s)) for s in SIZES)
    route_opts = ''.join('<option value="%s">%s</option>' % (k, e(v)) for k, v in ROUTE_LABEL.items())
    feat = sorted(ITEMS, key=lambda x: (['cao-toc', 'hon-hop', 'cong-trinh', ''].index(x['route']), x['g'], size_sort(x['size'])))
    shown = 0; cards = []
    for it in feat:
        ok = st_key(it['status']) in ('ok', 'warn') and shown < 8
        if ok: shown += 1
        cards.append(card(it, r, hidden=not ok))
    pills = [('nk', 'Nhập khẩu chính ngạch', 'Đặt hàng trực tiếp từ nhà máy, đủ chứng nhận xuất xứ (C/O), tờ khai hải quan và hóa đơn VAT cho từng lô hàng.'),
             ('qc', 'Tuân thủ QCVN 34:2024', 'Lốp nhập khẩu được Dương Gia đăng ký thử nghiệm và kiểm tra chất lượng theo quy chuẩn QCVN 34:2024 của Việt Nam.'),
             ('gh', 'Giao hàng toàn quốc', 'Giao theo địa chỉ trên toàn quốc, phí theo địa chỉ giao. Miễn phí giao hàng trong TP.HCM (địa bàn cũ).'),
             ('cs', 'Chính sách minh bạch', 'Giá niêm yết công khai, giá đại lý theo hạng, đặt hàng và theo dõi đơn trên ứng dụng DG Đặt Hàng.')]
    pill_html = ''.join(f'<div class="pil">{PILL_ICONS[k]}<h3 class="disp">{e(t)}</h3><p>{e(d)}</p></div>' for k, t, d in pills)
    steps = [('Đặt hàng nhà máy', 'Hợp đồng trực tiếp với nhà sản xuất, chốt mẫu gai, quy cách, PR theo nhu cầu thị trường Việt Nam.'),
             ('Kiểm tra chứng từ', 'Đối chiếu hàng với hợp đồng, C/O, hóa đơn và phiếu đóng gói trước khi xếp container.'),
             ('Vận chuyển', 'Container đường biển về cảng TP.HCM, theo dõi lịch tàu và tình trạng từng lô hàng.'),
             ('Thông quan & kiểm tra', 'Khai báo hải quan, đăng ký thử nghiệm và kiểm tra chất lượng theo quy chuẩn hiện hành.'),
             ('Nhập kho & giao hàng', 'Nhập kho, cập nhật tình trạng hàng trên ứng dụng, giao đến đại lý và khách hàng.')]
    step_html = ''.join(f'<div class="step"><div class="k">{n}</div><h3 class="disp">{e(t)}</h3><p>{e(d)}</p></div>' for n, (t, d) in enumerate(steps, 1))
    body = f'''
<section class="hero">
  <picture><source media="(max-width:640px)" srcset="img/hero-m.jpg"><img class="bg" src="img/hero.jpg" alt="" width="1920" height="1146" fetchpriority="high"></picture>
  <div class="shade"></div>
  <div class="wrap">
    <p class="eyebrow">Nhà nhập khẩu &amp; phân phối lốp ô tô · WYNSTAR</p>
    <h1 class="disp">Lốp tải nhập khẩu chính ngạch cho đường trường Việt Nam</h1>
    <p class="lead">Lốp tải radial toàn thép chịu tải nặng, bền bỉ trên cao tốc, quốc lộ và đường hỗn hợp — giải pháp lốp tải cho doanh nghiệp vận tải và logistics. Giao hàng toàn quốc, chính sách đại lý minh bạch.</p>
    <div class="ctas"><a class="btn btn-pri" href="#tim-lop">Tìm lốp theo size</a><a class="btn btn-ghost" href="{href(r, 'dai-ly.html')}">Trở thành đại lý</a></div>
    <div class="stats">
      <div><div class="n">2,7 triệu</div><div class="l">lốp radial toàn thép mỗi năm — công suất nhà máy sản xuất WYNSTAR</div></div>
      <div><div class="n">80+</div><div class="l">quốc gia nhập khẩu sản phẩm của nhà máy, trong đó có Việt Nam</div></div>
      <div><div class="n">3 năm</div><div class="l">bảo hành kể từ ngày mua hàng tại Dương Gia</div></div>
      <div><div class="n">Toàn quốc</div><div class="l">giao hàng theo địa chỉ, miễn phí trong TP.HCM (địa bàn cũ)</div></div>
    </div>
  </div>
</section>
<div class="finder" id="tim-lop"><div class="wrap">
  <form class="box" action="{href(r, 'san-pham/')}" method="get">
    <div class="ttl">Tìm lốp<small>theo cỡ &amp; tuyến đường</small></div>
    <div><label class="lb" for="f1">Cỡ lốp</label><select id="f1" name="size"><option value="">Tất cả cỡ</option>{size_opts}</select></div>
    <div><label class="lb" for="f2">Tuyến đường</label><select id="f2" name="route"><option value="">Tất cả tuyến</option>{route_opts}</select></div>
    <button class="btn btn-ink" type="submit">Tìm lốp</button>
  </form>
</div></div>
<section class="brand" style="margin-top:56px"><div class="wrap">
  <span class="lbl">Thương hiệu phân phối</span>
  <img src="img/wynstar-mau.svg" alt="WYNSTAR" width="282" height="34">
  <p>Thương hiệu của Double Coin Group (Chongqing) Tyre Co., Ltd. — nhà máy cung ứng cho Yutong, JAC và xuất khẩu hơn 80 quốc gia. Dương Gia nhập khẩu trực tiếp và phân phối tại Việt Nam.</p>
  <a class="link-more" href="{href(r, 'thuong-hieu-wynstar.html')}">Về WYNSTAR →</a>
</div></section>
<section class="sec"><div class="wrap">
  <p class="eyebrow">Vì sao chọn Dương Gia</p>
  <h2 class="disp">Bốn việc chúng tôi làm đúng từ đầu</h2>
  <p class="intro">Không hứa “hàng đầu”. Mỗi điều dưới đây là một việc cụ thể có chứng từ đi kèm.</p>
  <div class="pill4">{pill_html}</div>
</div></section>
<section class="dark"><div class="sec" style="padding-top:80px"><div class="wrap">
  <p class="eyebrow">Sản phẩm WYNSTAR</p>
  <h2 class="disp" style="color:var(--cream)">Hàng có sẵn trong kho</h2>
  <p class="intro">Giá niêm yết đã gồm VAT, tính trên một lốp. Đại lý đăng nhập ứng dụng DG Đặt Hàng để xem giá theo hạng.</p>
  <div class="promo" data-until="{PROMO['until']}"><span class="disp">{e(PROMO['title'])}</span><p>{e(PROMO['text'])}</p></div>
  <div class="grid4" data-featured data-limit="8" style="margin-top:24px">{''.join(cards)}</div>
  <p class="empty" data-featured-empty hidden>Hàng đang về thêm — vui lòng gọi hoặc Zalo {CTY['hotline']} để được báo tình trạng hàng.</p>
  <p class="stamp js-stamp" style="margin-top:16px">Giá và tình trạng hàng theo hệ thống DG Đặt Hàng ({SNAPSHOT_AT}).</p>
  <div class="ctas" style="margin-top:24px"><a class="btn btn-pri" href="{href(r, 'san-pham/')}">Xem toàn bộ {N_PAT} mẫu gai</a><a class="btn btn-ghost" href="{CTY['zalo']}" rel="noopener">Nhận catalog qua Zalo</a></div>
</div></div></section>
<section class="sec"><div class="wrap">
  <p class="eyebrow">Chương trình đại lý</p>
  <h2 class="disp">Ba hạng đại lý, quyền lợi tăng theo đồng hành</h2>
  <p class="intro">Hạng Bạc khi mở tài khoản; Vàng xét theo doanh số đã thanh toán mỗi quý; Kim Cương dành cho đối tác chiến lược. Giá theo hạng chỉ hiển thị khi đăng nhập ứng dụng.</p>
  {tiers_html(r)}
  <div class="ctas" style="margin-top:32px"><a class="btn btn-ink" href="{href(r, 'dai-ly.html')}#dang-ky">Mở tài khoản đại lý</a><a class="btn btn-line" href="{CTY['app']}" rel="noopener">Đặt hàng</a></div>
</div></section>
<section class="band-2"><div class="sec"><div class="wrap">
  <div class="two">
    <div><p class="eyebrow">Năng lực nhập khẩu</p><h2 class="disp">Từ nhà máy đến kho, một đường đi có chứng từ</h2>
      <p class="intro" style="margin-bottom:0">Dương Gia tự tổ chức chuỗi nhập khẩu: đặt hàng, vận chuyển, thông quan, kiểm tra chất lượng. Không qua trung gian, nên kiểm soát được cả chất lượng lẫn giá.</p></div>
    <figure class="photo" style="margin:0"><img src="img/nha-may.jpg" alt="Nhà máy sản xuất lốp WYNSTAR tại Trùng Khánh, Trung Quốc" loading="lazy" width="1200" height="1103"><figcaption>Nhà máy sản xuất WYNSTAR — Double Coin Group (Chongqing) Tyre Co., Ltd.</figcaption></figure>
  </div>
  <div class="steps">{step_html}</div>
</div></div></section>
<section class="sec" id="he-thong"><div class="wrap">
  <p class="eyebrow">Điểm phục vụ</p>
  <h2 class="disp">Cửa hàng &amp; giao hàng</h2>
  {stores_html(r)}
</div></section>
<section class="dark contact" id="lien-he"><div class="wrap">
  <div><p class="eyebrow">Liên hệ</p><h2 class="disp">Cần báo giá hoặc tư vấn chọn lốp?</h2>
    <div class="big"><a href="tel:{CTY['tel']}">{CTY['hotline']}</a></div>
    <div class="row"><span>Gọi hoặc Zalo cùng số</span><span>{CTY['email']}</span></div>
    <p class="muted" style="margin:28px 0 0;font-size:14px;max-width:440px">Bảo hành 3 năm kể từ ngày mua hàng tại Dương Gia đối với lỗi do sản xuất. Phản hồi bảo hành trong 7 ngày làm việc.</p>
    <div class="ctas" style="margin-top:24px"><a class="btn btn-pri" href="{CTY['zalo']}" rel="noopener">Chat Zalo</a><a class="btn btn-ghost" href="tel:{CTY['tel']}">Gọi ngay</a></div></div>
  {form_bao_gia(r)}
</div></section>'''
    ld = [{'@context': 'https://schema.org', '@type': 'Organization', 'name': 'Dương Gia', 'legalName': CTY['ten'], 'alternateName': CTY['ten_en'],
           'url': CTY['domain'] + '/', 'logo': CTY['domain'] + '/img/icon-512.png', 'taxID': CTY['mst'], 'email': CTY['email'], 'telephone': CTY['tel_intl'],
           'address': {'@type': 'PostalAddress', 'streetAddress': 'KM 10 Quốc lộ 27, Thôn 8', 'addressLocality': 'Xã Ea Ktur', 'addressRegion': 'Đắk Lắk', 'addressCountry': 'VN'},
           'slogan': CTY['slogan']},
          {'@context': 'https://schema.org', '@type': 'TireShop', 'name': 'Cửa hàng Dương Gia', 'url': CTY['domain'] + '/', 'image': CTY['domain'] + '/img/og.jpg', 'telephone': CTY['tel_intl'],
           'address': {'@type': 'PostalAddress', 'streetAddress': 'KM 10 Quốc lộ 27, Thôn 8', 'addressLocality': 'Xã Ea Ktur', 'addressRegion': 'Đắk Lắk', 'addressCountry': 'VN'},
           'openingHoursSpecification': [{'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], 'opens': '07:00', 'closes': '17:00'}]}]
    write('index.html', page('', 0, 'Lốp tải WYNSTAR nhập khẩu chính ngạch | Dương Gia', 'Dương Gia nhập khẩu và phân phối lốp tải radial toàn thép WYNSTAR cho đại lý, garage, đội xe. Giá niêm yết công khai, bảo hành 3 năm, giao hàng toàn quốc.', '', body, ld, 'Dương Gia — Lốp tải nhập khẩu chính ngạch'))

# ------------------------------------------------------------------ DANH MỤC
def build_listing():
    r = '../'
    chips = '<button class="chip" type="button" data-route="" aria-pressed="true">Tất cả tuyến</button>' + ''.join('<button class="chip" type="button" data-route="%s" aria-pressed="false">%s</button>' % (k, e(v)) for k, v in ROUTE_LABEL.items())
    size_opts = ''.join('<option value="%s">%s</option>' % (e(s), e(s)) for s in SIZES)
    order = sorted(ITEMS, key=lambda x: ({'ok': 0, 'warn': 0, 'info': 1}.get(st_key(x['status']), 2), x['type'] == 'lt', ['cao-toc', 'hon-hop', 'cong-trinh', ''].index(x['route']), x['g'], size_sort(x['size'])))
    for n, it in enumerate(order): it['i'] = n
    head = pagehead(r, [('Sản phẩm', 'san-pham/')], 'Sản phẩm', 'Lốp WYNSTAR',
                    f'{N_PAT} mẫu gai, {N_SKU} quy cách lốp tải radial toàn thép và lốp tải nhẹ. Giá niêm yết đã gồm VAT; giá và tình trạng hàng cập nhật từ hệ thống đặt hàng của Dương Gia.')
    body = head + f'''
<section class="dark"><div class="wrap" style="padding-bottom:72px">
  <div class="filters" role="group" aria-label="Lọc sản phẩm">
    <div><span class="lb">Tuyến đường</span><div class="chips">{chips}</div></div>
    <div><label class="lb" for="f-size">Cỡ lốp</label><select id="f-size"><option value="">Tất cả cỡ</option>{size_opts}</select></div>
    <div><label class="lb" for="f-type">Loại lốp</label><select id="f-type"><option value="">Tất cả</option><option value="tbr">Lốp tải nặng</option><option value="lt">Lốp tải nhẹ (LT)</option></select></div>
    <label class="toggle"><input id="f-avail" type="checkbox"> Chỉ hàng có sẵn</label>
    <span class="count" id="f-count" aria-live="polite">{N_SKU} quy cách</span>
  </div>
  <div class="grid4" id="sp-list">{''.join(card(it, r) for it in order)}</div>
  <div class="empty" id="f-empty" hidden>Chưa có quy cách phù hợp bộ lọc. <button class="chip" id="f-reset" type="button">Xóa bộ lọc</button> hoặc gọi {CTY['hotline']} để được tư vấn.</div>
  <p class="stamp js-stamp" style="margin-top:20px">Giá và tình trạng hàng theo hệ thống DG Đặt Hàng ({SNAPSHOT_AT}).</p>
  <p class="stamp">Thông số kỹ thuật theo công bố của nhà sản xuất. Đại lý đăng nhập <a href="{CTY['app']}" rel="noopener" style="text-decoration:underline">ứng dụng DG Đặt Hàng</a> để xem giá theo hạng và đặt hàng.</p>
</div></section>'''
    ld = [ld_crumbs([('Sản phẩm', 'san-pham/')])]
    write('san-pham/index.html', page('san-pham/', 1, 'Lốp tải WYNSTAR — bảng giá niêm yết & thông số | Dương Gia', f'{N_PAT} mẫu gai, {N_SKU} quy cách lốp tải WYNSTAR: giá niêm yết đã gồm VAT, tình trạng hàng, thông số kỹ thuật theo nhà sản xuất. Lọc theo cỡ lốp và tuyến đường.', 'san-pham', body, ld))

# ------------------------------------------------------------------ TRANG MẪU GAI
def build_patterns():
    r = '../'
    for P, items in PATTERNS.items():
        sel = next((n for n, it in enumerate(items) if st_key(it['status']) in ('ok', 'warn')), 0)
        s0 = items[sel]
        rt = ROUTE.get(P, '')
        rl = ROUTE_LABEL.get(rt) or ('Lốp tải nhẹ' if items[0]['type'] == 'lt' else 'Lốp tải radial')
        img = ('<img src="../img/lop/%s.jpg" alt="Mẫu gai lốp WYNSTAR %s" width="600" height="600">' % (slug(P), e(P))) if P in IMAGES else NOIMG
        sizes = ''.join(f'<button class="sz" type="button" data-i="{n}" aria-pressed="{str(n == sel).lower()}">{e(it["size"])} · {e(it["pr"])}<small class="st-{st_key(it["status"])}">{st_label(it["status"])}</small></button>' for n, it in enumerate(items))
        kv = lambda k, lab: f'<div><small>{lab}</small><b id="kv-{k}">{e(s0[k] or "—")}</b></div>'
        kv_html = ''.join([f'<div><small>Chỉ số tải / tốc độ</small><b id="kv-li">{e(s0["li_full"] or "—")}</b></div>', kv('od', 'Đường kính'), kv('sw', 'Bề rộng'), kv('td', 'Sâu gai'),
                           kv('rim', 'Mâm (vành)'), kv('single', 'Tải đơn'), kv('dual', 'Tải đôi'),
                           f'<div><small>Tình trạng</small><b><span class="st st-{st_key(s0["status"])}" id="p-status">{st_label(s0["status"])}</span></b></div>'])
        rows = ''.join(f'<tr data-sku="{e(it["k"])}"><td>{e(it["size"])}</td><td>{e(it["pr"])}</td><td>{e(it["li"] or "—")}</td><td>{e(it["ss"] or "—")}</td>'
                       f'<td>{e(it["od"].replace(" mm", "") or "—")}</td><td>{e(it["sw"].replace(" mm", "") or "—")}</td><td>{e(it["td"].replace(" mm", "") or "—")}</td><td>{e(it["rim"] or "—")}</td>'
                       f'<td>{e(it["single"].replace(" kg · ", " / ").replace(" kPa", "") or "—")}</td><td>{e(it["dual"].replace(" kg · ", " / ").replace(" kPa", "") or "—")}</td>'
                       f'<td><b class="js-price">{vnd(it["price"])}</b></td><td><span class="st js-status st-{st_key(it["status"])}">{st_label(it["status"])}</span></td></tr>' for it in items)
        in_cat = bool(SPECS.get(P))
        road = road_txt(P)
        pos_txt = ('<p><b>Vị trí lắp:</b> trục sơ mi rơ moóc. Nhà sản xuất công bố không dùng cho trục lái hoặc trục chủ động.</p>' if in_cat
                   else '<p><b>Vị trí lắp:</b> liên hệ Dương Gia để được tư vấn vị trí lắp và điều kiện sử dụng phù hợp.</p>')
        road_p = f'<p><b>Tuyến đường:</b> {e(road)}.</p>' if road else ''
        rel_p = [q for q in PATTERNS if q != P and ROUTE.get(q, '') == rt and q in IMAGES][:3] or [q for q in PATTERNS if q != P and q in IMAGES][:3]
        rel_html = ''
        for q in rel_p:
            a = PATTERNS[q][0]
            rel_html += (f'<a class="rc" href="{slug(q)}.html"><div class="img"><img src="../img/lop/{slug(q)}.jpg" alt="WYNSTAR {e(q)}" loading="lazy" width="600" height="600"></div>'
                         f'<div><div class="code disp">{e(q)}</div><div class="size">{e(", ".join(sorted({x["size"] for x in PATTERNS[q]}, key=size_sort)))}</div><div class="stamp" style="color:var(--muted-d)">{e(ROUTE_LABEL.get(ROUTE.get(q, ""), "Lốp tải radial"))}</div></div></a>')
        pdata = {'sel': sel, 'skus': [{'sku': it['k'], 'label': it['label'], 'anchor': it['anchor'], 'size': it['size'], 'pr': it['pr'], 'li': it['li_full'], 'od': it['od'], 'sw': it['sw'],
                                       'td': it['td'], 'rim': it['rim'], 'single': it['single'], 'dual': it['dual'], 'price': it['price'], 'status': it['status']} for it in items]}
        sizes_list = ', '.join(sorted({x['size'] for x in items}, key=size_sort))
        trail = [('Sản phẩm', 'san-pham/'), ('WYNSTAR ' + P, 'san-pham/%s.html' % slug(P))]
        adv = [('Tối ưu khả năng chịu tải nặng', 'Đáp ứng nhu cầu chở hàng nặng, chạy đường dài.'), ('Khung bố và tanh lốp gia cường', 'Kết cấu chắc chắn, bền bỉ khi chở nặng đường dài.'),
               ('Sinh nhiệt thấp, giảm lực cản lăn', 'Hạn chế nóng lốp khi xe chạy liên tục trên cao tốc.'), ('Chống mòn, chống nứt rãnh gai', 'Đáy rãnh chống kẹt đá, kéo dài tuổi thọ lốp.')]
        adv_html = ''.join(f'<div class="ad"><div class="k">0{n}</div><h3 class="disp">{e(t)}</h3><p>{e(d)}</p></div>' for n, (t, d) in enumerate(adv, 1))
        body = f'''
<div class="wrap">
  <div style="padding-top:18px">{crumbs(r, trail, light=True)}</div>
  <div class="phero">
    <div class="gal"><div class="main">{img}</div><p class="cap">Ảnh mặt gai theo tài liệu nhà sản xuất.</p></div>
    <div class="info">
      <p class="eyebrow">WYNSTAR · {e(rl)}</p>
      <h1 class="disp">{e(P)}</h1>
      <p class="sub">{e(pattern_sub(P, items))}</p>
      <div class="badges"><span class="badge">Bảo hành 3 năm</span><span class="badge">Đã gồm VAT</span><span class="badge">Nhập khẩu chính ngạch</span></div>
      <p class="lb" style="margin:22px 0 8px">Chọn cỡ lốp</p>
      <div class="sizes">{sizes}</div>
      <div class="kv">{kv_html}</div>
      <div class="pricebox">
        <div class="pl" id="p-pl">Giá niêm yết · {e(s0["size"])} {e(s0["pr"])}</div>
        <div class="pr"><span id="p-price">{vnd(s0["price"])}</span><small>/ lốp · đã gồm VAT</small></div>
        <div class="ctas"><a class="btn btn-pri" id="p-quote" data-base="../lien-he.html" href="../lien-he.html?ma={e(s0["label"])}">Yêu cầu báo giá</a><a class="btn btn-ghost" href="{CTY['app']}" rel="noopener">Đăng nhập xem giá đại lý</a></div>
        <div class="dl"><span>Giá đại lý theo hạng Bạc · Vàng · Kim Cương hiển thị trên ứng dụng DG Đặt Hàng.</span><a href="../dai-ly.html">Mở tài khoản đại lý →</a></div>
      </div>
      <p class="stamp" style="margin:14px 0 0">Tư vấn nhanh: <b style="color:var(--ink)">{CTY['hotline']}</b> (gọi hoặc Zalo) · Giao hàng toàn quốc</p>
    </div>
  </div>
</div>
<section class="band-2"><div class="sec"><div class="wrap">
  <p class="eyebrow">Ưu điểm thiết kế</p><h2 class="disp">Bốn điểm làm nên WYNSTAR</h2>
  <p class="intro">Theo công bố kỹ thuật của nhà sản xuất cho dòng lốp tải radial toàn thép WYNSTAR.</p>
  <div class="adv">{adv_html}</div>
</div></div></section>
<section class="sec"><div class="wrap">
  <p class="eyebrow">Bảng thông số kỹ thuật</p><h2 class="disp">Cỡ, tải trọng và áp suất</h2>
  <p class="intro">Các cỡ {e(P)} Dương Gia đang phân phối. Đường kính, bề rộng, sâu gai tính bằng mm; tải trọng tính bằng kg / áp suất kPa. “—”: nhà sản xuất chưa công bố trong tài liệu hiện có.</p>
  <div class="tbl"><table>
    <thead><tr><th>Cỡ</th><th>PR</th><th>Chỉ số tải</th><th>Tốc độ</th><th>Đ. kính</th><th>Rộng</th><th>Sâu gai</th><th>Mâm</th><th>Tải đơn</th><th>Tải đôi</th><th>Giá niêm yết</th><th>Tình trạng</th></tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
  <p class="stamp js-stamp" style="margin-top:12px">Giá và tình trạng hàng theo hệ thống DG Đặt Hàng ({SNAPSHOT_AT}).</p>
  <div class="ctas" style="margin-top:20px"><a class="btn btn-ink" href="{CTY['zalo']}" rel="noopener">Nhận hồ sơ kỹ thuật qua Zalo</a><a class="btn btn-line" href="../bao-hanh.html#doc-thong-so">Cách đọc thông số lốp</a></div>
</div></section>
<section class="sec" style="padding-top:0"><div class="wrap">
  <p class="eyebrow">Điều kiện sử dụng &amp; bảo hành</p><h2 class="disp">Dùng đúng chỗ, bảo hành rõ ràng</h2>
  <div class="cond" style="margin-top:28px">
    <div class="cd"><h3 class="disp">Vị trí lắp &amp; tuyến đường</h3>{pos_txt}{road_p}</div>
    <div class="cd"><h3 class="disp">Áp suất &amp; bảo dưỡng</h3><p>Bơm đúng áp suất theo bảng tải trọng – áp suất của nhà sản xuất (cột Tải đơn, Tải đôi ở bảng trên). Kiểm tra áp suất khi lốp nguội, đảo lốp định kỳ, không chở quá tải thiết kế.</p></div>
    <div class="cd"><h3 class="disp">Bảo hành 3 năm</h3><p>Kể từ ngày mua hàng tại Dương Gia, đối với lỗi do sản xuất.</p><ol><li>Báo qua đại lý hoặc hotline {CTY['hotline']}</li><li>Gửi ảnh lốp, số DOT và chứng từ mua hàng</li><li>Dương Gia thẩm định cùng nhà sản xuất</li><li>Phản hồi kết quả trong 7 ngày làm việc</li></ol></div>
  </div>
</div></section>
<section class="dark"><div class="sec"><div class="wrap">
  <p class="eyebrow">Mẫu gai liên quan</p><h2 class="disp" style="color:var(--cream)">Có thể bạn quan tâm</h2>
  <div class="rel" style="margin-top:28px">{rel_html}</div>
  <div class="ctas" style="margin-top:28px"><a class="btn btn-pri" href="{href(r, 'san-pham/')}">Xem toàn bộ {N_PAT} mẫu gai</a></div>
</div></div></section>
<script type="application/json" id="pdata">{json.dumps(pdata, ensure_ascii=False).replace("</", "<\\/")}</script>'''
        desc = f'Lốp tải WYNSTAR {P} — {sizes_list}. {pattern_sub(P, items)} Giá niêm yết đã gồm VAT, thông số theo nhà sản xuất.'
        ld = [ld_crumbs(trail), {'@context': 'https://schema.org', '@type': 'Product', 'name': 'Lốp WYNSTAR ' + P, 'brand': {'@type': 'Brand', 'name': 'WYNSTAR'},
                                 'category': 'Lốp tải', 'description': pattern_sub(P, items), 'sku': P,
                                 **({'image': CTY['domain'] + '/img/lop/%s.jpg' % slug(P)} if P in IMAGES else {})}]
        write('san-pham/%s.html' % slug(P), page('san-pham/%s.html' % slug(P), 1, f'Lốp WYNSTAR {P} — {sizes_list} | Dương Gia', desc[:300], 'san-pham', body, ld))

# ------------------------------------------------------------------ THƯƠNG HIỆU
def build_brand():
    r = ''
    groups = ''
    for k, v in list(ROUTE_LABEL.items()) + [('', 'Lốp tải khác & lốp tải nhẹ')]:
        ps = [p for p in PATTERNS if ROUTE.get(p, '') == k]
        if not ps: continue
        links = ' · '.join('<a href="%s">%s</a>' % (href(r, 'san-pham/%s.html' % slug(p)), e(p)) for p in ps)
        groups += f'<div class="lc"><span class="tag">{e(v)}</span><p style="font-size:16px;font-weight:600">{links}</p></div>'
    body = pagehead(r, [('Thương hiệu WYNSTAR', 'thuong-hieu-wynstar.html')], 'Thương hiệu phân phối', 'WYNSTAR',
                    'Lốp tải radial toàn thép của Double Coin Group (Chongqing) Tyre Co., Ltd. Dương Gia nhập khẩu trực tiếp và phân phối WYNSTAR tại Việt Nam.',
                    '', h1_html='<img src="img/wynstar-trang.svg" alt="WYNSTAR" width="495" height="60" style="height:clamp(40px,6vw,64px);width:auto;display:block;margin:6px 0 10px">') + f'''
<section class="sec"><div class="wrap">
  <div class="two">
    <div class="prose">
      <p class="eyebrow">Nhà máy</p><h2>Double Coin Group (Chongqing)</h2>
      <p>WYNSTAR là thương hiệu của Double Coin Group (Chongqing) Tyre Co., Ltd. — dự án trọng điểm của Shanghai Huayi Group và Double Coin Group, đặt tại Khu phát triển kinh tế – kỹ thuật Shuangqiao, Trùng Khánh, Trung Quốc.</p>
      <p>Nhà máy cung ứng cho các hãng xe Yutong, JAC và xuất khẩu đi hơn 80 quốc gia, trong đó có Việt Nam. Tổng vốn đầu tư hơn 1,8 tỷ nhân dân tệ, diện tích gần 1.000 mẫu Trung Quốc (khoảng 67 ha).</p>
    </div>
    <figure class="photo" style="margin:0"><img src="img/nha-may.jpg" alt="Nhà máy Double Coin Group (Chongqing)" loading="lazy" width="1200" height="1103"><figcaption>Nhà máy sản xuất WYNSTAR tại Trùng Khánh. Ảnh: tài liệu nhà sản xuất.</figcaption></figure>
  </div>
</div></section>
<section class="dark"><div class="sec"><div class="wrap">
  <p class="eyebrow">Theo công bố của nhà sản xuất</p><h2 class="disp" style="color:var(--cream)">Quy mô nhà máy</h2>
  <div class="facts">
    <div><div class="n">2,7 triệu</div><div class="l">lốp radial toàn thép mỗi năm — công suất thiết kế</div></div>
    <div><div class="n">2,594 triệu</div><div class="l">lốp sản xuất trong năm 2024</div></div>
    <div><div class="n">80+</div><div class="l">quốc gia nhập khẩu sản phẩm</div></div>
    <div><div class="n">2008</div><div class="l">ra chiếc lốp đầu tiên, 337 ngày sau khởi công</div></div>
  </div>
</div></div></section>
<section class="sec"><div class="wrap">
  <div class="two" style="align-items:start">
    <div><p class="eyebrow">Hành trình</p><h2 class="disp">Mốc phát triển</h2>
      <div class="timeline" style="margin-top:24px">
        <div><b>2007</b><span>Khởi công dự án nhà máy tại Trùng Khánh.</span></div>
        <div><b>2008</b><span>Ra chiếc lốp đầu tiên sau 337 ngày — kỷ lục hiệu quả của dự án cùng loại trong nước.</span></div>
        <div><b>2009</b><span>Đạt công suất 1,2 triệu bộ lốp.</span></div>
        <div><b>2016</b><span>Tiếp nhận công suất từ Thượng Hải, nâng công suất lên 2,5 triệu lốp mỗi năm.</span></div>
        <div><b>2024</b><span>Sản xuất 2,594 triệu lốp, giá trị sản lượng 2,425 tỷ nhân dân tệ.</span></div>
      </div></div>
    <div><p class="eyebrow">Tại Việt Nam</p><h2 class="disp">Dương Gia phân phối</h2>
      <p class="intro" style="margin-bottom:20px">Dương Gia nhập khẩu trực tiếp từ nhà máy, kiểm soát chứng từ từng lô hàng, bảo hành 3 năm và hỗ trợ đại lý trên toàn quốc.</p>
      <div style="display:grid;gap:14px">{groups}</div>
      <div class="ctas" style="margin-top:24px"><a class="btn btn-ink" href="{href(r, 'san-pham/')}">Xem bảng giá &amp; thông số</a><a class="btn btn-line" href="{href(r, 'dai-ly.html')}">Trở thành đại lý</a></div></div>
  </div>
</div></section>'''
    write('thuong-hieu-wynstar.html', page('thuong-hieu-wynstar.html', 0, 'Thương hiệu lốp WYNSTAR — nhà máy Double Coin Trùng Khánh | Dương Gia', 'WYNSTAR là thương hiệu lốp tải radial toàn thép của Double Coin Group (Chongqing), xuất khẩu hơn 80 quốc gia. Dương Gia nhập khẩu trực tiếp và phân phối tại Việt Nam.', 'wynstar', body, [ld_crumbs([('Thương hiệu WYNSTAR', 'thuong-hieu-wynstar.html')])]))

# ------------------------------------------------------------------ ĐẠI LÝ
def build_dealer():
    r = ''
    steps = [('Đăng ký', 'Gửi thông tin cửa hàng qua biểu mẫu bên dưới hoặc Zalo.'), ('Xác minh', 'Dương Gia liên hệ, xác nhận thông tin và mở tài khoản.'),
             ('Đặt hàng', 'Xem giá đại lý, chọn hàng và gửi đơn trên ứng dụng.'), ('Thanh toán', 'Chuyển khoản vào tài khoản công ty; công nợ theo chính sách từng hạng đại lý.'),
             ('Giao hàng', 'Giao toàn quốc theo địa chỉ; miễn phí giao hàng trong TP.HCM (địa bàn cũ).')]
    step_html = ''.join(f'<div class="step"><div class="k">{n}</div><h3 class="disp">{e(t)}</h3><p>{e(d)}</p></div>' for n, (t, d) in enumerate(steps, 1))
    body = f'''
<section class="hero dl-bg"><picture><source media="(max-width:640px)" srcset="img/bang-hieu-m.jpg"><img class="bg" src="img/bang-hieu.jpg" alt="" width="1920" height="863" loading="eager"></picture><div class="shade"></div><div class="wrap" style="max-width:860px">
  <div>{crumbs(r, [('Dành cho đại lý', 'dai-ly.html')])}<p class="eyebrow">Dành cho đại lý · garage · đội xe</p><h1 class="disp">Trở thành đồng đội Dương Gia</h1>
    <p class="lead">Nguồn hàng nhập khẩu chính ngạch, giá theo hạng đại lý, đặt hàng và theo dõi đơn trên ứng dụng — không phải gọi hỏi giá từng lần.</p>
    <div class="ctas"><a class="btn btn-pri" href="#dang-ky">Mở tài khoản đại lý</a><a class="btn btn-ghost" href="{CTY['app']}" rel="noopener">Đặt hàng</a></div></div>
</div></section>
<section class="sec"><div class="wrap">
  <p class="eyebrow">Vì sao hợp tác</p><h2 class="disp">Ba điều đại lý cần, Dương Gia làm sẵn</h2>
  <div class="pill4 pill3" style="margin-top:28px">
    <div class="pil">{PILL_ICONS['nk']}<h3 class="disp">Nguồn hàng rõ ràng</h3><p>Nhập trực tiếp từ nhà máy, đủ hóa đơn VAT và chứng từ nguồn gốc cho từng lô.</p></div>
    <div class="pil">{PILL_ICONS['cs']}<h3 class="disp">Giá ổn định, minh bạch</h3><p>Một bảng giá đại lý chung toàn hệ thống, chiết khấu theo hạng — không có giá riêng ngầm.</p></div>
    <div class="pil">{PILL_ICONS['qc']}<h3 class="disp">Hỗ trợ bán hàng</h3><p>Catalog, hồ sơ kỹ thuật, ảnh sản phẩm và tư vấn chọn lốp cho khách của đại lý.</p></div>
  </div>
</div></section>
<section class="band-2"><div class="sec"><div class="wrap">
  <p class="eyebrow">Hạng đại lý</p><h2 class="disp">Bạc · Vàng · Kim Cương</h2>
  <p class="intro">Hạng Bạc khi mở tài khoản; Vàng xét theo doanh số đã thanh toán mỗi quý; Kim Cương dành cho đối tác chiến lược do Giám đốc mời. Mức chiết khấu và mốc doanh số công bố riêng cho đại lý đã có tài khoản.</p>
  {tiers_html(r)}
</div></div></section>
<section class="sec"><div class="wrap">
  <p class="eyebrow">Quy trình</p><h2 class="disp">Từ đăng ký đến nhận hàng</h2>
  <div class="steps" style="margin-top:28px">{step_html}</div>
</div></section>
<section class="dark contact" id="dang-ky"><div class="wrap">
  <div><p class="eyebrow">Mở tài khoản đại lý</p><h2 class="disp">Để lại thông tin, Dương Gia gọi lại trong ngày làm việc</h2>
    <p class="muted" style="font-size:15px">Hoặc gọi / Zalo trực tiếp <a href="tel:{CTY['tel']}" style="color:var(--brass-l);font-weight:700">{CTY['hotline']}</a>.</p>
    <div class="prose" style="margin-top:28px"><h3 style="color:var(--cream);margin-top:0">Câu hỏi thường gặp</h3>
      <p style="color:var(--soft-d)"><b style="color:var(--cream)">Có được trộn nhiều mã gai trong một đơn?</b><br>Có. Một đơn có thể gồm nhiều mã gai và cỡ lốp khác nhau.</p>
      <p style="color:var(--soft-d)"><b style="color:var(--cream)">Bảo hành xử lý thế nào?</b><br>Bảo hành 3 năm kể từ ngày mua hàng tại Dương Gia đối với lỗi do sản xuất. Đại lý tiếp nhận và chuyển hồ sơ cho Dương Gia; Dương Gia phản hồi trong 7 ngày làm việc.</p>
      <p style="color:var(--soft-d)"><b style="color:var(--cream)">Có xuất hóa đơn VAT không?</b><br>Có. Giá đã gồm VAT; Dương Gia xuất hóa đơn VAT cho đơn sỉ và khách doanh nghiệp.</p></div></div>
  {form_dai_ly(r)}
</div></section>'''
    write('dai-ly.html', page('dai-ly.html', 0, 'Trở thành đại lý lốp WYNSTAR | Dương Gia', 'Chương trình đại lý lốp WYNSTAR của Dương Gia: giá theo hạng Bạc, Vàng, Kim Cương; đặt hàng và theo dõi đơn trên ứng dụng DG Đặt Hàng; đăng ký mở tài khoản trực tuyến.', 'dai-ly', body, [ld_crumbs([('Dành cho đại lý', 'dai-ly.html')])]))

# ------------------------------------------------------------------ BẢO HÀNH & KỸ THUẬT
def build_warranty():
    r = ''
    li_rows = ''.join('<tr><td>%s</td><td>%s kg</td></tr>' % (a, b) for a, b in [('146', '3.000'), ('148', '3.150'), ('149', '3.250'), ('152', '3.550'), ('154', '3.750'), ('156', '4.000'), ('158', '4.250'), ('160', '4.500'), ('164', '5.000')])
    ss_rows = ''.join('<tr><td>%s</td><td>%s km/h</td></tr>' % (a, b) for a, b in [('D', '65'), ('F', '80'), ('G', '90'), ('J', '100'), ('K', '110'), ('L', '120')])
    body = pagehead(r, [('Bảo hành & Kỹ thuật', 'bao-hanh.html')], 'Hỗ trợ', 'Bảo hành & kỹ thuật', 'Chính sách bảo hành lốp WYNSTAR do Dương Gia phân phối, cách đọc thông số lốp và hướng dẫn sử dụng an toàn.') + f'''
<section class="sec"><div class="wrap">
  <nav class="toc" aria-label="Mục lục"><a href="#chinh-sach">Chính sách bảo hành</a><a href="#quy-trinh">Quy trình bảo hành</a><a href="#doc-thong-so">Cách đọc thông số lốp</a><a href="#su-dung">Sử dụng &amp; bảo dưỡng</a></nav>
  <div class="prose">
    <h2 id="chinh-sach">Chính sách bảo hành</h2>
    <ul>
      <li><b>Thời hạn:</b> 3 năm kể từ ngày mua hàng tại Dương Gia.</li>
      <li><b>Phạm vi:</b> hư hỏng do lỗi sản xuất (vật liệu, chế tạo) của nhà sản xuất.</li>
      <li><b>Áp dụng cho:</b> lốp WYNSTAR do Dương Gia phân phối, có chứng từ mua hàng (hóa đơn hoặc đơn đặt hàng).</li>
      <li><b>Không thuộc phạm vi bảo hành:</b> hư hỏng do non hơi hoặc quá áp, chở quá tải, lắp sai vị trí hoặc sai vành, va chạm, cắt rách do vật sắc nhọn, mòn tự nhiên, sửa chữa không đúng kỹ thuật.</li>
      <li><b>Kết quả:</b> theo thẩm định của Dương Gia cùng nhà sản xuất.</li>
    </ul>
    <h2 id="quy-trinh">Quy trình bảo hành</h2>
    <ol>
      <li>Báo lỗi qua đại lý nơi mua hàng, hoặc hotline / Zalo <b>{CTY['hotline']}</b>.</li>
      <li>Gửi ảnh lốp (mặt gai, hông lốp, vị trí hư hỏng), số DOT trên hông lốp và chứng từ mua hàng.</li>
      <li>Dương Gia thẩm định cùng nhà sản xuất.</li>
      <li>Dương Gia phản hồi kết quả trong <b>7 ngày làm việc</b> kể từ khi nhận đủ hồ sơ.</li>
    </ol>
    <h2 id="doc-thong-so">Cách đọc thông số lốp</h2>
    <p>Ví dụ quy cách <b>12R22.5 18PR 152/149 L</b>:</p>
    <table class="kvtable"><tbody>
      <tr><th>12</th><td>Bề rộng danh nghĩa của lốp, tính bằng inch.</td></tr>
      <tr><th>R</th><td>Kết cấu radial (bố tỏa tròn).</td></tr>
      <tr><th>22.5</th><td>Đường kính vành (mâm) lắp lốp, tính bằng inch.</td></tr>
      <tr><th>18PR</th><td>Ply Rating — chỉ số khả năng chịu tải tương đương số lớp bố; không phải số lớp bố thực tế.</td></tr>
      <tr><th>152/149</th><td>Chỉ số tải: số đầu cho lốp lắp đơn, số sau cho mỗi lốp khi lắp đôi (152 = 3.550 kg; 149 = 3.250 kg).</td></tr>
      <tr><th>L</th><td>Chỉ số tốc độ tối đa (L = 120 km/h).</td></tr>
    </tbody></table>
    <p>Với quy cách hệ mét như <b>315/80R22.5</b>: 315 là bề rộng (mm), 80 là tỷ lệ chiều cao hông lốp so với bề rộng (%). Quy cách có chữ <b>LT</b> (ví dụ 7.50R16LT) là lốp tải nhẹ.</p>
    <div class="two" style="gap:24px;align-items:start">
      <div><h3>Chỉ số tải thường gặp</h3><table class="kvtable"><thead><tr><th>Chỉ số</th><th>Tải tối đa / lốp</th></tr></thead><tbody>{li_rows}</tbody></table></div>
      <div><h3>Chỉ số tốc độ</h3><table class="kvtable"><thead><tr><th>Ký hiệu</th><th>Tốc độ tối đa</th></tr></thead><tbody>{ss_rows}</tbody></table></div>
    </div>
    <h2 id="su-dung">Sử dụng &amp; bảo dưỡng</h2>
    <ul>
      <li>Kiểm tra áp suất khi lốp nguội, bơm theo bảng tải trọng – áp suất của nhà sản xuất.</li>
      <li>Không chở vượt tải trọng tương ứng với chỉ số tải của lốp.</li>
      <li>Lốp lắp đôi nên cùng quy cách, cùng mẫu gai và mức mòn tương đương.</li>
      <li>Kiểm tra định kỳ độ sâu gai, vết cắt, vết phồng; đảo lốp theo lịch bảo dưỡng của xe.</li>
    </ul>
    <div class="note-box">Cần hồ sơ kỹ thuật chi tiết của từng mẫu gai? Nhắn Zalo <b>{CTY['hotline']}</b> — Dương Gia gửi catalog và bảng thông số.</div>
  </div>
</div></section>'''
    write('bao-hanh.html', page('bao-hanh.html', 0, 'Bảo hành lốp WYNSTAR 3 năm & cách đọc thông số lốp | Dương Gia', 'Chính sách bảo hành 3 năm cho lốp WYNSTAR do Dương Gia phân phối, quy trình 4 bước phản hồi trong 7 ngày làm việc, cách đọc thông số lốp tải và hướng dẫn sử dụng.', 'bao-hanh', body, [ld_crumbs([('Bảo hành & Kỹ thuật', 'bao-hanh.html')])]))

# ------------------------------------------------------------------ GIỚI THIỆU
def build_about():
    r = ''
    body = pagehead(r, [('Về Dương Gia', 'gioi-thieu.html')], 'Về chúng tôi', 'Dương Gia', 'Nhà nhập khẩu và phân phối lốp ô tô — ' + CTY['slogan'].lower() + '.') + f'''
<section class="sec"><div class="wrap">
  <div class="two" style="align-items:start">
    <div class="prose"><h2>Chúng tôi là ai</h2>
      <p>Công ty TNHH Thương mại Dịch vụ XNK Dương Gia nhập khẩu trực tiếp lốp tải từ nhà máy và phân phối cho đại lý, garage, đội xe và doanh nghiệp vận tải.</p>
      <p>Dương Gia hiện là nhà phân phối lốp WYNSTAR tại Việt Nam và vận hành cửa hàng dịch vụ lốp tại Đắk Lắk: lốp xe, mâm xe, ắc quy, dầu nhớt và các dịch vụ lốp.</p>
      <h2>Nguyên tắc của chúng tôi</h2>
      <p>Bán đúng giá, nói đúng chất lượng, giữ đúng lời hẹn — làm ăn lâu dài không có đường tắt.</p></div>
    <div><h2 class="disp" style="font-size:34px;margin-bottom:16px">Cách chúng tôi làm việc</h2>
      <div style="display:grid;gap:14px">
        <div class="lc"><span class="tag">Minh bạch</span><p>Giá niêm yết công khai, chính sách đại lý rõ ràng, hóa đơn VAT đầy đủ cho đơn sỉ và khách doanh nghiệp.</p></div>
        <div class="lc"><span class="tag">Chính ngạch</span><p>Nhập khẩu trực tiếp, đủ chứng từ, kiểm tra chất lượng theo quy chuẩn kỹ thuật Việt Nam.</p></div>
        <div class="lc"><span class="tag">Đồng hành</span><p>Hỗ trợ đại lý từ chọn lốp, đặt hàng, giao nhận đến bảo hành.</p></div>
      </div></div>
  </div>
</div></section>
<section class="band-2"><div class="sec"><div class="wrap">
  <p class="eyebrow">Thông tin doanh nghiệp</p><h2 class="disp">Pháp nhân</h2>
  <div class="prose" style="max-width:860px"><table class="kvtable"><tbody>
    <tr><th>Tên doanh nghiệp</th><td>{CTY['ten']}</td></tr>
    <tr><th>Tên tiếng Anh</th><td>{CTY['ten_en']}</td></tr>
    <tr><th>Mã số thuế</th><td>{CTY['mst']}</td></tr>
    <tr><th>Trụ sở</th><td>{CTY['dia_chi']}</td></tr>
    <tr><th>Điện thoại</th><td><a href="tel:{CTY['tel']}">{CTY['hotline']}</a></td></tr>
    <tr><th>Email</th><td><a href="mailto:{CTY['email']}">{CTY['email']}</a></td></tr>
  </tbody></table></div>
  <div class="ctas" style="margin-top:28px"><a class="btn btn-ink" href="{href(r, 'san-pham/')}">Xem sản phẩm</a><a class="btn btn-line" href="{href(r, 'lien-he.html')}">Liên hệ</a></div>
</div></div></section>'''
    write('gioi-thieu.html', page('gioi-thieu.html', 0, 'Về Dương Gia — nhà nhập khẩu & phân phối lốp ô tô', 'Công ty TNHH TMDV XNK Dương Gia nhập khẩu trực tiếp và phân phối lốp tải WYNSTAR cho đại lý, garage, đội xe tại Việt Nam. Thông tin doanh nghiệp.', 'gioi-thieu', body, [ld_crumbs([('Về Dương Gia', 'gioi-thieu.html')])]))

# ------------------------------------------------------------------ LIÊN HỆ
def build_contact():
    r = ''
    body = pagehead(r, [('Liên hệ', 'lien-he.html')], 'Liên hệ', 'Liên hệ Dương Gia', 'Gọi, nhắn Zalo hoặc để lại yêu cầu — Dương Gia phản hồi trong giờ làm việc.') + f'''
<section class="sec"><div class="wrap">
  <div class="two" style="align-items:start">
    <div>
      <p class="eyebrow">Hotline · Zalo</p>
      <div class="big"><a href="tel:{CTY['tel']}" style="color:var(--ink)">{CTY['hotline']}</a></div>
      <div class="ctas" style="margin:20px 0 28px"><a class="btn btn-ink" href="tel:{CTY['tel']}">Gọi ngay</a><a class="btn" style="background:#0068FF;color:#fff" href="{CTY['zalo']}" rel="noopener">Chat Zalo</a></div>
      <p style="margin:0 0 28px">Email: <a href="mailto:{CTY['email']}">{CTY['email']}</a></p>
      {stores_html(r)}
    </div>
    {form_bao_gia(r, light=True)}
  </div>
</div></section>'''
    write('lien-he.html', page('lien-he.html', 0, 'Liên hệ Dương Gia — hotline 0973 929 321', 'Liên hệ Dương Gia: hotline/Zalo 0973 929 321, email, cửa hàng tại Đắk Lắk, giao hàng toàn quốc. Gửi yêu cầu báo giá lốp WYNSTAR trực tuyến.', 'lien-he', body, [ld_crumbs([('Liên hệ', 'lien-he.html')])]))

# ------------------------------------------------------------------ CHÍNH SÁCH
def build_policy():
    r = ''
    body = pagehead(r, [('Chính sách & điều khoản', 'chinh-sach.html')], 'Chính sách', 'Chính sách & điều khoản', 'Áp dụng cho khách hàng và đại lý mua lốp tại Dương Gia.') + f'''
<section class="sec"><div class="wrap">
  <nav class="toc" aria-label="Mục lục"><a href="#thanh-toan">Giá &amp; thanh toán</a><a href="#giao-hang">Giao hàng</a><a href="#doi-hang">Bảo hành &amp; đổi hàng</a><a href="#bao-mat">Dữ liệu cá nhân</a><a href="#khieu-nai">Khiếu nại</a><a href="#dieu-khoan">Điều khoản sử dụng</a><a href="#doanh-nghiep">Thông tin doanh nghiệp</a></nav>
  <div class="prose">
    <h2 id="thanh-toan">Giá &amp; thanh toán</h2>
    <ul>
      <li>Giá niêm yết trên website tính bằng đồng Việt Nam cho một lốp, đã gồm thuế giá trị gia tăng (VAT), chưa gồm phí vận chuyển (nếu có). Giá có thể thay đổi; giá áp dụng là giá trên báo giá hoặc đơn đặt hàng được Dương Gia xác nhận.</li>
      <li>Giá và tình trạng hàng trên website là thông tin tại thời điểm xem; số lượng bán theo tồn kho thực tế khi Dương Gia xác nhận đơn. Chương trình khuyến mại (nếu có) ghi rõ thời gian, đối tượng và điều kiện áp dụng.</li>
      <li>Hình thức thanh toán: chuyển khoản vào tài khoản ngân hàng đứng tên {CTY['ten']} (thông tin tài khoản ghi trên đơn đặt hàng), hoặc tiền mặt tại cửa hàng.</li>
      <li>Dương Gia xuất hóa đơn giá trị gia tăng cho đơn sỉ và khách doanh nghiệp.</li>
      <li>Đại lý: điều kiện thanh toán và công nợ theo chính sách từng hạng đại lý, thể hiện trên đơn đặt hàng.</li>
      <li>Dương Gia không yêu cầu chuyển tiền vào tài khoản cá nhân. Khi nhận thông báo thay đổi tài khoản, vui lòng gọi {CTY['hotline']} để xác nhận trước khi chuyển tiền.</li>
    </ul>
    <h2 id="giao-hang">Giao hàng</h2>
    <ul>
      <li>Giao hàng toàn quốc theo địa chỉ khách hàng; phí giao hàng theo địa chỉ giao và được báo trước khi xác nhận đơn.</li>
      <li>Miễn phí giao hàng trong TP.HCM (địa bàn cũ).</li>
      <li>Thời gian giao dự kiến ghi trên đơn đặt hàng.</li>
      <li>Khi nhận hàng, vui lòng kiểm tra số lượng, quy cách, mã gai; báo ngay cho Dương Gia nếu có sai lệch.</li>
    </ul>
    <h2 id="doi-hang">Bảo hành &amp; đổi hàng</h2>
    <ul>
      <li>Bảo hành 3 năm kể từ ngày mua hàng đối với lỗi do sản xuất — chi tiết tại trang <a href="{href(r, 'bao-hanh.html')}">Bảo hành &amp; kỹ thuật</a>.</li>
      <li>Dương Gia đổi đúng hàng khi giao sai quy cách, sai mã gai hoặc sai số lượng so với đơn đặt hàng đã xác nhận.</li>
      <li>Lốp đã lắp lên xe hoặc đã sử dụng không áp dụng đổi trả, trừ trường hợp được bảo hành.</li>
    </ul>
    <h2 id="bao-mat">Bảo vệ dữ liệu cá nhân</h2>
    <p>Dương Gia xử lý dữ liệu cá nhân theo Luật Bảo vệ dữ liệu cá nhân năm 2025 và các văn bản hướng dẫn.</p>
    <ul>
      <li><b>Bên kiểm soát dữ liệu:</b> {CTY['ten']}, MST {CTY['mst']}, trụ sở {CTY['dia_chi']}; liên hệ {CTY['hotline']} · {CTY['email']}.</li>
      <li><b>Dữ liệu thu thập:</b> tên cửa hàng hoặc đơn vị, họ tên người liên hệ, số điện thoại, tỉnh/thành, mã số thuế (nếu cung cấp) và nhu cầu bạn nhập vào biểu mẫu trên website.</li>
      <li><b>Mục đích:</b> liên hệ tư vấn, báo giá, mở tài khoản đại lý, giao hàng và chăm sóc khách hàng. Dương Gia không dùng dữ liệu này cho mục đích khác khi chưa có sự đồng ý của bạn.</li>
      <li><b>Căn cứ xử lý:</b> sự đồng ý của bạn, thể hiện bằng ô đồng ý trên biểu mẫu (không đánh dấu sẵn). Thời điểm bạn đồng ý được lưu cùng thông tin gửi đến.</li>
      <li><b>Lưu trữ và bảo mật:</b> trên hệ thống quản lý khách hàng của Dương Gia, vận hành trên dịch vụ lưu trữ đám mây của Google; chỉ nhân sự phụ trách được truy cập. Dữ liệu được lưu trong thời gian cần cho các mục đích trên hoặc đến khi bạn yêu cầu xóa, trừ trường hợp pháp luật yêu cầu lưu giữ.</li>
      <li><b>Chia sẻ:</b> Dương Gia không bán hoặc chia sẻ dữ liệu cho bên thứ ba, trừ đơn vị vận chuyển khi giao hàng hoặc theo yêu cầu của cơ quan nhà nước có thẩm quyền.</li>
      <li><b>Quyền của bạn:</b> xem, chỉnh sửa, xóa dữ liệu, rút lại sự đồng ý hoặc phản đối việc xử lý bằng cách gọi {CTY['hotline']} hoặc email {CTY['email']}. Dương Gia xử lý yêu cầu trong thời hạn pháp luật quy định.</li>
      <li><b>Trình duyệt:</b> website không dùng cookie quảng cáo hay công cụ theo dõi; chỉ lưu tạm giá và tình trạng hàng trong trình duyệt để trang tải nhanh hơn.</li>
    </ul>
    <h2 id="khieu-nai">Giải quyết khiếu nại</h2>
    <p>Mọi phản ánh về sản phẩm, giao hàng hoặc dịch vụ, vui lòng gửi qua hotline / Zalo {CTY['hotline']} hoặc email {CTY['email']}. Dương Gia phản hồi trong 7 ngày làm việc.</p>
    <ol>
      <li>Gửi phản ánh kèm thông tin đơn hàng hoặc chứng từ mua hàng, hình ảnh (nếu có).</li>
      <li>Dương Gia tiếp nhận và xác nhận đã nhận phản ánh qua kênh bạn đã liên hệ.</li>
      <li>Dương Gia kiểm tra, thẩm định; với lỗi sản phẩm, phối hợp cùng nhà sản xuất khi cần.</li>
      <li>Dương Gia thông báo kết quả và hướng xử lý trong 7 ngày làm việc kể từ khi nhận đủ thông tin.</li>
    </ol>
    <h2 id="dieu-khoan">Điều khoản sử dụng website</h2>
    <ul>
      <li>Website giới thiệu doanh nghiệp và sản phẩm; website không nhận đặt hàng hay thanh toán trực tuyến. Đơn hàng được xác nhận qua báo giá, đơn đặt hàng hoặc ứng dụng DG Đặt Hàng dành cho đại lý.</li>
      <li>Giá niêm yết được cập nhật theo hệ thống bán hàng của Dương Gia; khi giá thay đổi, website cập nhật theo.</li>
      <li>Thông số kỹ thuật và hình ảnh sản phẩm theo tài liệu công bố của nhà sản xuất.</li>
      <li>Nhãn hiệu WYNSTAR thuộc quyền sở hữu của nhà sản xuất. Nội dung, hình ảnh do Dương Gia biên soạn trên website thuộc quyền của Dương Gia.</li>
    </ul>
    <h2 id="doanh-nghiep">Thông tin doanh nghiệp</h2>
    <p>{CTY['ten']} · MST {CTY['mst']} · Trụ sở: {CTY['dia_chi']} · Điện thoại: {CTY['hotline']} · Email: {CTY['email']}.</p>
    <p>Giấy chứng nhận đăng ký doanh nghiệp số {CTY['mst']}, đăng ký lần đầu ngày 13/01/2025 tại Phòng Đăng ký kinh doanh – Sở Kế hoạch và Đầu tư tỉnh Đắk Lắk.</p>
    <p class="stamp">Cập nhật ngày {SNAPSHOT_AT}.</p>
  </div>
</div></section>'''
    write('chinh-sach.html', page('chinh-sach.html', 0, 'Chính sách & điều khoản | Dương Gia', 'Chính sách giá và thanh toán, giao hàng, bảo hành và đổi hàng, bảo mật thông tin, giải quyết khiếu nại của Dương Gia.', 'chinh-sach', body, [ld_crumbs([('Chính sách & điều khoản', 'chinh-sach.html')])]))

def build_404():
    body = f'''<section class="pagehead"><div class="wrap" style="padding-top:96px;padding-bottom:96px"><p class="eyebrow">Lỗi 404</p><h1 class="disp">Không tìm thấy trang</h1>
<p class="lead">Trang bạn tìm có thể đã đổi địa chỉ. Xem danh mục sản phẩm hoặc gọi {CTY['hotline']} để được hỗ trợ.</p>
<div class="ctas" style="margin-top:28px"><a class="btn btn-pri" href="/san-pham/">Xem sản phẩm</a><a class="btn btn-ghost" href="/">Về trang chủ</a></div></div></section>'''
    html_ = page('404.html', 0, 'Không tìm thấy trang | Dương Gia', 'Trang không tồn tại.', '', body)
    # 404 có thể được phục vụ ở mọi đường dẫn → dùng đường dẫn tuyệt đối
    html_ = html_.replace('href="img/', 'href="/img/').replace('src="img/', 'src="/img/').replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/')
    for p in ['san-pham/', 'dai-ly.html', 'bao-hanh.html', 'gioi-thieu.html', 'lien-he.html', 'chinh-sach.html', 'thuong-hieu-wynstar.html']:
        html_ = html_.replace('href="%s"' % p, 'href="/%s"' % p)
    html_ = html_.replace('href="./"', 'href="/"').replace('<meta name="description"', '<meta name="robots" content="noindex">\n<meta name="description"')
    write('404.html', html_)

def build_meta():
    pages = ['', 'san-pham/'] + ['san-pham/%s.html' % slug(p) for p in PATTERNS] + ['thuong-hieu-wynstar.html', 'dai-ly.html', 'bao-hanh.html', 'gioi-thieu.html', 'lien-he.html', 'chinh-sach.html']
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        '  <url><loc>%s/%s</loc><lastmod>%s</lastmod></url>\n' % (CTY['domain'], p, TODAY) for p in pages) + '</urlset>\n'
    write('sitemap.xml', sm)
    write('robots.txt', 'User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % CTY['domain'])
    write('CNAME', 'xnkduonggia.vn\n')
    write('.nojekyll', '')

def copy_assets():
    shutil.copytree(IMG_SRC, os.path.join(OUT, 'img'), dirs_exist_ok=True)
    if MODE == 'site':
        os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
        shutil.copy(os.path.join(B, 'src', 'site.css'), os.path.join(OUT, 'assets', 'site.css'))
        shutil.copy(os.path.join(B, 'src', 'site.js'), os.path.join(OUT, 'assets', 'site.js'))

if __name__ == '__main__':
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    copy_assets()
    build_home(); build_listing(); build_patterns(); build_brand(); build_dealer(); build_warranty(); build_about(); build_contact(); build_policy()
    if MODE == 'site': build_404(); build_meta()
    n = sum(len(f) for _, _, f in os.walk(OUT))
    print('OK', MODE, '·', N_PAT, 'mẫu gai ·', N_SKU, 'quy cách ·', n, 'tệp')
