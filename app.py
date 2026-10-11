#!/usr/bin/env python3
# Q.E.D. — a game of geometric proofs · PySide6 edition
# Run:  pip install PySide6 && python qed.py
import sys, os, json, math, time, wave, struct, random, tempfile, base64, datetime
from PySide6.QtCore import Qt, QTimer, QPoint, QPointF, QRectF, QSize, QUrl, QMimeData
from PySide6.QtGui import (QPainter, QPen, QColor, QFont, QBrush, QPolygonF, QPainterPath,
                           QPixmap, QDrag, QAction, QGuiApplication)
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QScrollArea, QStackedWidget, QFrame, QLineEdit, QComboBox, QCheckBox,
    QProgressBar, QSizePolicy, QGridLayout)
from PySide6.QtPrintSupport import QPrinter

# ============================================================ basics
def mulberry32(seed):
    s = seed & 0xFFFFFFFF
    def imul(x, y): return (x * y) & 0xFFFFFFFF
    def rnd():
        nonlocal s
        s = (s + 0x6D2B79F5) & 0xFFFFFFFF
        t = s
        t = imul(t ^ (t >> 15), (t | 1))
        t = ((t + imul(t ^ (t >> 7), (t | 61))) ^ t) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return rnd
def pickR(R, arr): return arr[int(R() * len(arr)) % len(arr)]
def rintR(R, a, b): return a + int(R() * (b - a + 1)) % (b - a + 1) if b >= a else a
def shuffleR(R, arr):
    a = list(arr)
    for i in range(len(a) - 1, 0, -1):
        j = int(R() * (i + 1)); a[i], a[j] = a[j], a[i]
    return a
def fmtT(s): return f"{s//60}:{s%60:02d}"
def dayKey(off=0):
    d = datetime.date.today() + datetime.timedelta(days=off)
    return f"{d.year}-{d.month}-{d.day}"
def hexit(h, a):  # '#rrggbb', 0..1 -> '#aarrggbb' for Qt stylesheets
    return '#%02X%s' % (int(a * 255), h[1:])

# ============================================================ themes
THEMES = [
 dict(id='emerald', name='Emerald Board', sw='#2b4034',
   ch='#e9e5d8', yl='#f2d389', rs='#ef9d90', mn='#a8d8b4', sk='#a5cdde',
   lb='rgba(234,230,218,.55)', shy='rgba(242,211,140,.10)', shb='rgba(165,205,222,.10)', dust='#efece1',
   css=dict(desk='#161310', frame='#57422a', board='qradialgradient(cx:.5, cy:.36, radius:1.2, fx:.5, fy:.36, stop:0 #2b4034, stop:.52 #26382f, stop:1 #1e2c24)',
     chalk='#eae6da', dim=hexit('#eae6da',.58), faint=hexit('#eae6da',.30), strong='#ffffff',
     yellow='#f2d389', rose='#ef9d90', mint='#a8d8b4', sky='#a5cdde',
     l1=hexit('#eae6da',.14), l2=hexit('#eae6da',.24), l3=hexit('#eae6da',.42), l4=hexit('#eae6da',.32), hov=hexit('#eae6da',.85),
     accsoft=hexit('#f2d389',.08), accmid=hexit('#f2d389',.75), mintsoft=hexit('#a8d8b4',.09),
     mintmid=hexit('#a8d8b4',.5), rosesoft=hexit('#ef9d90',.08),
     panel='#24352b', panel2='#1e2d24', toastbg='#F2182429', scrim='#9E0C120F', wash='#08ffffff', pritext='#22332a')),
 dict(id='slate', name='Slate', sw='#2c2e34',
   ch='#e6e5de', yl='#f6cd7c', rs='#f19489', mn='#a5d6bb', sk='#9fc2e4',
   lb='rgba(236,235,228,.55)', shy='rgba(246,205,124,.11)', shb='rgba(159,194,228,.11)', dust='#e9e7df',
   css=dict(desk='#131417', frame='#46484f', board='qradialgradient(cx:.5, cy:.36, radius:1.2, fx:.5, fy:.36, stop:0 #34373d, stop:.52 #282a30, stop:1 #1d1f23)',
     chalk='#ecebe4', dim=hexit('#ecebe4',.60), faint=hexit('#ecebe4',.32), strong='#ffffff',
     yellow='#f6cd7c', rose='#f19489', mint='#a5d6bb', sky='#9fc2e4',
     l1=hexit('#ecebe4',.14), l2=hexit('#ecebe4',.24), l3=hexit('#ecebe4',.42), l4=hexit('#ecebe4',.32), hov=hexit('#ecebe4',.85),
     accsoft=hexit('#f6cd7c',.09), accmid=hexit('#f6cd7c',.75), mintsoft=hexit('#a5d6bb',.09),
     mintmid=hexit('#a5d6bb',.5), rosesoft=hexit('#f19489',.08),
     panel='#2c2e34', panel2='#25272c', toastbg='#F21E2025', scrim='#9E0A0B0D', wash='#09ffffff', pritext='#24262b')),
 dict(id='blueprint', name='Blueprint', sw='#1f4d77',
   ch='#e2eef7', yl='#ffd98c', rs='#ffa294', mn='#93e2c2', sk='#cdeaf9',
   lb='rgba(232,241,248,.55)', shy='rgba(255,217,140,.12)', shb='rgba(147,226,194,.10)', dust='#d9e8f4',
   css=dict(desk='#0d1b29', frame='#7d95a8', board='qradialgradient(cx:.5, cy:.36, radius:1.2, fx:.5, fy:.36, stop:0 #21507b, stop:.52 #1a4166, stop:1 #133351)',
     chalk='#e8f1f8', dim=hexit('#e8f1f8',.62), faint=hexit('#e8f1f8',.34), strong='#ffffff',
     yellow='#ffd98c', rose='#ffa294', mint='#93e2c2', sky='#cdeaf9',
     l1=hexit('#e8f1f8',.15), l2=hexit('#e8f1f8',.26), l3=hexit('#e8f1f8',.44), l4=hexit('#e8f1f8',.34), hov=hexit('#e8f1f8',.88),
     accsoft=hexit('#ffd98c',.10), accmid=hexit('#ffd98c',.80), mintsoft=hexit('#93e2c2',.10),
     mintmid=hexit('#93e2c2',.55), rosesoft=hexit('#ffa294',.09),
     panel='#1d3d5c', panel2='#183350', toastbg='#F210263A', scrim='#9E06121E', wash='#0Dffffff', pritext='#143350')),
 dict(id='parchment', name='Parchment', sw='#f0e3c9',
   ch='#4a3d2b', yl='#b07d10', rs='#b5484a', mn='#3e7d5a', sk='#33628c',
   lb='rgba(61,51,37,.55)', shy='rgba(176,125,16,.12)', shb='rgba(51,98,140,.10)', dust='#cdb089',
   css=dict(desk='#2a2117', frame='#8a5f38', board='qradialgradient(cx:.5, cy:.36, radius:1.2, fx:.5, fy:.36, stop:0 #f7eeda, stop:.52 #efe2c8, stop:1 #e6d5b5)',
     chalk='#3d3325', dim=hexit('#3d3325',.62), faint=hexit('#3d3325',.34), strong='#241d12',
     yellow='#9a6b12', rose='#b0473f', mint='#2e7350', sky='#2f5f8a',
     l1=hexit('#3d3325',.18), l2=hexit('#3d3325',.30), l3=hexit('#3d3325',.50), l4=hexit('#3d3325',.40), hov=hexit('#3d3325',.80),
     accsoft=hexit('#9a6b12',.10), accmid=hexit('#9a6b12',.70), mintsoft=hexit('#2e7350',.10),
     mintmid=hexit('#2e7350',.5), rosesoft=hexit('#b0473f',.09),
     panel='#f8f1e0', panel2='#f3ead5', toastbg='#F5F8F1E0', scrim='#59533725', wash='#0B3d3325', pritext='#f8f1e0')),
 dict(id='washi', name='Washi Rose', sw='#f4e3dd',
   ch='#4a3a41', yl='#8a4a6b', rs='#b0473f', mn='#3e7d5a', sk='#33628c',
   lb='rgba(66,51,58,.55)', shy='rgba(138,74,107,.10)', shb='rgba(51,98,140,.09)', dust='#d9beb4',
   css=dict(desk='#241d22', frame='#a06a52', board='qradialgradient(cx:.5, cy:.36, radius:1.2, fx:.5, fy:.36, stop:0 #faf1ed, stop:.52 #f4e3dd, stop:1 #ecd3cb)',
     chalk='#42333a', dim=hexit('#42333a',.62), faint=hexit('#42333a',.34), strong='#2b1f26',
     yellow='#8a4a6b', rose='#b0473f', mint='#2e7d5a', sky='#33628c',
     l1=hexit('#42333a',.18), l2=hexit('#42333a',.30), l3=hexit('#42333a',.50), l4=hexit('#42333a',.40), hov=hexit('#42333a',.80),
     accsoft=hexit('#8a4a6b',.10), accmid=hexit('#8a4a6b',.70), mintsoft=hexit('#2e7d5a',.10),
     mintmid=hexit('#2e7d5a',.5), rosesoft=hexit('#b0473f',.09),
     panel='#faf3ef', panel2='#f5ebe6', toastbg='#F5FAF3EF', scrim='#5942333A', wash='#0B42333A', pritext='#faf3ef')),
]
class PAL_:
    ch=yl=rs=mn=sk=lb=shy=shb=dust=None
PAL = PAL_()
def apply_theme(tid):
    t = next((x for x in THEMES if x['id'] == tid), THEMES[0])
    PAL.ch, PAL.yl, PAL.rs, PAL.mn, PAL.sk = t['ch'], t['yl'], t['rs'], t['mn'], t['sk']
    def qca(s):
        if s.startswith('rgba'):
            parts = s[s.index('(')+1:s.index(')')].split(',')
            c = QColor(int(parts[0]), int(parts[1]), int(parts[2])); c.setAlphaF(float(parts[3])); return c
        return QColor(s)
    for k in ('lb','shy','shb'): setattr(PAL, k, qca(t[k]))
    PAL.dust = t['dust']
    return t

# ============================================================ fonts
def mkfont(fams, px=None, pt=None, bold=False):
    f = QFont(); f.setFamilies(fams); f.setBold(bold)
    if px: f.setPixelSize(px)
    if pt: f.setPointSize(pt)
    return f
def hand(px=None, pt=None, bold=False):
    return mkfont(['Kalam','Segoe Print','Bradley Hand','Comic Sans MS'], px, pt, bold)
def script(px=None, pt=None, bold=False):
    return mkfont(['Caveat','Segoe Print','Bradley Hand','Comic Sans MS'], px, pt, bold)
def disp(px=None, pt=None, bold=False):
    return mkfont(['Fredericka the Great','Segoe Print','Bradley Hand','Comic Sans MS'], px, pt, bold)

# ============================================================ sound
SND_MUTE = [False]
class SoundEngine:
    def __init__(self):
        self.fx = {}; self.ok = False
        try:
            from PySide6.QtMultimedia import QSoundEffect
            d = tempfile.mkdtemp(prefix='qed_'); SR = 22050
            def w(name, samples):
                p = os.path.join(d, name + '.wav')
                with wave.open(p, 'wb') as f:
                    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
                    f.writeframes(b''.join(struct.pack('<h', max(-32767, min(32767, int(s * 32767)))) for s in samples))
                e = QSoundEffect(); e.setSource(QUrl.fromLocalFile(p)); e.setVolume(0.85); self.fx[name] = e
            def tone(fq, dur=0.1, vol=0.34, typ='sine'):
                n = int(SR * dur); out = []
                for i in range(n):
                    t = i / SR; ph = 2 * math.pi * fq * t
                    v = math.sin(ph) if typ == 'sine' else 2 / math.pi * math.asin(math.sin(ph))
                    out.append(v * min(1, t / 0.012) * math.exp(-3.2 * t / dur) * vol)
                return out
            def nz(dur=0.15, vol=0.3, soft=2):
                n = int(SR * dur); rnd = random.Random(7); out = []; last = 0.0
                for i in range(n):
                    x = rnd.uniform(-1, 1)
                    for _ in range(soft): x = (x + last) * 0.5; last = x
                    out.append(x * math.exp(-4.0 * i / n) * vol)
                return out
            def gap(sec): return [0.0] * int(SR * sec)
            w('select', tone(740, .06, .3)); w('place', nz(.08, .5))
            w('row', tone(587, .1) + tone(880, .14)); w('err', tone(160, .16, .4, 'tri') + gap(.06) + tone(115, .2, .36, 'tri'))
            w('hint', tone(520, .09) + gap(.09) + tone(660, .12))
            w('win', nz(.55, .28, 3) + gap(.2) + tone(523, .18) + gap(.11) + tone(659, .18) + gap(.11) + tone(784, .18) + gap(.11) + tone(1046, .2))
            w('ach', tone(660, .1) + gap(.1) + tone(990, .16))
            w('wipe', nz(.28, .35)); w('sketch', nz(.7, .2, 3))
            self.ok = True
        except Exception:
            self.ok = False
    def play(self, name):
        if self.ok and not SND_MUTE[0] and name in self.fx: self.fx[name].play()
SND = None  # created in main()

# ============================================================ chalk prims
def seg(a, b, c='ch', w=2.6): return {'k':'seg','a':a,'b':b,'c':c,'w':w}
def q(a, c, b, col='yl', w=2.2): return {'k':'q','a':a,'c':c,'b':b,'col':col,'w':w}
def dot(p): return {'k':'dot','p':p,'c':'ch'}
def tx(p, t, c='ch', s=14): return {'k':'txt','p':p,'t':str(t),'c':c,'s':s}
lb = tx
def arc(v, a, b, r, c, tick=True):
    return {'k':'arc','v':v,'a':a,'b':b,'r':r,'c':c,'tick':tick}
def arcN(v, a, b, r, c, n=2):
    out = []
    for i in range(n):
        out.append(arc(v, a, b, r + i * 5, c, i == n - 1))
    return out
def ticks(a, b, n=1, c='rs'):
    return {'k':'ticks','a':a,'b':b,'n':n,'c':c}
def arrows(a, b, n=1, c='sk'):
    return {'k':'arrows','a':a,'b':b,'n':n,'c':c}
def rangle(v, a, b, c='sk', s=13): return {'k':'rangle','v':v,'a':a,'b':b,'c':c,'s':s}
def shade(pts, c): return {'k':'shade','pts':pts,'c':c}
def dashline(a, b, c='mn'): return {'k':'dash','a':a,'b':b,'c':c}
def circleFig(cx, cy, r, c='ch', w=2): return {'k':'circle','p':(cx,cy),'r':r,'c':c,'w':w}
def poly(pts, c='ch', w=2.6, close=False): return {'k':'poly','pts':pts,'c':c,'w':w,'close':close}
def rrect(x, y, w2, h2, c='ch', lw=3): return {'k':'rrect','r':(x,y,w2,h2),'c':c,'w':lw}
def norm(v):
    l = math.hypot(v[0], v[1]) or 1; return (v[0]/l, v[1]/l)
def neg(v): return (-v[0], -v[1])
def addv(a, b): return (a[0]+b[0], a[1]+b[1])
def mulv(a, k): return (a[0]*k, a[1]*k)
def bisAt(v, u, w):
    return norm(addv(norm((u[0]-v[0], u[1]-v[1])), norm((w[0]-v[0], w[1]-v[1]))))

# ============================================================ data: reasons & glossary
REASONS = ['Given','Reflexive Property','Symmetric Property','Transitive Property of Congruence',
 'Transitive Property of Equality','Substitution Property','Addition Property of Equality',
 'Subtraction Property of Equality','Division Property of Equality','SSS','SAS','ASA','AAS','HL','CPCTC',
 'Vertical Angles Theorem','Linear Pair Postulate','Corresponding Angles Postulate',
 'Alternate Interior Angles Theorem','Consecutive Interior Angles Theorem','Congruent Supplements Theorem',
 'Congruent Complements Theorem','Definition of supplementary angles','Definition of complementary angles',
 'Definition of congruent angles','Definition of congruent segments','Definition of angle bisector',
 'Definition of perpendicular','Definition of right angle','Definition of midpoint',
 'Definition of isosceles triangle','Triangle Angle-Sum Theorem','Exterior Angle Theorem',
 'Isosceles Triangle Theorem','Radii of a circle are congruent','Segment Addition Postulate',
 'Angle Addition Postulate']
GLOSS = [
['∠ ABC','n','An angle. The middle letter is always the vertex: ∠ABC has its vertex at B.','You can shorten to ∠B when only one angle lives at B, or to ∠1 when the figure numbers them. Order of the outer letters only matters for direction, not size.','angle'],
['m∠ ABC','n','The measure of an angle, in degrees.','The m turns a shape into a number: m∠ABC = 40°. Congruent angles have equal measures — which is why the final step of a proof often translates ≅ into =.','anglem'],
['Segment AB','n','The part of the line between A and B, written with a bar over the two letters.','A segment has two endpoints. Its length is written without the bar: AB = 5 means the distance is 5. Congruent segments (AB ≅ CD) have equal lengths (AB = CD).','segfig'],
['≅','n','Congruent — same size and same shape.','Segments: same length. Angles: same measure. Triangles: every corresponding part matches. Use ≅ for figures and = for numbers — mixing them is the classic notation error.','congr'],
['∥','n','Parallel — same direction, never meeting, no matter how far extended.','Parallel lines cut by a transversal create every angle pair in this game: corresponding, alternate interior, consecutive interior. The arrows on the figure mark which sides are parallel.','para'],
['⊥','n','Perpendicular — meeting at a right angle.','Perpendicular lines form four right angles, and all right angles are congruent — that fact alone is a whole proof step (the definition of perpendicular).','perpfig'],
['△ ABC','n','A triangle with vertices A, B and C.','Letter order is the correspondence: △ABC ≅ △DEF pairs A↔D, B↔E, C↔F. Read the correspondence off the statement, never off the picture — the figure may be rotated or flipped.','trifig'],
['Ray AB','n','Starts at A and runs forever through B.','Two opposite rays sharing an endpoint form a line together. That is the machinery behind every linear pair.','rayfig'],
['° (degrees)','n','The unit of angle measure: a full turn is 360°, a straight line is 180°, a right angle is 90°.','Every "180°" in this game traces back to one of those three anchors.',''],
['Postulate','w','A statement accepted as true without proof.','Linear Pair, Corresponding Angles, Segment Addition — postulates are the axioms the whole subject stands on. You may cite them freely; you may never be asked to prove them.',''],
['Theorem','w','A statement that has been proven, and stays proven forever.','Every proof in this game turns one theorem from "memorized" into "earned". After your five steps, Vertical Angles becomes a legal reason for the rest of your life.',''],
['Definition','w','The exact meaning of a word — reversible by design.','"Bisects" means two congruent angles, and two congruent angles mean a bisector. Most definition steps read both forwards and backwards, which is why they pair so often with substitution.',''],
['Two-column proof','w','Statements on the left, reasons on the right.','Each row must follow from the rows above by logic alone — no skipping, no trusting the picture. The final statement is whatever you were asked to prove, sealed with Q.E.D.',''],
['Q.E.D.','w','Quod erat demonstrandum — "which was to be demonstrated".','The traditional flourish at the end of a proof. Euclid closed his propositions with a line; later geometers stamped these four letters.',''],
['Vertex','w','The corner point of an angle or polygon.','In an isosceles triangle, "vertex angle" specifically means the angle between the two equal sides — the one the bisector cuts in half.','angle'],
['Adjacent angles','w','Two angles sharing a vertex and one side, with no overlap.','Adjacent angles that also form a straight line together get a special name and a postulate: a linear pair.','linpair'],
['Linear pair','w','Two adjacent angles whose outer sides form a straight line.','Their measures add to 180° — that is the Linear Pair Postulate. Nearly every "supplementary" step in this game starts by spotting a linear pair on the figure.','linpair'],
['Vertical angles','w','A pair of opposite angles formed by two crossing lines.','Crossing lines make two pairs, across the X from each other. The Vertical Angles Theorem — which you proved from two linear pairs — says each pair is congruent.','vert'],
['Transversal','w','A line cutting across two or more other lines.','Eight angles appear at the two crossings. When the cut lines are parallel, those eight angles fall into just two sizes.','corr'],
['Congruent vs. equal','w','≅ compares figures; = compares numbers.','Angles are congruent; their measures are equal. Writing m∠A ≅ m∠B mixes the two up — a favorite distractor card in this game. Watch the m.','congr'],
['Supplementary','w','Two angles whose measures add to 180°.','They do not need to touch. The touching kind is a linear pair; the non-touching kind is what the Congruent Supplements Theorem works on.','linpair'],
['Complementary','w','Two angles whose measures add to 90°.','The right-angle twin of supplementary. Same logic, different total.','comp'],
['Straight angle','w','An angle measuring exactly 180° — a line wearing an angle costume.','Bisect one and you get two right angles: the Bisected Line proof in a sentence. Its sides are opposite rays.','straight'],
['Segment bisector','w','Any line, ray or segment that cuts a segment into two congruent pieces.','A midpoint is a point; a bisector is a whole line through it. A perpendicular bisector does both jobs at once.','mid'],
['Included angle','w','The angle between two named sides of a triangle.','In SAS the angle must be included — squeezed between the two sides. An angle elsewhere leaves wiggle room. Position is part of the argument.','sas'],
['Included side','w','The side connecting the two named angles.','In ASA the side must sit between the angles. AAS survives without it, because the third angle is forced by the Angle-Sum Theorem anyway.','asa'],
['Corresponding parts','w','The matching pieces of congruent triangles.','Read the pairs off the letter order of the congruence statement: △ABC ≅ △DEF makes side AB pair with DE. The figure can lie; the letters cannot.','cpctc'],
['Legs, base & base angles','w','In an isosceles triangle: the two equal sides are legs, the third is the base, the angles on the base are base angles.','Isosceles Triangle Theorem: legs equal ⇒ base angles equal. The converse is true too — you proved it with AAS.','isos'],
['Hypotenuse & leg','w','In a right triangle, the side opposite the right angle is the hypotenuse; the other two are legs.','HL only exists for right triangles — the right angle is what makes comparing just two sides enough.','hlr'],
['Altitude','w','A segment from a vertex that meets the opposite side at a right angle.','The altitude to the base of an isosceles triangle does triple duty: it bisects the base (HL), stands perpendicular (capstone), and halves the vertex angle. Three proofs, one line.','perpfig'],
['Collinear','w','Points lying on one straight line.','Collinearity is the fine print behind linear pairs and segment addition — both postulates quietly require three collinear points.','segadd'],
['Opposite rays','w','Two rays from the same point heading in exactly opposite directions.','Together they form a line. "Angles that form a linear pair" is really a statement about opposite rays.','rayfig'],
['Exterior angle','w','The angle between one side of a triangle and the extension of the neighboring side.','Extend the base past a vertex and the new angle outside is the exterior angle. The theorem you proved: it equals the sum of the two remote interiors.','ext'],
['Remote interior angles','w','The two interior angles of a triangle that do not touch a given exterior angle.','"Remote" just means far from the door the side exited through. Exterior = remote + remote — never the adjacent interior.','ext'],
['Given','p','Stated before the proof begins — it needs no justification.','But only the given. Citing "Given" mid-proof for something not marked on the figure is the oldest trap in the tray.',''],
['Reflexive Property','p','Anything is congruent to itself: AB ≅ AB.','The free congruence hiding in nearly every two-triangle proof: the shared side. Look for the segment both triangles touch.','refl'],
['Symmetric Property','p','If a ≅ b, then b ≅ a.','Congruence and equality both read in both directions. Handy for presenting an answer the right way around.',''],
['Transitive Property of Congruence','p','If a ≅ b and b ≅ c, then a ≅ c.','The chain-move: ∠1 matches ∠3 and ∠3 matches ∠5, so ∠1 matches ∠5. Half of the parallel-lines proofs run on this.',''],
['Transitive Property of Equality','p','If a = b and b = c, then a = c.','Same chain, numeric version — it is what lets two different 180° sums equal each other.',''],
['Substitution Property','p','Replace a quantity with an equal quantity inside an expression.','The workhorse: swap a measure for its equal, swap a number for a known value. Any time a proof "plugs in", substitution is the license.',''],
['Addition Property of Equality','p','Add the same quantity to both sides of a true equation.','The equation stays true. Mostly used here in reverse — see its sibling below.',''],
['Subtraction Property of Equality','p','Subtract the same quantity from both sides.','The most-used property in the game: when both sides share a term, subtract it away and the real claim pops out.',''],
['Division Property of Equality','p','Divide both sides by the same nonzero quantity.','Two congruent halves of a linear pair: m + m = 180 becomes m = 90. The punchline of the capstone proof.',''],
['SSS','c','Side-Side-Side: three pairs of congruent sides force the triangles congruent.','No angles needed at all — the sides alone lock the shape rigid. The kite proof runs entirely on SSS plus one reflexive side.','sss'],
['SAS','c','Side-Angle-Side: two pairs of sides and the angle between them.','The angle must be included. Two sides and a non-included angle can swing — that ambiguous case is exactly what SSA gets wrong.','sas'],
['ASA','c','Angle-Side-Angle: two pairs of angles and the side between them.','The side must connect the two angles — it is the hinge. Both parallelogram diagonal proofs are ASA wearing a different figure.','asa'],
['AAS','c','Angle-Angle-Side: two pairs of angles plus any corresponding non-included side.','Works because two angles force the third (Angle-Sum), reducing AAS to ASA under the hood. The side may sit anywhere.','aas'],
['HL','c','Hypotenuse-Leg: in right triangles, congruent hypotenuse and one congruent leg.','Right triangles only — the right angle is the hidden third piece of information. The HL family puts it to work.','hlr'],
['CPCTC','c','Corresponding Parts of Congruent Triangles are Congruent.','It never proves triangles congruent — it spends a congruence you already earned on the leftover parts. If no △ ≅ △ sits above it, CPCTC is illegal.','cpctc'],
['SSA and AAA (not valid)','c','Two tempting shortcuts that prove nothing.','SSA can describe two different triangles — same two sides, same non-included angle, different shapes. AAA only fixes the angles: similar, not congruent. If a card offers either, leave it in the tray.',''],
['Vertical Angles Theorem','a','Angles across an intersection from each other are congruent.','Proven, not assumed: two linear pairs, both summing to 180°, subtract the shared angle. The first theorem most students ever earn.','vert'],
['Linear Pair Postulate','a','Two adjacent angles forming a straight line are supplementary.','A postulate — accepted, not proven. It is the raw material the Vertical Angles Theorem is manufactured from.','linpair'],
['Corresponding Angles Postulate','a','Parallel lines cut by a transversal: angles in matching corners are congruent.','Same corner of each intersection. The one postulate of the parallel chapter; everything else follows.','corr'],
['Alternate Interior Angles Theorem','a','Parallel lines: interior angles on opposite sides of the transversal are congruent.','The Z-shape pair. Provable from Corresponding plus vertical angles — and this game makes you run exactly that chain.','altint'],
['Consecutive Interior Angles Theorem','a','Parallel lines: interior angles on the same side of the transversal are supplementary.','The C-shape pair, adding to 180°. Follows from alternate interior plus one linear pair.','consint'],
['Congruent Supplements Theorem','a','Angles supplementary to the same angle are congruent to each other.','If ∠W and ∠Y both add with ∠Z to 180°, then ∠W ≅ ∠Y — subtract the shared part. The engine of the parallelogram opposite-angles proof.',''],
['Congruent Complements Theorem','a','Angles complementary to the same angle are congruent to each other.','Same argument as its supplement sibling, with 90° instead of 180°.',''],
['Definition of supplementary angles','a','Two angles whose measures add to 180°.','The definition converts a relationship into an equation — which the algebra properties can then manipulate.','linpair'],
['Definition of complementary angles','a','Two angles whose measures add to 90°.','Watch for it near right angles and perpendicular figures.','comp'],
['Definition of right angle','a','A right angle measures exactly 90°.','The ⊥ symbol promises four of these 90° corners. Inside one, every split obeys the 90° budget.','rightsplit'],
['Definition of congruent angles','a','Angles with equal measures.','The bridge from = back to ≅: m∠A = m∠B, therefore ∠A ≅ ∠B.','anglem'],
['Definition of congruent segments','a','Segments with equal lengths.','Congruence of segments is just equality of their lengths, wearing geometry clothes.','congr'],
['Definition of angle bisector','a','A ray that splits an angle into two congruent angles.','"Bisects" in the Given is a promise: two congruent half-angles, cashed in as a real proof step.','bis'],
['Definition of perpendicular','a','Lines that meet at right angles.','And all right angles are congruent — so one definition step delivers a whole angle pair, free.','perpfig'],
['Definition of midpoint','a','The point that splits a segment into two congruent segments.','Midpoints in the Given are gifts: each one converts directly into a pair of congruent sides.','mid'],
['Segment Addition Postulate','a','If B lies between A and C, then AB + BC = AC.','Parts make wholes. Add algebra and it becomes "solve for x".','segadd'],
['Angle Addition Postulate','a','If D sits inside ∠ABC, then m∠ABD + m∠DBC = m∠ABC.','The protractor twin of segment addition: parts compose the whole. Halve a known total through a bisector and algebra takes over.','angadd'],
['Triangle Angle-Sum Theorem','t','The three angles of a triangle add to 180°.','Provably true from the parallel postulate: slide the three angles to a corner and they form a straight line.','anglesum'],
['Exterior Angle Theorem','t','An exterior angle equals the sum of the two remote interior angles.','The proof you built: linear pair (180°) versus angle sum (180°), subtract the shared interior. Never cite this theorem while proving it — that would be circular.','ext'],
['Isosceles Triangle Theorem','t','If two sides of a triangle are congruent, the angles opposite them are congruent.','The first CPCTC payoff most students meet: build the bisector, prove SAS, collect the base angles. The converse holds too (AAS).','isos2'],
['Definition of isosceles triangle','t','A triangle with at least two congruent sides.','In the circle proofs this definition appears in its purest form: two radii plus a chord — isosceles, for free.','isos'],
['Parallelogram','q','A quadrilateral with both pairs of opposite sides parallel.','From that single sentence flow everything: opposite sides ≅, opposite angles ≅, consecutive angles supplementary. This game proves them from scratch.','parafig'],
['Diagonal','q','A segment joining two non-adjacent vertices of a polygon.','One diagonal slices a parallelogram into two congruent triangles — the engine behind its side and angle theorems.','diagfig'],
['Kite','q','A quadrilateral with two pairs of adjacent congruent sides.','The spine is the reflexive side; SSS does the rest. Kites are the friendliest SSS proofs in the game.','kitefig'],
['Radii of a circle are congruent','o','Every segment from the center to the circle has the same length.','The definition of a circle in action: the set of points at one fixed distance from the center. Any two radii are automatic twins.','rad'],
['Central angle','o','An angle with its vertex at the circle\'s center.','Two radii plus a chord form an isosceles triangle with the central angle at the apex — the punchline: 180° minus the two base angles.','central'],
['Chord','o','A segment joining two points on a circle.','Chord + two radii = isosceles triangle, every time.','chordfig'],
['Diameter','o','A chord through the center — the longest chord there is.','Twice the radius. Any chord through the center splits the circle into mirror halves.','diam'],
]
CATS = [['all','All'],['n','Notation'],['w','Words'],['p','Properties'],['c','Congruence'],
        ['a','Lines & Angles'],['t','Triangles'],['q','Quadrilaterals'],['o','Circles']]
