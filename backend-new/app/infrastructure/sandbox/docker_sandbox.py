from typing import Dict, Any, Optional
import uuid
import docker
import httpx
from app.core.config import get_settings


class DockerSandbox:
    def __init__(self, ip: str = None, container_name: str = None):
        self.client = httpx.AsyncClient(timeout=600)
        self.ip = ip
        self.base_url = f"http://{self.ip}:8080"
        self._container_name = container_name

    @property
    def id(self) -> str:
        return self._container_name if self._container_name else "dev-sandbox"

    @staticmethod
    def _get_container_ip(container) -> str:
        network_settings = container.attrs['NetworkSettings']
        ip_address = network_settings['IPAddress']

        if not ip_address and 'Networks' in network_settings:
            networks = network_settings['Networks']
            for network_name, network_config in networks.items():
                if 'IPAddress' in network_config and network_config['IPAddress']:
                    ip_address = network_config['IPAddress']
                    break

        return ip_address

    @staticmethod
    def create() -> 'DockerSandbox':
        settings = get_settings()

        image = settings.sandbox_image
        name_prefix = settings.sandbox_name_prefix
        container_name = f"{name_prefix}-{str(uuid.uuid4())[:8]}"

        try:
            docker_client = docker.from_env()

            container_config = {
                "image": image,
                "name": container_name,
                "detach": True,
                "remove": True,
                "environment": {
                    "SERVICE_TIMEOUT_MINUTES": settings.sandbox_ttl_minutes,
                    "CHROME_ARGS": settings.sandbox_chrome_args,
                },
                "network": settings.sandbox_network,
                "shm_size": "2g",
            }

            if settings.sandbox_http_proxy:
                container_config["environment"]["HTTP_PROXY"] = settings.sandbox_http_proxy
                container_config["environment"]["HTTPS_PROXY"] = settings.sandbox_https_proxy
                container_config["environment"]["NO_PROXY"] = settings.sandbox_no_proxy or "localhost"

            container = docker_client.containers.run(**container_config)

            import time
            time.sleep(2)

            ip = DockerSandbox._get_container_ip(container)

            return DockerSandbox(ip, container_name)

        except Exception as e:
            raise RuntimeError(f"Failed to create sandbox: {str(e)}")

    async def shutdown(self):
        try:
            docker_client = docker.from_env()
            if self._container_name:
                try:
                    container = docker_client.containers.get(self._container_name)
                    container.stop()
                    container.remove()
                except Exception:
                    pass
        except Exception as e:
            pass

    async def health_check(self) -> bool:
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False
