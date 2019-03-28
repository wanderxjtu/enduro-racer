# coding=utf-8
from collections import namedtuple
from .certi_templates import *


CompConfig = namedtuple("CompetitionTemplateConfig", ("name", "template", "extra_contents"))


TEMPLATE_CONFIG = {
    "sy2019s1": CompConfig("20190324上虞", temp_sy2019s1, tuple()),
    "cat2019s1": CompConfig("20190331野猫", temp_hibp_pink, ("March 31th, 2019", "2019西湖小野猫赛")),
}

