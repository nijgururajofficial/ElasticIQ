from google.oauth2 import service_account
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

credentials = service_account.Credentials.from_service_account_file(
    r"E:\GuruDev\ElasticIQ\infra\credentials\vertex_ai_service_account.json",
    scopes=SCOPES,
)

# Refresh token
credentials.refresh(Request())
print("Token acquired:", credentials.token[:10], "...")
