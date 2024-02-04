import yaml
import os
import subprocess
import json
import tempfile
import base64
import ssl
from pathlib import Path
from typing import Dict, Any

kubeconfig = os.environ.get("KUBECONFIG", "~/.kube/config")
kubeconfig = os.path.expanduser(kubeconfig)

def exec_subprocess( *args: tuple, **kwargs: Dict[str, Any]) -> subprocess.CompletedProcess:
    try:
        run = subprocess.run(*args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True, **kwargs)
        return run.stdout.decode('utf-8')
    except subprocess.CalledProcessError as err:
      raise RuntimeError(f"command execution failed. Output: {err.output.decode('utf-8')}, exit status: {err.returncode}")


def to_tmp_file(data: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as tmpf:
        tmpf.write(
            base64.b64decode(
                data
            )
        )
        return tmpf.name

def load_ssl(cacert=None, cert=None, key=None) -> ssl.SSLContext:
    ssl_context = ssl.create_default_context(cafile=cacert)
    if cert and key:
        ssl_context.load_cert_chain(certfile=cert, keyfile=key)
    return ssl_context

def load_kubeconfig() -> Dict[str, Any]:

    ca_cert_path = None
    server_cert_path = None
    server_key_path = None
    token = None

    with open(kubeconfig, 'r') as kc:
        kube = yaml.safe_load(kc)

    for context in kube['contexts']:
        if context['name'] == kube['current-context']:
            active_user = context['context']['user']
            active_cluster = context['context']['cluster']

    for cluster in kube['clusters']:
        if cluster['name'] == active_cluster:
            if 'certificate-authority' in cluster['cluster']:
                ca_cert_path = Path(cluster['cluster']['certificate-authority'])
            if 'certificate-authority-data' in cluster['cluster']:
                ca_cert_path = to_tmp_file(cluster['cluster']['certificate-authority-data'])
            server = cluster['cluster']['server']

    for user in kube['users']:
        if user['name'] == active_user:
            if 'exec' in user['user']:
                args = [user['user']['exec']['command']] + user['user']['exec']['args']
                env = os.environ.copy()
                result = json.loads(exec_subprocess(args, env=env))
                token = result['status']['token']
            if 'client-certificate' in user['user']:
                server_cert_path = Path(user['user']['client-certificate'])
            if 'client-certificate-data' in user['user']:
                server_cert_path = to_tmp_file(user['user']['client-certificate-data'])
            if 'client-key' in user['user']:
                server_key_path = Path(user['user']['client-key'])
            if 'client-key-data' in user['user']:
                server_key_path = to_tmp_file(user['user']['client-key-data'])

    return {'cacert': ca_cert_path, 'token': token, 'cert': server_cert_path, 'certkey': server_key_path, 'server': server}
