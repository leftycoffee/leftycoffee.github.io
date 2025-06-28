
# Full updated version of your script with automatic markdown creation and token refresh

import requests
import time
import smtplib
import subprocess
from email.message import EmailMessage
from msal import ConfidentialClientApplication
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from PIL import Image
import os
from datetime import datetime

# === Config ===
# Onedrive information, get these from Microsoft Entra, you will need business account to work. Onedrive personal is not supported unfortunately
TENANT_ID = "xxxxxxx-xxxxxxx"
CLIENT_ID = "xxxxxxx-xxxxxxx"
CLIENT_SECRET = "xxxxxxxxx-xxxxxxxxx"
DRIVE_ID = 'xxxxxxxxxxxx'

# Onedrive folder path to monitor, this is where you upload new videos/photos
ROOT_FOLDER_PATH = '/xxxxxxxxe/videos'

# Github repo base, e.g. the standard ~/gitrepo/gitpage
GIT_REPO_BASE = os.path.expanduser("~/gitrepo/gitpage")

# For email notification
EMAIL_FROM = "xxx@xxxxxx.com"
EMAIL_TO = "xxx@xxxxx.com"
SMTP_SERVER = "x.x.x.x"
SMTP_PORT = 25
SMTP_USERNAME = None
SMTP_PASSWORD = None

# Video parameters
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv'}
POLL_INTERVAL = 60  # seconds

# === YouTube OAuth Config ===
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
TOKEN_PATH = 'token.json'
CLIENT_SECRET_PATH = 'client_secrets.json'

def get_youtube_credentials():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return creds

def get_access_token():
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET,
    )
    scopes = ["https://graph.microsoft.com/.default"]
    result = app.acquire_token_for_client(scopes=scopes)
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"Failed to get access token: {result.get('error_description')}")

def get_folder_id(access_token, folder_path):
    url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/root:{folder_path}"
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json()["id"]

def list_children(access_token, folder_id):
    url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{folder_id}/children"
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json().get("value", [])

def recursive_list_files(access_token, folder_path):
    folder_id = get_folder_id(access_token, folder_path)
    all_files = []

    def recurse(fid):
        items = list_children(access_token, fid)
        for item in items:
            if item.get("folder"):
                recurse(item["id"])
            else:
                all_files.append(item)

    recurse(folder_id)
    return all_files

def send_email_notification(subject, body):
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            if SMTP_USERNAME and SMTP_PASSWORD:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"[EMAIL] Notification sent: {subject}")
    except Exception as e:
        print(f"[ERROR] Email failed: {e}")

