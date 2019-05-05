from os import path
from pathlib import PurePath
from collections import namedtuple
from wand.image import Image

ContentStyle = namedtuple("ContentStyle", ("font_size", "font_color", "position", "text_align", "formatter"))
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


_TEMPLATES = {
    "temp_sy2019s1": CertiTemplate(path.join(path.dirname(path.abspath(__file__)), 'templates/image/sy2019.jpg'),
                                   ContentStyle(30, "#ffffff", (300, 440), "left", None),
                                   ContentStyle(30, "#ffffff", (382, 588), "center", None),
                                   ContentStyle(30, "#ffffff", (300, 512), "left", None),
                                   ContentStyle(30, "#ffffff", (450, 588), "left", None),
                                   qr_style=QrStyle((100, 100), (80, 80), "#000000", "#ffffff"),
                                   ),
    "temp_hibp_pink": CertiTemplate(path.join(path.dirname(path.abspath(__file__)), 'templates/image/hibp-pink.png'),
                                    ContentStyle(50, "#f029a9", (770, 725), "right", None),  # name
                                    ContentStyle(50, "#f029a9", (380, 828), "center", "第 {} 名".format),  # rank
                                    ContentStyle(50, "#f029a9", (770, 630), "right", None),  # cate
                                    ContentStyle(50, "#f029a9", (770, 828), "right", None),  # result
                                    ContentStyle(50, "#f029a9", (770, 925), "right", None),  # Date
                                    qr_style=QrStyle((100, 100), (40, 40), "#000", "#5d687d"),
                                    )
}


class CompConfig(object):
    def __init__(self, name, template, extra_contents):
        self.name = name
        self.template = template
        self.extra_contents = extra_contents

    @classmethod
    def from_dict(cls, conf_dict):
        if isinstance(conf_dict["template"], str):
            conf_dict["template"] = _TEMPLATES[conf_dict["template"]]
        return cls(**conf_dict)
