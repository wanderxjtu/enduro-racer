from os import path
from pathlib import PurePath
from collections import namedtuple
from wand.image import Image

ContentStyle = namedtuple("ContentStyle", ("font_size", "font_color", "position", "text_align"))
QrStyle = namedtuple("QrStyle", ("size", "position", "fill_color", "back_color"))


class CertiTemplate(object):
    def __init__(self, image_path, *content_styles, qr_style):
        self.image_path = image_path
        self.content_styles = content_styles
        self.qr_style = qr_style
        self.file_suffix = PurePath(image_path).suffix

    def get_image(self):
        """Get a clean image """
        with Image(filename=self.image_path) as image:
            return image.clone()


temp_sy2019s1 = CertiTemplate(path.join(path.dirname(path.abspath(__file__)), 'templates/image/sy2019.jpg'),
                              ContentStyle(30, "#ffffff", (300, 440), "left"),
                              ContentStyle(30, "#ffffff", (382, 588), "center"),
                              ContentStyle(30, "#ffffff", (300, 512), "left"),
                              ContentStyle(30, "#ffffff", (450, 588), "left"),
                              qr_style=QrStyle((100, 100), (80, 80), "#000000", "#ffffff"),
                              )
temp_hibp_pink = CertiTemplate(path.join(path.dirname(path.abspath(__file__)), 'templates/image/hibp-pink.png'),
                               ContentStyle(50, "#f029a9", (770, 725), "right"),  # name
                               ContentStyle(65, "#f029a9", (380, 828), "center"),  # rank
                               ContentStyle(50, "#f029a9", (770, 630), "right"),  # cate
                               ContentStyle(50, "#f029a9", (770, 828), "right"),  # result
                               ContentStyle(50, "#f029a9", (770, 925), "right"),  # Date
                               qr_style=QrStyle((100, 100), (40, 40), "#f029a9", "#000"),
                               )
