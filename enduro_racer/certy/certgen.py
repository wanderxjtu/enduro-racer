# coding=utf-8
import os
import sys

sys.path.append(os.path.dirname(__file__) + "/..")

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import math

from certy.template.sy0324 import Sy0324
from certy.qrsigner import qrsign


def get_draw():
    draw = Drawing()
    draw.font = '/Users/jiaqi/Library/Fonts/SourceHanSansSC/SourceHanSansSC-Bold.otf'
    draw.font_size = 30
    draw.text_antialias = True
    return draw


def render_cert(name, rank, cate, result, keyfile):
    temp = Sy0324()
    for pos, s, alignment in ((temp.name_pos, name, "left"), (temp.cate_pos, cate, "left"),
                              (temp.rank_pos, rank, "center"), (temp.result_pos, result, "left")):
        draw = get_draw()
        draw.text_alignment = alignment
        draw.text(*pos, s)
        draw(temp.image)
        del draw

    msg = "%s%s%s%s" % (name, rank, cate, result)
    qrimage = qrsign(keyfile, msg)
    qrimage.resize(100, 100)

    temp.image.composite(qrimage, 80, 80)

    temp.image.save(filename=os.path.join(temp.save_path, "%s-%s.jpg" % (rank, name)))


if __name__ == "__main__":
    keyfile = sys.argv[5]
    render_cert(*sys.argv[1:5], keyfile)
