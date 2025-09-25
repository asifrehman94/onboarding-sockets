import re
import aiohttp
from jose import jwt


class Authenticator:
    
    def __init__(
        self,
        client_secret_url: str,
        client_id: str,
        introspect_url: str,
    ):
        self.client_secret_url = client_secret_url
        self.client_id = client_id       
        self.introspect_url = introspect_url
    
    def extract_tenant_id(self, token: str):
        try:
            payload = jwt.decode(token, key="", options={"verify_signature": False, "verify_aud": False})
            iss = payload.get("iss", "")
            match = re.search(r"^http:\/\/[^\/]+\/realms\/([^\/]+)", iss)
            return match.group(1) if match else None
        except Exception as e:
            return None
    
    async def fetch_client_secret(self, tenant_id: str) -> str:
        return "K2QCge5EG9uDfogFfRhxgQrrXthj8JyN" #will be replaced.
        url = self.client_secret_url + f"?clientId={self.client_id}&organization={tenant_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"accept": "*/*"}) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                return data.get("responseData", {}).get("secrets")
    
    async def introspect_token(self, token: str, tenant_id: str, client_secret: str) -> bool:
        url = self.introspect_url.format(tenant_id=tenant_id)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "client_id": self.client_id,
                    "client_secret": client_secret,
                    "token": token,
                },
            ) as response:
                if response.status != 200:
                    return False
                data = await response.json()
                return data.get("active", False)
    
    
    async def validate_token(self, token: str):

        if not token:
            raise Exception("Missing token")

        tenant_id = self.extract_tenant_id(token)

        if not tenant_id:
            raise Exception("Invalid token issuer")

        client_secret = await self.fetch_client_secret(tenant_id)

        if not client_secret:
            raise Exception("Failed to fetch client secret")

        is_valid = await self.introspect_token(token, tenant_id, client_secret)

        if not is_valid:
            raise Exception("Token is either invalid or expired")
        
        return True
