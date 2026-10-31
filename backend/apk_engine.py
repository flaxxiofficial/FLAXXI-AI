import tempfile
import subprocess
import shutil
import os

from androguard.core.apk import APK


def analyze_apk(data):

    with tempfile.NamedTemporaryFile(suffix=".apk") as f:

        f.write(data)

        f.flush()

        apk = APK(f.name)

        return {
            "app_name":apk.get_app_name(),
            "package":apk.get_package(),
            "version":apk.get_androidversion_name(),
            "permissions":apk.get_permissions(),
            "activities":apk.get_activities()
        }


def rebuild_apk(data):

    work = tempfile.mkdtemp(prefix="flaxxi_")

    try:

        source = os.path.join(work,"source.apk")

        decoded = os.path.join(work,"decoded")

        output = os.path.join(work,"rebuilt.apk")

        with open(source,"wb") as f:
            f.write(data)

        subprocess.run(
            ["apktool","d",source,"-o",decoded,"-f"],
            check=True,
            timeout=180
        )

        subprocess.run(
            ["apktool","b",decoded,"-o",output],
            check=True,
            timeout=180
        )

        with open(output,"rb") as f:
            return f.read()

    finally:

        shutil.rmtree(work,ignore_errors=True)