ACH = [['first','First Chalk','Complete your first proof.'],['flawless','Flawless','Earn 3 stars on a proof.'],
 ['pure','Pure Chalk','Finish with zero mistakes and zero hints.'],['hat','Hat Trick','Three 3-star proofs in a row.'],
 ['streak10','Flow State','Ten correct placements in a row.'],['ten','Ten Boards','Complete ten proofs.'],
 ['fifty','Fifty Boards','Complete fifty proofs.'],['capstone','Standing Tall','Prove The Altitude Secret.'],
 ['righton','Right On','Prove a Square Corner family proof.'],['daily','Daily Habit','Complete a Daily Proof.'],
 ['week','Three Suns','Keep a daily streak of three days.'],['drill','Quick Study','Score 7 or better in a reason drill.'],
 ['detective','Proof Detective','Catch three planted flaws.'],['exam',"Examiner's Seal",'Score 8+ stars across one exam.'],
 ['explorer','Field Surveyor','Chalk at least one proof in every family.'],['allfam','The Whole Chalkbox','Unlock every shape family.'],
 ['hardflaw','Cold Chalk','Flawless with extra distractors on.'],['heir',"Euclid's Heir",'Reach the top chalk rank.']]
RANKS = [[0,'Chalk Apprentice'],[12,'Scribe'],[30,'Geometer'],[60,'Compass Bearer'],[110,"Euclid's Heir"]]
def rankOf(st):
    r = RANKS[0][1]
    for t, n in RANKS:
        if st >= t: r = n
    return r
def stars(n, earn):
    return '<span style="color:%s">%s</span><span style="color:%s">%s</span>' % (
        PAL.yl, '★' * earn, PAL.lb.replace('.55', '.35'), '★' * (n - earn))

# ============================================================ glossary mini figures
def _tri(A, B, C): return [seg(A, B), seg(B, C), seg(C, A)]
def twoTri(fn):
    A, B, C, D, E, G = (6,60),(40,60),(23,14),(56,60),(90,60),(73,14)
    return fn(A, B, C) + fn(D, E, G)
FIGS = {
'angle': lambda: [seg((20,60),(88,50)), seg((20,60),(62,12)), arc((20,60),(88,50),(62,12),13,'yl',False), dot((20,60)),
                  lb((94,54),'A','ch',10), lb((10,66),'B','ch',10), lb((58,8),'C','ch',10)],
'anglem': lambda: [seg((20,60),(88,50)), seg((20,60),(62,12)), arc((20,60),(88,50),(62,12),13,'yl',False), tx((58,44),'40°','yl',12)],
'segfig': lambda: [seg((10,40),(86,40)), dot((10,40)), dot((86,40)), lb((10,32),'A','ch',10), lb((86,32),'B','ch',10),
                   seg((40,15),(56,15),'yl',1.6)],
'congr': lambda: [seg((8,20),(44,20)), ticks((8,20),(44,20),1,'yl'), seg((8,56),(44,56)), ticks((8,56),(44,56),1,'yl'), tx((70,40),'≅','yl',22)],
'para': lambda: [seg((6,20),(90,20),'ch',2), seg((6,54),(90,54),'ch',2), arrows((26,20),(70,20),1,'sk'), arrows((26,54),(70,54),1,'sk')],
'perpfig': lambda: [seg((8,54),(88,54)), seg((48,10),(48,68)), rangle((48,54),(88,54),(48,10),'sk',9)],
'trifig': lambda: _tri((48,10),(12,62),(84,62)) + [lb((48,7),'A','ch',10), lb((6,70),'B','ch',10), lb((90,70),'C','ch',10)],
'rayfig': lambda: [dot((12,50)), lb((8,62),'A','ch',10), seg((12,50),(88,24)), seg((74,30),(88,24),'yl',2), seg((88,24),(79,37),'yl',2)],
'vert': lambda: [seg((10,60),(86,16)), seg((86,60),(10,16)), arc((48,38),(10,60),(10,16),9,'yl'), arc((48,38),(86,16),(86,60),9,'yl')],
'linpair': lambda: [seg((6,48),(90,48)), seg((48,48),(80,12)), arc((48,48),(6,48),(80,12),11,'yl',False),
                    arc((48,48),(90,48),(80,12),11,'sk',False), tx((26,30),'a°','yl',10), tx((70,30),'b°','sk',10), tx((48,66),'180°','ch',10)],
'corr': lambda: [seg((6,18),(90,18),'ch',2), seg((6,54),(90,54),'ch',2), seg((34,68),(64,6)),
                 arc((58,18),(88,18),(64,6),8,'yl',False), arc((41,54),(88,54),(64,6),8,'yl',False)],
'altint': lambda: [seg((6,18),(90,18),'ch',2), seg((6,54),(90,54),'ch',2), seg((34,68),(64,6)),
                   arc((58,18),(6,18),(41,54),8,'yl',False), arc((41,54),(90,54),(58,18),8,'yl',False)],
'consint': lambda: [seg((6,18),(90,18),'ch',2), seg((6,54),(90,54),'ch',2), seg((34,68),(64,6)),
                    arc((58,18),(6,18),(41,54),8,'yl',False), arc((41,54),(6,54),(58,18),8,'mn',False), tx((16,38),'180°','ch',9)],
'comp': lambda: [seg((14,60),(90,60)), seg((14,60),(14,10)), seg((14,60),(72,22)),
                 arc((14,60),(90,60),(72,22),10,'yl',False), arc((14,60),(72,22),(14,10),10,'mn',False), tx((52,52),'90°','sk',10)],
'bis': lambda: [seg((14,60),(90,54)), seg((14,60),(58,10)), seg((14,60),(76,28)),
                arc((14,60),(76,28),(58,10),12,'yl'), arc((14,60),(90,54),(76,28),12,'yl')],
'mid': lambda: [seg((10,44),(86,44)), ticks((10,44),(48,44),1,'mn'), ticks((48,44),(86,44),1,'mn'), dot((48,44)),
                lb((48,32),'M','ch',10), dot((10,44)), dot((86,44)), lb((10,32),'A','ch',10), lb((86,32),'B','ch',10)],
'isos': lambda: _tri((48,10),(14,62),(82,62)) + [ticks((48,10),(14,62),1,'rs'), ticks((48,10),(82,62),1,'rs'),
                 arc((14,62),(48,10),(82,62),10,'yl'), arc((82,62),(48,10),(14,62),10,'yl')],
'isos2': lambda: _tri((48,10),(14,62),(82,62)) + [ticks((48,10),(14,62),1,'rs'), ticks((48,10),(82,62),1,'rs')] +
                 arcN((14,62),(48,10),(82,62),8,'rs',2) + arcN((82,62),(48,10),(14,62),8,'rs',2),
'anglesum': lambda: _tri((48,10),(12,62),(84,62)) + [arc((48,10),(12,62),(84,62),9,'yl',False),
                 arc((12,62),(48,10),(84,62),9,'mn',False), arc((84,62),(48,10),(12,62),9,'rs',False), tx((47,44),'180°','yl',11)],
'ext': lambda: [seg((36,12),(10,60)), seg((10,60),(92,60)), seg((64,60),(36,12)),
                arc((36,12),(10,60),(64,60),9,'yl',False), arc((10,60),(36,12),(64,60),8,'yl',False), arc((64,60),(36,12),(92,60),10,'rs',False)],
'rad': lambda: [circleFig(48,40,26), seg((48,40),(24,29)), seg((48,40),(72,29)), seg((24,29),(72,29)),
                ticks((48,40),(24,29),1,'yl'), ticks((48,40),(72,29),1,'yl'), dot((48,40)), lb((48,58),'O','ch',10)],
'central': lambda: [circleFig(48,40,26), seg((48,40),(24,29)), seg((48,40),(72,29)), arc((48,40),(24,29),(72,29),10,'rs'), dot((48,40)), lb((48,58),'O','ch',10)],
'chordfig': lambda: [circleFig(48,40,26), seg((24,29),(72,29),'rs',3), dot((48,40)), lb((48,58),'O','lb',10)],
'diam': lambda: [circleFig(48,40,26), seg((22,40),(74,40)), dot((48,40)), lb((48,58),'O','lb',10)],
'segadd': lambda: [seg((8,44),(88,44)), dot((8,44)), dot((48,44)), dot((88,44)),
                   ticks((8,44),(48,44),1,'mn'), ticks((48,44),(88,44),1,'mn'),
                   lb((8,34),'A','ch',10), lb((48,34),'B','ch',10), lb((88,34),'C','ch',10)],
'refl': lambda: [seg((10,30),(48,18)), seg((10,30),(48,56)), seg((86,30),(48,18)), seg((86,30),(48,56)),
                 seg((48,18),(48,56),'yl',3), tx((48,68),'shared side','yl',9)],
'kitefig': lambda: [seg((48,8),(76,30)), seg((76,30),(48,64)), seg((48,64),(20,30)), seg((20,30),(48,8)), seg((48,8),(48,64),'mn',1.8),
                    ticks((48,8),(76,30),1,'rs'), ticks((48,8),(20,30),1,'rs'), ticks((48,64),(76,30),2,'mn'), ticks((48,64),(20,30),2,'mn')],
'diagfig': lambda: [seg((10,18),(64,18)), seg((64,18),(84,52)), seg((84,52),(30,52)), seg((30,52),(10,18)), seg((64,18),(30,52),'sk',2.2)],
'parafig': lambda: [seg((10,18),(64,18)), seg((64,18),(84,52)), seg((84,52),(30,52)), seg((30,52),(10,18)),
                    arrows((10,18),(64,18),1,'sk'), arrows((30,52),(84,52),1,'sk'), arrows((10,18),(30,52),1,'mn'), arrows((64,18),(84,52),1,'mn')],
'angadd': lambda: [seg((12,60),(88,16)), seg((12,60),(92,52)), seg((12,60),(84,34)),
                   arc((12,60),(84,34),(92,52),10,'yl',False), arc((12,60),(88,16),(84,34),12,'mn',False), arc((12,60),(88,16),(92,52),19,'sk',False),
                   dot((12,60)), lb((6,68),'B','ch',10), lb((92,12),'A','ch',10), lb((96,58),'C','ch',10), lb((88,30),'D','ch',10)],
'rightsplit': lambda: [seg((14,58),(90,58)), seg((14,58),(14,8)), seg((14,58),(66,14)),
                       rangle((14,58),(90,58),(14,8),'sk',9), arc((14,58),(66,14),(14,8),10,'yl',False),
                       arc((14,58),(90,58),(66,14),10,'mn',False), tx((56,50),'90°','sk',10)],
'hlr': lambda: twoTri(lambda A, B, C: _tri(A, B, C) + [rangle(A, B, C, 'sk', 7), ticks(B, C, 1, 'rs'), ticks(A, C, 2, 'mn')]),
'straight': lambda: [seg((8,46),(88,46)), seg((48,46),(48,10)), dot((48,46)),
                     arc((48,46),(8,46),(48,10),10,'yl',False), arc((48,46),(48,10),(88,46),10,'yl',False),
                     lb((6,58),'A','ch',10), lb((90,58),'C','ch',10), lb((48,6),'D','ch',10), lb((48,60),'B','ch',10)],
}
FIGS['sss'] = lambda: twoTri(lambda A, B, C: _tri(A, B, C) + [ticks(A, B, 1, 'yl'), ticks(A, C, 2, 'mn'), ticks(B, C, 3, 'rs')])
FIGS['sas'] = lambda: twoTri(lambda A, B, C: _tri(A, B, C) + [ticks(A, B, 1, 'yl'), ticks(B, C, 2, 'mn'), arc(B, A, C, 9, 'rs')])
FIGS['asa'] = lambda: twoTri(lambda A, B, C: _tri(A, B, C) + [arc(A, B, C, 8, 'yl'), arc(B, A, C, 8, 'mn'), ticks(A, B, 1, 'rs')])
FIGS['aas'] = lambda: twoTri(lambda A, B, C: _tri(A, B, C) + [arc(A, B, C, 8, 'yl'), arc(C, A, B, 8, 'mn'), ticks(B, C, 1, 'rs')])
FIGS['hl'] = FIGS['hlr']
FIGS['cpctc'] = lambda: twoTri(lambda A, B, C: _tri(A, B, C) + [ticks(A, B, 1, 'yl'), arc(C, A, B, 9, 'mn')]) + [tx((48,36),'≅','yl',16)]
FIGS['ssatrap'] = lambda: (lambda A,B,C,D,E,F:
    _tri(A,B,C) + [ticks(A,B,1,'yl'), ticks(B,C,2,'rs'), arc(A,B,C,8,'mn')] +
    _tri(D,E,F) + [ticks(D,E,1,'yl'), ticks(E,F,2,'rs'), arc(D,E,F,8,'mn'), tx((48,8),'?','rs',15)])(
    (6,60),(40,60),(23,14),(56,60),(90,60),(80,22))

# ============================================================ shared figure builders
def transFigure(R):
    mirror = R() < 0.5
    xt = (150 + R()*26) if mirror else (284 + R()*26)
    xb = (284 + R()*26) if mirror else (150 + R()*26)
    T = (xt, 22); Bt = (xb, 358); yl_, ym_ = 112, 268
    def xAt(y): return T[0] + (Bt[0]-T[0])*(y-T[1])/(Bt[1]-T[1])
    Pt = (xAt(yl_), yl_); Qt = (xAt(ym_), ym_)
    dT = norm((Bt[0]-T[0], Bt[1]-T[1])); dL = (1.0, 0.0)
    def regions(v, base):
        rays = sorted([dL, neg(dL), dT, neg(dT)], key=lambda u: math.atan2(u[1], u[0]))
        out = {}
        for i in range(4):
            r1 = rays[i]; r2 = rays[(i+1) % 4]; b = norm(addv(r1, r2))
            num = ((1 if b[0] > 0 else 2) if b[1] < 0 else (3 if b[0] < 0 else 4)) + base
            out[num] = (v, r1, r2, b)
        return out
    NM = {}; NM.update(regions(Pt, 0)); NM.update(regions(Qt, 4))
    sk = [seg((36,yl_),(424,yl_),'ch',2.4), seg((36,ym_),(424,ym_),'ch',2.4), seg(T,Bt,'ch',2.4),
          arrows((64,yl_),(118,yl_),1,'sk'), arrows((64,ym_),(118,ym_),1,'sk')]
    return dict(Pt=Pt, Qt=Qt, T=T, Bt=Bt, yl=yl_, ym=ym_, NM=NM,
                altPairs=[[3,5],[4,6]], samePairs=[[3,6],[4,5]], sk=sk)
def angArc(NM, k, r, c):
    v, r1, r2, _ = NM[k]
    return arc(v, addv(v, mulv(r1, 50)), addv(v, mulv(r2, 50)), r, c, False)
def angArc2(NM, k, r, c): return [angArc(NM, k, r, c), angArc(NM, k, r + 5, c)]
def numLabels(NM):
    out = []
    for k in range(1, 9):
        v, r1, r2, b = NM[k]
        out.append(tx((v[0]+b[0]*31, v[1]+b[1]*31+4), k, 'yl', 13))
    return out
def paraGeo(R):
    AZ = 'ABCDEFGH'; st = int(R()*5) % 5
    W, X, Y, Z = AZ[st], AZ[st+1], AZ[st+2], AZ[st+3]
    x1 = 88 + R()*22; shv = 62 + R()*34; wv = 172 + R()*44
    A0, B0, C0, D0 = (x1,76), (x1+wv,76), (x1+wv+shv,304), (x1+shv,304)
    labels = [lb((A0[0]-14,A0[1]-8),W), lb((B0[0]+14,B0[1]-8),X), lb((C0[0]+14,C0[1]+18),Y), lb((D0[0]-14,D0[1]+18),Z),
              dot(A0), dot(B0), dot(C0), dot(D0)]
    sk = [seg(A0,B0), seg(B0,C0), seg(C0,D0), seg(D0,A0)]
    return dict(W=W,X=X,Y=Y,Z=Z,A0=A0,B0=B0,C0=C0,D0=D0,sk=sk,labels=labels)

# ============================================================ the 21 shape families
FAMILIES = [
dict(name='Crossing Lines', tag='Two straight lines cross. Nothing comes for free.',
 take=['Vertical angles are congruent — and now you can prove it with letters or with numbers.','Two linear pairs and a subtraction: that is the whole secret.'],
 glyph=lambda: [seg((12,8),(52,36)), seg((52,8),(12,36)), q((25,15),(30,19),(34,17)), q((39,29),(34,25),(30,27))],
 def gen(self, n, R):
    A,B,C,D,M = shuffleR(R, list('ABCDPQRSNM'))[:5]
    al = (16+R()*22)*math.pi/180; L0 = 158+R()*14; M0 = (230,192)
    d1 = (math.cos(al), math.sin(al)); d2 = (math.cos(al), -math.sin(al))
    pA = (M0[0]-d1[0]*L0, M0[1]-d1[1]*L0); pB = (M0[0]+d1[0]*L0, M0[1]+d1[1]*L0)
    pC = (M0[0]+d2[0]*L0, M0[1]-d2[1]*L0); pD = (M0[0]-d2[0]*L0, M0[1]+d2[1]*L0)
    an = dict(top=f'∠{A}{M}{C}', bot=f'∠{B}{M}{D}', left=f'∠{A}{M}{D}', right=f'∠{C}{M}{B}')
    rays = dict(top=[pA,pC], bot=[pB,pD], left=[pA,pD], right=[pC,pB])
    bis = dict(top=(0,-1), bot=(0,1), left=(-1,0), right=(1,0))
    labels = [lb((pA[0]-14,pA[1]-6),A), lb((pB[0]+14,pB[1]+16),B), lb((pC[0]+14,pC[1]-6),C),
              lb((pD[0]-14,pD[1]+16),D), lb((M0[0]-8,M0[1]+20),M,'lb',13),
              dot(pA), dot(pB), dot(pC), dot(pD), dot(M0)]
    sk = [seg(pA,pB), seg(pC,pD)]
    AC2 = lambda k, r, c: arc(M0, rays[k][0], rays[k][1], r, c)
    ACN = lambda k, r, c: arcN(M0, rays[k][0], rays[k][1], r, c)
    if n % 2 == 1:
        v1, v2 = pickR(R, [('top','bot'), ('left','right')])
        adj = dict(top=('left','right'), bot=('left','right'), left=('top','bot'), right=('top','bot'))
        s = pickR(R, adj[v1])
        p1, p2, sh = an[v1], an[v2], an[s]
        return dict(given=f'Lines {A}{B} and {C}{D} meet at {M}.', prove=f'{p1} ≅ {p2}',
          steps=[
            {'s':f'{p1} and {sh} are a linear pair','r':'Linear Pair Postulate','why':f'{p1} and {sh} sit together on a straight line — a linear pair.'},
            {'s':f'm{p1} + m{sh} = 180°','r':'Definition of supplementary angles','why':'“Supplementary” means the measures add to 180° — write the sum down.'},
            {'s':f'm{p2} + m{sh} = 180°','r':'Linear Pair Postulate','why':f'Same idea on the other side: {p2} and {sh} also form a linear pair.'},
            {'s':f'm{p1} = m{p2}','r':'Subtraction Property of Equality','why':f'Both sums equal 180° and share m{sh} — subtract it from both sides.'},
            {'s':f'{p1} ≅ {p2}','r':'Definition of congruent angles','why':'Equal measures are exactly what “congruent angles” means. Q.E.D.'}],
          sPool=[f'{an["left"]} ≅ {an["right"]}', f'{an["top"]} ≅ {an["left"]}', f'{an["bot"]} ≅ {an["right"]}',
                 f'm{an["top"]} = m{an["right"]}', f'm{an["left"]} + m{an["right"]} = 180°', f'{an["top"]} ≅ {an["bot"]}'],
          diagram=lambda: dict(sk=sk, labels=labels, fx=[
            [AC2(v1,30,'sk'), AC2(s,30,'sk')],
            [AC2(v1,30,'yl'), AC2(s,30,'yl'), tx((M0[0]+bis[s][0]*56, M0[1]+bis[s][1]*56+4),'180°','sk',13)],
            [AC2(v2,30,'yl'), AC2(s,30,'yl'), tx((M0[0]+bis[s][0]*56, M0[1]+bis[s][1]*56+4),'180°','sk',13)],
            ACN(v1,40,'rs') + ACN(v2,40,'rs'),
            [tx((M0[0]+bis[v1][0]*46, M0[1]+bis[v1][1]*46+8),'≅','rs',24)]]))
    a = rintR(R, 35, 145); b = 180 - a
    labels2 = labels + [tx((M0[0],M0[1]-30),'1','yl',14), tx((M0[0]+30,M0[1]+5),'2','yl',14), tx((M0[0],M0[1]+36),'3','yl',14)]
    return dict(given=f'Lines {A}{B} and {C}{D} meet at {M};  m∠1 = {a}°.', prove=f'm∠3 = {a}°',
      steps=[
        {'s':f'm∠1 = {a}°','r':'Given','why':f'The top angle is marked {a}° — that part is given.'},
        {'s':'m∠1 + m∠2 = 180°','r':'Linear Pair Postulate','why':'∠1 and ∠2 sit together on a straight line.'},
        {'s':f'm∠2 = {b}°','r':'Subtraction Property of Equality','why':f'Subtract the given {a}° from 180°.'},
        {'s':'m∠2 + m∠3 = 180°','r':'Linear Pair Postulate','why':'∠2 and ∠3 form the other linear pair.'},
        {'s':f'm∠3 = {a}°','r':'Subtraction Property of Equality','why':f'180° − {b}° = {a}° — the vertical angle matches the original.'}],
      sPool=[f'm∠2 = {a}°', f'm∠3 = {b}°', 'm∠1 ≅ m∠3', 'm∠1 + m∠3 = 180°', 'm∠1 = m∠2', '∠1 ≅ ∠2'],
      diagram=lambda: dict(sk=sk, labels=labels2, fx=[
        [AC2('top',30,'yl'), tx((M0[0],M0[1]-48),f'{a}°','yl',14)],
        [AC2('top',26,'sk'), AC2('right',26,'sk'), tx((M0[0]+60,M0[1]-4),'180°','sk',12)],
        [AC2('right',26,'mn'), tx((M0[0]+64,M0[1]+18),f'{b}°','mn',14)],
        [AC2('right',26,'sk'), AC2('bot',26,'sk'), tx((M0[0]+60,M0[1]-4),'180°','sk',12)],
        ACN('bot',38,'rs') + [tx((M0[0],M0[1]+58),f'{a}°','rs',15)]]))
},
]
# (families 1–20 are appended programmatically below to keep this file navigable)
F = FAMILIES[0]['gen']; FAMILIES[0]['gen'] = F

def _fam(name, tag, takes, glyph, gen):
    return dict(name=name, tag=tag, take=takes, glyph=glyph, gen=gen)

# --- 1 Segment Addition
def gen1(n, R):
    A,B,C = shuffleR(R, list('ABCDEF'))[:3]
    yv = 186 + rintR(R,-10,10)
    A0,B0,C0 = (64,yv),(230,yv),(396,yv)
    base = [lb((64,yv-16),A), lb((230,yv-16),B), lb((396,yv-16),C), dot(A0), dot(B0), dot(C0), seg(A0,C0)]
    if n % 2 == 0:
        a = rintR(R,2,9); b = rintR(R,2,9)
        return dict(given=f'{B} is between {A} and {C};  {A}{B} = {a},  {B}{C} = {b}.', prove=f'{A}{C} = {a+b}',
          steps=[
            {'s':f'{A}{B} + {B}{C} = {A}{C}','r':'Segment Addition Postulate','why':f'{B} sits between {A} and {C} — the two parts add to the whole.'},
            {'s':f'{a} + {b} = {A}{C}','r':'Substitution Property','why':f'Swap in the given lengths: {a} and {b}.'},
            {'s':f'{A}{C} = {a+b}','r':'Symmetric Property','why':'Flip the equation to present the answer.'}],
          sPool=[f'{A}{B} = {a+b}', f'{B}{C} = {a+b}', f'{A}{C} = {a}·{b}', f'{A}{B} ≅ {A}{C}', f'{A}{B} + {A}{C} = {B}{C}'],
          diagram=lambda: dict(sk=base, labels=[tx(((64+230)/2,yv+28),a,'yl',15), tx(((230+396)/2,yv+28),b,'yl',15)], fx=[
            [ticks(A0,B0,1,'sk'), ticks(B0,C0,1,'sk')],
            [tx((230,yv+54),f'{A}{B} + {B}{C}','mn',14)],
            [tx((230,yv+80),f'{a} + {b} = {A}{C}','yl',15)],
            [ticks(A0,C0,2,'rs'), tx((230,yv+106),f'{A}{C} = {a+b}','rs',17)]]))
    x0 = rintR(R,4,8); a = rintR(R,2,4); c = a + rintR(R,1,3); d = rintR(R,1,6)
    b = (c-a)*x0 + d; ab = a*x0 + b
    return dict(given=f'{B} is the midpoint of {A}{C};  {A}{B} = {a}x+{b},  {B}{C} = {c}x+{d}.', prove=f'x = {x0},  {A}{B} = {ab}',
      steps=[
        {'s':f'{A}{B} ≅ {B}{C}','r':'Definition of midpoint','why':f'{B} is the midpoint — the two pieces are congruent.'},
        {'s':f'{A}{B} = {B}{C}','r':'Definition of congruent segments','why':'Congruent segments have equal lengths.'},
        {'s':f'{a}x+{b} = {c}x+{d}','r':'Substitution Property','why':'Swap in the expressions for each length.'},
        {'s':f'{b} = {c-a}x+{d}','r':'Subtraction Property of Equality','why':f'Subtract {a}x from both sides.'},
        {'s':f'{b-d} = {c-a}x','r':'Subtraction Property of Equality','why':f'Subtract {d} from both sides.'},
        {'s':f'x = {x0}','r':'Division Property of Equality','why':f'Divide both sides by {c-a}.'},
        {'s':f'{A}{B} = {ab}','r':'Substitution Property','why':f"{a}({x0}) + {b} = {ab} — the segment's length."}],
      sPool=[f'x = {x0+1}', f'x = {x0-1}', f'{A}{B} = {ab+2}', f'{B}{C} = {c*x0+d+3}', f'{A}{C} ≅ {A}{B}', f'{a}x+{d} = {c}x+{b}'],
      diagram=lambda: dict(sk=base, labels=[tx(((64+230)/2,yv+28),f'{a}x+{b}','yl',14), tx(((230+396)/2,yv+28),f'{c}x+{d}','yl',14)], fx=[
        [ticks(A0,B0,1,'mn'), ticks(B0,C0,1,'mn')],
        [tx((230,yv+54),f'{A}{B} = {B}{C}','mn',15)],
        [tx((230,yv+80),f'{a}x+{b} = {c}x+{d}','yl',15)],
        [tx((230,yv+106),f'{b} = {c-a}x+{d}','yl',14)],
        [tx((230,yv+132),f'{b-d} = {c-a}x','yl',14)],
        [tx((230,yv+158),f'x = {x0}','yl',15)],
        [ticks(A0,B0,2,'rs'), ticks(B0,C0,2,'rs'), tx((230,yv+184),f'{A}{B} = {ab}','rs',16)]]))
