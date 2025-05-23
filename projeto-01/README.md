# Explicação do Projeto 1

Este projeto faz parte dos meus estudos no [curso do Mateus Müller](https://www.udemy.com/course/docker-basico-ao-avancado/), com o objetivo de aprender ainda mais sobre Docker e automação. A ideia principal é monitorar automaticamente quando um container é finalizado e, a partir disso, enviar uma notificação para um canal no Discord usando um webhook. Além disso, registrei todo o processo e os testes com várias imagens no README, para facilitar a visualização e reforçar o aprendizado. Esse projeto me ajudou a entender na prática como integrar o Docker com outras ferramentas e como automatizar tarefas de administração de containers.

# Etapas do Projeto

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

### Webhook no Discord (parte 1)

1. No canto inferior esquerdo, clique no `+` para Adicionar um servidor

![image](https://github.com/user-attachments/assets/284b3822-cf52-4d5f-8d7a-2770e8e1bceb)

### Webhook no Discord (parte 2)

1. Clique em `Criar o meu`

![image](https://github.com/user-attachments/assets/3bbf2f8f-979d-4ace-a008-84347403832a)

### Webhook no Discord (parte 3)

1. Clique em `Para meus amigos e eu`

![image](https://github.com/user-attachments/assets/fbd4f6d2-4321-43ab-b22d-8703a3a98f6d)

### Webhook no Discord (parte 4)

1. Dê um nome ao servidor
2. Clique em `Criar`

![image](https://github.com/user-attachments/assets/ff75502d-44d0-4365-ac15-ca851b8e8797)

### Webhook no Discord (parte 5)

1. Em canais de texto, clique no `+` para criar canal

![image](https://github.com/user-attachments/assets/f18194d3-de7e-4025-a084-7c15cac7ae2d)

### Webhook no Discord (parte 6)

1. Selecione o tipo como `Texto`
2. Dê um nome para o canal

> [!NOTE]
> 3. Optei em deixar o canal como privado, mas vai da sua preferência

4. Clique em `Próximo`

### Webhook no Discord (parte 7)

1. Clique em `Pular`
![image](https://github.com/user-attachments/assets/16ae830c-6b24-4a12-a8db-640688628b10)

### Webhook no Discord (parte 8)

1. No canal criado, clique em `...` para abrir as opções de canal

![image](https://github.com/user-attachments/assets/a4aeff2c-caa8-41b4-92a1-88d2778ee5db)

### Webhook no Discord (parte 9)

1. Clique em `Editar canal`

![image](https://github.com/user-attachments/assets/972831b5-92f6-4f60-803a-7ef51ecd338b)

### Webhook no Discord (parte 10)

1. Clique em `Integrações`

![image](https://github.com/user-attachments/assets/d75abe35-7e44-4245-9b5f-f9ae8a16caf8)

### Webhook no Discord (parte 11)

1. Clique em `Criar webhook`

![image](https://github.com/user-attachments/assets/a78f290a-73d0-4be9-b6fa-b228e7bb32af)

### Webhook no Discord (parte 12)

> [!NOTE]
> Você provavelmente já terá um webhook criá-lo, vai da sua preferência usá-lo ou criar outro.
> Eu usei o padrão mesmo.

1. Clique no `Webhook`

![image](https://github.com/user-attachments/assets/b08e57bd-bf42-49f1-a31c-5576298e0c1e)

### Webhook no Discord (parte 13)

1. Dê o nome de sua preferência
2. Copie a `URL`

> [!IMPORTANT]
> Essa é a URL que deve ser alterada na linha 6 do arquivo [events.py](https://github.com/andrrade/Projetos-Docker/blob/main/projeto-01/events.py):

```py
webhook_url = "<coloque a URL do seu webhook do Discord aqui>"
```

3. Clique em `Salvar alterações`

![image](https://github.com/user-attachments/assets/80875f33-80e1-4575-8a9c-47d0a5605699)

## `5` Testando 


![image](https://github.com/user-attachments/assets/3a32df93-4e0c-4188-b3bd-ed0ce6b2365d)

---
![image](https://github.com/user-attachments/assets/43e9fe4d-fde5-4f9e-8a7f-be2abd8b908d)
![image](https://github.com/user-attachments/assets/4f6e7101-7631-4a06-98f1-0fcded0057e8)
![image](https://github.com/user-attachments/assets/132b6fc2-bdcf-4450-82d7-2f63f579a410)
![image](https://github.com/user-attachments/assets/3b8e64de-6f9b-4bd9-a37d-d2b905ba6596)
![image](https://github.com/user-attachments/assets/c74bc105-57fa-4f71-be96-e7fe522ed84f)
![image](https://github.com/user-attachments/assets/6f3dfc58-d55f-4981-9c61-25233d7038f6)

✅ **Pronto!** Agora, sempre que um container for finalizado, você receberá automaticamente uma notificação via **Discord**.

