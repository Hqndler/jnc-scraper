import subprocess, os
from time import sleep

def jncep_launcher(url) -> True:
    print("Wait to avoid to many requests -> " + url)
    sleep(5)
    mail = os.environ.get("JNC_NINA_EMAIL")
    psswrd = os.environ.get("JNC_NINA_PASSWORD")
    cmd = f'jncep epub {url} -l {mail} -p {psswrd}'
    p = subprocess.run(cmd, capture_output = True, text = True, shell = True)
    print(p.stdout)
    print(p.stderr)
    # dirty fix for poor people
    if "No EPUB will be generated" in p.stdout:
        return ""
    if p.returncode == 0:
        files = os.listdir(os.getcwd())
        return [i for i in files if i.endswith(".epub")][0]
    return ""
    
