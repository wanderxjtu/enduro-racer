# coding=utf-8
import os
import sys

from django.conf import settings

sys.path.append(os.path.dirname(__file__) + "/..")

from wand.drawing import Drawing

from certy.templates.sy0324 import Sy0324
from certy.qrsigner import qrsign


def get_draw():
    draw = Drawing()
    draw.font = settings.CERT_FONT_PATH
    draw.font_size = 30
    draw.text_antialias = True
    return draw


def render_cert(name, rank, cate, result):
    temp = Sy0324()
    for pos, s, alignment in ((temp.name_pos, name, "left"), (temp.cate_pos, cate, "left"),
                              (temp.rank_pos, rank, "center"), (temp.result_pos, result, "left")):
        draw = get_draw()
        draw.text_alignment = alignment
        draw.text(*pos, s)
        draw(temp.image)
        del draw

    msg = "%s%s%s%s%s" % (name, rank, cate, result, temp.comp_name)
    qrimage = qrsign(settings.CERT_KEY_PATH, msg)
    qrimage.resize(100, 100)

    temp.image.composite(qrimage, 80, 80)

    temp.image.save(filename=os.path.join(settings.CERT_SAVE_PATH, "%s-%s.jpg" % (rank, name)))


if __name__ == "__main__":
    render_cert(*sys.argv[1:5])
