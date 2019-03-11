# coding=utf-8
import os
import sys

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from template.sy0324 import Sy0324
import math

def get_draw():
    draw = Drawing()
    draw.font = '/Users/jiaqi/Library/Fonts/SourceHanSansSC/SourceHanSansSC-Bold.otf'
    draw.font_size = 24
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

    temp.image.save(filename=os.path.join(temp.save_path, "%s-%s.jpg" % (rank, name)))


if __name__ == "__main__":
    render_cert(*sys.argv[1:5])
