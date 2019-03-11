from os import path
from wand.image import Image


class Sy0324():
    template_path = path.join(path.dirname(path.abspath(__file__)),'image/sy0324.jpg')
    name_pos = (250, 335)
    cate_pos = (250, 395)
    rank_pos = (290, 455)
    save_path = path.dirname(path.abspath(__file__))

    def __init__(self):
        with Image(filename=self.template_path) as image:
            self.image = image.clone()

