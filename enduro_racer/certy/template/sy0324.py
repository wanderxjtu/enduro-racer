from os import path
from wand.image import Image


class Sy0324():
    template_path = path.join(path.dirname(path.abspath(__file__)),'image/sy0324.jpg')
    name_pos = (300, 440)
    cate_pos = (300, 512)
    rank_pos = (382, 588)
    result_pos = (450, 588)
    save_path = path.dirname(path.abspath(__file__))

    def __init__(self):
        with Image(filename=self.template_path) as image:
            self.image = image.clone()

