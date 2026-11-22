"""Run MoneyPrinterTurbo's CLI with Edge TTS routed through the session HTTPS proxy.

Usage: python run_mpt.py <MPT_DIR> [cli args...]
Patches only edge_tts' SSL context (trusts the proxy CA bundle) and injects the
HTTPS_PROXY into edge_tts.Communicate; TLS verification stays on.
"""
import os
import ssl
import sys

mpt_dir = sys.argv.pop(1)
sys.path.insert(0, mpt_dir)
os.chdir(mpt_dir)

import edge_tts  # noqa: E402
import edge_tts.communicate as _c  # noqa: E402

_ca = os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt"
if os.path.exists(_ca):
    _c._SSL_CTX = ssl.create_default_context(cafile=_ca)

_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
_Orig = edge_tts.Communicate


class _Communicate(_Orig):
    def __init__(self, *a, **kw):
        if _proxy and not kw.get("proxy"):
            kw["proxy"] = _proxy
        super().__init__(*a, **kw)


edge_tts.Communicate = _Communicate
_c.Communicate = _Communicate

import runpy  # noqa: E402

sys.argv[0] = os.path.join(mpt_dir, "cli.py")
runpy.run_path(sys.argv[0], run_name="__main__")
