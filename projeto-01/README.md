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
![image](https://github.com/user-attachments/assets/284b3822-cf52-4d5f-8d7a-2770e8e1bceb)
![image](https://github.com/user-attachments/assets/3bbf2f8f-979d-4ace-a008-84347403832a)
![image](https://github.com/user-attachments/assets/fbd4f6d2-4321-43ab-b22d-8703a3a98f6d)
![image](https://github.com/user-attachments/assets/ff75502d-44d0-4365-ac15-ca851b8e8797)
![image](https://github.com/user-attachments/assets/f18194d3-de7e-4025-a084-7c15cac7ae2d)
![image](https://github.com/user-attachments/assets/16ae830c-6b24-4a12-a8db-640688628b10)
![image](https://github.com/user-attachments/assets/a4aeff2c-caa8-41b4-92a1-88d2778ee5db)
![image](https://github.com/user-attachments/assets/972831b5-92f6-4f60-803a-7ef51ecd338b)
![image](https://github.com/user-attachments/assets/d75abe35-7e44-4245-9b5f-f9ae8a16caf8)
![image](https://github.com/user-attachments/assets/a78f290a-73d0-4be9-b6fa-b228e7bb32af)
![image](https://github.com/user-attachments/assets/b08e57bd-bf42-49f1-a31c-5576298e0c1e)
![image](https://github.com/user-attachments/assets/80875f33-80e1-4575-8a9c-47d0a5605699)
![image](https://github.com/user-attachments/assets/3a32df93-4e0c-4188-b3bd-ed0ce6b2365d)

---
![image](https://github.com/user-attachments/assets/43e9fe4d-fde5-4f9e-8a7f-be2abd8b908d)
![image](https://github.com/user-attachments/assets/4f6e7101-7631-4a06-98f1-0fcded0057e8)
![image](https://github.com/user-attachments/assets/132b6fc2-bdcf-4450-82d7-2f63f579a410)
![image](https://github.com/user-attachments/assets/3b8e64de-6f9b-4bd9-a37d-d2b905ba6596)
![image](https://github.com/user-attachments/assets/c74bc105-57fa-4f71-be96-e7fe522ed84f)
![image](https://github.com/user-attachments/assets/6f3dfc58-d55f-4981-9c61-25233d7038f6)


