# coding=utf-8
import tempfile

import qrcode
import subprocess
import base64

from certy.wandimage import WandImage


def qrsign(privkey_file, content, *, fill_color, back_color):
    cmd = ["openssl", "dgst", "-sha256", "-sign", privkey_file]
    cproc = subprocess.run(cmd, input=content.encode('utf-8'), check=True, stdout=subprocess.PIPE)
    qr = qrcode.QRCode(image_factory=WandImage)
    qr.add_data(content.encode('utf-8') + b"|" + base64.b64encode(cproc.stdout))
    return qr.make_image(fill_color=fill_color, back_color=back_color)


def verify(privkey_file, content_sig):
    content, sig = content_sig.split("|", maxsplit=1)
    signature = base64.b64decode(sig.encode(), validate=True)
    with tempfile.NamedTemporaryFile(prefix="ere") as sigfile:
        sigfile.write(signature)
        sigfile.flush()
        cmd = ["openssl", "dgst", "-sha256", "-verify", privkey_file, "-signature", sigfile.name]
        cproc = subprocess.run(cmd, input=content.encode('utf-8'), check=True, stdout=subprocess.PIPE)
        return b"OK" in cproc.stdout
