# coding=utf-8
import os
import sys

from django.conf import settings

sys.path.append(os.path.dirname(__file__) + "/..")

from wand.drawing import Drawing
from wand.color import Color

from certy.qrsigner import qrsign
from certy.competition_config import TEMPLATE_CONFIG


class CertGen(object):
    def __init__(self, compname):
        self.comp_name = compname
        self.temp_conf = TEMPLATE_CONFIG[compname]

    def get_draw(self):
        draw = Drawing()
        draw.font = settings.CERT_FONT_PATH
        draw.text_antialias = True
        return draw

    def get_cert_filename(self, rank, name):
        fn = rank + name + self.temp_conf.template.file_suffix
        return fn.replace("/", "-")

    def render_cert(self, *contents, filename=None):
        """contents should be ordered as 'name, rank, cate, result, ...' """
        temp = self.temp_conf.template
        image = temp.get_image()
        for content, style in zip(contents + self.temp_conf.extra_contents, temp.content_styles):
            draw = self.get_draw()
            draw.font_size = style.font_size
            draw.fill_color = Color(style.font_color)
            draw.text_alignment = style.text_align
            if style.formatter:
                content = style.formatter(content)
            draw.text(*style.position, content)
            draw(image)
            del draw

        msg = "".join(contents) + self.temp_conf.name
        qrimage = qrsign(settings.CERT_KEY_PATH, msg,
                         fill_color=temp.qr_style.fill_color, back_color=temp.qr_style.back_color)
        qrimage.resize(*temp.qr_style.size)

        image.composite(qrimage, *temp.qr_style.position)

        save_file = os.path.join(settings.CERT_SAVE_PATH, self.comp_name,
                                 filename or self.get_cert_filename(*contents[1::-1]))
        print(save_file)
        image.save(filename=save_file)


if __name__ == "__main__":
    g = CertGen(sys.argv[1])
    g.render_cert(*sys.argv[2:6])
