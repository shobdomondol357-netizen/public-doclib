import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from .config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def creds_from_refresh(refresh_token: str) -> Credentials:
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds

def build_service(refresh_token: str):
    return build("drive", "v3", credentials=creds_from_refresh(refresh_token), cache_discovery=False)

SUPPORTED_MIMES_PREFIX = ("application/", "text/", "image/")

def list_files_recursive(service, folder_id: str, exclude_ids: set) -> list:
    """Return list of file dicts with id,name,mimeType,size,modifiedTime,webViewLink."""
    results = []
    stack = [folder_id]
    seen_folders = set()
    while stack:
        fid = stack.pop()
        if fid in seen_folders:
            continue
        seen_folders.add(fid)
        page_token = None
        while True:
            q = f"'{fid}' in parents and trashed=false"
            resp = service.files().list(
                q=q,
                spaces="drive",
                fields="nextPageToken, files(id,name,mimeType,size,modifiedTime,webViewLink,parents)",
                pageToken=page_token,
                pageSize=200,
            ).execute()
            for f in resp.get("files", []):
                if f["id"] in exclude_ids:
                    continue
                if f["mimeType"] == "application/vnd.google-apps.folder":
                    stack.append(f["id"])
                else:
                    results.append(f)
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
    return results

def download_file(service, file_id: str) -> bytes:
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return fh.getvalue()

def get_file_metadata(service, file_id: str) -> dict:
    return service.files().get(fileId=file_id, fields="id,name,mimeType,size,modifiedTime,webViewLink").execute()
