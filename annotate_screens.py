# -*- coding: utf-8 -*-
"""
Annotation des captures d'écran (cadres numérotés + légende).

UTILISATION
-----------
1) Trouver les coordonnées :  python annotate_screens.py grid
   -> génère, à côté de chaque image, un fichier _grid_<nom>.png avec une grille
      graduée (rouge = X horizontal, bleu = Y vertical). Ouvrez-le et lisez les
      coordonnées des coins de chaque composant.

2) Régler les cadres : modifiez les coordonnées dans le dictionnaire CONFIG
   ci-dessous. Un cadre = (numéro, (x1, y1, x2, y2)) :
       x1,y1 = coin HAUT-GAUCHE      x2,y2 = coin BAS-DROITE
       origine (0,0) = coin HAUT-GAUCHE de l'image ; x vers la droite, y vers le bas.

3) Générer les images annotées :  python annotate_screens.py
   -> écrit figures/<nom>-annot.png (référencé dans main.tex).

4) Recompiler le rapport :  pdflatex main.tex   (deux fois)

PRÉREQUIS : Python + Pillow  (déjà installé).  Installer si besoin :
            python -m pip install Pillow
"""

import sys
from PIL import Image, ImageDraw, ImageFont

# ===========================================================================
#  CONFIG : c'est ICI que vous ajustez les cadres et les légendes.
#  Pour DÉPLACER un cadre, changez ses 4 nombres (x1, y1, x2, y2).
# ===========================================================================
CONFIG = {
    # ---- List Report (liste des commandes) -------------------------------
    "demo-voir-po": {
        "strip_h": 130,                 # hauteur du bandeau de légende (px)
        "boxes": [
            (1, (704, 14, 772, 40)),    # sélecteur de langue FR/EN
            (2, (8,   55, 858, 148)),   # barre de filtres
            (3, (455, 168, 862, 193)),  # barre d'outils (Imprimer / Conf. masse)
            (4, (6,   196, 862, 414)),  # tableau des commandes
            (5, (816, 367, 858, 409)),  # bulle de chat Joule
        ],
        "legend": [
            (1, "Sélecteur de langue (FR / EN)"),
            (2, "Barre de filtres (+ Lancer / Adapter)"),
            (3, "Barre d'outils : Imprimer, Confirmation en masse"),
            (4, "Tableau des commandes (colonnes et lignes)"),
            (5, "Bulle de chat (assistant Joule)"),
        ],
    },
    # ---- Fiori Launchpad --------------------------------------------------
    "demo-launchpad": {
        "strip_h": 120,
        "boxes": [
            (1, (2,   2,   868, 40)),   # barre de menu (shell bar : magenta + nav)
            (2, (2,   42,  300, 60)),   # onglets / espaces
            (3, (26,  68,  242, 184)),  # tuiles du portail
            (4, (26,  222, 346, 332)),  # groupe de tuiles
            (5, (834, 16,  868, 38)),   # avatar utilisateur
        ],
        "legend": [
            (1, "Barre de menu (shell bar)"),
            (2, "Espaces et pages (onglets)"),
            (3, "Tuiles du portail (Supplier Portal, Dashboard)"),
            (4, "Groupes de tuiles"),
            (5, "Profil / avatar utilisateur"),
        ],
    },
    # Pour annoter une nouvelle capture, copiez un bloc ci-dessus et changez
    # le nom (doit correspondre à figures/<nom>.png).
}

COLOR = (214, 40, 40)   # couleur des cadres et pastilles (rouge). RGB.
FIG = "figures"

# ===========================================================================
#  Code (en principe pas besoin d'y toucher)
# ===========================================================================
def _font(sz, bold=False):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def make_grid(src, dst, step=50):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    d = ImageDraw.Draw(im)
    ft = _font(11)
    for x in range(0, w, step):
        d.line([x, 0, x, h], fill=(255, 0, 0), width=1)
        d.text((x + 1, 1), str(x), fill=(255, 0, 0), font=ft)
    for y in range(0, h, step):
        d.line([0, y, w, y], fill=(0, 120, 255), width=1)
        d.text((1, y + 1), str(y), fill=(0, 90, 220), font=ft)
    im.save(dst)
    print("grille ->", dst, im.size)


def annotate(src, dst, boxes, legend, strip_h=130, col=COLOR):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    cv = Image.new("RGB", (w, h + strip_h), (255, 255, 255))
    cv.paste(im, (0, 0))
    d = ImageDraw.Draw(cv)
    fb, fl, ft = _font(15, True), _font(15), _font(13)
    for n, (x1, y1, x2, y2) in boxes:
        d.rectangle([x1, y1, x2, y2], outline=col, width=3)
        r = 12
        cx = min(max(x1, r + 1), w - r - 1)
        cy = min(max(y1, r + 1), h - r - 1)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=(255, 255, 255), width=2)
        tw = d.textlength(str(n), font=fb)
        d.text((cx - tw / 2, cy - 9), str(n), fill=(255, 255, 255), font=fb)
    d.line([0, h, w, h], fill=(180, 180, 180), width=1)
    d.text((12, h + 8), "Composants de l'écran :", fill=(20, 20, 20), font=_font(15, True))
    half = (len(legend) + 1) // 2
    colw = w // 2
    for i, (n, txt) in enumerate(legend):
        cx = 18 + (0 if i < half else colw)
        row = i if i < half else i - half
        cy = h + 34 + row * 26
        r = 10
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=(255, 255, 255), width=1)
        tw = d.textlength(str(n), font=ft)
        d.text((cx - tw / 2, cy - 8), str(n), fill=(255, 255, 255), font=ft)
        d.text((cx + 18, cy - 9), txt, fill=(30, 30, 30), font=fl)
    cv.save(dst)
    print("annoté  ->", dst)


def main():
    mode_grid = len(sys.argv) > 1 and sys.argv[1] == "grid"
    for name, cfg in CONFIG.items():
        src = f"{FIG}/{name}.png"
        if mode_grid:
            make_grid(src, f"_grid_{name}.png")
        else:
            annotate(src, f"{FIG}/{name}-annot.png",
                     cfg["boxes"], cfg["legend"], cfg.get("strip_h", 130))


if __name__ == "__main__":
    main()