FAMILIES.append(_fam('Segment Addition','Parts make wholes — then algebra takes over.',
  ['Segment addition is the postulate version of “the parts make the whole”.','Algebra and geometry are the same subject wearing different clothes.'],
  lambda: [seg((8,22),(56,22)), dot((32,22)), seg((19,17),(19,27),'mn'), seg((45,17),(45,27),'mn')], gen1))

# --- 2 Angle Sum
def gen2(n, R):
    A,B,C = shuffleR(R, list('ABCPQR'))[:3]
    a = rintR(R,35,85); b = rintR(R,35,min(85,145-a)); c = 180-a-b
    A0 = (230+rintR(R,-42,42), 56+R()*20); B0 = (70+R()*22,314); C0 = (390-R()*22,314)
    bA, bB, bC = bisAt(A0,B0,C0), bisAt(B0,A0,C0), bisAt(C0,A0,B0)
    labels = [lb((A0[0]+bA[0]*22,A0[1]+bA[1]*22-4),A), lb((B0[0]-12,B0[1]+16),B), lb((C0[0]+12,C0[1]+16),C),
              tx((A0[0]+bA[0]*46,A0[1]+bA[1]*46+4),f'{a}°','yl',14), tx((B0[0]+bB[0]*42,B0[1]+bB[1]*42+4),f'{b}°','yl',14),
              dot(A0), dot(B0), dot(C0)]
    cen = ((A0[0]+B0[0]+C0[0])/3, (A0[1]+B0[1]+C0[1])/3)
    return dict(given=f'In △{A}{B}{C}:  m∠{A} = {a}°,  m∠{B} = {b}°.', prove=f'm∠{C} = {c}°',
      steps=[
        {'s':f'm∠{A} = {a}°,  m∠{B} = {b}°','r':'Given','why':f'The two marked angles — {a}° and {b}° — are given.'},
        {'s':f'm∠{A} + m∠{B} + m∠{C} = 180°','r':'Triangle Angle-Sum Theorem','why':'The three angles of any triangle add up to a straight line: 180°.'},
        {'s':f'{a}° + {b}° + m∠{C} = 180°','r':'Substitution Property','why':f'Swap in the known measures: {a}° and {b}°.'},
        {'s':f'm∠{C} = {c}°','r':'Subtraction Property of Equality','why':f'Subtract {a+b}° from both sides: what is left for {C} is {c}°.'}],
      sPool=[f'm∠{C} = {a+b}°', f'm∠{A} + m∠{B} = 180°', f'm∠{C} = {180-a}°', f'm∠{A} ≅ m∠{C}',
             f'△{A}{B}{C} ≅ △{A}{C}{B}', f'm∠{B} = {c}°'],
      diagram=lambda: dict(sk=[seg(A0,B0),seg(B0,C0),seg(C0,A0)], labels=labels, fx=[
        [arc(A0,B0,C0,30,'yl'), arc(B0,A0,C0,24,'yl'), arc(C0,A0,B0,28,'rs')],
        arcN(A0,B0,C0,38,'yl') + arcN(B0,A0,C0,32,'yl'),
        [tx(cen,'180°','yl',16)],
        [arc(C0,A0,B0,36,'rs'), tx((C0[0]+bC[0]*50,C0[1]+bC[1]*50+4),f'{c}°','rs',15)]]))
FAMILIES.append(_fam('Angle Sum','Every triangle hides a straight line inside.',
  ['The three angles of a triangle always make a straight line — 180°.','Substitution turns a theorem about letters into a number.'],
  lambda: [seg((32,7),(11,37)), seg((11,37),(53,37)), seg((53,37),(32,7)), q((27,14),(31,13),(35,15))], gen2))

# --- 3 Exterior Angle
def gen3(n, R):
    A,B,C,D = shuffleR(R, list('ABCDEFGH'))[:4]
    a = rintR(R,30,70); b = rintR(R,30,70)
    A0 = (228+rintR(R,-26,26),64); B0 = (74+R()*18,314); C0 = (292+R()*36,314); D0 = (C0[0]+92,314)
    bA, bB, bCe = bisAt(A0,B0,C0), bisAt(B0,A0,C0), bisAt(C0,A0,D0)
    labels = [lb((A0[0]-4,A0[1]-12),A), lb((B0[0]-12,B0[1]+16),B), lb((C0[0]-2,C0[1]+16),C), lb((D0[0]+4,D0[1]+16),D),
              tx((A0[0]+bA[0]*44,A0[1]+bA[1]*44+4),f'{a}°','yl',14), tx((B0[0]+bB[0]*40,B0[1]+bB[1]*40+4),f'{b}°','yl',14),
              dot(A0), dot(B0), dot(C0), dot(D0)]
    cen = ((A0[0]+B0[0]+C0[0])/3, (A0[1]+B0[1]+C0[1])/3)
    return dict(given=f'△{A}{B}{C} with {D} on ray {B}{C};  m∠{A} = {a}°,  m∠{B} = {b}°.', prove=f'm∠{A}{C}{D} = {a+b}°',
      steps=[
        {'s':f'm∠{A}{C}{B} + m∠{A}{C}{D} = 180°','r':'Linear Pair Postulate','why':f'{B}, {C}, {D} are collinear — the interior and exterior angles at {C} form a linear pair.'},
        {'s':f'm∠{A} + m∠{B} + m∠{A}{C}{B} = 180°','r':'Triangle Angle-Sum Theorem','why':'The three inside angles of the triangle also add to 180°.'},
        {'s':f'm∠{A} + m∠{B} + m∠{A}{C}{B} = m∠{A}{C}{B} + m∠{A}{C}{D}','r':'Transitive Property of Equality','why':'Both expressions equal 180°, so they equal each other.'},
        {'s':f'm∠{A} + m∠{B} = m∠{A}{C}{D}','r':'Subtraction Property of Equality','why':f'm∠{A}{C}{B} appears on both sides — subtract it away.'},
        {'s':f'm∠{A}{C}{D} = {a+b}°','r':'Substitution Property','why':f'Put in the given measures: {a}° + {b}° = {a+b}°.'}],
      sPool=[f'm∠{A}{C}{D} = {180-a-b}°', f'm∠{A}{C}{B} = {a+b}°', f'm∠{A} + m∠{B} = 180°',
             f'm∠{A}{C}{D} = {a}°', f'm∠{A}{C}{D} ≅ m∠{A} + m∠{B}'],
      diagram=lambda: dict(sk=[seg(A0,B0),seg(B0,D0),seg(C0,A0)], labels=labels, fx=[
        [arc(C0,A0,B0,26,'sk'), arc(C0,A0,D0,36,'sk'), tx((C0[0]+bCe[0]*62,C0[1]+bCe[1]*62+4),'180°','sk',12)],
        [arc(A0,B0,C0,28,'yl'), arc(B0,A0,C0,22,'yl'), arc(C0,A0,B0,30,'yl')],
        [tx(cen,'both 180°','yl',13)],
        arcN(C0,A0,D0,44,'mn'),
        [arc(C0,A0,D0,36,'rs'), tx((C0[0]+bCe[0]*54,C0[1]+bCe[1]*54+4),f'{a+b}°','rs',15)]]))
FAMILIES.append(_fam('Exterior Angle','Push one side out and the triangle confesses.',
  ['The exterior angle equals the two far angles added together.','You cannot cite the Exterior Angle Theorem here — you are proving it.'],
  lambda: [seg((27,7),(10,37)), seg((10,37),(44,37)), seg((44,37),(56,37)), q((37,30),(43,32),(44,37),'rs')], gen3))

# --- 4 Isosceles Triangle (two routes)
def gen4(n, R):
    A,B,C,D = shuffleR(R, list('ABCPQ'))[:4]
    route = 'bisector' if n % 2 == 1 else 'midpoint'
    A0 = (230+rintR(R,-18,18), 56+R()*14); B0 = (72+R()*20,314); C0 = (388-R()*20,314); D0 = (A0[0],314)
    given = (f'In △{A}{B}{C}:  {A}{B} ≅ {A}{C};  {A}{D} bisects ∠{B}{A}{C}.' if route == 'bisector'
             else f'In △{A}{B}{C}:  {A}{B} ≅ {A}{C};  {D} is the midpoint of {B}{C}.')
    if route == 'bisector':
        steps = [
          {'s':f'{A}{B} ≅ {A}{C}','r':'Given','why':'The two legs with matching ticks — that part is given.'},
          {'s':f'∠{B}{A}{D} ≅ ∠{D}{A}{C}','r':'Definition of angle bisector','why':'“Bisects” means AD splits the big angle into two congruent halves.'},
          {'s':f'{A}{D} ≅ {A}{D}','r':'Reflexive Property','why':'Both triangles share the side AD — anything is congruent to itself.'},
          {'s':f'△{A}{B}{D} ≅ △{A}{C}{D}','r':'SAS','why':'Two sides and the angle between them match — Side-Angle-Side.'},
          {'s':f'∠{B} ≅ ∠{C}','r':'CPCTC','why':'Corresponding Parts of Congruent Triangles are Congruent — cash it in.'}]
        fx = lambda: [
          [ticks(A0,B0,1,'rs'), ticks(A0,C0,1,'rs')],
          [arc(A0,B0,D0,26,'yl'), arc(A0,D0,C0,26,'yl')],
          [dashline(A0,D0)],
          [shade([A0,B0,D0],'shy'), shade([A0,C0,D0],'shb'), tx(((A0[0]+D0[0])/2-58,A0[1]+120),'SAS','mn',15)],
          arcN(B0,A0,D0,26,'rs') + arcN(C0,A0,D0,26,'rs')]
    else:
        steps = [
          {'s':f'{A}{B} ≅ {A}{C}','r':'Given','why':'The two legs with matching ticks — that part is given.'},
          {'s':f'{B}{D} ≅ {D}{C}','r':'Definition of midpoint','why':'The midpoint cuts BC into two congruent pieces.'},
          {'s':f'{A}{D} ≅ {A}{D}','r':'Reflexive Property','why':'Both triangles share the whole side AD.'},
          {'s':f'△{A}{B}{D} ≅ △{A}{C}{D}','r':'SSS','why':'All three pairs of sides match — Side-Side-Side.'},
          {'s':f'∠{B} ≅ ∠{C}','r':'CPCTC','why':'Match the leftover angles — CPCTC finishes it.'}]
        fx = lambda: [
          [ticks(A0,B0,1,'rs'), ticks(A0,C0,1,'rs')],
          [ticks(B0,D0,1,'mn'), ticks(D0,C0,1,'mn')],
          [dashline(A0,D0)],
          [shade([A0,B0,D0],'shy'), shade([A0,C0,D0],'shb'), tx(((A0[0]+D0[0])/2-58,A0[1]+120),'SSS','mn',15)],
          arcN(B0,A0,D0,26,'rs') + arcN(C0,A0,D0,26,'rs')]
    labels = [lb((A0[0]-2,A0[1]-12),A), lb((B0[0]-12,B0[1]+16),B), lb((C0[0]+12,C0[1]+16),C),
              lb((D0[0]+2,D0[1]+18),D,'lb',14), dot(A0), dot(B0), dot(C0), dot(D0)]
    return dict(given=given, prove=f'∠{B} ≅ ∠{C}', steps=steps,
      sPool=[f'{A}{B} ≅ {B}{C}', f'∠{A} ≅ ∠{B}', f'△{A}{B}{D} ≅ △{A}{D}{C}', f'{A}{D} ≅ {B}{C}', f'∠{B}{D}{A} ≅ ∠{C}{D}{A}'],
      diagram=lambda: dict(sk=[seg(A0,B0),seg(A0,C0),seg(B0,C0),seg(A0,D0)], labels=labels, fx=fx()))
FAMILIES.append(_fam('Isosceles Triangle','Two equal sides — watch the base angles follow.',
  ['SAS + CPCTC: lock in two sides and the angle between them, and every part follows.','Same theorem, second road: swap the bisector for a midpoint and SSS does the work.'],
  lambda: [seg((32,7),(13,37)), seg((13,37),(51,37)), seg((51,37),(32,7)), seg((32,7),(32,37),'mn'), seg((20,24),(25,26),'rs')], gen4))

# --- 5 Isosceles Converse (AAS)
def gen5(n, R):
    A,B,C,D = shuffleR(R, list('ABCPQ'))[:4]
    A0 = (230+rintR(R,-16,16),58); B0 = (74,314); C0 = (386,314); D0 = (A0[0],314)
    return dict(given=f'In △{A}{B}{C}:  ∠{B} ≅ ∠{C};  {A}{D} bisects ∠{B}{A}{C}.', prove=f'{A}{B} ≅ {A}{C}',
      steps=[
        {'s':f'∠{B} ≅ ∠{C}','r':'Given','why':'The matching base angles — given.'},
        {'s':f'∠{B}{A}{D} ≅ ∠{D}{A}{C}','r':'Definition of angle bisector','why':f'{A}{D} splits the vertex angle into two congruent halves.'},
        {'s':f'{A}{D} ≅ {A}{D}','r':'Reflexive Property','why':'Both triangles share the bisector AD.'},
        {'s':f'△{A}{B}{D} ≅ △{A}{C}{D}','r':'AAS','why':'Two pairs of angles and a corresponding non-included side — Angle-Angle-Side.'},
        {'s':f'{A}{B} ≅ {A}{C}','r':'CPCTC','why':'The legs correspond — CPCTC delivers the converse.'}],
      sPool=[f'∠{A} ≅ ∠{B}', f'{B}{D} ≅ {D}{C}', f'△{A}{B}{D} ≅ △{A}{D}{C}', f'{A}{B} ≅ {B}{C}', f'∠{B}{D}{A} ≅ ∠{A}{D}{C}'],
      diagram=lambda: dict(sk=[seg(A0,B0),seg(A0,C0),seg(B0,C0),seg(A0,D0)],
        labels=[lb((A0[0]-2,A0[1]-12),A), lb((B0[0]-12,B0[1]+16),B), lb((C0[0]+12,C0[1]+16),C),
                lb((D0[0]+2,D0[1]+18),D,'lb',14), dot(A0), dot(B0), dot(C0), dot(D0)],
        fx=[
          [arc(B0,A0,C0,24,'yl'), arc(C0,A0,B0,24,'yl')],
          [arc(A0,B0,D0,26,'sk'), arc(A0,D0,C0,26,'sk')],
          [dashline(A0,D0)],
          [shade([A0,B0,D0],'shy'), shade([A0,C0,D0],'shb'), tx(((A0[0]+D0[0])/2-58,A0[1]+120),'AAS','mn',15)],
          [ticks(A0,B0,2,'rs'), ticks(A0,C0,2,'rs')]]))
FAMILIES.append(_fam('Isosceles Converse','Equal base angles demand equal legs.',
  ['Flip a theorem and you get a new one — the converse proves the legs, not the angles.','AAS: two angles and a non-included side — the side rides along for free.'],
  lambda: [seg((32,7),(13,37)), seg((13,37),(51,37)), seg((51,37),(32,7)), seg((32,7),(32,37),'mn'),
           seg((14,30),(20,37),'rs'), q((50,37),(46,33),(44,30),'rs')], gen5))

# --- 6 Perpendicular Bisector
def gen6(n, R):
    A,B,C,D = shuffleR(R, list('ABCPQ'))[:4]
    A0 = (230+rintR(R,-16,16),58); B0 = (70,314); C0 = (390,314); D0 = (A0[0],314)
    return dict(given=f'{A}{D} ⊥ {B}{C};  {B}{D} ≅ {D}{C}.', prove=f'{A}{B} ≅ {A}{C}',
      steps=[
        {'s':f'∠{A}{D}{B} ≅ ∠{A}{D}{C}','r':'Definition of perpendicular','why':'Perpendicular lines meet at right angles — and all right angles are congruent.'},
        {'s':f'{B}{D} ≅ {D}{C}','r':'Given','why':'The matching ticks on the base are a given.'},
        {'s':f'{A}{D} ≅ {A}{D}','r':'Reflexive Property','why':'Both triangles share the whole side AD.'},
        {'s':f'△{A}{B}{D} ≅ △{A}{C}{D}','r':'SAS','why':'Two sides and the included right angle match — Side-Angle-Side.'},
        {'s':f'{A}{B} ≅ {A}{C}','r':'CPCTC','why':'Match the leftover parts — CPCTC finishes it.'}],
      sPool=[f'{A}{D} ≅ {B}{C}', f'∠{B}{A}{D} ≅ ∠{D}{A}{C}', f'{A}{B} ≅ {B}{C}', f'△{A}{B}{D} ≅ △{A}{D}{C}', f'∠{A} ≅ ∠{D}'],
      diagram=lambda: dict(sk=[seg(A0,B0),seg(A0,C0),seg(B0,C0),seg(A0,D0)],
        labels=[lb((A0[0]-2,A0[1]-12),A), lb((B0[0]-12,B0[1]+16),B), lb((C0[0]+12,C0[1]+16),C),
                lb((D0[0]+2,D0[1]+18),D,'lb',14), dot(A0), dot(B0), dot(C0), dot(D0)],
        fx=[
          [rangle(D0,A0,B0,'sk',15), rangle(D0,A0,C0,'sk',15)],
          [ticks(B0,D0,1,'rs'), ticks(D0,C0,1,'rs')],
          [dashline(A0,D0)],
          [shade([A0,B0,D0],'shy'), shade([A0,C0,D0],'shb'), tx(((A0[0]+D0[0])/2-58,A0[1]+122),'SAS','mn',15)],
          [ticks(A0,B0,2,'ch'), ticks(A0,C0,2,'ch')]]))
FAMILIES.append(_fam('Perpendicular Bisector','Two right triangles hiding inside one figure.',
  ['The reflexive property is the free congruence hiding in nearly every proof.','A right angle + a midpoint + SAS = the whole perpendicular bisector theorem.'],
  lambda: [seg((32,7),(14,37)), seg((14,37),(50,37)), seg((50,37),(32,7)), seg((32,7),(32,37),'mn'),
           seg((27,31),(27,26),'sk'), seg((27,26),(32,26),'sk')], gen6))

# --- 7 Third Angle
def gen7(n, R):
    A,B,C,D,E,F = shuffleR(R, list('ABPQRS'))[:6]
    jx = rintR(R,-8,8); jy = rintR(R,-6,6)
    A0 = (96+jx,72+jy); B0 = (46+jx,302); C0 = (214+jx,302)
    D0 = (300+jx,72+jy); E0 = (250+jx,302); F0 = (418+jx,302)
    tri = [seg(A0,B0),seg(B0,C0),seg(C0,A0),seg(D0,E0),seg(E0,F0),seg(F0,D0)]
    labels = [lb((A0[0]-2,A0[1]-12),A), lb((B0[0]-8,B0[1]+16),B), lb((C0[0]+10,C0[1]+16),C),
              lb((D0[0]-2,D0[1]-12),D), lb((E0[0]-8,E0[1]+16),E), lb((F0[0]+10,F0[1]+16),F),
              dot(A0), dot(B0), dot(C0), dot(D0), dot(E0), dot(F0)]
    return dict(given=f'In △{A}{B}{C} and △{D}{E}{F}:  ∠{A} ≅ ∠{D};  ∠{B} ≅ ∠{E}.', prove=f'∠{C} ≅ ∠{F}',
      steps=[
        {'s':f'm∠{A} + m∠{B} + m∠{C} = 180°','r':'Triangle Angle-Sum Theorem','why':'The angles of the first triangle add to 180°.'},
        {'s':f'm∠{D} + m∠{E} + m∠{F} = 180°','r':'Triangle Angle-Sum Theorem','why':'So do the angles of the second.'},
        {'s':f'm∠{A} + m∠{B} + m∠{C} = m∠{D} + m∠{E} + m∠{F}','r':'Transitive Property of Equality','why':'Both sums equal 180° — so they equal each other.'},
        {'s':f'm∠{D} + m∠{E} + m∠{C} = m∠{D} + m∠{E} + m∠{F}','r':'Substitution Property','why':f'Swap ∠{A} → ∠{D} and ∠{B} → ∠{E} on the left, since they are congruent.'},
        {'s':f'm∠{C} = m∠{F}','r':'Subtraction Property of Equality','why':f'm∠{D} + m∠{E} sits on both sides — subtract it away.'},
        {'s':f'∠{C} ≅ ∠{F}','r':'Definition of congruent angles','why':'Equal measures are congruent angles. The third angle had no choice.'}],
      sPool=[f'm∠{C} + m∠{F} = 180°', f'∠{A} ≅ ∠{F}', f'△{A}{B}{C} ≅ △{D}{E}{F}', f'm∠{C} = m∠{A}', f'∠{B} ≅ ∠{F}'],
      diagram=lambda: dict(sk=tri, labels=labels, fx=[
        [arc(A0,B0,C0,24,'yl'), arc(D0,E0,F0,24,'yl')],
        arcN(B0,A0,C0,20,'mn',2) + arcN(E0,D0,F0,20,'mn',2),
        [tx((230,178),'both = 180°','yl',15)],
        [tx((230,208),'substitute equals','sk',13)],
        arcN(C0,A0,B0,28,'rs') + arcN(F0,D0,E0,28,'rs')]))
FAMILIES.append(_fam('Third Angle','Two matches force the third — 180° leaves no freedom.',
  ['If two angles match, the third has no choice — 180° leaves no freedom.','Equal subtracted from equal: the oldest move in the book.'],
  lambda: [seg((8,36),(17,10)), seg((17,10),(27,36)), seg((27,36),(8,36)), seg((38,36),(47,10)), seg((47,10),(57,36)), seg((57,36),(38,36)),
           q((14,17),(17,15),(19,16),'yl'), q((44,17),(47,15),(49,16),'yl')], gen7))

# --- 8 Bisected Segments
def gen8(n, R):
    A,B,C,D = shuffleR(R, list('ABPQRS'))[:4]
    Mn = pickR(R, list('MXP'))
    jx = rintR(R,-10,10); jy = rintR(R,-8,8)
    M0 = (230+jx,190+jy); A0 = (84+jx,190+jy); C0 = (376+jx,190+jy)
    B0 = (306+jx,66+jy); D0 = (154+jx,314+jy)
    return dict(given=f'Segments {A}{C} and {B}{D} meet at {Mn};  {Mn} is the midpoint of both.', prove=f'{A}{B} ≅ {C}{D}',
      steps=[
        {'s':f'{A}{Mn} ≅ {C}{Mn}','r':'Definition of midpoint','why':f'{Mn} halves {A}{C} — the two pieces match.'},
        {'s':f'{B}{Mn} ≅ {D}{Mn}','r':'Definition of midpoint','why':f'Same for {B}{D}.'},
        {'s':f'∠{A}{Mn}{B} ≅ ∠{C}{Mn}{D}','r':'Vertical Angles Theorem','why':'The angles across the crossing are vertical — congruent for free.'},
        {'s':f'△{A}{B}{Mn} ≅ △{C}{D}{Mn}','r':'SAS','why':'Two pairs of sides and the included vertical angle — Side-Angle-Side.'},
        {'s':f'{A}{B} ≅ {C}{D}','r':'CPCTC','why':'The crossbars correspond — CPCTC closes the deal.'}],
      sPool=[f'△{A}{B}{Mn} ≅ △{D}{C}{Mn}', f'{A}{Mn} ≅ {B}{Mn}', f'{A}{B} ≅ {B}{C}',
             f'∠{B}{A}{Mn} ≅ ∠{D}{C}{Mn}', f'{A}{D} ≅ {B}{C}'],
      diagram=lambda: dict(sk=[seg(A0,C0),seg(B0,D0)],
        labels=[lb((A0[0]-12,A0[1]+5),A), lb((C0[0]+12,C0[1]+5),C), lb((B0[0]+12,B0[1]-4),B),
                lb((D0[0]-12,D0[1]+18),D), lb((M0[0]-8,M0[1]+20),Mn,'lb',14),
                dot(A0), dot(B0), dot(C0), dot(D0), dot(M0)],
        fx=[
          [ticks(A0,M0,1,'mn'), ticks(M0,C0,1,'mn')],
          [ticks(B0,M0,2,'mn'), ticks(M0,D0,2,'mn')],
          [arc(M0,A0,B0,26,'rs'), arc(M0,C0,D0,26,'rs')],
          [shade([A0,B0,M0],'shy'), shade([C0,D0,M0],'shb'), tx((A0[0]+34,A0[1]-52),'SAS','mn',15)],
          [ticks(A0,B0,2,'rs'), ticks(C0,D0,2,'rs')]]))
FAMILIES.append(_fam('Bisected Segments','Two segments swap halves at a crossing.',
  ['Two shared midpoints + one pair of vertical angles = SAS with style.','Vertical angles are the free angle in every crossing figure.'],
  lambda: [seg((10,10),(54,34)), seg((10,34),(54,10)), dot((32,22)), seg((28,16),(32,18),'rs')], gen8))

# --- 9 The Altitude Secret (capstone)
def gen9(n, R):
    A,B,C,D = shuffleR(R, list('ABCPQ'))[:4]
    A0 = (230+rintR(R,-14,14),56); B0 = (76,314); C0 = (384,314); D0 = (A0[0],314)
    tri = [seg(A0,B0),seg(A0,C0),seg(B0,C0),seg(A0,D0)]
    labels = [lb((A0[0]-2,A0[1]-12),A), lb((B0[0]-12,B0[1]+16),B), lb((C0[0]+12,C0[1]+16),C),
              lb((D0[0]+2,D0[1]+18),D,'lb',14), dot(A0), dot(B0), dot(C0), dot(D0)]
    return dict(given=f'In △{A}{B}{C}:  {A}{B} ≅ {A}{C};  {A}{D} bisects ∠{B}{A}{C},  with {D} on {B}{C}.', prove=f'{A}{D} ⊥ {B}{C}',
      steps=[
        {'s':f'{A}{B} ≅ {A}{C}','r':'Given','why':'The legs of the isosceles triangle — given.'},
        {'s':f'∠{B}{A}{D} ≅ ∠{D}{A}{C}','r':'Definition of angle bisector','why':f'{A}{D} splits the vertex angle in half.'},
        {'s':f'{A}{D} ≅ {A}{D}','r':'Reflexive Property','why':'Both triangles share the bisector.'},
        {'s':f'△{A}{B}{D} ≅ △{A}{C}{D}','r':'SAS','why':'Legs, half-angle, shared side — Side-Angle-Side.'},
        {'s':f'∠{A}{D}{B} ≅ ∠{A}{D}{C}','r':'CPCTC','why':f'The two angles at {D} correspond.'},
        {'s':f'm∠{A}{D}{B} + m∠{A}{D}{C} = 180°','r':'Linear Pair Postulate','why':f'{B}, {D}, {C} are collinear — the angles at {D} form a linear pair.'},
        {'s':f'm∠{A}{D}{B} = m∠{A}{D}{C}','r':'Definition of congruent angles','why':'Congruent angles have equal measures.'},
        {'s':f'm∠{A}{D}{B} + m∠{A}{D}{B} = 180°','r':'Substitution Property','why':'Swap the second measure for its equal — the same number twice.'},
        {'s':f'm∠{A}{D}{B} = 90°','r':'Division Property of Equality','why':'Half of 180° is 90° — a right angle.'},
        {'s':f'{A}{D} ⊥ {B}{C}','r':'Definition of perpendicular','why':'Meeting at right angles is exactly what perpendicular means.'}],
      sPool=[f'{B}{D} ≅ {D}{C}', f'∠{B} ≅ ∠{C}', f'△{A}{B}{D} ≅ △{A}{D}{C}', f'm∠{A}{D}{B} = 45°',
             f'{A}{D} ≅ {B}{C}', f'∠{B}{A}{D} ≅ ∠{D}{A}{C}'],
      diagram=lambda: dict(sk=tri, labels=labels, fx=[
        [ticks(A0,B0,1,'rs'), ticks(A0,C0,1,'rs')],
        [arc(A0,B0,D0,26,'yl'), arc(A0,D0,C0,26,'yl')],
        [dashline(A0,D0)],
        [shade([A0,B0,D0],'shy'), shade([A0,C0,D0],'shb'), tx(((A0[0]+D0[0])/2-58,A0[1]+118),'SAS','mn',15)],
        [arc(D0,A0,B0,22,'mn'), arc(D0,A0,C0,22,'mn')],
        [tx((230,246),f'∠{A}{D}{B} ≅ ∠{A}{D}{C}','sk',13)],
        [tx((230,272),'m + m = 180°','sk',13)],
        [tx((230,298),'m = 90°','yl',14)],
        [rangle(D0,A0,B0,'sk',14), rangle(D0,A0,C0,'sk',14)],
        [tx((352,112),f'{A}{D} ⊥ {B}{C}','rs',16)]]))
