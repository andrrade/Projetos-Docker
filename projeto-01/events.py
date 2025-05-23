import docker
import requests
from datetime import datetime

client = docker.DockerClient(base_url='unix://var/run/docker.sock')
webhook_url = "https://discordapp.com/api/webhooks/1375494258995499058/V1f6WoZ7jKhHDO5wMhi4nLi5ni4vKezjF_1-YmJU7UoclyYAQlVcyDEwSeDboLf-wYJs"

for event in client.events(decode=True, filters={"event": "die"}):
    container_id = event["id"]
    container_name = event["Actor"]["Attributes"]["name"]
    epoch_time = event["time"]
    data = datetime.fromtimestamp(epoch_time).strftime("%d/%m/%Y")
    hora = datetime.fromtimestamp(epoch_time).strftime("%H:%M:%S")

    payload = {"content": f"O container {container_name} ({container_id}) foi finalizado no dia {data} às {hora}"}

    print(payload)
    requests.post(webhook_url, data=payload)
