from __future__ import print_function
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import io
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload

import os

class GDrive():
    def getService():
        scope = ['https://www.googleapis.com/auth/drive']
        # CHANGE KEY
        credentials = ServiceAccountCredentials.from_json_keyfile_name('/etc/secrets/db-gdrive-key.json', scope)
        service = build('drive', 'v3', credentials=credentials)
        return service


    def getFileId(filename):
        service = GDrive.getService()
        id = None

        results = (service
                    .files()
                    .list(pageSize=10, fields="nextPageToken, files(id, name)")
                    .execute())
            #fields="*",corpora = 'drive',supportsAllDrives = True, driveId = '1gF1DeKeHFSUtLL2_F14b99KjWOzJuakF', includeItemsFromAllDrives = True).execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            for item in items:
                if item['name'] == filename:
                    id = item['id']
        return id


    def downloadDB():
        service = GDrive.getService()
        id = GDrive.getFileId('flaskr.sqlite')

        if id is None:
            return False

        request = service.files().get_media(fileId=id)

        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()

        save_file = open("./instance/flaskr.sqlite", "wb+")
        save_file.write(file.getvalue())
        save_file.close()

        return True
    

    def uploadDB(name='flaskr.sqlite', folder='db'):
        service = GDrive.getService()
        folder_id = GDrive.getFileId(folder)

        if GDrive.getFileId(name):
            return False

        file_metadata = {
            'name': name,
            'parents': [folder_id]
        }

        media = MediaFileUpload('./instance/flaskr.sqlite', resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        if not file:
            return False
        return True


    def renameBackupDB(name_before, name_after):
        service = GDrive.getService()
        folder_id = GDrive.getFileId('db')
        file_id = GDrive.getFileId(name_before)

        if not file_id:
            return False

        file_metadata = {
            'name': name_after
        }

        file = service.files().update(fileId=file_id, body=file_metadata, fields='id').execute()

        if not file:
            return False
        return True


    def deleteOldBackupDB():
        service = GDrive.getService()
        id = GDrive.getFileId('flaskr_backup_delete.sqlite')
        
        if id is None:
            return False
        
        service.files().delete(fileId=id).execute()

        return True

