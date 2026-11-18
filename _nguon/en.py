# -*- coding: utf-8 -*-
"""Sinh bản tiếng Anh /en/ từ các trang tiếng Việt đã dựng.
   python3 en.py site|preview   (chạy sau build.py)"""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en_dict import T, DESC

B = os.path.dirname(os.path.abspath(__file__))
MODE = sys.argv[1] if len(sys.argv) > 1 else 'site'
OUT = os.path.join(B, MODE)
DOMAIN = 'https://xnkduonggia.vn'
VI = re.compile(r'[À-ỹĐđ]')
MISSING = {}

TAB = {'Sản phẩm': 'Products', 'Đại lý': 'Dealers', 'WYNSTAR': 'WYNSTAR', 'Bảo hành': 'Warranty', 'Về chúng tôi': 'About us',
       'Liên hệ': 'Contact', 'Chính sách': 'Policies', 'Không tìm thấy trang': 'Page not found'}
ALL_DESC = {**DESC}

def num_en(s):
    s = re.sub(r'(?<![\d.,])(\d+),(\d{1,2})(?![\d,])', r'\1.\2', s)
    s = re.sub(r'(?<![\d.,])(\d{1,3}(?:\.\d{3})+)(?![\d]|\.\d)', lambda m: m.group(1).replace('.', ','), s)
    return s

def price_en(m):
    return m.group(1).replace('.', ',') + ' VND'

PATTERNS = [
    (re.compile(r'^([\d.]+) đ$'), price_en),
    (re.compile(r'^Mẫu gai lốp WYNSTAR (\S+)$'), lambda m: 'WYNSTAR %s truck tyre tread pattern' % m.group(1)),
    (re.compile(r'^Mẫu gai WYNSTAR (\S+)$'), lambda m: 'WYNSTAR %s tread pattern' % m.group(1)),
    (re.compile(r'^Các cỡ (\S+) Dương Gia đang phân phối\. .*$'), lambda m: 'Sizes of %s currently distributed by Dương Gia. Overall diameter, section width and tread depth in mm; loads in kg / pressures in kPa. “—”: not published in the manufacturer documentation available to us.' % m.group(1)),
    (re.compile(r'^Dương Gia · (.+)$'), lambda m: 'Dương Gia · ' + TAB.get(m.group(1), m.group(1))),
    (re.compile(r'^Giá niêm yết · (.+)$'), lambda m: 'List price · ' + m.group(1)),
    (re.compile(r'^Lốp WYNSTAR (\S+) — (.+) \| Dương Gia$'), lambda m: 'WYNSTAR %s truck tyres — %s | Dương Gia' % (m.group(1), m.group(2))),
    (re.compile(r'^Lốp WYNSTAR (\S+)$'), lambda m: 'WYNSTAR %s tyre' % m.group(1)),
    (re.compile(r'^Lốp tải WYNSTAR (\S+) — ([^.]+(?:\.\d[^.]*)*)\. (.+) Giá niêm yết đã gồm VAT, thông số theo nhà sản xuất\.$'),
     lambda m: 'WYNSTAR %s truck tyre — %s. %s List prices include VAT; specifications as published by the manufacturer.' % (m.group(1), m.group(2), tr(m.group(3)))),
    (re.compile(r'^(\d+) quy cách$'), lambda m: m.group(1) + (' size' if m.group(1) == '1' else ' sizes')),
]

def tr(s):
    """Dịch một chuỗi đã bỏ khoảng trắng đầu/cuối."""
    if not s: return s
    if s in T: return T[s]
    if s in ALL_DESC: return ALL_DESC[s]
    for rx, fn in PATTERNS:
        m = rx.match(s)
        if m: return fn(m)
    if VI.search(s):
        MISSING[s] = MISSING.get(s, 0) + 1
        return s
    return num_en(s)

def tr_ws(raw):
    """Dịch giữ nguyên khoảng trắng đầu/cuối; raw là văn bản HTML (đã escape)."""
    txt = html.unescape(raw)
    core = txt.strip()
    if not core: return raw
    lead = txt[:len(txt) - len(txt.lstrip())]; trail = txt[len(txt.rstrip()):]
    return html.escape(lead + tr(core) + trail, quote=False)

def tr_json(o):
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            if k in ('item', 'url') and isinstance(v, str) and v.startswith(DOMAIN + '/') and '/img/' not in v:
                out[k] = DOMAIN + '/en/' + v[len(DOMAIN) + 1:]
            elif k in ('@context', '@type', 'sku', 'logo', 'image', 'email', 'telephone', 'taxID', 'addressCountry', 'legalName', 'alternateName', 'dayOfWeek', 'opens', 'closes'):
                out[k] = v
            else:
                out[k] = tr_json(v)
        return out
    if isinstance(o, list): return [tr_json(x) for x in o]
    if isinstance(o, str):
        if o == 'KM 10 Quốc lộ 27, Thôn 8': return 'KM 10, National Road 27, Hamlet 8'
        if o == 'Xã Ea Ktur': return 'Ea Ktur Commune'
        return tr(o)
    return o

ATTR = re.compile(r'\b(alt|placeholder|aria-label|title)="([^"]*)"')
META = re.compile(r'(<meta (?:name="description"|property="og:(?:title|description|image:alt)") content=")([^"]*)(")')
TEXT = re.compile(r'>([^<]+)<')
PROTECT = re.compile(r'<(script|style)\b[^>]*>.*?</\1>', re.S)