FAMILIES.append(_fam('The Altitude Secret','Ten steps to prove the bisector stands up straight.',
  ['The bisector of an isosceles vertex is secretly an altitude — ten steps to say “perpendicular”.','Big proofs are just small proofs holding hands.'],
  lambda: [seg((32,7),(14,37)), seg((14,37),(50,37)), seg((50,37),(32,7)), seg((32,7),(32,37),'mn'),
           seg((28,33),(28,29),'sk'), seg((28,29),(32,29),'sk'), seg((20,24),(25,26),'rs')], gen9))

# --- 10 Alternate Interior / corresponding
def gen10(n, R):
    Fg = transFigure(R)
    l1, l2 = shuffleR(R, list('lmpqrs'))[:2]
    alt = n % 2 == 1
    if alt:
        i, j = pickR(R, Fg['altPairs']); vc = i - 2
        steps = [
          {'s':f'∠{vc} ≅ ∠{j}','r':'Corresponding Angles Postulate','why':f'∠{vc} and ∠{j} sit in the same corner of each intersection — corresponding angles.'},
          {'s':f'∠{vc} ≅ ∠{i}','r':'Vertical Angles Theorem','why':f'At the top intersection, ∠{vc} and ∠{i} are vertical — formed by opposite rays.'},
          {'s':f'∠{i} ≅ ∠{j}','r':'Transitive Property of Congruence','why':f'∠{i} matches ∠{vc}, and ∠{vc} matches ∠{j} — chain them together.'}]
        fx = lambda: [angArc(Fg['NM'],vc,26,'rs')+angArc(Fg['NM'],j,26,'rs'),
                      angArc(Fg['NM'],vc,34,'mn')+angArc(Fg['NM'],i,26,'mn'),
                      angArc2(Fg['NM'],i,26,'yl')+angArc2(Fg['NM'],j,26,'yl')]
    else:
        i, j = pickR(R, [[1,5],[2,6],[3,7],[4,8]])
        if i >= 3:
            j2 = i + 2
            steps = [
              {'s':f'∠{i} ≅ ∠{j2}','r':'Alternate Interior Angles Theorem','why':f'∠{i} and ∠{j2} are between the parallels, on opposite sides of the cut.'},
              {'s':f'∠{j2} ≅ ∠{j}','r':'Vertical Angles Theorem','why':f'∠{j2} and ∠{j} are vertical angles at the bottom intersection.'},
              {'s':f'∠{i} ≅ ∠{j}','r':'Transitive Property of Congruence','why':f'Chain the two congruences: ∠{i} → ∠{j2} → ∠{j}.'}]
            fx = lambda: [angArc(Fg['NM'],i,26,'mn')+angArc(Fg['NM'],j2,26,'mn'),
                          angArc(Fg['NM'],j2,34,'rs')+angArc(Fg['NM'],j,26,'rs'),
                          angArc2(Fg['NM'],i,26,'yl')+angArc2(Fg['NM'],j,26,'yl')]
        else:
            iv = i + 2
            steps = [
              {'s':f'∠{i} ≅ ∠{iv}','r':'Vertical Angles Theorem','why':f'∠{i} and ∠{iv} are vertical angles at the top intersection.'},
              {'s':f'∠{iv} ≅ ∠{j}','r':'Alternate Interior Angles Theorem','why':f'∠{iv} and ∠{j} are between the parallels, on opposite sides of the cut.'},
              {'s':f'∠{i} ≅ ∠{j}','r':'Transitive Property of Congruence','why':f'Chain the two congruences: ∠{i} → ∠{iv} → ∠{j}.'}]
            fx = lambda: [angArc(Fg['NM'],i,26,'mn')+angArc(Fg['NM'],iv,26,'mn'),
                          angArc(Fg['NM'],iv,34,'rs')+angArc(Fg['NM'],j,26,'rs'),
                          angArc2(Fg['NM'],i,26,'yl')+angArc2(Fg['NM'],j,26,'yl')]
    sPool = [f'∠{p} ≅ ∠{q}' for p,q in [[1,5],[2,6],[3,7],[4,8],[3,5],[4,6],[3,6],[4,5],[1,3],[2,4],[5,7],[6,8],[1,8],[2,7],[1,6],[2,5]]]
    sPool += [f'm∠{p} + m∠{q} = 180°' for p,q in [[1,8],[3,6],[2,7],[4,5]]] + ['m∠3 ≅ m∠5']
    labels = [lb((432,116),l1), lb((432,274),l2), lb((Fg['T'][0]+12,20),'t')] + numLabels(Fg['NM'])
    return dict(given=f'line {l1} ∥ line {l2};  line t is a transversal.', prove=steps[-1]['s'], steps=steps, sPool=sPool,
      diagram=lambda: dict(sk=Fg['sk'], labels=labels, fx=fx()))
FAMILIES.append(_fam('Alternate Interior','What every pair of parallel lines agrees on.',
  ['Congruence is contagious: two things congruent to the same thing are congruent to each other.','Corresponding angles ride the same chain — vertical angles plus alternate interior.'],
  lambda: [seg((10,14),(54,14)), seg((10,30),(54,30)), seg((20,40),(46,6)),
           q((22,20),(26,22),(27,23),'yl'), q((42,24),(38,22),(37,21),'yl')], gen10))

# --- 11 Same-Side Interior
def gen11(n, R):
    Fg = transFigure(R)
    l1, l2 = shuffleR(R, list('lmpqrs'))[:2]
    i, j = pickR(R, Fg['samePairs']); j2 = i + 2
    prove = f'∠{i} and ∠{j} are supplementary'
    steps = [
      {'s':f'∠{i} ≅ ∠{j2}','r':'Alternate Interior Angles Theorem','why':f'∠{i} and ∠{j2} are between the parallels, on opposite sides of the cut.'},
      {'s':f'm∠{j} + m∠{j2} = 180°','r':'Linear Pair Postulate','why':f'∠{j} and ∠{j2} sit together on line {l2} — a linear pair.'},
      {'s':f'm∠{j} + m∠{i} = 180°','r':'Substitution Property','why':f'Swap m∠{j2} for its equal, m∠{i}, in the sum.'},
      {'s':prove,'r':'Definition of supplementary angles','why':'Two angles whose measures add to 180° are, by definition, supplementary.'}]
    sPool = [f'∠{i} ≅ ∠{j}', f'm∠{i} + m∠{j2} = 180°', f'∠{j} ≅ ∠{j2}', f'm∠{i} ≅ m∠{j}']
    sPool += [f'∠{p} ≅ ∠{q}' for p,q in [[1,5],[2,6],[3,7],[4,8],[3,5],[4,6],[1,8],[2,7]]]
    labels = [lb((432,116),l1), lb((432,274),l2), lb((Fg['T'][0]+12,20),'t')] + numLabels(Fg['NM'])
    Pt, Qt, yl_, ym_ = Fg['Pt'], Fg['Qt'], Fg['yl'], Fg['ym']
    return dict(given=f'line {l1} ∥ line {l2};  line t is a transversal.', prove=prove, steps=steps, sPool=sPool,
      diagram=lambda: dict(sk=Fg['sk'], labels=labels, fx=[
        angArc(Fg['NM'],i,26,'mn')+angArc(Fg['NM'],j2,26,'mn'),
        angArc(Fg['NM'],j,26,'sk')+angArc(Fg['NM'],j2,32,'sk')+[tx((Qt[0]+58,ym_-22),'180°','sk',13)],
        angArc(Fg['NM'],i,26,'yl')+angArc(Fg['NM'],j,26,'yl')+[tx(((Pt[0]+Qt[0])/2,(yl_+ym_)/2+6),'180°','yl',14)],
        angArc2(Fg['NM'],i,28,'rs')+angArc2(Fg['NM'],j,28,'rs')]))
FAMILIES.append(_fam('Same-Side Interior','The inside angles on one side always team up to 180°.',
  ['Alternate interior angles are congruent; slide one over a linear pair and they turn supplementary.','Substitution is how one equation inherits another.'],
  lambda: [seg((10,14),(54,14)), seg((10,30),(54,30)), seg((20,40),(46,6)),
           q((24,21),(27,23),(27,25),'yl'), q((40,23),(37,25),(37,27),'yl')], gen11))

# --- 12 Parallelogram Angles
def gen12(n, R):
    g = paraGeo(R)
    W,X,Y,Z,A0,B0,C0,D0 = g['W'],g['X'],g['Y'],g['Z'],g['A0'],g['B0'],g['C0'],g['D0']
    return dict(given=f'{W}{X}{Y}{Z} is a parallelogram.', prove=f'∠{W} ≅ ∠{Y}',
      steps=[
        {'s':f'∠{W} and ∠{Z} are supplementary','r':'Consecutive Interior Angles Theorem','why':f'{W}{X} ∥ {Z}{Y} cut by transversal {W}{Z} — the same-side interior angles at {W} and {Z} add to 180°.'},
        {'s':f'∠{Y} and ∠{Z} are supplementary','r':'Consecutive Interior Angles Theorem','why':f'{W}{Z} ∥ {X}{Y} cut by transversal {Z}{Y} — same idea at the other corner.'},
        {'s':f'∠{W} ≅ ∠{Y}','r':'Congruent Supplements Theorem','why':'Two angles supplementary to the same angle are congruent to each other.'}],
      sPool=[f'∠{X} ≅ ∠{Z}', f'∠{W} ≅ ∠{X}', f'∠{W} and ∠{X} are supplementary', f'∠{X} ≅ ∠{Y}',
             f'm∠{W} ≅ m∠{Y}', f'{W}{X} ≅ {X}{Y}'],
      diagram=lambda: dict(sk=g['sk'], labels=g['labels'], fx=[
        [arrows(A0,B0,1,'sk'), arrows(D0,C0,1,'sk'), arc(A0,B0,D0,24,'sk',False), arc(D0,A0,C0,24,'sk',False)],
        [arrows(A0,D0,1,'mn'), arrows(B0,C0,1,'mn'), arc(C0,B0,D0,24,'mn',False), arc(D0,A0,C0,32,'mn',False)],
        arcN(A0,B0,D0,30,'rs') + arcN(C0,B0,D0,30,'rs')]))
FAMILIES.append(_fam('Parallelogram Angles','Two pairs of parallels vote, and opposite angles agree.',
  ['Congruent Supplements: two angles supplementary to the same angle must match.','Each pair of parallel sides contributes one supplementary pair.'],
  lambda: [seg((17,9),(49,9)), seg((49,9),(56,33)), seg((56,33),(10,33)), seg((10,33),(17,9)),
           q((15,15),(13,18),(13,21),'yl'), q((51,27),(53,24),(53,21),'yl')], gen12))

# --- 13 Parallelogram Diagonal
def gen13(n, R):
    g = paraGeo(R)
    W,X,Y,Z,A0,B0,C0,D0 = g['W'],g['X'],g['Y'],g['Z'],g['A0'],g['B0'],g['C0'],g['D0']
    prove = f'△{W}{X}{Z} ≅ △{Y}{Z}{X}'
    return dict(given=f'{W}{X}{Y}{Z} is a parallelogram.', prove=prove,
      steps=[
        {'s':f'∠{W}{X}{Z} ≅ ∠{Y}{Z}{X}','r':'Alternate Interior Angles Theorem','why':f'{W}{X} ∥ {Z}{Y} with transversal {X}{Z} — alternate interior angles at {X} and {Z}.'},
        {'s':f'∠{W}{Z}{X} ≅ ∠{Y}{X}{Z}','r':'Alternate Interior Angles Theorem','why':f'{W}{Z} ∥ {X}{Y} with the same transversal — the other pair.'},
        {'s':f'{X}{Z} ≅ {X}{Z}','r':'Reflexive Property','why':'Both triangles share the diagonal XZ.'},
        {'s':prove,'r':'ASA','why':'Two pairs of angles with the included side between them — Angle-Side-Angle.'}],
      sPool=[f'△{W}{X}{Z} ≅ △{Y}{X}{Z}', f'△{W}{X}{Z} ≅ △{Z}{Y}{X}', f'{W}{X} ≅ {Y}{Z}',
             f'∠{W} ≅ ∠{Y}', f'{X}{Z} ≅ {W}{Y}', f'∠{W}{X}{Z} ≅ ∠{Y}{X}{Z}'],
      diagram=lambda: dict(sk=g['sk'], labels=g['labels'], fx=[
        [arc(B0,A0,D0,24,'yl',False), arc(D0,C0,B0,24,'yl',False)],
        [arc(D0,A0,B0,32,'mn',False), arc(B0,C0,D0,32,'mn',False)],
        [seg(B0,D0,'sk',2.4)],
        [shade([A0,B0,D0],'shy'), shade([C0,D0,B0],'shb'), tx(((A0[0]+C0[0])/2-52,190+52),'ASA','mn',15)]]))
FAMILIES.append(_fam('Parallelogram Diagonal','One slice, and the parallelogram splits into twins.',
  ['ASA needs the side between the two angles — position is part of the argument.','A shared side plus two alternate interior pairs: ASA with a free side.'],
  lambda: [seg((17,9),(49,9)), seg((49,9),(56,33)), seg((56,33),(10,33)), seg((10,33),(17,9)), seg((49,9),(17,33),'mn')], gen13))

# --- 14 Parallelogram Sides
def gen14(n, R):
    g = paraGeo(R)
    W,X,Y,Z,A0,B0,C0,D0 = g['W'],g['X'],g['Y'],g['Z'],g['A0'],g['B0'],g['C0'],g['D0']
    return dict(given=f'{W}{X}{Y}{Z} is a parallelogram.', prove=f'{W}{X} ≅ {Y}{Z}',
      steps=[
        {'s':f'∠{W}{X}{Z} ≅ ∠{Y}{Z}{X}','r':'Alternate Interior Angles Theorem','why':f'{W}{X} ∥ {Z}{Y} with transversal {X}{Z} — alternate interior angles.'},
        {'s':f'∠{W}{Z}{X} ≅ ∠{Y}{X}{Z}','r':'Alternate Interior Angles Theorem','why':f'The other pair, from {W}{Z} ∥ {X}{Y}.'},
        {'s':f'{X}{Z} ≅ {X}{Z}','r':'Reflexive Property','why':'Both triangles share the diagonal.'},
        {'s':f'△{W}{X}{Z} ≅ △{Y}{Z}{X}','r':'ASA','why':'Two angles and the included side — Angle-Side-Angle.'},
        {'s':f'{W}{X} ≅ {Y}{Z}','r':'CPCTC','why':'The opposite sides correspond — the payout.'}],
      sPool=[f'△{W}{X}{Z} ≅ △{Z}{Y}{X}', f'{X}{Y} ≅ {Y}{Z}', f'∠{W} ≅ ∠{Y}', f'{W}{X} ≅ {X}{Y}', f'{X}{Z} ≅ {W}{Y}'],
      diagram=lambda: dict(sk=g['sk'], labels=g['labels'], fx=[
        [arc(B0,A0,D0,24,'yl',False), arc(D0,C0,B0,24,'yl',False)],
        [arc(D0,A0,B0,32,'mn',False), arc(B0,C0,D0,32,'mn',False)],
        [seg(B0,D0,'sk',2.4)],
        [shade([A0,B0,D0],'shy'), shade([C0,D0,B0],'shb'), tx(((A0[0]+C0[0])/2-52,190+52),'ASA','mn',15)],
        [ticks(A0,B0,1,'rs'), ticks(C0,D0,1,'rs')]]))
FAMILIES.append(_fam('Parallelogram Sides','Same twins, different payout — this time in sides.',
  ['Once the diagonals prove triangles congruent, CPCTC pays out sides too.','Every parallelogram theorem is two alternate-interior pairs and a reflexive away.'],
  lambda: [seg((17,9),(49,9)), seg((49,9),(56,33)), seg((56,33),(10,33)), seg((10,33),(17,9)),
           seg((31,5),(31,12),'rs'), seg((31,30),(31,37),'rs')], gen14))

# --- 15 Kite
def gen15(n, R):
    A,B,C,D = shuffleR(R, list('ABPQ'))[:4]
    A0 = (230+rintR(R,-12,12), 50+R()*16); C0 = (230+rintR(R,-12,12), 318-R()*16)
    e = 95+R()*30; ey = 186+R()*16; B0 = (230+e,ey); D0 = (230-e,ey)
    return dict(given=f'{A}{B} ≅ {A}{D};  {C}{B} ≅ {C}{D}.', prove=f'∠{B} ≅ ∠{D}',
      steps=[
        {'s':f'{A}{B} ≅ {A}{D}','r':'Given','why':'The upper pair of neighboring sides — marked with single ticks.'},
        {'s':f'{C}{B} ≅ {C}{D}','r':'Given','why':'The lower pair of neighboring sides — marked with double ticks.'},
        {'s':f'{A}{C} ≅ {A}{C}','r':'Reflexive Property','why':'Both triangles share the whole spine AC.'},
        {'s':f'△{A}{B}{C} ≅ △{A}{D}{C}','r':'SSS','why':'All three pairs of sides match — Side-Side-Side.'},
        {'s':f'∠{B} ≅ ∠{D}','r':'CPCTC','why':'The wings of the kite correspond — CPCTC seals it.'}],
      sPool=[f'{A}{B} ≅ {C}{B}', f'∠{A} ≅ ∠{C}', f'△{A}{B}{C} ≅ △{C}{D}{A}', f'{A}{C} ≅ {B}{D}', f'∠{B} ≅ ∠{C}'],
      diagram=lambda: dict(sk=[seg(A0,B0),seg(B0,C0),seg(C0,D0),seg(D0,A0)],
        labels=[lb((A0[0]-2,A0[1]-12),A), lb((B0[0]+14,B0[1]+5),B), lb((C0[0]-2,C0[1]+18),C),
                lb((D0[0]-14,D0[1]+5),D), dot(A0), dot(B0), dot(C0), dot(D0)],
        fx=[
          [ticks(A0,B0,1,'rs'), ticks(A0,D0,1,'rs')],
          [ticks(C0,B0,2,'mn'), ticks(C0,D0,2,'mn')],
          [dashline(A0,C0)],
          [shade([A0,B0,C0],'shy'), shade([A0,D0,C0],'shb'), tx(((A0[0]+C0[0])/2-64,(A0[1]+C0[1])/2),'SSS','mn',15)],
          arcN(B0,A0,C0,26,'rs') + arcN(D0,A0,C0,26,'rs')]))
FAMILIES.append(_fam('Kite','Two pairs of neighboring equals, one shared spine.',
  ['SSS is the bluntest instrument in the box — and often exactly the right one.','The kite\'s cross-section: the diagonal is the shared side nobody has to prove.'],
  lambda: [seg((32,6),(48,21)), seg((48,21),(32,38)), seg((32,38),(16,21)), seg((16,21),(32,6)),
           seg((32,6),(32,38),'mn'), seg((22,15),(27,18),'rs')], gen15))

# --- 16 Circle Radii
def gen16(n, R):
    Ap, Bp = shuffleR(R, list('ABCDEF'))[:2]
    Oname = pickR(R, list('OZU'))
    O0 = (230,202); r = 126
    a1 = (188+R()*44)*math.pi/180; a2 = (-12-R()*44)*math.pi/180
    A0 = (O0[0]+r*math.cos(a1), O0[0]*0+O0[1]+r*math.sin(a1))
    B0 = (O0[0]+r*math.cos(a2), O0[1]+r*math.sin(a2))
    lA = [lb((O0[0]+(r+17)*math.cos(a1), O0[1]+(r+17)*math.sin(a1)+5),Ap),
          lb((O0[0]+(r+17)*math.cos(a2), O0[1]+(r+17)*math.sin(a2)+5),Bp),
          lb((O0[0]-4,O0[1]+22),Oname,'lb',14), dot(O0), dot(A0), dot(B0)]
    sk = [circleFig(O0[0],O0[1],r,'ch',2.6), seg(O0,A0), seg(O0,B0), seg(A0,B0)]
    bA, bB, bO = bisAt(A0,O0,B0), bisAt(B0,A0,O0), bisAt(O0,A0,B0)
    if n % 2 == 1:
        return dict(given=f'Circle {Oname} with {Ap} and {Bp} on the circle.', prove=f'∠{Oname}{Ap}{Bp} ≅ ∠{Ap}{Bp}{Oname}',
          steps=[
            {'s':f'{Oname}{Ap} ≅ {Oname}{Bp}','r':'Radii of a circle are congruent','why':f'Both segments run from the center {Oname} to the circle — they are radii.'},
            {'s':f'△{Ap}{Oname}{Bp} is isosceles','r':'Definition of isosceles triangle','why':'A triangle with two congruent sides is isosceles — that is the definition.'},
            {'s':f'∠{Oname}{Ap}{Bp} ≅ ∠{Ap}{Bp}{Oname}','r':'Isosceles Triangle Theorem','why':'In an isosceles triangle, the angles opposite the equal sides are congruent.'}],
          sPool=[f'{Oname}{Ap} ≅ {Ap}{Bp}', f'∠{Ap}{Oname}{Bp} ≅ ∠{Oname}{Ap}{Bp}', f'△{Ap}{Oname}{Bp} ≅ △{Bp}{Oname}{Ap}',
                 f'{Ap}{Bp} ≅ {Oname}{Bp}', f'∠{Ap} ≅ ∠{Bp}'],
          diagram=lambda: dict(sk=sk, labels=lA, fx=[
            [ticks(O0,A0,1,'yl'), ticks(O0,B0,1,'yl')],
            [tx((230,352),f'△{Ap}{Oname}{Bp} is isosceles','mn',15)],
            arcN(A0,O0,B0,24,'rs') + arcN(B0,A0,O0,24,'rs')]))
    a = rintR(R,32,66); c = 180 - 2*a
    lB = lA + [tx((A0[0]+bA[0]*38, A0[1]+bA[1]*38+4), f'{a}°','yl',14)]
    return dict(given=f'Circle {Oname} with {Ap}, {Bp} on the circle;  m∠{Oname}{Ap}{Bp} = {a}°.', prove=f'm∠{Ap}{Oname}{Bp} = {c}°',
      steps=[
        {'s':f'{Oname}{Ap} ≅ {Oname}{Bp}','r':'Radii of a circle are congruent','why':f'Both segments run from the center {Oname} to the circle.'},
        {'s':f'∠{Oname}{Ap}{Bp} ≅ ∠{Ap}{Bp}{Oname}','r':'Isosceles Triangle Theorem','why':'Two equal radii make an isosceles triangle — the base angles match.'},
        {'s':f'm∠{Ap}{Bp}{Oname} = {a}°','r':'Substitution Property','why':f'The base angle equals the given one: {a}°.'},
        {'s':f'm∠{Ap}{Bp}{Oname} + m∠{Ap}{Oname}{Bp} + m∠{Oname}{Ap}{Bp} = 180°','r':'Triangle Angle-Sum Theorem','why':'The three angles of the triangle add to 180°.'},
        {'s':f'{a}° + {a}° + m∠{Ap}{Oname}{Bp} = 180°','r':'Substitution Property','why':f'Both base angles are {a}° — write the sum.'},
        {'s':f'm∠{Ap}{Oname}{Bp} = {c}°','r':'Subtraction Property of Equality','why':f'180° − {2*a}° = {c}° — the angle at the center.'}],
      sPool=[f'{Oname}{Ap} ≅ {Ap}{Bp}', f'∠{Ap}{Oname}{Bp} ≅ ∠{Oname}{Ap}{Bp}', f'm∠{Ap}{Oname}{Bp} = {180-a}°',
             f'△{Ap}{Oname}{Bp} ≅ △{Bp}{Oname}{Ap}', f'm∠{Ap}{Bp}{Oname} = {c}°'],
      diagram=lambda: dict(sk=sk, labels=lB, fx=[
        [ticks(O0,A0,1,'yl'), ticks(O0,B0,1,'yl')],
        arcN(A0,O0,B0,24,'rs') + arcN(B0,A0,O0,24,'rs'),
        [tx((B0[0]+bB[0]*38, B0[1]+bB[1]*38+4), f'{a}°','mn',14)],
        [tx((230,352),'180°','yl',15)],
        [tx((230,330), f'{a}° + {a}° + m∠{Oname} = 180°','yl',13)],
        [arc(O0,A0,B0,34,'rs'), tx((O0[0]+bO[0]*48, O0[1]+bO[1]*48+4), f'{c}°','rs',15)]]))
FAMILIES.append(_fam('Circle Radii','Every radius is a hidden isosceles triangle.',
  ['Two radii make any triangle inside a circle isosceles — for free.','Draw two radii and the Isosceles Triangle Theorem hands you the base angles.'],
  lambda: [circleFig(32,21,13), seg((32,21),(19.8,16.6)), seg((32,21),(44.2,16.6)), seg((19.8,16.6),(44.2,16.6)),
           q((25,18),(27,15),(29,16),'rs')], gen16))

