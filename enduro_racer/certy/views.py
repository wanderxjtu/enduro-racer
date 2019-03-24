from django.conf import settings
from django.forms import Form, CharField

# Create your views here.
from django.views.generic import TemplateView, FormView
import requests

from certy.qrsigner import verify
from race.utils import get_client_ip


class VerifyForm(Form):
    message = CharField()
    vaptcha_token = CharField()

    def vaptcha_validate(self, token, request):
        try:
            data = {
                "id": "",
                "secret_key": settings.VAPTCHA_SECRET,
                "scene": "03",
                "token": token,
                "ip": get_client_ip(request)
            }
            req = requests.post("http://api.vaptcha.com/v2/validate", data=data)
            ret = req.json()
            return ret["success"] == 1
        except Exception:
            return False


class VerifyView(TemplateView):
    template_name = "verify.html"


class VerifyResultView(FormView):
    template_name = "verify_result.html"
    form_class = VerifyForm

    def form_valid(self, form):
        if not form.vaptcha_validate(form.cleaned_data['vaptcha_token'], self.request):
            return self.render_to_response({"result": "Unknown error."})
        if verify(settings.CERT_PUBKEY_PATH, form.cleaned_data['message']):
            return self.render_to_response({"result": "Verify Success!"})
        return self.render_to_response({"result": "Verify Failed!"})

    def form_invalid(self, form):
        return self.render_to_response({"result": "Please check your input."})
