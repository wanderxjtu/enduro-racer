# coding=utf-8
import os
import sys

from django.conf import settings

sys.path.append(os.path.dirname(__file__) + "/..")

from wand.drawing import Drawing
from wand.color import Color

from certy.qrsigner import qrsign
from certy.competition_config import TEMPLATE_CONFIG


def get_draw():
    draw = Drawing()
    draw.font = settings.CERT_FONT_PATH
    draw.text_antialias = True
    return draw


def render_cert(temp_name, *contents):
    """contents should be ordered as 'name, rank, cate, result, ...' """
    temp_conf = TEMPLATE_CONFIG[temp_name]
    temp = temp_conf.template
    image = temp.get_image()
    for content, style in zip(contents + temp_conf.extra_contents, temp.content_styles):
        print(content)
        draw = get_draw()
        draw.font_size = style.font_size
        draw.fill_color = Color(style.font_color)
        draw.text_alignment = style.text_align
        draw.text(*style.position, content)
        draw(image)
        del draw

    msg = "".join(contents) + temp_conf.name
    print(msg)
    qrimage = qrsign(settings.CERT_KEY_PATH, msg)
    qrimage.resize(*temp.qr_style.size)

    image.composite(qrimage, *temp.qr_style.position)

    image.save(filename=os.path.join(settings.CERT_SAVE_PATH, "-".join(contents[1::-1]) + temp.file_suffix))


if __name__ == "__main__":
    render_cert(*sys.argv[1:6])