# --- 17 Angle Addition
def gen17(n, R):
    A,B,C,D = shuffleR(R, list('ABPQ'))[:4]
    B0 = (64,318)
    dA = norm((80,-250)); dD = norm((190,-180)); dC = norm((320,-30))
    A0 = (B0[0]+dA[0]*252, B0[1]+dA[1]*252); C0 = (B0[0]+dC[0]*252, B0[1]+dC[1]*252); D0 = (B0[0]+dD[0]*252, B0[1]+dD[1]*252)
    bBD, bDC, bAC = bisAt(B0,A0,D0), bisAt(B0,D0,C0), bisAt(B0,A0,C0)
    angAD = f'm∠{A}{B}{D}'; angDC = f'm∠{D}{B}{C}'; angAC = f'm∠{A}{B}{C}'
    labels = [lb((A0[0]-4,A0[1]-12),A), lb((C0[0]+16,C0[1]+6),C), lb((D0[0]+14,D0[1]-6),D), lb((B0[0]-10,B0[1]+18),B),
              dot(A0), dot(B0), dot(C0), dot(D0), seg(A0,B0), seg(B0,C0), seg(B0,D0)]
    if n % 2 == 0:
        a = rintR(R,25,60); b = rintR(R,25,60); s = a + b
        return dict(given=f'{D} is inside ∠{A}{B}{C};  {angAD} = {a}°,  {angDC} = {b}°.', prove=f'{angAC} = {s}°',
          steps=[
            {'s':f'{angAD} + {angDC} = {angAC}','r':'Angle Addition Postulate','why':f'{D} sits inside the big angle — the two parts compose the whole.'},
            {'s':f'{a}° + {b}° = {angAC}','r':'Substitution Property','why':f'Swap in the given measures: {a}° and {b}°.'},
            {'s':f'{angAC} = {s}°','r':'Symmetric Property','why':'Flip the equation to present the answer.'}],
          sPool=[f'{angAD} = {s}°', f'{angDC} = {s}°', f'{angAD} ≅ {angDC}', f'{angAC} = {a*b}°', f'{angAC} = 90°'],
          diagram=lambda: dict(sk=labels, labels=[], fx=[
            [arc(B0,D0,C0,36,'yl'), arc(B0,A0,D0,46,'mn')],
            [tx((352,140), f'{a}° + {b}°','yl',14), tx((352,164), f'= {angAC}','yl',13)],
            [arc(B0,A0,C0,62,'rs',False), tx((352,196), f'{s}°','rs',17)]]))
    a = rintR(R,1,3); x0 = rintR(R,4,9); b = rintR(R,3,9)
    k = a*x0 + b; T = 2*k
    return dict(given=f'{B}{D} bisects ∠{A}{B}{C};  {angAC} = {T}°,  {angAD} = {a}x+{b}.', prove=f'x = {x0}',
      steps=[
        {'s':f'{angAD} = {angDC}','r':'Definition of angle bisector','why':'A bisector splits the angle into two congruent halves.'},
        {'s':f'{angAD} + {angDC} = {angAC}','r':'Angle Addition Postulate','why':'The two halves compose the whole angle.'},
        {'s':f'{angAD} + {angAD} = {T}°','r':'Substitution Property','why':'The halves are equal, and together they are the whole — the same number twice.'},
        {'s':f'{angAD} = {k}°','r':'Division Property of Equality','why':f'Half of {T}° is {k}°.'},
        {'s':f'{a}x+{b} = {k}','r':'Substitution Property','why':'Swap in the expression for the half-angle.'},
        {'s':f'{a}x = {k-b}','r':'Subtraction Property of Equality','why':f'Subtract {b} from both sides.'},
        {'s':f'x = {x0}','r':'Division Property of Equality','why':f'Divide both sides by {a}.'}],
      sPool=[f'x = {x0+1}', f'x = {x0-1}', f'{angAD} = {k+10}°', f'{angAC} = {T+20}°', f'{angDC} = {a}x+{b}', f'∠{A}{B}{D} ≅ ∠{A}{B}{C}'],
      diagram=lambda: dict(sk=labels, labels=[], fx=[
        [arc(B0,A0,D0,36,'yl'), arc(B0,D0,C0,36,'yl')],
        [tx((B0[0]+bAC[0]*70, B0[1]+bAC[1]*70+4), f'{T}°','sk',15)],
        [tx((352,120), angAD,'yl',12), tx((352,142), f'= {angDC}','yl',12)],
        [tx((352,168), f'2m = {T}°','yl',14), tx((352,192), f'm = {k}°','mn',14)],
        [tx((352,218), f'{a}x+{b} = {k}','yl',13), tx((352,244), f'x = {x0}','rs',16)]]))
FAMILIES.append(_fam('Angle Addition','One ray, two parts, one whole angle.',
  ['Angle addition is segment addition wearing a protractor.','Bisect a known angle and algebra halves it for you.'],
  lambda: [seg((8,36),(56,36)), seg((8,36),(50,10)), seg((8,36),(42,16)), q((22,28),(24,22),(26,21),'yl')], gen17))

# --- 18 Square Corner
def gen18(n, R):
    B0 = (60,316); A0 = (60,54); C0 = (414,316)
    dD = norm((160,-150)); D0 = (B0[0]+dD[0]*260, B0[1]+dD[1]*260)
    bAD, bDC = bisAt(B0,A0,D0), bisAt(B0,D0,C0)
    sk = [seg(B0,A0), seg(B0,C0), seg(B0,D0), dot(B0), dot(A0), dot(C0)]
    if n % 2 == 0:
        a = rintR(R,15,70); c = 90 - a
        return dict(given='∠ABC is a right angle;  BD is inside it,  m∠ABD = %d°.' % a, prove=f'm∠DBC = {c}°',
          steps=[
            {'s':'m∠ABC = 90°','r':'Definition of right angle','why':'A right angle measures exactly 90° — that is its definition.'},
            {'s':'m∠ABD + m∠DBC = m∠ABC','r':'Angle Addition Postulate','why':'BD sits inside the corner — the two parts compose the whole.'},
            {'s':'m∠ABD + m∠DBC = 90°','r':'Substitution Property','why':'Swap in the 90° from step 1.'},
            {'s':f'{a}° + m∠DBC = 90°','r':'Substitution Property','why':f'Swap in the given {a}°.'},
            {'s':f'm∠DBC = {c}°','r':'Subtraction Property of Equality','why':f"90° − {a}° = {c}° — the corner's remaining budget."}],
          sPool=[f'm∠DBC = {a}°', 'm∠ABD + m∠DBC = 180°', f'm∠ABC = {c}°', '∠ABD ≅ ∠DBC', f'm∠ABD = {c}°'],
          diagram=lambda: dict(sk=sk,
            labels=[lb((46,42),'A','ch',15), lb((430,330),'C','ch',15), lb((244,124),'D','ch',15), lb((46,332),'B','ch',15),
                    tx((B0[0]+bAD[0]*46, B0[1]+bAD[1]*46+4), f'{a}°','yl',14)],
            fx=[
              [rangle(B0,A0,C0,'sk',16), tx((100,286),'90°','sk',13)],
              [arc(B0,D0,C0,40,'mn')],
              [tx((310,150), f'{a}° + m∠DBC','yl',13), tx((310,174),'= 90°','yl',13)],
              [arc(B0,D0,C0,52,'rs'), tx((B0[0]+bDC[0]*62, B0[1]+bDC[1]*62+4), f'{c}°','rs',16)]]))
    V = (230,306); L = 200
    def ray(t): return (V[0]+L*math.cos(t*math.pi/180), V[1]-L*math.sin(t*math.pi/180))
    Ra, Rb, Rc, Rd = ray(155), ray(115), ray(65), ray(25)
    b1, b2, b3 = bisAt(V,Ra,Rb), bisAt(V,Rb,Rc), bisAt(V,Rc,Rd)
    sk2 = [seg(V,Ra), seg(V,Rb), seg(V,Rc), seg(V,Rd), dot(V)]
    return dict(given='∠1 and ∠2 are complementary;  ∠3 and ∠2 are complementary.', prove='∠1 ≅ ∠3',
      steps=[
        {'s':'∠1 and ∠2 are complementary','r':'Given','why':'Handed to you on the tin — the first corner pairs to 90°.'},
        {'s':'∠3 and ∠2 are complementary','r':'Given','why':'Same ∠2, other corner — also pairing to 90°.'},
        {'s':'∠1 ≅ ∠3','r':'Congruent Complements Theorem','why':'Both spend themselves against the same ∠2: each is 90° − m∠2, so they match. Subtract the shared part.'}],
      sPool=['∠1 ≅ ∠2', '∠2 ≅ ∠3', 'm∠1 + m∠3 = 90°', '∠1 and ∠3 are complementary', 'm∠1 ≅ m∠3'],
      diagram=lambda: dict(sk=sk2,
        labels=[tx((V[0]+b1[0]*30, V[1]+b1[1]*30+4),'1','yl',15), tx((V[0]+b2[0]*30, V[1]+b2[1]*30+4),'2','lb',15),
                tx((V[0]+b3[0]*30, V[1]+b3[1]*30+4),'3','mn',15),
                lb((28,232),'A','ch',14), lb((128,112),'B','ch',14), lb((332,112),'C','ch',14), lb((432,232),'D','ch',14)],
        fx=[
          [rangle(V,Ra,Rc,'sk',12), rangle(V,Rb,Rd,'mn',17), tx((96,290),'90°','sk',11), tx((372,290),'90°','sk',11)],
          [arc(V,Ra,Rb,38,'rs'), arc(V,Rc,Rd,38,'rs')],
          [tx((230,58),'∠1 ≅ ∠3','rs',17)]]))
FAMILIES.append(_fam('Square Corner','Everything inside a right angle adds to 90°.',
  ['A right angle is a 90° budget — the pieces inside must spend it exactly.','Two angles that complete the same corner are twins: that is the Complements theorem in action.'],
  lambda: [seg((8,34),(44,34)), seg((8,34),(8,10)), seg((8,34),(26,14)),
           seg((8,26),(8,20),'sk'), seg((8,20),(14,20),'sk'), q((15,24),(16,20),(18,19),'yl')], gen18))

# --- 19 Hypotenuse Leg
def gen19(n, R):
    A,B,C,D = shuffleR(R, list('ABPQ'))[:4]
    A0 = (230+rintR(R,-14,14),58); B0 = (74,314); C0 = (386,314); D0 = (A0[0],314)
    sk = [seg(A0,B0),seg(A0,C0),seg(B0,C0),seg(A0,D0)]
    labels = [lb((A0[0]-2,A0[1]-12),A), lb((B0[0]-12,B0[1]+16),B), lb((C0[0]+12,C0[1]+16),C),
              lb((D0[0]+2,D0[1]+18),D,'lb',14), dot(A0), dot(B0), dot(C0), dot(D0)]
    return dict(given=f'In △{A}{B}{C}:  {A}{B} ≅ {A}{C};  {A}{D} ⊥ {B}{C}.', prove=f'{B}{D} ≅ {D}{C}',
      steps=[
        {'s':f'∠{A}{D}{B} ≅ ∠{A}{D}{C}','r':'Definition of perpendicular','why':'Perpendicular means right angles at the foot — and all right angles are congruent.'},
        {'s':f'{A}{B} ≅ {A}{C}','r':'Given','why':'The legs of the big triangle — the hypotenuses of the two right triangles.'},
        {'s':f'{A}{D} ≅ {A}{D}','r':'Reflexive Property','why':'Both right triangles share the altitude AD — a leg of each.'},
        {'s':f'△{A}{B}{D} ≅ △{A}{C}{D}','r':'HL','why':'Congruent hypotenuses, one congruent leg, right angles included — Hypotenuse-Leg.'},
        {'s':f'{B}{D} ≅ {D}{C}','r':'CPCTC','why':'The two base pieces correspond — the altitude bisects the base.'}],
      sPool=[f'∠{A}{B}{D} ≅ ∠{A}{C}{D}', f'{A}{D} ≅ {B}{C}', f'△{A}{B}{D} ≅ △{A}{D}{C}', f'∠{A} ≅ ∠{B}', f'{A}{B} ≅ {B}{C}'],
      diagram=lambda: dict(sk=sk, labels=labels, fx=[
        [rangle(D0,A0,B0,'sk',15), rangle(D0,A0,C0,'sk',15)],
        [ticks(A0,B0,1,'rs'), ticks(A0,C0,1,'rs')],
        [dashline(A0,D0)],
        [shade([A0,B0,D0],'shy'), shade([A0,C0,D0],'shb'), tx(((A0[0]+D0[0])/2-52,A0[1]+122),'HL','mn',15)],
        [ticks(B0,D0,2,'ch'), ticks(D0,C0,2,'ch')]]))
FAMILIES.append(_fam('Hypotenuse Leg','Right triangles travel light — two parts are enough.',
  ['HL is SAS\'s right-triangle shortcut: the right angle is the hidden third piece.','Equal legs of an isosceles triangle, one shared altitude — and the base splits in half.'],
  lambda: [seg((32,7),(14,37)), seg((14,37),(50,37)), seg((50,37),(32,7)), seg((32,7),(32,37),'mn'),
           seg((27,31),(27,26),'sk'), seg((27,26),(32,26),'sk'), seg((19,22),(25,24),'rs')], gen19))

# --- 20 Bisected Line
def gen20(n, R):
    A,B,C,D = shuffleR(R, list('ABPQ'))[:4]
    B0 = (230,292); L0 = (52,292); R0 = (408,292); D0 = (230+rintR(R,-8,8),58)
    an1 = f'∠{A}{B}{D}'; an2 = f'∠{D}{B}{C}'
    sk = [seg(L0,R0), seg(B0,D0), dot(B0), dot(L0), dot(R0), dot(D0)]
    labels = [lb((L0[0]-4,L0[1]-14),A), lb((R0[0]+4,R0[1]-14),C), lb((D0[0]+2,D0[1]-12),D), lb((B0[0]-2,B0[1]+22),B)]
    return dict(given=f'{A}, {B}, {C} are collinear;  {B}{D} bisects ∠{A}{B}{C}.', prove=f'{B}{D} ⊥ {A}{C}',
      steps=[
        {'s':f'{an1} and {an2} are a linear pair','r':'Linear Pair Postulate','why':f'{A}, {B}, {C} form a line, so the two angles at {B} are a linear pair.'},
        {'s':f'm{an1} + m{an2} = 180°','r':'Definition of supplementary angles','why':'A linear pair is supplementary — the measures add to 180°.'},
        {'s':f'{an1} ≅ {an2}','r':'Definition of angle bisector','why':f'{B}{D} bisects the straight angle — two congruent halves.'},
        {'s':f'm{an1} = m{an2}','r':'Definition of congruent angles','why':'Congruent angles have equal measures.'},
        {'s':f'm{an1} + m{an1} = 180°','r':'Substitution Property','why':'Swap the second measure for its equal — the same number twice.'},
        {'s':f'm{an1} = 90°','r':'Division Property of Equality','why':'Half of 180° is 90° — a right angle.'},
        {'s':f'{B}{D} ⊥ {A}{C}','r':'Definition of perpendicular','why':'Meeting at right angles is exactly what perpendicular means. Q.E.D.'}],
      sPool=[f'm{an1} = 45°', f'{an1} and {an2} are complementary', f'm{an1} + m{an2} = 90°',
             f'{B}{D} bisects {A}{C}', f'{an1} ≅ ∠{A}{B}{C}', f'{B}{D} ≅ {A}{C}'],
      diagram=lambda: dict(sk=sk, labels=labels, fx=[
        [arc(B0,L0,D0,34,'sk',False), arc(B0,D0,R0,34,'sk',False), tx((B0[0]+118,B0[1]-96),'180°','sk',13)],
        [tx((352,150), f'm{an1} + m{an2}','sk',12), tx((352,172),'= 180°','sk',12)],
        [arc(B0,L0,D0,26,'yl'), arc(B0,D0,R0,26,'yl')],
        [tx((352,200), an1,'yl',12), tx((352,222), f'≅ {an2}','yl',12)],
        [tx((352,250),'m + m = 180°','yl',13)],
        [tx((352,278),'m = 90°','yl',14)],
        [rangle(B0,L0,D0,'sk',17), rangle(B0,D0,R0,'sk',17), tx((B0[0]+92,B0[1]-42),'90°','rs',14)]]))
FAMILIES.append(_fam('Bisected Line','Cut a straight angle in half — you built a perpendicular.',
  ['Bisect a straight angle and the cut stands at 90° — perpendicular for free.','The capstone\'s straight-line twin: same algebra, no triangles needed.'],
  lambda: [seg((8,24),(56,24)), seg((32,24),(45,9)), q((38,15),(36,12),(32,11),'yl')], gen20))

CHAPTERS = [['Lines & Angles',[0,1,2,3,17,18,20]], ['Triangles',[4,5,6,7,8,9,19]],
            ['Parallel Lines',[10,11]], ['Quadrilaterals',[12,13,14,15]], ['Circles',[16]]]
def chOf(fi):
    for i, (_, fids) in enumerate(CHAPTERS):
        if fi in fids: return i
    return 0
ROMAN = ['I','II','III','IV','V']

# ============================================================ persistence
SAVE_PATH = os.path.join(os.path.expanduser('~'), '.qed_proofs.json')
def blank_profile():
    return dict(unlocked=0, coach=False, muted=False, hard=False, relaxed=False, theme='emerald',
                daily=None, dailyStreak=0, streak3=0, combo=0,
                stats=dict(flawless=0, stars=0, time=0, flaws=0), ach={}, mastery={},
                fams=[dict(count=0, results=[]) for _ in FAMILIES])
class Store:
    def __init__(self):
        self.p = self._load()
    def _load(self):
        try:
            with open(SAVE_PATH) as f: p = json.load(f)
        except Exception:
            return blank_profile()
        bl = blank_profile()
        if not isinstance(p, dict): return bl
        fams = [ (p.get('fams') or [])[i] if i < len(p.get('fams') or []) else bl['fams'][i] for i in range(len(bl['fams'])) ]
        stats = dict(bl['stats']); stats.update(p.get('stats') or {})
        out = dict(bl); out.update(p); out['fams'] = fams; out['stats'] = stats
        return out
    def save(self):
        try:
            with open(SAVE_PATH, 'w') as f: json.dump(self.p, f)
        except Exception: pass
    def mastery_tick(self, reason, ok):
        m = self.p['mastery'].setdefault(reason, dict(c=0, e=0))
        m['c' if ok else 'e'] += 1
STORE = Store()

# ============================================================ engine
def makeLevel(fi, n):
    R = mulberry32(fi * 7919 + n * 104729 + 13)
    fam = FAMILIES[fi]
    L = fam['gen'](n, R)
    p = STORE.p
    trueS = [s['s'] for s in L['steps']]; trueR = [s['r'] for s in L['steps']]
    boost = 2 if p['hard'] else 0
    sN = min(len(L['sPool']), 2 + math.ceil(n * 0.6) + boost)
    rN = min(6 + boost, 3 + math.ceil(n * 0.7) + boost)
    L['sD'] = shuffleR(R, [t for t in L['sPool'] if t not in trueS])[:sN]
    rp = shuffleR(R, [r for r in REASONS if r not in trueR])
    if 'Given' not in trueR: rp = ['Given'] + [r for r in rp if r != 'Given']
    L['rD'] = rp[:rN]
    L['take'] = fam['take'][(n - 1) % len(fam['take'])]
    return L
def weakReasons():
    p = STORE.p
    ent = [(r, v) for r, v in p['mastery'].items() if v['e'] > 0]
    ent.sort(key=lambda kv: -kv[1]['e'])
    return [r for r, _ in ent[:3]]
def focusTarget():
    wr = weakReasons()
    if not wr: return None
    cands = []
    for fi in range(STORE.p['unlocked'] + 1):
        L = makeLevel(fi, 1)
        if any(s['r'] in wr for s in L['steps']): cands.append(fi)
    return random.choice(cands) if cands else None
def surpriseTarget():
    p = STORE.p; ws = []; tot = 0.0
    for fi in range(p['unlocked'] + 1):
        f = p['fams'][fi]
        best = max(f['results']) if f['results'] else 0
        wgt = 1 + 2 / (1 + f['count']) + (1 if best < 2 else 0)
        ws.append((fi, wgt)); tot += wgt
    r = random.random() * tot
    for fi, wgt in ws:
        r -= wgt
        if r <= 0: return fi
    return p['unlocked']
def dailySpec():
    d = datetime.date.today()
    seed = d.year * 372 + d.month * 31 + d.day
    fi = (seed * 2654435761 & 0xFFFFFFFF) % (STORE.p['unlocked'] + 1)
    return dict(fi=fi, n=4 + (seed >> 7) % 5)

# ============================================================ chalk figure canvas
class FigureCanvas(QWidget):
    def __init__(self, parent=None, board=True):
        super().__init__(parent)
        self.board = board
        self.fig = None; self.sk_t = 0.0; self.lbl_a = 0.0
        self.fx_p = []; self.hl = -1; self.stamp_p = 0.0
        self.parts = []
        self.timer = QTimer(self); self.timer.timeout.connect(self.tick)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._phase = ''
    def heightForWidth(self, w): return int(w * 380.0 / 460.0)
    def set_figure(self, fig, animate=True):
        self.fig = fig; self.sk_t = 0.0 if animate else 1.0; self.lbl_a = 0.0 if animate else 1.0
        self.fx_p = [-1.0] * len(fig['fx']); self.hl = -1; self.stamp_p = 0.0; self.parts = []
        self._phase = 'sk' if animate else ''
        if animate:
            if SND: SND.play('sketch')
            self.timer.start(16)
        self.update()
    def reveal_fx(self, i):
        if 0 <= i < len(self.fx_p):
            self.fx_p[i] = 0.0; self._phase = self._phase or 'fx'; self.timer.start(16)
    def show_stamp(self):
        self.stamp_p = 0.001; self._phase = self._phase or 'st'; self.timer.start(16)
    def clear_fx(self):
        self.fx_p = [-1.0] * len(self.fig['fx']); self.stamp_p = 0.0; self.update()
    def burst(self, x, y, n=14, sp=2.4):
        for _ in range(n):
            a = random.random() * math.pi * 2; v = (0.4 + random.random()) * sp
            self.parts.append(dict(x=x, y=y, vx=math.cos(a)*v, vy=math.sin(a)*v-0.7,
                                   life=0.0, mx=0.55+random.random()*0.5, s=0.8+random.random()*1.8))
        self.timer.start(16)
    def tick(self):
        active = False
        if self._phase == 'sk':
            self.sk_t = min(1.0, self.sk_t + 0.022); self.lbl_a = max(0.0, min(1.0, (self.sk_t - 0.65) / 0.35))
            if self.sk_t >= 1.0: self._phase = ''
            active = True
        if any(0 <= p < 1 for p in self.fx_p):
            self.fx_p = [min(1.0, p + 0.045) if p >= 0 else p for p in self.fx_p]; active = True
        if 0 < self.stamp_p < 1:
            self.stamp_p = min(1.0, self.stamp_p + 0.028); active = True
        for pt in self.parts[:]:
            pt['life'] += 0.016
            if pt['life'] > pt['mx']: self.parts.remove(pt); continue
            pt['x'] += pt['vx']; pt['y'] += pt['vy']; pt['vy'] += 0.02; pt['vx'] *= 0.985
        if self.parts: active = True
        if not active: self.timer.stop()
        self.update()
    def _geom(self):
        w, h = self.width(), self.height()
        sc = min(w / 460.0, h / 380.0)
        ox = (w - 460 * sc) / 2; oy = (h - 380 * sc) / 2
        return sc, ox, oy
    def paintEvent(self, ev):
        qp = QPainter(self); qp.setRenderHint(QPainter.Antialiasing)
        if self.board:
            qp.setPen(Qt.NoPen); qp.setBrush(Qt.NoBrush)
        if not self.fig:
            return
        sc, ox, oy = self._geom()
        qp.translate(ox, oy); qp.scale(sc, sc)
        n = max(1, len(self.fig['sk']))
        for i, pr in enumerate(self.fig['sk']):
            t = 1.0 if self.sk_t >= 1 else max(0.0, min(1.0, (self.sk_t * (1 + 0.6) - (i / n) * 0.6) / 0.4))
            self._paint_prim(qp, pr, t, 1.0)
        for pr in self.fig['lb']:
            self._paint_prim(qp, pr, self.lbl_a, 1.0)
        for gi, group in enumerate(self.fig['fx']):
            p = self.fx_p[gi]
            if p < 0: continue
            boost = 1.6 if gi == self.hl else 1.0
            m = max(1, len(group))
            for i, pr in enumerate(group):
                t = max(0.0, min(1.0, (p * 1.6 - (i / m) * 0.6) / 0.5))
                self._paint_prim(qp, pr, t, boost)
        if self.stamp_p > 0:
            self._paint_stamp(qp)
        qp.setPen(Qt.NoPen)
        for pt in self.parts:
            a = int(190 * (1 - pt['life'] / pt['mx']))
            qp.setBrush(QColor(PAL.dust)); qp.setBrush(QColor(PAL.dust[:7] + '' if False else PAL.dust))
            c = QColor(PAL.dust); c.setAlpha(a)
            qp.setBrush(c)
            qp.drawEllipse(QPointF(pt['x'], pt['y']), pt['s'], pt['s'])
    def _paint_prim(self, qp, pr, t, boost):
        if t <= 0: return
        k = pr['k']
        colkey = pr.get('c', pr.get('col', 'ch'))
        base = getattr(PAL, colkey, QColor('#fff'))
        if k == 'seg':
            self._line(qp, pr['a'], pr['b'], base, pr['w'] * boost, t)
        elif k == 'q':
            pts = self._quad_pts(pr['a'], pr['c'], pr['b'])
            self._pts(qp, pts, getattr(PAL, pr['col'], base), pr['w'] * boost, t)
        elif k == 'poly':
            pts = list(pr['pts'])
            if pr.get('close'): pts = pts + [pts[0]]
            self._pts(qp, pts, getattr(PAL, pr['c'], base), pr['w'] * boost, t)
        elif k == 'rrect':
            x, y, w2, h2 = pr['r']
            path = QPainterPath(); path.addRoundedRect(QRectF(x, y, w2, h2), 14, 14)
            self._path(qp, path, getattr(PAL, pr['c'], base), pr['w'] * boost, t)
        elif k == 'circle':
            self._circle(qp, pr['p'], pr['r'], getattr(PAL, pr['c'], base), pr['w'] * boost, t)
        elif k == 'arc':
            v, a, b, r = pr['v'], pr['a'], pr['b'], pr['r']
            t1 = math.atan2(a[1]-v[1], a[0]-v[0]); t2 = math.atan2(b[1]-v[1], b[0]-v[0])
            d = t2 - t1
            while d > math.pi: d -= 2 * math.pi
            while d < -math.pi: d += 2 * math.pi
            N = max(10, int(abs(d) * r / 5))
            pts = [(v[0] + r * math.cos(t1 + d * i / N), v[1] + r * math.sin(t1 + d * i / N)) for i in range(N + 1)]
            self._pts(qp, pts, getattr(PAL, pr['c'], base), 2.2 * boost, t)
            if pr.get('tick') and t >= 1:
                tm = t1 + d / 2
                q1 = (v[0] + (r - 4.5) * math.cos(tm), v[1] + (r - 4.5) * math.sin(tm))
                q2 = (v[0] + (r + 4.5) * math.cos(tm), v[1] + (r + 4.5) * math.sin(tm))
                self._line(qp, q1, q2, getattr(PAL, pr['c'], base), 2.2 * boost, 1)
        elif k == 'ticks':
            a, b, cnt = pr['a'], pr['b'], pr['n']
            mx, my = (a[0]+b[0])/2, (a[1]+b[1])/2
            u = norm((b[0]-a[0], b[1]-a[1])); qv = (-u[1], u[0])
            c = getattr(PAL, pr['c'], base)
            for i in range(cnt):
                o = (i - (cnt - 1) / 2) * 5.5
                cx, cy = mx + u[0]*o, my + u[1]*o
                self._line(qp, (cx - qv[0]*6, cy - qv[1]*6), (cx + qv[0]*6, cy + qv[1]*6), c, 2.4 * boost, t)
        elif k == 'arrows':
            a, b, cnt = pr['a'], pr['b'], pr['n']
            mx, my = (a[0]+b[0])/2, (a[1]+b[1])/2
            u = norm((b[0]-a[0], b[1]-a[1])); px_, py_ = -u[1], u[0]
            c = getattr(PAL, pr['c'], base)
            for i in range(cnt):
                o = (i - (cnt - 1) / 2) * 10
                cx, cy = mx + u[0]*o, my + u[1]*o
                pts = [(cx - u[0]*4 + px_*4.5, cy - u[1]*4 + py_*4.5), (cx + u[0]*4, cy + u[1]*4),
                       (cx - u[0]*4 - px_*4.5, cy - u[1]*4 - py_*4.5)]
                self._pts(qp, pts, c, 2.0 * boost, t)
        elif k == 'rangle':
            v, a, b, s = pr['v'], pr['a'], pr['b'], pr['s']
            u1 = norm((a[0]-v[0], a[1]-v[1])); u2 = norm((b[0]-v[0], b[1]-v[1]))
            p1 = (v[0]+u1[0]*s, v[1]+u1[1]*s); p2 = (v[0]+(u1[0]+u2[0])*s, v[1]+(u1[1]+u2[1])*s); p3 = (v[0]+u2[0]*s, v[1]+u2[1]*s)
            self._pts(qp, [p1, p2, p3], getattr(PAL, pr['c'], base), 2.0 * boost, t)
        elif k == 'shade':
            if t < 1: return
            c = getattr(PAL, pr['c'], base)
            qp.setPen(Qt.NoPen); qp.setBrush(c)
            qp.drawPolygon(QPolygonF([QPointF(x, y) for x, y in pr['pts']]))
        elif k == 'dash':
            if t < 1: return
            pen = QPen(getattr(PAL, pr['c'], base), 4.5); pen.setCapStyle(Qt.RoundCap); pen.setStyle(Qt.DotLine); pen.setDashPattern([1, 6])
            qp.setPen(pen); qp.drawLine(QPointF(*pr['a']), QPointF(*pr['b']))
        elif k == 'dot':
            c = QColor(getattr(PAL, pr['c'], base)); c.setAlpha(int(255 * t))
            qp.setPen(Qt.NoPen); qp.setBrush(c)
            qp.drawEllipse(QPointF(*pr['p']), 3, 3)
        elif k == 'txt':
            c = QColor(getattr(PAL, pr['c'], base)); c.setAlpha(int(255 * t))
            qp.setPen(c); qp.setBrush(Qt.NoBrush)
            f = hand(pr['s'], bold=True)
            qp.setFont(f)
            r = QRectF(pr['p'][0] - 90, pr['p'][1] - pr['s'], 180, pr['s'] * 2)
            qp.drawText(r, Qt.AlignCenter, pr['t'])
    def _quad_pts(self, a, c, b):
        out = []
        for i in range(13):
            t2 = i / 12
            x = (1-t2)**2*a[0] + 2*(1-t2)*t2*c[0] + t2**2*b[0]
            y = (1-t2)**2*a[1] + 2*(1-t2)*t2*c[1] + t2**2*b[1]
            out.append((x, y))
        return out
    def _line(self, qp, a, b, col, w, t):
        self._pts(qp, [a, b], col, w, t)
    def _pts(self, qp, pts, col, w, t):
        if len(pts) < 2 or t <= 0: return
        seglens = [math.hypot(pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1]) for i in range(len(pts)-1)]
        total = sum(seglens) or 1
        target = total * t
        out = [pts[0]]; acc = 0
        for i, L in enumerate(seglens):
            if acc + L >= target:
                f = (target - acc) / (L or 1)
                out.append((pts[i][0] + (pts[i+1][0]-pts[i][0])*f, pts[i][1] + (pts[i+1][1]-pts[i][1])*f))
                break
            out.append(pts[i+1]); acc += L
        rnd = random.Random(int(out[0][0] * 7 + out[-1][0] * 3) & 0xFFFF)
        jit = [(x + rnd.uniform(-1.0, 1.0), y + rnd.uniform(-1.0, 1.0)) for x, y in out]
        c1 = QColor(col); c1.setAlpha(235)
        pen = QPen(c1, w); pen.setCapStyle(Qt.RoundCap); pen.setJoinStyle(Qt.RoundJoin)
        qp.setPen(pen); qp.drawPolyline([QPointF(x, y) for x, y in out])
        c2 = QColor(col); c2.setAlpha(38)
        pen2 = QPen(c2, w * 2.1); pen2.setCapStyle(Qt.RoundCap)
        qp.setPen(pen2); qp.drawPolyline([QPointF(x, y) for x, y in jit])
    def _path(self, qp, path, col, w, t):
        c1 = QColor(col); c1.setAlpha(int(235 * t))
        pen = QPen(c1, w); pen.setCapStyle(Qt.RoundCap)
        qp.setPen(pen); qp.setBrush(Qt.NoBrush); qp.drawPath(path)
        c2 = QColor(col); c2.setAlpha(int(38 * t))
        qp.setPen(QPen(c2, w * 2.1)); qp.drawPath(path)
    def _circle(self, qp, c, r, col, w, t):
        N = max(14, int(r / 4)); pts = []
        for i in range(N + 1):
            a = -math.pi/2 + 2 * math.pi * i / N * t
            pts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
        self._pts(qp, pts, col, w, 1.0)
    def _paint_stamp(self, qp):
        t = self.stamp_p
        rnd = random.Random(11)
        cx, cy, rx, ry = 230, 198, 96, 24
        pts = []
        for i in range(41):
            a = 2 * math.pi * i / 40
            wob = 1 + rnd.uniform(-0.12, 0.12)
            pts.append((cx + rx * wob * math.cos(a), cy + ry * wob * math.sin(a)))
        pts.append(pts[0])
        self._pts(qp, pts, PAL.rs, 3.0, min(1.0, t * 1.3))
        if t > 0.45:
            c = QColor(PAL.rs); c.setAlpha(int(255 * min(1.0, (t - 0.45) / 0.4)))
            qp.setPen(c); qp.setFont(disp(44))
            qp.save(); qp.translate(230, 198); qp.rotate(-6)
            qp.drawText(QRectF(-120, -34, 240, 60), Qt.AlignCenter, 'Q.E.D.')
            qp.restore()
    def stamp_bursts(self, three_star):
        n = 34 if three_star else 20
        QTimer.singleShot(350, lambda: self.burst(230, 195, n, 2.8))
        QTimer.singleShot(650, lambda: self.burst(320, 175, n, 2.8))
        QTimer.singleShot(800, lambda: self.burst(140, 205, n, 2.8))
