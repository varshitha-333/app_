import io
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

class DriveService:
    def __init__(self, config):
        """
        Initialize using service account credentials from config.
        """
        try:
            # Expecting GOOGLE_DRIVE_CREDENTIALS to be a path to JSON or a dict
            creds_info = config.get("GOOGLE_DRIVE_CREDENTIALS")
            if not creds_info:
                raise ValueError("GOOGLE_DRIVE_CREDENTIALS not found in config")

            if isinstance(creds_info, dict):
                self.creds = service_account.Credentials.from_service_account_info(creds_info)
            else:
                self.creds = service_account.Credentials.from_service_account_file(creds_info)
            
            self.scoped_creds = self.creds.with_scopes(['https://www.googleapis.com/auth/drive'])
            self.service = build('drive', 'v3', credentials=self.scoped_creds)
        except Exception as e:
            logger.error(f"Failed to initialize DriveService: {e}")
            raise

    def create_folder(self, name, parent_id=None):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        file = self.service.files().create(body=file_metadata, fields='id, name').execute()
        return file

    def create_file(self, name, mime_type='application/vnd.google-apps.document', parent_id=None, content=None):
        file_metadata = {'name': name, 'mimeType': mime_type}
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        media_body = None
        if content:
            fh = io.BytesIO(content.encode('utf-8'))
            media_body = MediaIoBaseUpload(fh, mimetype='text/plain', resumable=True)

        file = self.service.files().create(
            body=file_metadata,
            media_body=media_body,
            fields='id, name'
        ).execute()
        return file

    def edit_file(self, file_id, new_name=None, new_content=None, mime_type='text/plain'):
        file_metadata = {}
        if new_name:
            file_metadata['name'] = new_name
        
        media_body = None
        if new_content:
            fh = io.BytesIO(new_content.encode('utf-8'))
            media_body = MediaIoBaseUpload(fh, mimetype=mime_type, resumable=True)

        updated_file = self.service.files().update(
            fileId=file_id,
            body=file_metadata,
            media_body=media_body,
            fields='id, name'
        ).execute()
        return updated_file

    def upload_file(self, local_path, drive_name, mime_type, parent_id=None):
        file_metadata = {'name': drive_name}
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()
        return file