def upload_to_youtube(file_name, file_bytes):
    try:
        creds = get_youtube_credentials()
        youtube = build('youtube', 'v3', credentials=creds)

        media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype='video/*', chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part='snippet,status',
            body={
                'snippet': {
                    'title': file_name,
                    'description': 'Uploaded via OneDrive Monitor',
                    'tags': ['onedrive', 'auto-upload'],
                    'categoryId': '22'
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclareMadeForKids': False
                }
            },
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"[UPLOAD] Upload progress: {int(status.progress() * 100)}%")

        video_id = response['id']
        print(f"[UPLOAD] Upload complete: https://www.youtube.com/watch?v={video_id}")

        time.sleep(30)
        base_name = file_name.rsplit('.', 1)[0].lower()
        access_token = get_access_token()
        files = recursive_list_files(access_token, ROOT_FOLDER_PATH)

        matching_thumb = next(
            (f for f in files if f['name'].rsplit('.', 1)[0].lower() == base_name and f['name'].lower().endswith('.jpg')),
            None
        )

        if matching_thumb:
            thumb_url = matching_thumb.get('@microsoft.graph.downloadUrl')
            if thumb_url:
                thumb_data = requests.get(thumb_url).content
                thumb_img = Image.open(io.BytesIO(thumb_data)).convert("RGB")

                def resize_to_under_1mb(img):
                    quality = 95
                    scale_percent = 100
                    while quality > 10:
                        w = int(img.width * scale_percent / 100)
                        h = int(img.height * scale_percent / 100)
                        resized = img.resize((w, h), Image.LANCZOS)
                        buffer = io.BytesIO()
                        resized.save(buffer, format='JPEG', quality=quality)
                        if buffer.tell() <= 1024 * 1024:
                            buffer.seek(0)
                            return buffer
                        quality -= 5 if quality > 30 else 0
                        scale_percent -= 5 if quality <= 30 else 0
                    buffer.seek(0)
                    return buffer

                thumb_buffer = resize_to_under_1mb(thumb_img)
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaIoBaseUpload(thumb_buffer, mimetype='image/jpeg')
                ).execute()

                print(f"[THUMBNAIL] Applied: {matching_thumb['name']}")

                today = datetime.now()
                date_str = today.strftime("%Y-%m-%d")
                asset_subpath = os.path.join("assets", "img", today.strftime("%Y"), today.strftime("%m"), today.strftime("%d"))
                asset_dir = os.path.join(GIT_REPO_BASE, asset_subpath)
                os.makedirs(asset_dir, exist_ok=True)
                thumb_filename = os.path.basename(matching_thumb['name'])
                thumb_path = os.path.join(asset_dir, thumb_filename)
                thumb_img.save(thumb_path, format="JPEG")

                post_title = os.path.splitext(os.path.basename(file_name))[0]
                slug_title = post_title.replace(" ", "-")
                md_path = os.path.join(GIT_REPO_BASE, "_posts", f"{date_str}-{slug_title}.markdown")
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(f"""---
layout: single
title:  \"{post_title}\"
date:   {date_str}
tags:
- Latte Art
---

Practice {post_title.lower()}

练练{post_title.lower()}

<div class=\"embed-container\">
  <iframe
      src=\"https://www.youtube.com/embed/{video_id}\"
      width=\"700\"
      height=\"480\"
      frameborder=\"0\"
      allowfullscreen=\"true\">
  </iframe>
</div>

![](/assets/img/{today.strftime('%Y')}/{today.strftime('%m')}/{today.strftime('%d')}/{thumb_filename})
""")
                print(f"[MARKDOWN] Created: {md_path}")

                try:
                    commit_msg = f"Auto-commit {date_str}"
                    cmds = [
                        ['git', '-C', GIT_REPO_BASE, 'add', '.'],
                        ['git', '-C', GIT_REPO_BASE, 'commit', '-m', commit_msg],
                        ['git', '-C', GIT_REPO_BASE, 'push', 'origin', 'master']
                    ]
                    for cmd in cmds:
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode != 0:
                            print(f"[GIT ERROR] {' '.join(cmd)}:\n{result.stderr}")
                        else:
                            print(f"[GIT OK] {' '.join(cmd)}:\n{result.stdout.strip()}")
                except Exception as e:
                    print(f"[GIT EXCEPTION] {e}")

                return f"https://www.youtube.com/watch?v={video_id}", "Thumbnail applied"

        print(f"[THUMBNAIL] No matching thumbnail found for {file_name}")
        return f"https://www.youtube.com/watch?v={video_id}", "No thumbnail found"

    except Exception as e:
        print(f"[ERROR] YouTube upload failed for {file_name}: {e}")
        return None, f"Upload failed: {e}"

def main():
    access_token = get_access_token()
    print("[INFO] Initial scan of all video files recursively...")

    known_files = set()
    files = recursive_list_files(access_token, ROOT_FOLDER_PATH)
    for f in files:
        known_files.add(f["id"])

    print(f"[INFO] Found {len(known_files)} video files initially.")

    while True:
        try:
            time.sleep(POLL_INTERVAL)
            access_token = get_access_token()
            files = recursive_list_files(access_token, ROOT_FOLDER_PATH)

            new_files = [
                f for f in files
                if f["id"] not in known_files and any(f["name"].lower().endswith(ext) for ext in VIDEO_EXTENSIONS)
            ]

            for nf in new_files:
                print(f"[INFO] New video detected: {nf['name']}")
                known_files.add(nf["id"])

                download_url = nf.get('@microsoft.graph.downloadUrl')
                video_data = requests.get(download_url).content if download_url else None
                youtube_link, thumb_status = upload_to_youtube(nf['name'], video_data) if video_data else (None, "No download URL")

                email_body = f"A new video named '{nf['name']}' has been uploaded.\n\nView on OneDrive: {nf.get('webUrl', 'N/A')}"
                if youtube_link:
                    email_body += f"\n\nYouTube: {youtube_link}\nThumbnail status: {thumb_status}"
                else:
                    email_body += f"\n\nYouTube upload failed.\nThumbnail status: {thumb_status}"

                send_email_notification(subject=f"New video uploaded: {nf['name']}", body=email_body)

        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()

