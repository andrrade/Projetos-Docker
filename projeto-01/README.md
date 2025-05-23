# **Passos do Projeto**

---

## `1` Editar o arquivo `docker.service`

### ➡️ Por que?

Para permitir que a API do Docker seja acessada via **socket TCP**, facilitando integrações externas, como monitorar eventos de containers a partir de um script Python.

> \[!WARNING]
> ⚠️ **Aviso Importante de Segurança**
>
> Esta configuração expõe a API do Docker na rede através de **TCP sem autenticação ou criptografia** (`tcp://0.0.0.0:2375`).
> **Não use isso em ambientes de produção!**
>
> ✅ Recomendações:
>
> * Usar somente para **testes locais** ou em uma **rede isolada**.
> * Se for necessário expor em produção, configure **TLS** e **autenticação** seguindo a documentação oficial:
>   [🔗 Docker Secure TCP](https://docs.docker.com/engine/security/protect-access/).

---

### ➡️ Como?

Abra o arquivo de configuração:

```bash
sudo nano /usr/lib/systemd/system/docker.service
```

### ➡️ Linha a ser alterada:

```ini
ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375 --containerd=/run/containerd/containerd.sock
```

➡️ Isso adiciona o parâmetro `-H tcp://0.0.0.0:2375`, que expõe o serviço do Docker para conexões via TCP.

---

### ✅ **Arquivo completo com a alteração:**

```ini
[Unit]
Description=Docker Application Container Engine
Documentation=https://docs.docker.com
After=network-online.target nss-lookup.target docker.socket firewalld.service containerd.service time-set.target
Wants=network-online.target containerd.service
Requires=docker.socket

[Service]
Type=notify
ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375 --containerd=/run/containerd/containerd.sock
ExecReload=/bin/kill -s HUP $MAINPID
TimeoutStartSec=0
RestartSec=2
Restart=always
StartLimitBurst=3
StartLimitInterval=60s
LimitNPROC=infinity
LimitCORE=infinity
TasksMax=infinity
Delegate=yes
KillMode=process
OOMScoreAdjust=-500

[Install]
WantedBy=multi-user.target
```

---

### ➡️ Reiniciar o daemon do `systemd` e o Docker:

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl restart docker
```

✅ Agora o Docker estará ouvindo na porta **2375** via TCP.

---

## `2` Inicializar o ambiente Python

Crie e ative o ambiente virtual:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
```

➡️ **Se você usa o fish shell (assim como eu):**

```fish
source .venv/bin/activate.fish
```

---

## `3` Instalar dependência e criar script

### ➡️ Instalar o pacote `docker`:

```bash
pip install docker
```

---

### ➡️ Criar o arquivo `events.py`:

```python
import docker
import requests
from datetime import datetime

client = docker.DockerClient(base_url='unix://var/run/docker.sock')
webhook_url = "<coloque a URL do seu webhook do Discord aqui>"

for event in client.events(decode=True, filters={"event": "die"}):
    container_id = event["id"]
    container_name = event["Actor"]["Attributes"]["name"]
    epoch_time = event["time"]
    data = datetime.fromtimestamp(epoch_time).strftime("%d/%m/%Y")
    hora = datetime.fromtimestamp(epoch_time).strftime("%H:%M:%S")

    payload = {
        "content": f"O container {container_name} ({container_id}) foi finalizado no dia {data} às {hora}"
    }

    print(payload)
    requests.post(webhook_url, data=payload)
```

---

## `4` Criar o Webhook no Discord

➡️ No canal desejado:

1. Vá em **Configurações do canal** → **Integrações** → **Webhooks**.
2. Crie um novo webhook e copie a **URL**.
3. Substitua a variável `webhook_url` no arquivo `events.py` com a sua URL.

---

✅ **Pronto!** Agora, sempre que um container for finalizado, você receberá automaticamente uma notificação via **Discord**.
