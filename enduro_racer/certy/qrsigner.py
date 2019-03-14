# coding=utf-8
import qrcode
import subprocess
import base64

from certy.signature.authentication import load_private_key, Signer
from certy.signature.identifiers import Algorithm
from certy.wandimage import WandImage


def qrsign(privkey_file, content):
    cmd = ["openssl", "dgst", "-sha256", "-sign", privkey_file]
    cproc = subprocess.run(cmd, input=content.encode('utf-8'), check=True, stdout=subprocess.PIPE)

    return qrcode.make(content.encode('utf-8') + b"|" + base64.b64encode(cproc.stdout), image_factory=WandImage)
