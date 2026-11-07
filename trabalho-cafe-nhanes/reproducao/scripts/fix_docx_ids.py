"""Renumera os ids de <wp:docPr> (únicos no pacote) sem reformatar o XML."""
import re, shutil, sys, tempfile, zipfile
src = sys.argv[1]
tmp = tempfile.mktemp(suffix='.docx')
counter = [0]
def renum(m):
    counter[0] += 1
    return f'<wp:docPr id="{counter[0]}"'
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
    names = zin.namelist()
    order = sorted(names, key=lambda n: (0 if n == 'word/document.xml' else 1, n))
    data = {}
    for n in order:
        b = zin.read(n)
        if n.startswith('word/') and n.endswith('.xml') and b'<wp:docPr' in b:
            b = re.sub(r'<wp:docPr id="\d+"', renum, b.decode('utf-8')).encode('utf-8')
        data[n] = b
    for n in names:
        if n.endswith('/'):
            continue
        zout.writestr(zin.getinfo(n), data[n])
shutil.move(tmp, src)
print('docPr ids:', counter[0])