def render_fig_pixmap(fig, w, h, ink=None, scale=2.0):
    tmp = FigureCanvas(board=False)
    tmp.fig = fig; tmp.sk_t = 1; tmp.lbl_a = 1; tmp.fx_p = [1.0] * len(fig['fx'])
    if ink:
        tmp._ink = ink
        orig = tmp._paint_prim
        def inked(qp, pr, t, boost):
            pr = dict(pr)
            for key in ('c', 'col'):
                if key in pr: pr[key] = 'ink'
            orig(qp, pr, t, boost)
        PAL.ink = QColor(ink)
        tmp._paint_prim = inked
    pm = QPixmap(int(w * scale), int(h * scale))
    pm.fill(Qt.transparent)
    old_w, old_h = tmp.width(), tmp.height()
    tmp.resize(w, h)
    tmp.render(pm)
    tmp.resize(old_w, old_h)
    if ink: del PAL.ink
    return pm

# monkey-patch ink color resolution inside _paint_prim
_orig_getattr_paint = FigureCanvas._paint_prim
def _paint_prim_ink(self, qp, pr, t, boost):
    if hasattr(self, '_ink'):
        pr = dict(pr)
        for key in ('c', 'col'):
            if key in pr: pr[key] = 'ink'
        PAL.ink = QColor(self._ink)
    _orig_getattr_paint(self, qp, pr, t, boost)
    if hasattr(self, '_ink'): del PAL.ink
FigureCanvas._paint_prim = _paint_prim_ink
# extend getattr(PAL,...) fallback: patch getattrs by adding 'ink' attribute when needed
def _pal_getattr(self, name):
    try:
        return object.__getattribute__(self, name)
    except AttributeError:
        if name == 'ink': return QColor(self._ink_color) if hasattr(self, '_ink_color') else QColor('#000')
        raise
PAL.__getattr__ = _pal_getattr
def _canvas_ink_setup(self, ink):
    self._ink = True; PAL._ink_color = ink
def render_fig_pixmap(fig, w, h, ink=None, scale=2.0):
    tmp = FigureCanvas(board=False)
    tmp.fig = fig; tmp.sk_t = 1; tmp.lbl_a = 1; tmp.fx_p = [1.0] * len(fig['fx'])
    tmp.resize(w, h)
    if ink: PAL._ink_color = ink
    pm = QPixmap(int(w * scale), int(h * scale)); pm.fill(Qt.transparent)
    tmp.render(pm)
    if ink: del PAL._ink_color
    return pm

# ============================================================ widgets: mini figure & flow layout
class GFig(QWidget):
    def __init__(self, prims, vw, vh, w, h, parent=None):
        super().__init__(parent)
        self.prims = prims; self.vw, self.vh = vw, vh
        self.setFixedSize(w, h)
    def paintEvent(self, ev):
        qp = QPainter(self); qp.setRenderHint(QPainter.Antialiasing)
        sc = min(self.width() / self.vw, self.height() / self.vh)
        qp.translate((self.width() - self.vw * sc) / 2, (self.height() - self.vh * sc) / 2)
        qp.scale(sc, sc)
        tmp = FigureCanvas(board=False)
        for pr in self.prims: tmp._paint_prim(qp, pr, 1.0, 1.0)