def to_en(src, rel):
    """src: HTML tiếng Việt của trang rel (đường dẫn tương đối trong site, vd 'san-pham/d303.html')."""
    depth = rel.count('/')
    # 1) che script/style; JSON-LD dịch riêng
    blocks = []
    def keep(m):
        b = m.group(0)
        if 'application/ld+json' in b[:60]:
            body = re.search(r'>(.*)</script>', b, re.S).group(1)
            data = tr_json(json.loads(body.replace('<\\/', '</')))
            b = '<script type="application/ld+json">%s</script>' % json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
        blocks.append(b); return '\x00%d\x00' % (len(blocks) - 1)
    h = PROTECT.sub(keep, src)
    # 2) những cụm có thẻ chen giữa, dịch nguyên khối
    h = h.replace('<span>Nhà phân phối <b>WYNSTAR</b> tại Việt Nam · Lốp tải radial toàn thép</span>',
                  '<span>Authorised distributor of <b>WYNSTAR</b> tyres in Vietnam · All-steel radial truck tyres</span>')
    # 3) thuộc tính, meta, văn bản
    h = META.sub(lambda m: m.group(1) + html.escape(tr(html.unescape(m.group(2))), quote=True) + m.group(3), h)
    h = ATTR.sub(lambda m: '%s="%s"' % (m.group(1), html.escape(tr(html.unescape(m.group(2))), quote=True)) if VI.search(m.group(2)) else m.group(0), h)
    title = re.search(r'<title>([^<]*)</title>', h)
    h = TEXT.sub(lambda m: '>' + tr_ws(m.group(1)) + '<', h)
    # 4) ngôn ngữ, canonical, og
    h = h.replace('<html lang="vi">', '<html lang="en">', 1)
    h = h.replace('<meta property="og:locale" content="vi_VN">', '<meta property="og:locale" content="en_GB">')
    h = re.sub(r'(<link rel="canonical" href=")%s/' % re.escape(DOMAIN), r'\1%s/en/' % DOMAIN, h)
    h = re.sub(r'(<meta property="og:url" content=")%s/' % re.escape(DOMAIN), r'\1%s/en/' % DOMAIN, h)
    # 5) đường dẫn tài nguyên dùng chung: lùi thêm một cấp
    up = '../' * depth
    h = re.sub(r'((?:src|href)=")(%s)(assets/|img/)' % re.escape(up), lambda m: m.group(1) + '../' + m.group(2) + m.group(3), h)
    # 6) nút chuyển ngôn ngữ → bản tiếng Việt
    vi_path = rel
    if MODE == 'site' and vi_path.endswith('index.html'): vi_path = vi_path[:-len('index.html')]
    vi_href = '../' * (depth + 1) + vi_path
    if vi_href.endswith('../') is False and vi_href == '': vi_href = '../'
    h = re.sub(r'<span class="lg">.*?</span>',
               '<span class="lg"><a href="%s" hreflang="vi" lang="vi">VN</a><i>|</i><b aria-current="true">EN</b></span>' % (vi_href or '../'), h)
    # 7) chính sách: ghi chú bản dịch
    if rel == 'chinh-sach.html':
        h = h.replace('<nav class="toc"', '<div class="note-box" style="margin-bottom:24px">This English page is a translation provided for reference. If there is any difference in meaning, the Vietnamese version prevails.</div>\n  <nav class="toc"', 1)
    # 8) trả lại script/style
    h = re.sub(r'\x00(\d+)\x00', lambda m: blocks[int(m.group(1))], h)
    return h

def main():
    files = []
    for dp, dns, fs in os.walk(OUT):
        if os.path.relpath(dp, OUT).split(os.sep)[0] in ('en', 'img', 'assets'): continue
        for f in fs:
            if f.endswith('.html') and f != '404.html': files.append(os.path.relpath(os.path.join(dp, f), OUT).replace(os.sep, '/'))
    for rel in sorted(files):
        src = open(os.path.join(OUT, rel), encoding='utf-8').read()
        out = to_en(src, rel)
        fp = os.path.join(OUT, 'en', rel); os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, 'w', encoding='utf-8').write(out)
    # sitemap: thêm trang /en/
    sm = os.path.join(OUT, 'sitemap.xml')
    if os.path.exists(sm):
        x = open(sm, encoding='utf-8').read()
        urls = re.findall(r'<url><loc>%s/([^<]*)</loc><lastmod>([^<]*)</lastmod></url>' % re.escape(DOMAIN), x)
        add = ''.join('  <url><loc>%s/en/%s</loc><lastmod>%s</lastmod></url>\n' % (DOMAIN, p, d) for p, d in urls if not p.startswith('en/'))
        open(sm, 'w', encoding='utf-8').write(x.replace('</urlset>', add + '</urlset>'))
    print('EN', MODE, '·', len(files), 'trang')
    if MISSING:
        print('CHƯA DỊCH (%d):' % len(MISSING))
        for k, n in sorted(MISSING.items(), key=lambda kv: -kv[1]): print(' ', n, '|', k[:200])

if __name__ == '__main__':
    main()
