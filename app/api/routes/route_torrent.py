import os
from typing import List
from sqlalchemy.orm import Session
from fastapi import(
    Depends,
    Response,
    status,
    APIRouter,
    File,
    UploadFile
)
from fastapi.responses import JSONResponse
from app.core.rutorrent import(
    get_ruTorrentManager,
    ruTorrentManager
)
from utils.encode import(
    hash_torrent
)


from app.core.database import get_db

from app.api.deps import(
    allow_create_resource
)



router = APIRouter()



@router.post(
    '/upload-torrent',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_create_resource)]
)
async def create_upload_file(
    file: UploadFile,
    server: ruTorrentManager = Depends(get_ruTorrentManager)
):
    contents = await file.read()
    path_file = os.path.join(os.getcwd(), 'files', file.filename)
    if os.path.isfile(path_file) == False:
        with open(path_file, 'wb') as f:
            f.write(contents)
    hash = hash_torrent(path_file)
    server = get_ruTorrentManager().pick_server()
    server['server'].add_torrent(path_file)
    return {
        'filename': file.filename, 
        'server': server['id'],
        'server_name': server['name'],
        'path': path_file,
        'hash': hash_torrent(path_file)
    }


@router.get(
    '/list-torrents',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_create_resource)]
)
def list_torrents(
    server: ruTorrentManager = Depends(get_ruTorrentManager)
):
    r = []
    manager_instance = get_ruTorrentManager()
    for item in manager_instance.servers:
        torrents = []
        keys = list(item['server'].torrents.keys())
        for key in keys:
            torrent = item['server'].torrents[key]
            temp = {
                'name': torrent.name,
                'hash': torrent.hash,
                'size': torrent.size,
                'downloaded': torrent.downloaded,
                'speed_down': torrent.speed_down,
                'speed_up': torrent.speed_up,
                'path': torrent.output_path,
                'added_date': torrent.added_datetime,
                'added_unix': torrent.added_unix,
                'server_name': item['server'].name
            }
            torrents.append(temp)
        r.append({item['name']: {'data': torrents}})
    return {'data': r}


@router.get(
    '/status/{hash}',
    dependencies=[Depends(allow_create_resource)]
)
def status_from_hash(
    hash: str,
    server: ruTorrentManager = Depends(get_ruTorrentManager)
):
    manager_instance = get_ruTorrentManager()
    if manager_instance:
        temp_data = manager_instance.find_hash(hash.upper())
        if temp_data:
            return {
                'name': temp_data.name,
                'hash': temp_data.hash,
                'size': temp_data.size, 
                'downloaded': temp_data.downloaded, 
                'speed_down': temp_data.speed_down, 
                'speed_up': temp_data.speed_up, 
                'path': temp_data.output_path
            }
        else:
            return {
                "error": True,
                "message": "didnt find hash"
            }
    else:
        return {
            "error": True
        }


@router.get(
    '/files/{hash}',
    dependencies=[Depends(allow_create_resource)]
)
def get_files(
    hash: str,
    server: ruTorrentManager = Depends(get_ruTorrentManager)
):
    manager_instance = get_ruTorrentManager()
    if manager_instance:
        temp_data = manager_instance.get_files_by_hash(hash.upper())
        if temp_data:
            data = {
                'name': temp_data['torrent'].name,
                'size': temp_data['torrent'].size,
                'path': temp_data['torrent'].output_path,
                'files': []
            }
            for item in temp_data['files']:
                full_path = os.path.join(temp_data['torrent'].output_path, item[0])
                full_path_serve = os.path.join(temp_data['server'].serve, temp_data['torrent'].name, item[0])
                data_file = {
                    'name': item[0],
                    'path': full_path,
                    'size': int(item[3]),
                    'serve': full_path_serve
                }
                data['files'].append(data_file)
            return data
    return {"error": True}