class FlowLayout(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lay = QHBoxLayout(); self.lay.setContentsMargins(0, 0, 0, 0); self.lay.setSpacing(8)
        self.setLayout(self.lay)
        self.wids = []
    def clear(self):
        for w in self.wids:
            w.setParent(None); w.deleteLater()
        self.wids = []
    def add(self, w):
        self.wids.append(w)
        self.lay.addWidget(w, 0, Qt.AlignTop | Qt.AlignLeft)
        # simple wrap: reflow into rows based on width
    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self.reflow()
    def reflow(self):
        # rebuild rows to wrap at width
        for w in self.wids: self.lay.removeWidget(w)
        while self.lay.count(): self.lay.takeAt(0)
        maxw = max(120, self.width())
        row = QHBoxLayout(); row.setSpacing(8)
        def flush():
            if row.count():
                cont = QWidget(); cont.setLayout(row)
                self.lay.addWidget(cont, 0, Qt.AlignTop | Qt.AlignLeft)
        for w in self.wids:
            row.addWidget(w, 0, Qt.AlignTop | Qt.AlignLeft)
            if row.sizeHint().width() > maxw and row.count() > 1:
                last = row.takeAt(row.count() - 1).widget()
                flush(); row = QHBoxLayout(); row.setSpacing(8)
                row.addWidget(last, 0, Qt.AlignTop | Qt.AlignLeft)
        flush()
        self.lay.addStretch(1)

# ============================================================ stylesheet
def build_stylesheet(css):
    return f"""
QWidget {{ background: {css['desk']}; color: {css['chalk']}; font-family: 'Kalam','Segoe Print','Bradley Hand','Comic Sans MS'; }}
QFrame#board {{ background: {css['board']}; border: 11px solid {css['frame']}; border-radius: 8px; }}
QLabel {{ background: transparent; }}
QLabel#wm {{ font-size: 22px; }}
QLabel#lvl {{ color: {css['yellow']}; font-size: 16px; }}
QLabel#given {{ color: {css['yellow']}; }}
QLabel#prove {{ color: {css['strong']}; font-weight: bold; }}
QLabel#note {{ color: {css['yellow']}; font-size: 15px; }}
QLabel#toast {{ background: {css['toastbg']}; border: 1.5px dashed {css['rose']}; color: {css['rose']};
   border-radius: 10px; padding: 8px 18px; font-size: 16px; font-weight: bold; }}
QPushButton {{ background: transparent; border: 1.7px solid {css['l3']}; border-radius: 10px;
   padding: 7px 16px; font-size: 14px; color: {css['chalk']}; }}
QPushButton:hover {{ border-color: {css['hov']}; }}
QPushButton[cls="pri"] {{ background: {css['chalk']}; color: {css['pritext']}; border-color: {css['chalk']}; font-weight: bold; }}
QPushButton[cls="pri"]:hover {{ background: {css['strong']}; }}
QPushButton[cls="ibtn"] {{ border: 1.5px solid {css['l2']}; border-radius: 9px; padding: 4px 10px;
   color: {css['dim']}; font-size: 13px; font-weight: bold; }}
QPushButton[cls="ibtn"]:hover {{ color: {css['chalk']}; border-color: {css['hov']}; }}
QPushButton[cls="sm"] {{ font-size: 12.5px; padding: 5px 12px; }}
QPushButton[cls="on"] {{ border-color: {css['mint']}; color: {css['mint']}; }}
QPushButton[cls="chip"] {{ border: 1.6px solid {css['l3']}; border-radius: 10px; padding: 6px 11px;
   font-size: 12.5px; text-align: left; background: {css['wash']}; }}
QPushButton[cls="chip"]:hover {{ border-color: {css['hov']}; }}
QPushButton[cls="chip"][sel="true"] {{ border-color: {css['yellow']}; color: {css['yellow']}; background: {css['accsoft']}; }}
QPushButton[cls="chip"][pulse="true"] {{ border-color: {css['yellow']}; color: {css['yellow']}; }}
QPushButton[cls="swatch"] {{ border: 2px solid {css['l3']}; border-radius: 12px; padding: 0; min-width: 24px; max-width: 24px; min-height: 24px; max-height: 24px; }}
QPushButton[cls="swatch"][on="true"] {{ border-color: {css['yellow']}; }}
QFrame#slot {{ border: 1.7px dashed {css['l2']}; border-radius: 11px; padding: 6px 12px; font-size: 12.5px; background: transparent; }}
QFrame#slot[avail="true"] {{ border-color: {css['accmid']}; }}
QFrame#slot[filled="true"] {{ border-style: solid; border-color: {css['l3']}; background: {css['wash']}; }}
QFrame#slot[done="true"] {{ border-color: {css['l2']}; }}
QFrame#slot[err="true"] {{ border-color: {css['rose']}; border-style: solid; }}
QFrame#slot[drop="true"] {{ border-color: {css['mint']}; border-style: solid; background: {css['mintsoft']}; }}
QLabel#pnum {{ border: 1.6px solid {css['l4']}; border-radius: 14px; color: {css['dim']};
   font-size: 11px; min-width: 24px; max-width: 24px; min-height: 24px; max-height: 24px; }}
QLabel#pnum[cur="true"] {{ border-color: {css['yellow']}; color: {css['yellow']}; }}
QLabel#pnum[flash="true"] {{ border-color: {css['rose']}; color: {css['rose']}; }}
QLabel#pchk {{ color: {css['rose']}; font-size: 16px; }}
QLabel#bankh {{ color: {css['dim']}; font-size: 13px; font-weight: bold; }}
QLabel#phead {{ color: {css['yellow']}; font-weight: bold; letter-spacing: 2px; font-size: 14px; }}
QFrame#card {{ background: {css['panel']}; border: 1.7px solid {css['l2']}; border-radius: 16px; }}
QFrame#cardIn {{ background: {css['panel']}; }}
QLabel#qedbig {{ font-size: 40px; color: {css['yellow']}; font-weight: bold; }}
QLabel#unlock {{ color: {css['mint']}; font-weight: bold; font-size: 15px; }}
QLabel#take {{ color: {css['yellow']}; font-size: 16px; }}
QLabel#dim {{ color: {css['dim']}; }}
QLabel#pace {{ color: {css['faint']}; font-size: 12px; }}
QPushButton[cls="dopt"] {{ text-align: left; padding: 9px 13px; font-size: 13px; }}
QPushButton[cls="dopt"][st="ok"] {{ border-color: {css['mint']}; color: {css['mint']}; background: {css['mintsoft']}; }}
QPushButton[cls="dopt"][st="bad"] {{ border-color: {css['rose']}; color: {css['rose']}; background: {css['rosesoft']}; }}
QFrame#frow {{ border: 1.5px dashed {css['l2']}; border-radius: 10px; padding: 8px 11px; }}
QFrame#frow[bad="true"] {{ border-color: {css['rose']}; border-style: solid; background: {css['rosesoft']}; }}
QFrame#frow[err="true"] {{ border-color: {css['rose']}; border-style: solid; }}
QFrame#frow:hover {{ border-color: {css['accmid']}; }}
QProgressBar {{ border: 1.4px solid {css['l4']}; border-radius: 4px; background: transparent;
   min-height: 6px; max-height: 6px; min-width: 86px; max-width: 86px; }}
QProgressBar::chunk {{ background: {css['yellow']}; border-radius: 3px; }}
QLineEdit, QComboBox {{ background: {css['wash']}; border: 1.6px solid {css['l2']}; border-radius: 9px;
   padding: 7px 11px; color: {css['chalk']}; font-size: 13px; }}
QComboBox QAbstractItemView {{ background: {css['panel']}; color: {css['chalk']}; selection-background-color: {css['accsoft']}; }}
QFrame#panelbox {{ border: 1.5px dashed {css['l2']}; border-radius: 12px; }}
QFrame#gitem {{ border-bottom: 1.5px dashed {css['l1']}; }}
QFrame#gitem[open="true"] {{ background: {css['wash']}; }}
QLabel#gtitle {{ color: {css['yellow']}; font-weight: bold; font-size: 13px; }}
QScrollArea {{ border: none; }}
QScrollBar:vertical {{ background: transparent; width: 9px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {css['l3']}; border-radius: 4px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QFrame#combo {{ border: 1.5px dashed {css['mintmid']}; border-radius: 9px; color: {css['mint']};
   font-weight: bold; padding: 2px 10px; font-size: 13px; }}
QLabel#hr {{ color: {css['faint']}; font-size: 12px; }}
QLabel#tally {{ color: {css['faint']}; font-size: 14px; }}
QLabel#tally b {{ color: {css['yellow']}; }}
QLabel#tag {{ color: {css['yellow']}; font-size: 21px; }}
QLabel#chtitle {{ color: {css['yellow']}; font-weight: bold; font-size: 16px; }}
QLabel#meta {{ color: {css['dim']}; font-size: 12px; }}
QLabel#famname {{ font-size: 13.5px; }}
QLabel#famtag {{ color: {css['dim']}; font-size: 12px; }}
QFrame#lvrow {{ border-bottom: 1.5px dashed {css['l1']}; }}
QFrame#lvrow:hover {{ background: {css['wash']}; }}
QFrame#lvrow[locked="true"] {{ background: transparent; }}
QLabel#klabel {{ color: {css['yellow']}; font-weight: bold; font-size: 15px; margin-right: 8px; }}
"""

# ============================================================ UI widgets
def repolish(w):
    w.style().unpolish(w); w.style().polish(w)
def mkbtn(text, cls='', cb=None, tip=''):
    b = QPushButton(text); b.setProperty('cls', cls or 'x')
    b.setCursor(Qt.PointingHandCursor)
    if cb: b.clicked.connect(cb)
    if tip: b.setToolTip(tip)
    return b
class Card(QFrame):
    def __init__(self, page, chip):
        super().__init__()
        self.setObjectName('slot'); self.setProperty('cls2', 'card')
        self.page = page; self.chip = chip
        self.setCursor(Qt.PointingHandCursor)
        lay = QHBoxLayout(self); lay.setContentsMargins(6, 6, 8, 6); lay.setSpacing(6)
        ic = QLabel('△' if chip['kind'] == 's' else '∴')
        ic.setStyleSheet('color:%s;font-size:12px;' % (PAL.mn if chip['kind'] == 's' else PAL.yl))
        lab = QLabel(chip['text']); lab.setWordWrap(True)
        lab.setFont(hand(pt=10))
        lay.addWidget(ic, 0, Qt.AlignTop); lay.addWidget(lab, 1)
        self._press = None; self._dragging = False
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton: self._press = e.position()
        super().mousePressEvent(e)
    def mouseMoveEvent(self, e):
        if self._press is not None and not self._dragging:
            if (e.position() - self._press).manhattanLength() > 10:
                self._dragging = True
                drag = QDrag(self)
                md = QMimeData(); md.setData('application/x-qed-chip', self.chip['id'].encode())
                drag.setMimeData(md); drag.setPixmap(self.grab())
                drag.exec(Qt.CopyAction)
                self._dragging = False; self._press = None
    def mouseReleaseEvent(self, e):
        if self._press is not None and not self._dragging:
            self.page.toggle_sel(self.chip['id'])
        self._press = None
class Slot(QFrame):
    def __init__(self, page, kind, i):
        super().__init__()
        self.setObjectName('slot'); self.page = page; self.kind = kind; self.i = i
        self.lay = QHBoxLayout(self); self.lay.setContentsMargins(8, 4, 8, 4)
        self.lab = QLabel(''); self.lab.setWordWrap(True); self.lab.setFont(hand(pt=10))
        self.lay.addWidget(self.lab)
        self.setCursor(Qt.PointingHandCursor)
        self.setAcceptDrops(True)
        self._ph = 'statement…' if kind == 's' else 'reason…'
    def set_state(self, text=None, avail=False, filled=False, done=False, err=False, drop=False):
        for prop in ('avail', 'filled', 'done', 'err', 'drop'):
            self.setProperty(prop, False)
        if avail: self.setProperty('avail', True)
        if filled: self.setProperty('filled', True)
        if done: self.setProperty('done', True)
        if err: self.setProperty('err', True)
        if drop: self.setProperty('drop', True)
        self.lab.setText(text if text else f'<span style="color:{PAL.lb}">{self._ph}</span>')
        self.lab.setFont(hand(pt=10))
        repolish(self)
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton: self.page.slot_click(self)
    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('application/x-qed-chip') and self.page.slot_acceptable(self):
            self.setProperty('drop', True); repolish(self); e.accept()
        else: e.ignore()
    def dragLeaveEvent(self, e):
        self.setProperty('drop', False); repolish(self)
    def dropEvent(self, e):
        self.setProperty('drop', False); repolish(self)
        cid = bytes(e.mimeData().data('application/x-qed-chip')).decode()
        self.page.drop_attempt(cid, self)
        e.accept()

class Toast(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName('toast'); self.setWordWrap(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hide(); self.timer = QTimer(self); self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)
    def show_msg(self, msg, good=False, sticky=False):
        self.setText(msg)
        self.setStyleSheet(self.styleSheet().replace('border: 1.5px dashed %s' % PAL.rs, ''))
        self.setStyleSheet(f"background: {'#F2'+self.parent().palette().color(self.parent().backgroundRole()).name()[1:] if False else ''}")
        self.setStyleSheet('')
        c = PAL.mn if good else PAL.rs
        self.setStyleSheet(f'QLabel#toast {{ border-color: {c}; color: {c}; }}')
        self.adjustSize()
        self.move((self.parent().width() - self.width()) // 2, 18)
        self.show(); self.raise_()
        if not sticky: self.timer.start(3200)

# ============================================================ main window
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Q.E.D. — a game of geometric proofs')
        self.resize(1180, 820); self.setMinimumSize(980, 700)
        self.state = None
        self.drill = None; self.flaw = None; self.examQueue = None
        self.replayTok = 0
        central = QWidget(); self.setCentralWidget(central)
        root = QVBoxLayout(central); root.setContentsMargins(10, 10, 10, 30)
        self.board = QFrame(); self.board.setObjectName('board')
        root.addWidget(self.board)
        bl = QVBoxLayout(self.board); bl.setContentsMargins(0, 0, 0, 0); bl.setSpacing(0)
        self.stack = QStackedWidget()
        bl.addWidget(self.stack)
        self.homePage = QWidget(); self.gamePage = QWidget()
        self.stack.addWidget(self.homePage); self.stack.addWidget(self.gamePage)
        self.toast = Toast(self)
        self.build_game_page()
        self.show_home()
    # ---------- helpers
    def toast_msg(self, m, good=False, sticky=False): self.toast.show_msg(m, good, sticky)
    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.toast.move((self.width() - self.toast.width()) // 2, 18)
    # ---------- HOME
    def show_home(self):
        self.state = None; self.replayTok += 1
        self.drill = None; self.flaw = None; self.examQueue = None
        while self.stack.count() > 2 and self.stack.widget(2):
            w2 = self.stack.widget(2); self.stack.removeWidget(w2); w2.deleteLater()
        page = QWidget(); v = QVBoxLayout(page); v.setContentsMargins(14, 4, 14, 14)
        hdr = QHBoxLayout()
        wm = QLabel('Q.E.D.'); wm.setObjectName('wm'); wm.setFont(disp(pt=20))
        sub = QLabel('a game of geometric proofs'); sub.setObjectName('lvl'); sub.setFont(script(pt=14))
        hdr.addWidget(wm); hdr.addWidget(sub); hdr.addStretch()
        hdr.addWidget(mkbtn('📖 Reference', 'ibtn', lambda: self.open_gloss()))
        self.sndBtn = mkbtn('🔊' if not SND_MUTE[0] else '🔇', 'ibtn', self.toggle_mute)
        hdr.addWidget(self.sndBtn)
        v.addLayout(hdr)
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setWidget(self._home_body())
        v.addWidget(sc, 1)
        self.stack.addWidget(page); self.stack.setCurrentWidget(page)
        SND and SND.play('wipe')
    def _home_body(self):
        p = STORE.p
        w = QWidget(); v = QVBoxLayout(w); v.setAlignment(Qt.AlignHCenter)
        v.setSpacing(6)
        crest = FigureCanvas(board=False); crest.setFixedHeight(120)
        crest.set_figure(dict(sk=[rrect(6, 6, 328, 96, 'ch', 3), rrect(18, 18, 304, 72, 'yl', 2)],
                              fx=[], lb=[tx((170, 54), 'Q.E.D.', 'ch', 44)]))
        crest.setFixedWidth(360); crest.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cw = QWidget(); ch = QHBoxLayout(cw); ch.setContentsMargins(0,0,0,0); ch.addStretch(); ch.addWidget(crest); ch.addStretch()
        v.addWidget(cw)
        tag = QLabel(f'{len(FAMILIES)} shape families. Endless proofs. One piece of chalk.')
        tag.setObjectName('tag'); tag.setFont(script(pt=17)); tag.setAlignment(Qt.AlignCenter)
        v.addWidget(tag)
        sub = QLabel("Don't memorize theorems — earn them. Every board is generated fresh: new labels, new measures,\n"
                     "new proof routes, and distractor cards tuned to trip you. Drills, flaw-hunts and exams turn finished proofs into mastery.")
        sub.setObjectName('dim'); sub.setAlignment(Qt.AlignCenter); sub.setWordWrap(True)
        v.addWidget(sub)
        total = sum(f['count'] for f in p['fams'])
        mins = round(p['stats']['time'] / 60)
        tally = QLabel(f'<b>{rankOf(p["stats"]["stars"])}</b> · <b>{total}</b> proofs chalked · <b>{p["stats"]["stars"]}</b>★ · '
                       f'<b>{p["stats"]["flawless"]}</b> flawless' + (f' · {mins} min at the board' if mins else '') +
                       (f' · <b>{p["dailyStreak"]}</b>-day daily streak' if p['dailyStreak'] > 1 else ''))
        tally.setObjectName('tally'); tally.setAlignment(Qt.AlignCenter)
        v.addWidget(tally)
        # chapters
        for ci, (cname, fids) in enumerate(CHAPTERS):
            ch_l = QHBoxLayout()
            rn = QLabel(ROMAN[ci]); rn.setFont(disp(pt=11)); rn.setObjectName('dim')
            ttl = QLabel(cname); ttl.setObjectName('chtitle'); ttl.setFont(script(pt=14, bold=True))
            prog = QLabel(f'{sum(1 for f2 in fids if p["fams"][f2]["count"] > 0)}/{len(fids)}'); prog.setObjectName('meta')
            line = QFrame(); line.setFixedHeight(1); line.setStyleSheet(f'background:{PAL.lb}; border:none;')
            ch_l.addWidget(rn); ch_l.addWidget(ttl); ch_l.addWidget(prog, 0, Qt.AlignVCenter); ch_l.addWidget(line, 1)
            v.addLayout(ch_l)
            for fi in fids:
                fam = FAMILIES[fi]; fp = p['fams'][fi]; locked = fi > p['unlocked']
                row = QFrame(); row.setObjectName('lvrow'); row.setCursor(Qt.PointingHandCursor if not locked else Qt.ArrowCursor)
                if locked: row.setProperty('locked', True)
                hl = QHBoxLayout(row); hl.setContentsMargins(8, 5, 8, 5)
                gfig = GFig(fam['glyph'](), 64, 44, 62, 44)
                hl.addWidget(gfig)
                mid = QVBoxLayout(); mid.setSpacing(0)
                nm = QLabel(fam['name']); nm.setObjectName('famname')
                tg = QLabel(fam['tag']); tg.setObjectName('famtag')
                mid.addWidget(nm); mid.addWidget(tg)
                hl.addWidget(mid, 1)
                if locked:
                    meta = QLabel('🔒'); meta.setObjectName('meta')
                else:
                    best = max(fp['results']) if fp['results'] else None
                    meta = QLabel(('<b>Proof %d</b><br>%s' % (fp['count'] + 1, stars(3, best))) if fp['count'] else 'awaits chalk')
                    meta.setObjectName('meta'); meta.setAlignment(Qt.AlignRight)
                hl.addWidget(meta)
                row.mousePressEvent = (lambda ev, fi=fi: self.start_level(fi)) if not locked else (lambda ev: self.toast_msg('Finish the earlier families first — Euclid was strict about order.'))
                v.addWidget(row)
        # action buttons
        def row2(btns):
            h = QHBoxLayout(); h.setAlignment(Qt.AlignCenter); h.setSpacing(10)
            for b in btns: h.addWidget(b)
            v.addLayout(h)
        t = 0
        for i in range(p['unlocked'] + 1):
            if p['fams'][i]['count'] == 0: t = i; break
        else: t = p['unlocked']
        row2([mkbtn(('Continue · ' + FAMILIES[t]['name']) if p['unlocked'] > 0 else 'Begin', 'pri',
                     lambda: self.start_level(self._continue_target()))])
        ft = focusTarget()
        r1 = [mkbtn('🎲 Surprise me', '', lambda: self.start_level(surpriseTarget()))]
        if ft is not None:
            r1.insert(0, mkbtn(f'◎ Focus: {FAMILIES[ft]["name"]}', '', lambda: self.start_level(focusTarget())))
        row2(r1)
        dailyDone = p['daily'] and p['daily']['day'] == dayKey()
        row2([mkbtn(f'📅 Daily{" ✓" if dailyDone else ""}{(" ·×%d" % p["dailyStreak"]) if p["dailyStreak"] > 1 else ""}', '',
                    self.start_daily),
              mkbtn('📝 Exam', '', self.start_exam),
              mkbtn('⚡ Drill', '', self.start_drill),
              mkbtn('🔎 Spot the flaw', '', self.start_flaw),
              mkbtn('🖨 Worksheet', '', self.ws_picker)])
        # toggles + panels
        opts = QHBoxLayout(); opts.setAlignment(Qt.AlignCenter); opts.setSpacing(10)
        hb = mkbtn(f'Extra distractors: {"ON" if p["hard"] else "off"}', 'sm', self.toggle_hard)
        if p['hard']: hb.setProperty('cls', 'sm on'); hb.setProperty('on', True); repolish(hb)
        rb = mkbtn(f'Relaxed start: {"ON" if p["relaxed"] else "off"}', 'sm', self.toggle_relaxed)
        if p['relaxed']: rb.setProperty('cls', 'sm on'); rb.setProperty('on', True); repolish(rb)
        opts.addWidget(hb); opts.addWidget(rb)
        self.achPanelBtn = mkbtn(f'Honors {sum(1 for a in ACH if p["ach"].get(a[0]))}/{len(ACH)}', 'sm', lambda: self._toggle_panel('ach'))
        self.mastPanelBtn = mkbtn('Mastery', 'sm', lambda: self._toggle_panel('mastery'))
        opts.addWidget(self.achPanelBtn); opts.addWidget(self.mastPanelBtn)
        v.addLayout(opts)
        self.achPanel = self._panel(self._ach_html())
        self.mastPanel = self._panel(self._mastery_html())
        self.achPanel.hide(); self.mastPanel.hide()
        v.addWidget(self.achPanel); v.addWidget(self.mastPanel)
        # themes
        th = QHBoxLayout(); th.setAlignment(Qt.AlignCenter); th.setSpacing(9)
        tl = QLabel('BOARD'); tl.setObjectName('bankh'); th.addWidget(tl)
        for t2 in THEMES:
            b = QPushButton(); b.setProperty('cls', 'swatch'); b.setFixedSize(24, 24)
            b.setStyleSheet(f'background:{t2["sw"]};')
            b.setProperty('on', p['theme'] == t2['id'])
            b.setToolTip(t2['name'])
            b.clicked.connect(lambda _, tid=t2['id']: self.set_theme(tid))
            th.addWidget(b)
        curT = next((x for x in THEMES if x['id'] == p['theme']), THEMES[0])
        tn = QLabel(curT['name']); tn.setObjectName('meta'); th.addWidget(tn)
        v.addLayout(th)
        keys = QLabel('<b>H</b> hint · <b>G</b> reference · <b>R</b> restart · <b>M</b> mute · <b>1–4</b> answer drills · <b>Esc</b> deselect')
        keys.setObjectName('hr'); keys.setAlignment(Qt.AlignCenter)
        v.addWidget(keys)
        rs = mkbtn('erase the chalkboard', 'sm', lambda: self._reset(rs))
        rs.setStyleSheet(f'color:{PAL.lb}; border:none; font-size:11px; text-decoration: underline;')
        v.addWidget(rs, 0, Qt.AlignCenter)
        v.addStretch(1)
        return w
    def _panel(self, html):
        f = QFrame(); f.setObjectName('panelbox')
        v = QVBoxLayout(f); v.setContentsMargins(14, 8, 14, 8)
        lab = QLabel(html); lab.setWordWrap(True); lab.setFont(hand(pt=10))
        lab.setOpenExternalLinks(False)
        v.addWidget(lab)
        f._lab = lab
        return f
    def _ach_html(self):
        p = STORE.p
        return '<br>'.join(f'<b style="color:{PAL.yl if p["ach"].get(a[0]) else PAL.lb}">{"✓ " if p["ach"].get(a[0]) else ""}{a[1]}</b> '
                           f'<span style="color:{PAL.lb}">— {a[2]}</span>' for a in ACH)
    def _mastery_html(self):
        p = STORE.p
        ent = [(r, v) for r, v in p['mastery'].items() if v['c'] + v['e'] > 0]
        ent.sort(key=lambda kv: (-kv[1]['e'], -(kv[1]['e'] / max(1, kv[1]['c'] + kv[1]['e']))))
        if not ent: return f'<span style="color:{PAL.lb}">No marks against you yet — the board is clean.</span>'
        return '<br>'.join(f'<b>{r}</b> <span style="color:{PAL.mn}">{v["c"]}✓</span>'
                           + (f' <span style="color:{PAL.rs}">{v["e"]}✗</span>' if v['e'] else '')
                           for r, v in ent[:7]) + \
               f'<br><span style="color:{PAL.lb}">Tap a reason in the Reference to see its record.</span>'
    def _toggle_panel(self, which):
        a, m = self.achPanel, self.mastPanel
        if which == 'ach':
            a.setVisible(not a.isVisible())
            if a.isVisible(): m.hide()
        else:
            m.setVisible(not m.isVisible())
            if m.isVisible():
                m.findChild(QLabel).setText(self._mastery_html()); a.hide()
    def _reset(self, btn):
        if not getattr(self, '_arm', False):
            self._arm = True; btn.setText('really erase everything?')
            QTimer.singleShot(2600, lambda: (setattr(self, '_arm', False), btn.setText('erase the chalkboard')))
        else:
            th = STORE.p.get('theme', 'emerald'); mu = SND_MUTE[0]
            try: os.remove(SAVE_PATH)
            except Exception: pass
            STORE.p = blank_profile(); STORE.p['theme'] = th; STORE.p['muted'] = mu
            SND_MUTE[0] = mu; STORE.save()
            self.show_home(); self.toast_msg('Fresh chalkboard.', good=True)
    def _continue_target(self):
        p = STORE.p
        for i in range(p['unlocked'] + 1):
            if p['fams'][i]['count'] == 0: return i
        return p['unlocked']
    def toggle_hard(self):
        STORE.p['hard'] = not STORE.p['hard']; STORE.save(); self.show_home()
    def toggle_relaxed(self):
        STORE.p['relaxed'] = not STORE.p['relaxed']; STORE.save(); self.show_home()
    def toggle_mute(self):
        SND_MUTE[0] = not SND_MUTE[0]; STORE.p['muted'] = SND_MUTE[0]; STORE.save()
        self.sndBtn.setText('🔇' if SND_MUTE[0] else '🔊')
        for b in self.findChildren(QPushButton):
            if b.text() in ('🔊', '🔇'): b.setText('🔇' if SND_MUTE[0] else '🔊')
        if not SND_MUTE[0] and SND: SND.play('select')
    def set_theme(self, tid):
        STORE.p['theme'] = tid; STORE.save()
        t = apply_theme(tid)
        QApplication.instance().setStyleSheet(build_stylesheet(t['css']))
        self.show_home()
        self.toast_msg('Board switched — ' + t['name'] + '.', good=True)
    # ---------- glossary
    def open_gloss(self, focus=None):
        self.gw = GlossWin(self, focus)
        self.gw.show(); self.gw.raise_()
    # ---------- GAME
    def build_game_page(self):
        v = QVBoxLayout(self.gamePage); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(0)
        hdr = QFrame(); hdr.setFixedHeight(52)
        hh = QHBoxLayout(hdr); hh.setContentsMargins(14, 6, 14, 6); hh.setSpacing(10)
        self.backBtn = mkbtn('←', 'ibtn', self.go_home)
        self.wm2 = QLabel('Q.E.D.'); self.wm2.setFont(disp(pt=14)); self.wm2.setObjectName('wm')
        self.lvl = QLabel(''); self.lvl.setObjectName('lvl'); self.lvl.setFont(script(pt=13))
        self.dots = QLabel('')
        self.pbar = QProgressBar(); self.pbar.setTextVisible(False); self.pbar.setRange(0, 100)
        hh.addWidget(self.backBtn); hh.addWidget(self.wm2); hh.addWidget(self.lvl); hh.addWidget(self.dots)
        hh.addWidget(self.pbar); hh.addStretch()
        self.combo = QLabel(''); self.combo.setObjectName('combo'); self.combo.hide()
        hh.addWidget(self.combo)
        self.hintBtn = mkbtn('💡 Hint', 'ibtn', self.do_hint)
        self.blurBtn = mkbtn('👁', 'ibtn', self.toggle_blur, 'Blur the figure — prove from the mind\'s eye')
        self.glosBtn = mkbtn('📖', 'ibtn', lambda: self.open_gloss())
        self.rstBtn = mkbtn('↺', 'ibtn', self.restart)
        self.sndBtn2 = mkbtn('🔊', 'ibtn', self.toggle_mute)
        for b in (self.hintBtn, self.blurBtn, self.glosBtn, self.rstBtn, self.sndBtn2): hh.addWidget(b)
        v.addWidget(hdr)
        body = QWidget(); bh = QHBoxLayout(body); bh.setContentsMargins(18, 8, 18, 16); bh.setSpacing(18)
        v.addWidget(body, 1)
        left = QWidget(); lw = QVBoxLayout(left); lw.setContentsMargins(0, 0, 0, 0); lw.setSpacing(4)
        self.canvas = FigureCanvas()
        self.canvas.setFixedWidth(430)
        lw.addWidget(self.canvas, 0, Qt.AlignTop)
        self.given = QLabel(''); self.given.setObjectName('given'); self.given.setWordWrap(True)
        self.prove = QLabel(''); self.prove.setObjectName('prove'); self.prove.setWordWrap(True)
        self.note = QLabel(''); self.note.setObjectName('note'); self.note.setWordWrap(True); self.note.setMinimumHeight(58)
        lw.addWidget(self.given); lw.addWidget(self.prove); lw.addWidget(self.note); lw.addStretch(1)
        bh.addWidget(left, 0, Qt.AlignTop)
        right = QWidget(); rw = QVBoxLayout(right); rw.setContentsMargins(0, 0, 0, 0); rw.setSpacing(6)
        ph = QHBoxLayout()
        for t2 in ('', 'STATEMENTS', 'REASONS', ''):
            l2 = QLabel(t2); l2.setObjectName('phead'); l2.setFont(script(pt=12, bold=True))
            ph.addWidget(l2, (2 if t2 == 'STATEMENTS' else 1 if t2 == 'REASONS' else 0))
        rw.addLayout(ph)
        self.rowsBox = QVBoxLayout(); self.rowsBox.setSpacing(7)
        rowsW = QWidget(); rowsW.setLayout(self.rowsBox)
        rw.addWidget(rowsW)
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setWidget(right)
        sc.setFrameShape(QFrame.NoFrame)
        bh.addWidget(sc, 1)
        self.banksW = QWidget(); bvw = QVBoxLayout(self.banksW); bvw.setContentsMargins(0, 4, 0, 0); bvw.setSpacing(4)
        h3s = QLabel('Statement cards'); h3s.setObjectName('bankh')
        self.sbank = FlowLayout()
        h3r = QLabel('Reason cards'); h3r.setObjectName('bankh')
        self.rbank = FlowLayout()
        bvw.addWidget(h3s); bvw.addWidget(self.sbank); bvw.addWidget(h3r); bvw.addWidget(self.rbank)
        bh.addWidget(self.banksW, 0, Qt.AlignTop)
        self.rightScroll = sc
    def start_level(self, fi, n=None, daily=False, exam=None):
        if n is None: n = STORE.p['fams'][fi]['count'] + 1
        L = makeLevel(fi, n)
        self.state = dict(fi=fi, n=n, daily=daily, exam=exam, level=L, t0=time.time(),
                          rows=[dict(s=None, r=None, done=False, h=0) for _ in L['steps']],
                          sel=None, mistakes=0, hints=0, doneAll=False, rowErrs={}, replaying=False)
        chips = shuffleR(random.Random(), [s['s'] for s in L['steps']] + L['sD'])
        chipsR = shuffleR(random.Random(), [s['r'] for s in L['steps']] + L['rD'])
        self.state['chips'] = [dict(id='s%d' % i, text=t, kind='s', used=False) for i, t in enumerate(chips)] + \
                              [dict(id='r%d' % i, text=t, kind='r', used=False) for i, t in enumerate(chipsR)]
        if STORE.p['relaxed']:
            need = L['steps'][0]['s']
            for c in self.state['chips']:
                if c['text'] == need and not c['used']:
                    c['used'] = True; self.state['rows'][0]['s'] = need; break
        self._refresh_hdr()
        self.given.setText(f'<b style="color:{PAL.yl}">Given.</b> {L["given"]}')
        self.prove.setText(f'<b style="color:{PAL.yl}">Prove.</b> <u>{L["prove"]}</u>')
        self.note.setText(f'<b style="color:{PAL.rs}">RELAXED</b>The opening statement is chalked for you — take it from step 2.'
                          if STORE.p['relaxed'] else '')
        self.canvas.set_figure(L['diagram']())
        self.render_proof()
        self.stack.setCurrentWidget(self.gamePage)
        if self.blurBtn.text() == '👁●': self.blurBtn.setText('👁')
        self.canvas.grab()
        if not STORE.p['coach']:
            self.toast_msg('Pick a card, then tap its place in the proof. Press H for a hint.', sticky=True)
    def start_daily(self):
        d = dailySpec(); self.start_level(d['fi'], d['n'], daily=True)
    def restart(self):
        s = self.state
        if s: self.start_level(s['fi'], s['n'], s['daily'], s['exam'])
    def go_home(self):
        if self.state and self.state['exam'] and not self.state['doneAll']:
            self.toast_msg('Exam abandoned — chalk waits for no one.')
        self.show_home()
    def _refresh_hdr(self):
        s = self.state; p = STORE.p
        if s['exam']:
            ex = s['exam']
            self.lvl.setText(f'Exam — board {ex["idx"]+1} of {len(ex["queue"])} · no hints')
            dots = ''
            for i in range(len(ex['queue'])):
                if i < len(ex['stars']):
                    dots += {3: f'<span style="color:{PAL.yl}">●</span> ', 2: f'<span style="color:{hexit(PAL.yl[1:],.45)}">●</span> '}.get(ex['stars'][i], f'<span style="color:{PAL.lb}">●</span> ')
                elif i == len(ex['stars']):
                    dots += f'<span style="color:{PAL.ch}">●</span> '
                else:
                    dots += f'<span style="color:{PAL.lb}">●</span> '
            self.dots.setText(dots)
        else:
            self.lvl.setText(('Daily Proof' if s['daily'] else ROMAN[chOf(s['fi'])] + ' · ' + FAMILIES[s['fi']]['name'] + ' — Proof ' + str(s['n'])))
            dots = ''
            for st in p['fams'][s['fi']]['results'][-8:]:
                dots += {3: f'<span style="color:{PAL.yl}">●</span> ', 2: f'<span style="color:{hexit(PAL.yl[1:],.45)}">●</span> '}.get(st, f'<span style="color:{PAL.lb}">●</span> ')
            dots += f'<span style="color:{PAL.ch}">●</span>'
            self.dots.setText(dots)
        self.sndBtn2.setText('🔇' if SND_MUTE[0] else '🔊')
    def render_proof(self):
        s = self.state
        if not s: return
        while self.rowsBox.count():
            it = self.rowsBox.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        self.rowW = []
        cur = next((i for i, r in enumerate(s['rows']) if not r['done']), -1)
        for i, step in enumerate(s['level']['steps']):
            r = s['rows'][i]
            row = QFrame(); h = QHBoxLayout(row); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(8)
            num = QLabel(str(i + 1)); num.setObjectName('pnum'); num.setAlignment(Qt.AlignCenter)
            num.setProperty('cur', i == cur); num.setProperty('flash', False)
            ssl = Slot(self, 's', i); rsl = Slot(self, 'r', i)
            h.addWidget(num); h.addWidget(ssl, 5); h.addWidget(rsl, 4)
            chk = QLabel(''); chk.setObjectName('pchk'); chk.setAlignment(Qt.AlignCenter)
            chk.setFixedWidth(20)
            h.addWidget(chk)
            self.rowsBox.addWidget(row)
            self.rowW.append(dict(row=row, num=num, ssl=ssl, rsl=rsl, chk=chk))
            if r['done']:
                ssl.set_state(r['s'], done=True, filled=True)
                rsl.set_state(r['r'], done=True, filled=True)
                chk.setText('✓')
            elif i == cur:
                if r['s']:
                    ssl.set_state(r['s'], filled=True)
                    needR = (s['sel'] is None or self._chip(s['sel'])['kind'] == 'r')
                    rsl.set_state(None, avail=needR)
                else:
                    needS = (s['sel'] is None or self._chip(s['sel'])['kind'] == 's')
                    ssl.set_state(None, avail=needS)
                    rsl.set_state(None)
            else:
                ssl.set_state(None); rsl.set_state(None)
        self.render_banks()
        done = sum(1 for r in s['rows'] if r['done'])
        self.pbar.setValue(round(done / len(s['rows']) * 100))
        c = STORE.p['combo']
        if c >= 3:
            self.combo.setText(f'streak ×{c}'); self.combo.show()
        else: self.combo.hide()
    def render_banks(self):
        s = self.state
        self.sbank.clear(); self.rbank.clear()
        for c in s['chips']:
            if c['used']: continue
            b = Card(self, c)
            b.setProperty('cls', 'chip'); b.setProperty('sel', s['sel'] == c['id'])
            repolish(b)
            (self.sbank if c['kind'] == 's' else self.rbank).add(b)
        self.sbank.reflow(); self.rbank.reflow()
    def _chip(self, cid):
        return next(c for c in self.state['chips'] if c['id'] == cid)
    # ---------- interactions
    def toggle_sel(self, cid):
        s = self.state
        if not s or s['doneAll'] or s['replaying']: return
        c = self._chip(cid)
        if c['used']: return
        s['sel'] = None if s['sel'] == cid else cid
        if SND: SND.play('select')
        STORE.p['coach'] = True; STORE.save()
        self.render_proof()
    def slot_acceptable(self, slot):
        s = self.state
        if not s or s['doneAll'] or s['replaying']: return False
        cur = next((i for i, r in enumerate(s['rows']) if not r['done']), -1)
        if cur < 0 or slot.i != cur: return False
        r = s['rows'][cur]
        return (not r['s']) if slot.kind == 's' else (bool(r['s']) and not r['r'])
    def slot_click(self, slot):
        s = self.state
        if not s: return
        if s['doneAll']:
            self.toast_msg('This proof is finished — Q.E.D.', good=True); return
        cur = next((i for i, r in enumerate(s['rows']) if not r['done']), -1)
        row = s['rows'][slot.i]
        if slot.kind == 'r' and slot.i == cur - 1 and row['r']:
            for c in s['chips']:
                if c['text'] == row['r']: c['used'] = False
            row['r'] = None; row['done'] = False
            self.canvas.fx_p[slot.i] = -1.0; self.canvas.update()
            if SND: SND.play('select')
            self.render_proof(); self.toast_msg('Reason returned to the tray.'); return
        if row['done']:
            if slot.kind == 's':
                self.note.setText(f'<b style="color:{PAL.rs}">WHY</b>{s["level"]["steps"][slot.i]["why"]}')
                if SND: SND.play('select')
            else:
                self.open_gloss(s['level']['steps'][slot.i]['r'])
            return
        if slot.i > cur:
            self.toast_msg(f'Proofs build in order — finish step {cur+1} first.'); return
        if slot.kind == 's' and row['s']:
            for c in s['chips']:
                if c['text'] == row['s']: c['used'] = False
            row['s'] = None; s['sel'] = None
            if SND: SND.play('select')
            self.render_proof(); return
        if slot.kind == 'r' and not row['s']:
            self.toast_msg('Place the statement before its reason.'); return
        if slot.kind == 'r' and row['r']: return
        if not s['sel']:
            self.toast_msg('Pick a card from the tray first — or drag it over.'); return
        self.attempt(s['sel'], slot.i, slot.kind, slot)
    def drop_attempt(self, cid, slot):
        s = self.state
        if not s or s['doneAll']: return
        if not self.slot_acceptable(slot):
            cur = next((i for i, r in enumerate(s['rows']) if not r['done']), -1)
            if slot.i != cur: self.toast_msg(f'Proofs build in order — finish step {cur+1} first.')
            elif slot.kind == 's': self.toast_msg('That statement is already chalked.')
            else: self.toast_msg('Place the statement before its reason.')
            return
        self.attempt(cid, slot.i, slot.kind, slot)
    def explain_error(self, chip, kind, i):
        steps = self.state['level']['steps']; t = chip['text']
        if kind == 'r':
            if t == 'Given': return 'Only the opening facts come from the Given — this step has to be earned.'
            if t == 'CPCTC' and not any('△' in x['s'] and '≅' in x['s'] for x in steps[:i]):
                return 'CPCTC needs a pair of congruent triangles proven first — none on the board yet.'
            for j in range(i + 1, len(steps)):
                if steps[j]['r'] == t:
                    return f'Save it — that reason earns its keep at step {j+1}. This step needs a different license.'
        else:
            for j in range(i + 1, len(steps)):
                if steps[j]['s'] == t:
                    self.flash_row(j)
                    return 'True — but not yet earned. Something must come first.'
        return random.choice(["Not yet — that doesn't follow from what's on the board.",
            'Hmm — the figure disagrees. Look again.', "Close, but we haven't earned that step yet.",
            'Careful: a proof is only as strong as its weakest link.'])
    def flash_row(self, j):
        w = self.rowW[j]
        w['num'].setProperty('flash', True); repolish(w['num'])
        QTimer.singleShot(1400, lambda: (w['num'].setProperty('flash', False), repolish(w['num'])))
    def attempt(self, cid, i, kind, slot):
        s = self.state
        chip = self._chip(cid); exp = s['level']['steps'][i]
        want = exp['s'] if kind == 's' else exp['r']
        if chip['text'] != want:
            s['mistakes'] += 1; s['rowErrs'][i] = s['rowErrs'].get(i, 0) + 1
            if SND: SND.play('err')
            s['sel'] = None
            if STORE.p['combo']: STORE.p['combo'] = 0; STORE.save()
            if kind == 'r': STORE.mastery_tick(chip['text'], False)
            slot.set_state(None, err=True, filled=(kind == 'r'))
            QTimer.singleShot(520, self.render_proof)
            m = self.explain_error(chip, kind, i)
            if s['rowErrs'][i] >= 3: m += '  (press H for a hint)'
            self.toast_msg(m)
            self.render_banks()
            return
        chip['used'] = True; s['sel'] = None
        row = s['rows'][i]
        STORE.p['combo'] = STORE.p['combo'] + 1
        STORE.p['coach'] = True
        if kind == 'r': STORE.mastery_tick(exp['r'], True)
        if STORE.p['combo'] >= 10 and not STORE.p['ach'].get('streak10'):
            STORE.p['ach']['streak10'] = 1
            if SND: SND.play('ach'); QTimer.singleShot(900, lambda: self.toast_msg('Honors earned — Flow State', good=True))
        STORE.save()
        if kind == 's':
            row['s'] = chip['text']
            if SND: SND.play('place')
            self.render_proof()
        else:
            row['r'] = chip['text']
            if SND: SND.play('place')
            self.render_proof()
            self.row_done(i)
    def row_done(self, i):
        s = self.state
        s['rows'][i]['done'] = True
        self.canvas.reveal_fx(i)
        if SND: SND.play('row')
        self.canvas.burst(self.canvas.width() * 0.5, self.canvas.height() * 0.45, 10, 1.8)
        if all(r['done'] for r in s['rows']):
            s['doneAll'] = True
            QTimer.singleShot(850, self.win)
    def do_hint(self):
        s = self.state
        if not s or s['doneAll'] or s['replaying']: return
        if s['exam']:
            self.toast_msg('No hints during the exam — trust the toolbox.')
            if SND: SND.play('err')
            return
        cur = next((i for i, r in enumerate(s['rows']) if not r['done']), -1)
        if cur < 0: return
        row = s['rows'][cur]; row['h'] += 1
        s['hints'] += 2 if row['h'] == 3 else 1
        exp = s['level']['steps'][cur]; needS = not row['s']
        text = exp['s'] if needS else exp['r']
        self.note.setText(f'<b style="color:{PAL.rs}">HINT {row["h"]}/3</b>{exp["why"]}')
        chip = next((c for c in s['chips'] if not c['used'] and c['text'] == text), None)
        if row['h'] >= 2 and chip:
            for b in self.sbank.wids + self.rbank.wids:
                if b.chip['id'] == chip['id']:
                    b.setProperty('pulse', True); repolish(b)
                    QTimer.singleShot(2200, lambda b=b: (b.setProperty('pulse', False), repolish(b)))
        if row['h'] >= 3 and chip:
            chip['used'] = True; s['sel'] = None
            if needS:
                row['s'] = chip['text']; self.render_proof()
            else:
                row['r'] = chip['text']; self.render_proof(); self.row_done(cur)
            self.toast_msg('Chalk placed for you — study the why.', good=True)
            return
        if SND: SND.play('hint')
    # ---------- winning
    def win(self):
        s = self.state
        tot = s['mistakes'] + s['hints']
        starsN = 3 if tot <= 1 else 2 if tot <= 4 else 1
        secs = max(1, round(time.time() - s['t0']))
        p = STORE.p; fp = p['fams'][s['fi']]
        if p['relaxed']: starsN = min(starsN, 2)
        fp['count'] += 1; fp['results'].append(starsN)
        if len(fp['results']) > 12: fp['results'].pop(0)
        p['stats']['stars'] += starsN; p['stats']['time'] += secs
        newAch = []
        def g(cid):
            if not p['ach'].get(cid): p['ach'][cid] = 1; newAch.append(cid)
        g('first')
        if starsN == 3: g('flawless')
        if s['mistakes'] == 0 and s['hints'] == 0: g('pure')
        if p['hard'] and s['mistakes'] == 0 and s['hints'] == 0: g('hardflaw')
        p['streak3'] = p['streak3'] + 1 if starsN == 3 else 0
        if p['streak3'] >= 3: g('hat')
        tt = sum(f['count'] for f in p['fams'])
        if tt >= 10: g('ten')
        if tt >= 50: g('fifty')
        if s['fi'] == 9: g('capstone')
        if s['fi'] == 18: g('righton')
        if all(f['count'] > 0 for f in p['fams']): g('explorer')
        chClear = None
        cname, fids = CHAPTERS[chOf(s['fi'])]
        if all(p['fams'][f]['count'] > 0 for f in fids): chClear = cname
        if s['daily']:
            g('daily')
            p['dailyStreak'] = p['dailyStreak'] + 1 if (p['daily'] and p['daily']['day'] == dayKey(-1)) else 1
            if p['dailyStreak'] >= 3: g('week')
            p['daily'] = dict(day=dayKey(), stars=starsN)
        examDone = None
        if s['exam']:
            ex = s['exam']; ex['stars'].append(starsN)
            total = sum(ex['stars'])
            if ex['idx'] >= len(ex['queue']) - 1 and total >= 8: g('exam')
            examDone = dict(stars=list(ex['stars']), total=total, idx=ex['idx'])
        if p['unlocked'] >= len(FAMILIES) - 1: g('allfam')
        if rankOf(p['stats']['stars']) == "Euclid's Heir": g('heir')
        if starsN == 3: p['stats']['flawless'] += 1
        newFam = None
        if s['fi'] == p['unlocked'] and starsN >= 1 and p['unlocked'] < len(FAMILIES) - 1:
            p['unlocked'] += 1; newFam = FAMILIES[p['unlocked']]['name']
        STORE.save()
        s['done'] = dict(stars=starsN, newFam=newFam, newAch=newAch, secs=secs, chClear=chClear, exam=examDone)
        if SND: SND.play('win')
        if newAch: QTimer.singleShot(700, lambda: SND.play('ach'))
        self._stamp()
    def _stamp(self):
        self.canvas.show_stamp()
        self.canvas.stamp_bursts(self.state['done']['stars'] == 3)
        QTimer.singleShot(1700, self.show_done)
    def show_done(self):
        s = self.state; d = s['done']; L = s['level']
        card = QFrame(); card.setObjectName('card')
        v = QVBoxLayout(card); v.setContentsMargins(28, 22, 28, 20); v.setSpacing(6); v.setAlignment(Qt.AlignHCenter)
        def big(t):
            l2 = QLabel(t); l2.setObjectName('qedbig'); l2.setAlignment(Qt.AlignCenter); l2.setFont(disp(pt=30))
            return l2
        def dim(t, obj='dim'):
            l2 = QLabel(t); l2.setObjectName(obj); l2.setAlignment(Qt.AlignCenter); l2.setWordWrap(True)
            return l2
        if d['exam']:
            ex = s['exam']; de = d['exam']
            if de['idx'] < len(ex['queue']) - 1:
                v.addWidget(big(f'Board {de["idx"]+1}'))
                v.addWidget(dim(f'sealed with <b>{d["stars"]} of 3</b> stars'))
                v.addWidget(QLabel(stars(3, d['stars'])))
                v.addWidget(dim(f'{s["mistakes"]} missteps · {s["hints"]} hints'))
                h = QHBoxLayout(); h.setAlignment(Qt.AlignCenter)
                h.addWidget(mkbtn('Next board →', 'pri', self.exam_next))
                h.addWidget(mkbtn('Leave the exam', '', self.go_home))
                v.addLayout(h)
            else:
                v.addWidget(big(f'{de["total"]}/9'))
                verdict = ('A perfect examination — frame it.' if de['total'] == 9 else
                           'The seal is yours — Euclid nods.' if de['total'] >= 8 else
                           'Solid work — the shaky board is the one to revisit.' if de['total'] >= 6 else
                           'The chalkbox forgives. Review, then sit again.')
                v.addWidget(dim(f'Exam verdict — <b>{verdict}</b>'))
                v.addWidget(dim(' · '.join(f'board {i+1}: {"★"*st}' for i, st in enumerate(de['stars']))))
                if d['newAch']:
                    v.addWidget(QLabel(f'<span style="color:{PAL.mn};font-weight:bold">Honors — ' +
                                       ' · '.join(a[1] for a in ACH if a[0] in d['newAch']) + '</span>'))
                h = QHBoxLayout(); h.setAlignment(Qt.AlignCenter)
                h.addWidget(mkbtn('Sit another exam', 'pri', self.start_exam))
                h.addWidget(mkbtn('Back to the board', '', self.go_home))
                v.addLayout(h)
            self.show_card(card); return
        v.addWidget(big('Q.E.D.'))
        v.addWidget(dim(f'Proof {s["n"]} — <b>{L["prove"]}</b>'))
        if d['newFam']: v.addWidget(QLabel(f'<span style="color:{PAL.mn};font-weight:bold">New family unlocked — {d["newFam"]}</span>'))
        if d['chClear']: v.addWidget(QLabel(f'<span style="color:{PAL.mn};font-weight:bold">Chapter cleared — {d["chClear"]}</span>'))
        if d['newAch']:
            v.addWidget(QLabel(f'<span style="color:{PAL.mn};font-weight:bold">Honors — ' +
                               ' · '.join(a[1] for a in ACH if a[0] in d['newAch']) + '</span>'))
        v.addWidget(QLabel(stars(3, d['stars'])))
        fl = s['mistakes'] == 0 and s['hints'] == 0
        v.addWidget(dim(('Flawless — not a single smudge.' if fl else
                         f'{s["mistakes"]} missteps · {s["hints"]} hint nudges') +
                        f' · ⏱ {fmtT(d["secs"])}'))
        v.addWidget(dim('3★: at most 1 nudge · 2★: at most 4 · tap placed reasons to open the Reference', 'pace'))
        v.addWidget(QLabel(f'<div style="color:{PAL.yl};font-size:15px">{L["take"]}</div>'))
        v.addWidget(dim('<i>tap "Read the proof" below for the full walkthrough</i>', 'pace'))
        h = QHBoxLayout(); h.setAlignment(Qt.AlignCenter); h.setSpacing(8)
        h.addWidget(mkbtn('📖 Read the proof', '', lambda: self.toggle_readout(card, L)))
        h.addWidget(mkbtn('▶ Watch the chalk', '', self.watch_chalk))
        h.addWidget(mkbtn('⧉ Copy', '', self.copy_proof))
        h.addWidget(mkbtn('🖨 Worksheet', '', lambda: self.print_worksheet(s['fi'], s['n'], False)))
        v.addLayout(h)
        h2 = QHBoxLayout(); h2.setAlignment(Qt.AlignCenter); h2.setSpacing(8)
        h2.addWidget(mkbtn('Chalk it again', '', self.restart))
        h2.addWidget(mkbtn(f'Proof {s["n"]+1} →', 'pri', lambda: self.start_level(s['fi'], s['n'] + 1)))
        h2.addWidget(mkbtn('Board', '', self.go_home))
        v.addLayout(h2)
        self.show_card(card)
    def toggle_readout(self, card, L):
        key = '_readout'
        old = getattr(card, key, None)
        if old:
            old.setParent(None); old.deleteLater(); card._readout = None; return
        box = QFrame(); box.setStyleSheet(f'border:1.5px dashed {PAL.lb}; border-radius:10px;')
        bv = QVBoxLayout(box); bv.setContentsMargins(12, 8, 12, 8)
        for i, st in enumerate(L['steps']):
            l2 = QLabel(f'{i+1}. {st["s"]}  —  <b style="color:{PAL.yl}">{st["r"]}</b><br>'
                        f'<span style="color:{PAL.lb}">{st["why"]}</span>')
            l2.setWordWrap(True); l2.setFont(hand(pt=9)); bv.addWidget(l2)
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setWidget(box); sc.setFixedHeight(220)
        card._readout = sc
        card.layout().insertWidget(card.layout().count() - 2, sc)
    def watch_chalk(self):
        self.hide_card()
        s = self.state
        tok = self.replayTok = self.replayTok + 1
        s['replaying'] = True
        self.canvas.clear_fx()
        self.render_proof()
        idx = [0]
        def step():
            if tok != self.replayTok or not self.state: return
            if idx[0] >= len(s['rows']):
                QTimer.singleShot(450, lambda: (self.canvas.show_stamp(),
                    self.canvas.stamp_bursts(s['done']['stars'] == 3),
                    QTimer.singleShot(1500, lambda: (setattr(s, '_x', None), self._finish_replay(tok)))))
                # note: s is a dict; use wrapper
                return
            w = self.rowW[idx[0]]
            w['num'].setProperty('flash', True); repolish(w['num'])
            QTimer.singleShot(900, lambda: (w['num'].setProperty('flash', False), repolish(w['num'])))
            self.canvas.reveal_fx(idx[0])
            if SND: SND.play('row')
            idx[0] += 1
            QTimer.singleShot(1250, step)
        QTimer.singleShot(500, step)
    def _finish_replay(self, tok):
        if tok != self.replayTok or not self.state: return
        self.state['replaying'] = False
        self.show_done()
    def copy_proof(self):
        L = self.state['level']
        txt = '\n'.join([f'Q.E.D. — {FAMILIES[self.state["fi"]]["name"]}, Proof {self.state["n"]}',
                         f'Given: {L["given"]}', f'Prove: {L["prove"]}', ''] +
                        [f'{i+1}. {st["s"]}  —  {st["r"]}' for i, st in enumerate(L['steps'])])
        QApplication.clipboard().setText(txt)
        self.toast_msg('Proof copied to the clipboard.', good=True)
    # ---------- exam
    def start_exam(self):
        self.hide_card()
        p = STORE.p
        if p['unlocked'] < 2:
            self.toast_msg('The exam opens after three families — keep chalking.'); return
        fis = shuffleR(random.Random(), list(range(p['unlocked'] + 1)))[:3]
        self.examQueue = [dict(fi=fi, n=random.randint(1, 4)) for fi in fis]
        card = QFrame(); card.setObjectName('card')
        v = QVBoxLayout(card); v.setContentsMargins(28, 22, 28, 20); v.setSpacing(8); v.setAlignment(Qt.AlignHCenter)
        t = QLabel('The Exam'); t.setObjectName('qedbig'); t.setFont(disp(pt=24))
        v.addWidget(t)
        d = QLabel('Three random boards. <b>No hints.</b><br>Your combined stars are the verdict — <b>8 of 9</b> earns the Examiner\'s Seal.')
        d.setObjectName('dim'); d.setAlignment(Qt.AlignCenter); v.addWidget(d)
        h = QHBoxLayout(); h.setAlignment(Qt.AlignCenter)
        h.addWidget(mkbtn('Begin the exam', 'pri', self.exam_begin))
        h.addWidget(mkbtn('Not yet', '', self.hide_card))
        v.addLayout(h)
        self.show_card(card)
    def exam_begin(self):
        if not self.examQueue: return
        q = self.examQueue; self.examQueue = None
        self.hide_card()
        self.start_level(q[0]['fi'], q[0]['n'], False, dict(queue=q, idx=0, stars=[]))
    def exam_next(self):
        self.hide_card()
        ex = self.state['exam']; ex['idx'] += 1
        q = ex['queue'][ex['idx']]
        self.start_level(q['fi'], q['n'], False, ex)
    # ---------- drill
    def start_drill(self):
        self.hide_card()
        p = STORE.p
        pool = []; seen = set()
        for fi in range(p['unlocked'] + 1):
            for n in (1, 2):
                L = makeLevel(fi, n)
                for st in L['steps']:
                    if st['s'] not in seen:
                        seen.add(st['s']); pool.append(st)
        weak = weakReasons(); qs = []; usedS = set()
        for _ in range(8):
            weakPool = [q2 for q2 in pool if q2['r'] in weak and q2['s'] not in usedS]
            gen = [q2 for q2 in pool if q2['s'] not in usedS]
            src = weakPool if (weakPool and random.random() < 0.6) else gen
            if not src: break
            cand = random.choice(src); usedS.add(cand['s'])
            others = shuffleR(random.Random(), [r for r in REASONS if r != cand['r']])[:3]
            qs.append(dict(s=cand['s'], r=cand['r'], why=cand['why'],
                           opts=shuffleR(random.Random(), [cand['r']] + others)))
        if len(qs) < 4:
            self.toast_msg('Play a proof or two first — drills feed on real boards.'); return
        self.drill = dict(qs=qs, i=0, score=0, answered=False)
        if SND: SND.play('hint')
        self.render_drill()
    def render_drill(self):
        d = self.drill; q = d['qs'][d['i']]; d['answered'] = False
        card = QFrame(); card.setObjectName('card')
        v = QVBoxLayout(card); v.setContentsMargins(28, 20, 28, 18); v.setSpacing(8)
        h = QLabel(f'Reason drill — <b>{d["i"]+1} / {len(d["qs"])}</b> · score {d["score"]}')
        h.setObjectName('dim'); h.setAlignment(Qt.AlignCenter); v.addWidget(h)
        qs = QLabel(q['s']); qs.setObjectName('take'); qs.setWordWrap(True); qs.setAlignment(Qt.AlignCenter)
        qs.setFont(script(pt=14)); v.addWidget(qs)
        d['btns'] = []
        for j, o in enumerate(q['opts']):
            b = mkbtn(f'{j+1}   {o}', 'dopt', lambda _, j=j: self.answer_drill(j))
            b.setProperty('st', ''); d['btns'].append(b); v.addWidget(b)
        why = QLabel(' '); why.setObjectName('pace'); why.setAlignment(Qt.AlignCenter)
        why.setWordWrap(True); why.setMinimumHeight(40); v.addWidget(why)
        d['why'] = why
        v.addWidget(mkbtn('Quit drill', '', self.hide_card), 0, Qt.AlignCenter)
        self.show_card(card)
    def answer_drill(self, j):
        d = self.drill
        if not d or d['answered']: return
        d['answered'] = True
        q = d['qs'][d['i']]
        ok = q['opts'][j] == q['r']
        if ok: d['score'] += 1; SND and SND.play('row')
        else: SND and SND.play('err')
        for k, b in enumerate(d['btns']):
            b.setEnabled(False)
            if q['opts'][k] == q['r']: b.setProperty('st', 'ok')
            elif k == j: b.setProperty('st', 'bad')
            repolish(b)
        d['why'].setText(('✓ ' if ok else '✗ ') + q['why'])
        STORE.mastery_tick(q['r'], ok); STORE.save()
        QTimer.singleShot(1500, self._drill_next)
    def _drill_next(self):
        d = self.drill
        if not d: return
        d['i'] += 1
        if d['i'] >= len(d['qs']): self.end_drill()
        else: self.render_drill()
    def end_drill(self):
        d = self.drill; p = STORE.p; hon = ''
        if d['score'] >= 7 and len(d['qs']) >= 8 and not p['ach'].get('drill'):
            p['ach']['drill'] = 1; hon = '<br><span style="color:%s;font-weight:bold">Honors — Quick Study</span>' % PAL.mn
            SND and SND.play('ach')
        STORE.save()
        card = QFrame(); card.setObjectName('card')
        v = QVBoxLayout(card); v.setContentsMargins(28, 22, 28, 20); v.setAlignment(Qt.AlignHCenter); v.setSpacing(6)
        t = QLabel(f'{d["score"]}/{len(d["qs"])}'); t.setObjectName('qedbig'); t.setAlignment(Qt.AlignCenter); t.setFont(disp(pt=30))
        v.addWidget(t)
        msg = ('Perfect recall — the toolbox is yours.' if d['score'] == len(d['qs']) else
               'Sharp — the weak spots are thinning out.' if d['score'] >= len(d['qs']) - 1 else
               'Every miss feeds your Focus practice — check the Reference for the ✗ marks.')
        m = QLabel(msg); m.setObjectName('dim'); m.setAlignment(Qt.AlignCenter); v.addWidget(m)
        if hon: v.addWidget(QLabel(hon))
        h = QHBoxLayout(); h.setAlignment(Qt.AlignCenter)
        h.addWidget(mkbtn('Drill again', 'pri', self.start_drill))
        h.addWidget(mkbtn('Done', '', self.hide_card))
        v.addLayout(h)
        self.drill = None
        self.show_card(card)
    # ---------- flaw
    def start_flaw(self):
        self.hide_card()
        p = STORE.p
        fis = shuffleR(random.Random(), list(range(p['unlocked'] + 1)))
        L = None; idx = -1
        for fi in fis:
            for _ in range(3):
                if L: break
                Lc = makeLevel(fi, random.randint(1, 3))
                for i in range(1, len(Lc['steps']) - 1):
                    r = Lc['steps'][i]['r']
                    if sum(1 for x in Lc['steps'] if x['r'] == r) == 1:
                        L = Lc; idx = i; break
            if L: break
        if not L:
            self.toast_msg('Not enough boards to plant a flaw yet — chalk a few proofs first.'); return
        orig = L['steps'][idx]['r']
        wrong = shuffleR(random.Random(), [r for r in REASONS if not any(s['r'] == r for s in L['steps'])])[0]
        self.flaw = dict(L=L, idx=idx, orig=orig, wrong=wrong, solved=False)
        if SND: SND.play('hint')
        self.render_flaw()
    def render_flaw(self):
        f = self.flaw; L = f['L']
        card = QFrame(); card.setObjectName('card')
        v = QVBoxLayout(card); v.setContentsMargins(24, 18, 24, 16); v.setSpacing(7)
        t = QLabel('Spot the flaw — <b>one reason is wrong</b>')
        t.setObjectName('dim'); t.setAlignment(Qt.AlignCenter); v.addWidget(t)
        g = QLabel(f'{L["given"]} · Prove: {L["prove"]}')
        g.setObjectName('pace'); g.setWordWrap(True); g.setAlignment(Qt.AlignCenter); v.addWidget(g)
        f['rows'] = []
        for i, st in enumerate(L['steps']):
            row = QFrame(); row.setObjectName('frow'); row.setCursor(Qt.PointingHandCursor)
            rv = QHBoxLayout(row); rv.setContentsMargins(8, 4, 8, 4)
            n = QLabel(str(i + 1)); n.setObjectName('meta')
            txt = QLabel(f'{st["s"]}   <b style="color:{PAL.yl}">{f["wrong"] if i == f["idx"] else st["r"]}</b>')
            txt.setWordWrap(True); txt.setFont(hand(pt=9))
            rv.addWidget(n); rv.addWidget(txt, 1)
            row.mousePressEvent = lambda ev, i=i, w=row: self.guess_flaw(i, w)
            v.addWidget(row); f['rows'].append(row)
        why = QLabel(' '); why.setObjectName('pace'); why.setAlignment(Qt.AlignCenter)
        why.setWordWrap(True); why.setMinimumHeight(44); v.addWidget(why)
        f['why'] = why
        h = QHBoxLayout(); h.setAlignment(Qt.AlignCenter)
        h.addWidget(mkbtn('Reveal', '', self.reveal_flaw))
        h.addWidget(mkbtn('Another board', 'pri', self.start_flaw))
        h.addWidget(mkbtn('Done', '', self.hide_card))
        v.addLayout(h)
        self.show_card(card)
    def guess_flaw(self, i, w):
        f = self.flaw
        if not f or f['solved']: return
        if i == f['idx']:
            f['solved'] = True
            w.setProperty('bad', True); repolish(w)
            p = STORE.p; p['stats']['flaws'] += 1; hon = ''
            if p['stats']['flaws'] >= 3 and not p['ach'].get('detective'):
                p['ach']['detective'] = 1; hon = ' Honors — Proof Detective!'; SND and SND.play('ach')
            STORE.save(); SND and SND.play('row')
            f['why'].setText(f'<span style="color:{PAL.mn}">Caught it.</span> Step {f["idx"]+1} should be licensed by '
                             f'“{f["orig"]}” — not “{f["wrong"]}”. {f["L"]["steps"][f["idx"]]["why"]}{hon}')
        else:
            w.setProperty('err', True); repolish(w)
            QTimer.singleShot(520, lambda: (w.setProperty('err', False), repolish(w)))
            SND and SND.play('err')
            f['why'].setText('That step checks out — its license is valid. Keep hunting.')
    def reveal_flaw(self):
        f = self.flaw
        if not f or f['solved']: return
        f['solved'] = True
        w = f['rows'][f['idx']]; w.setProperty('bad', True); repolish(w)
        f['why'].setText(f'Step {f["idx"]+1} was the planted flaw: it should read “{f["orig"]}”. {f["L"]["steps"][f["idx"]]["why"]}')
    # ---------- overlay
    def show_card(self, w):
        self._card = w
        self.cardHost = QFrame(self.board)
        self.cardHost.setStyleSheet(f'background: {STORE and ""}; background-color: rgba(0,0,0,140);')
        self.cardHost.setStyleSheet(f'background-color: {STORE.p and ""}transparent;')
        self.cardHost.setStyleSheet('background-color: rgba(8,12,10,150);')
        lay = QVBoxLayout(self.cardHost); lay.setAlignment(Qt.AlignCenter); lay.setContentsMargins(20, 20, 20, 20)
        lay.addWidget(w, 0, Qt.AlignHCenter)
        self.cardHost.setGeometry(0, 0, self.board.width(), self.board.height())
        self.cardHost.show(); self.cardHost.raise_()
    def hide_card(self):
        if getattr(self, 'cardHost', None):
            self.cardHost.setParent(None); self.cardHost.deleteLater(); self.cardHost = None
        self.drill = None; self.flaw = None; self.examQueue = None
    def toggle_blur(self):
        from PySide6.QtWidgets import QGraphicsBlurEffect
        if not hasattr(self.canvas, '_blur'):
            self.canvas._blur = QGraphicsBlurEffect(); self.canvas._blur.setBlurRadius(11)
        on = not self.canvas.graphicsEffect()
        self.canvas.setGraphicsEffect(self.canvas._blur if on else None)
        self.blurBtn.setText('👁●' if on else '👁')
    # ---------- worksheets
    def ws_picker(self):
        self.hide_card()
        p = STORE.p
        card = QFrame(); card.setObjectName('card')
        v = QVBoxLayout(card); v.setContentsMargins(24, 18, 24, 16); v.setSpacing(4)
        t = QLabel('Print a worksheet'); t.setObjectName('dim'); t.setAlignment(Qt.AlignCenter); v.addWidget(t)
        d = QLabel('A fresh generated board, a blank two-column table — chalk on paper.')
        d.setObjectName('pace'); d.setAlignment(Qt.AlignCenter); v.addWidget(d)
        v.addWidget(QLabel('Figure family'))
        cbF = QComboBox()
        for fi in range(p['unlocked'] + 1): cbF.addItem(FAMILIES[fi]['name'], fi)
        v.addWidget(cbF)
        v.addWidget(QLabel('Proof number'))
        cbN = QComboBox()
        for n in range(1, 7): cbN.addItem(str(n), n)
        v.addWidget(cbN)
        key = QCheckBox('include answer key (page 2)'); v.addWidget(key)
        h = QHBoxLayout(); h.setAlignment(Qt.AlignCenter)
        def make():
            self.print_worksheet(cbF.currentData(), cbN.currentData(), key.isChecked())
        h.addWidget(mkbtn('🖨 Open print view', 'pri', make))
        h.addWidget(mkbtn('Cancel', '', self.hide_card))
        v.addLayout(h)
        self.show_card(card)
    def print_worksheet(self, fi, n, key):
        from PySide6.QtGui import QTextDocument
        L = makeLevel(fi, n)
        d = L['diagram']()
        pm = render_fig_pixmap(dict(sk=d['sk'], fx=[], lb=d['sk'] and d.get('labels', []) or []), 460, 380, ink='#1a1a1a')
        # include labels layer too
        pm = render_fig_pixmap(dict(sk=d['sk'], fx=[], lb=d.get('labels', [])), 460, 380, ink='#1a1a1a')
        buf = __import__('io').BytesIO()
        pm.save(__import__('io').BufferedIOBase and buf, 'PNG') if False else None
        ba = __import__('PySide6.QtCore', fromlist=['QBuffer'])
        from PySide6.QtCore import QBuffer
        qb = QBuffer(); qb.open(QBuffer.ReadWrite); pm.save(qb, 'PNG')
        b64 = bytes(qb.data()).hex()
        import base64 as b64mod
        img = 'data:image/png;base64,' + b64mod.b64encode(bytes(qb.data())).decode()
        rows = ''.join(f'<tr><td class="num">{i+1}</td><td></td><td></td></tr>' for i in range(len(L['steps'])))
        rows += '<tr><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td></tr>'
        keyHtml = ''
        if key:
            keyHtml = ('<div style="page-break-before:always"><h3>Answer key — %s, Proof %d</h3><table class="kt">'
                       '<tr><th></th><th>Statements</th><th>Reasons</th></tr>%s</table></div>') % (
                FAMILIES[fi]['name'], n,
                ''.join(f'<tr><td>{i+1}</td><td>{s["s"]}</td><td><i>{s["r"]}</i></td></tr>' for i, s in enumerate(L['steps'])))
        html = f"""<html><body style="font-family:'Segoe Print','Comic Sans MS',cursive;color:#1a1a1a">
        <h2>Q.E.D. — {FAMILIES[fi]['name']}</h2>
        <p>Proof {n} · complete the two-column proof.</p>
        <p><b>Given:</b> {L['given']}<br><b>Prove:</b> {L['prove']}</p>
        <img src="{img}" width="430"><br>
        <table border="1" cellspacing="0" cellpadding="14" style="border-collapse:collapse;border:1.6px solid #1a1a1a">
        <tr><th></th><th>Statements</th><th>Reasons</th></tr>{rows}</table>
        <p>Name ______________________ · Date ____________</p>{keyHtml}</body></html>"""
        from PySide6.QtPrintSupport import QPrintDialog
        printer = QPrinter(QPrinter.HighResolution)
        dlg = QPrintDialog(printer, self)
        dlg.setWindowTitle('Print worksheet')
        if dlg.exec():
            doc = QTextDocument(); doc.setHtml(html)
            doc.print_(printer)
            self.hide_card()
    # ---------- keys
    def keyPressEvent(self, e):
        k = e.key()
        fw = QApplication.focusWidget()
        if isinstance(fw, QLineEdit) or isinstance(fw, QComboBox):
            if k == Qt.Key_Escape and getattr(self, 'gw', None) and self.gw.isVisible():
                self.gw.close(); return
            return super().keyPressEvent(e)
        if k == Qt.Key_Escape:
            if getattr(self, 'gw', None) and self.gw.isVisible(): self.gw.close()
            elif getattr(self, 'cardHost', None): self.hide_card()
            elif self.state and self.state['sel']:
                self.state['sel'] = None; self.render_proof()
            return
        if self.drill and getattr(self, 'cardHost', None) and not self.drill['answered'] and Qt.Key_1 <= k <= Qt.Key_4:
            self.answer_drill(k - Qt.Key_1); return
        ch = e.text().lower()
        if ch == 'h': self.do_hint()
        elif ch == 'm': self.toggle_mute()
        elif ch == 'g' or ch == '/': self.open_gloss()
        elif ch == 'r' and self.state: self.restart()

# ============================================================ glossary window
class GlossWin(QWidget):
    def __init__(self, mw, focus=None):
        super().__init__(None)
        self.mw = mw
        self.setWindowTitle('Q.E.D. — Reference')
        self.resize(470, 640)
        v = QVBoxLayout(self); v.setContentsMargins(12, 10, 12, 10); v.setSpacing(6)
        top = QHBoxLayout()
        t = QLabel('Reference'); t.setObjectName('wm'); t.setFont(disp(pt=13))
        self.count = QLabel(''); self.count.setObjectName('meta')
        top.addWidget(t); top.addStretch(); top.addWidget(self.count)
        x = mkbtn('✕', 'ibtn', self.close); top.addWidget(x)
        v.addLayout(top)
        self.qedit = QLineEdit(); self.qedit.setPlaceholderText('search the whole toolbox…')
        self.qedit.textChanged.connect(self.rebuild)
        v.addWidget(self.qedit)
        self.cat = QComboBox()
        for k, l2 in CATS: self.cat.addItem(l2, k)
        self.cat.currentIndexChanged.connect(self.rebuild)
        v.addWidget(self.cat)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.inner = QWidget(); self.iv = QVBoxLayout(self.inner)
        self.iv.setContentsMargins(2, 2, 6, 10); self.iv.setSpacing(2)
        self.scroll.setWidget(self.inner)
        v.addWidget(self.scroll, 1)
        foot = QLabel('Tap any entry for the deeper story · green dot = used in the current proof')
        foot.setObjectName('hr'); v.addWidget(foot)
        self.focusName = focus
        self.rebuild()
    def rebuild(self):
        while self.iv.count():
            it = self.iv.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        q = self.qedit.text().lower()
        cat = self.cat.currentData()
        p = STORE.p
        used = set(s['r'] for s in self.mw.state['level']['steps']) if (self.mw.state and not self.mw.state['replaying'] or self.mw.state) and self.mw.state else set()
        items = [g for g in GLOSS if (cat == 'all' or g[1] == cat) and q in (g[0] + ' ' + g[2] + ' ' + (g[3] or '')).lower()]
        self.count.setText(f'{len(items)} of {len(GLOSS)}')
        m = p['mastery']
        for gname, gcat2, gdef, gmore, gfig in items:
            fr = QFrame(); fr.setObjectName('gitem')
            hl = QHBoxLayout(fr); hl.setContentsMargins(6, 6, 6, 6); hl.setSpacing(10)
            if gfig and gfig in FIGS:
                hl.addWidget(GFig(FIGS[gfig](), 96, 72, 68, 52), 0, Qt.AlignTop)
            body = QVBoxLayout(); body.setSpacing(2)
            mast = ''
            if gname in m:
                mm = m[gname]
                mast = f' <span style="color:{PAL.mn}">{mm["c"]}✓</span>' + (f' <span style="color:{PAL.rs}">{mm["e"]}✗</span>' if mm['e'] else '')
            usedDot = f'<span style="color:{PAL.mn}">●</span> ' if gname in used else ''
            tt = QLabel(usedDot + f'<b style="color:{PAL.yl}">{gname}</b>{mast}')
            body.addWidget(tt)
            dd = QLabel(gdef); dd.setWordWrap(True); dd.setFont(hand(pt=9)); dd.setStyleSheet(f'color:{PAL.dim};border:none')
            body.addWidget(dd)
            more = None
            if gmore:
                more = QLabel(gmore); more.setWordWrap(True); more.setFont(hand(pt=9))
                more.setStyleSheet(f'color:{PAL.dim};border-left:2px solid {PAL.yl};padding-left:8px')
                more.hide(); body.addWidget(more)
            hl.addLayout(body, 1)
            if gmore:
                fr.setCursor(Qt.PointingHandCursor)
                def toggle(ev=None, f=fr, m2=more):
                    m2.setVisible(not m2.isVisible())
                    f.setProperty('open', m2.isVisible()); repolish(f)
                fr.mousePressEvent = toggle
            self.iv.addWidget(fr)
            if self.focusName and gname == self.focusName:
                fr.setProperty('open', True); more and more.show(); repolish(fr)
                QTimer.singleShot(120, lambda f2=fr: self.scroll.ensureWidgetVisible(f2, 0, 200))
        self.iv.addStretch(1)

# ============================================================ main
def main():
    app = QApplication(sys.argv)
    t = apply_theme(STORE.p.get('theme') or 'emerald')
    if not THEMES or STORE.p.get('theme') not in [x['id'] for x in THEMES]:
        STORE.p['theme'] = 'emerald'
    t = apply_theme(STORE.p['theme'])
    SND_MUTE[0] = bool(STORE.p.get('muted'))
    app.setStyleSheet(build_stylesheet(t['css']))
    global SND
    SND = SoundEngine()
    win = Main()
    win.show()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()