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

# from app.models.domain.file import(
#     File,
#     FileStatus,
#     FileData

# )
# from app.models.schemas.file import(
#     FileAdd,
#     FileDetail,
#     FileStatusUpdate,
#     FileAddData
# )


from app.core.database import get_db



router = APIRouter()



@router.post(
    '/upload-torrent',
    status_code=status.HTTP_200_OK
)
async def create_upload_file(file: UploadFile, server: ruTorrentManager = Depends(get_ruTorrentManager)):
    contents = await file.read()
    path_file = os.path.join(os.getcwd(), 'files', file.filename)
    if os.path.isfile(path_file) == False:
        with open(path_file, 'wb') as f:
            f.write(contents)
    dir
    hash = hash_torrent(path_file)
    server = get_ruTorrentManager().pick_server()
    server['server'].add_torrent(path_file)
    return {"filename": file.filename, 'server': server['id'], 'server_name': server['name'], 'path': path_file, 'hash': hash_torrent(path_file)}


@router.get(
    '/list-torrents',
    status_code=status.HTTP_200_OK
)
def list_torrents(server: ruTorrentManager = Depends(get_ruTorrentManager)):
    r = []
    manager_instance = get_ruTorrentManager()
    for item in manager_instance.servers:
        torrents = []
        keys = list(item['server'].torrents.keys())
        for key in keys:
            torrent = item['server'].torrents[key]
            temp = {
                'name': torrent.name,
                'size': torrent.size,
                'downloaded': torrent.downloaded,
                'speed_down': torrent.speed_down,
                'speed_up': torrent.speed_up,
                'path': torrent.output_path
            }
            torrents.append(temp)
        r.append({item['name']: {'data': torrents}})
    return {'k': r}


@router.get(
    '/status/{hash}'
)
def status_from_hash(hash: str, server: ruTorrentManager = Depends(get_ruTorrentManager)):
    manager_instance = get_ruTorrentManager()
    if manager_instance:
        temp_data = manager_instance.find_hash(hash.upper())
        if temp_data:
            return {'name': temp_data.name, 'size': temp_data.size, 'downloaded': temp_data.downloaded, 'speed_down': temp_data.speed_down, 'speed_up': temp_data.speed_up, 'path': temp_data.output_path}
        else:
            return {"error": True, "message": "didnt find hash"}
    else:
        return {"error": True}




# @router.post(
#     '/add',
#     status_code=status.HTTP_200_OK,
#     response_model=FileDetail
# )
# def add_file(data: FileAdd, response: Response, db: Session = Depends(get_db)):
#     """List all logs"""
#     return File.add(session=db, data=data)



# @router.post(
#     '/add-data',
#     status_code=status.HTTP_200_OK,
#     response_model=FileAddData
# )
# def add_file_data(data: FileAddData, response: Response, db: Session = Depends(get_db)):
#     """List all logs"""
#     return FileData.add(session=db, data=data)



# @router.get(
#     '/status-data/{id}',
#     status_code=status.HTTP_200_OK,
# )
# def status_data_file(id: int, response: Response, db: Session = Depends(get_db)):
#     """List all logs"""
#     return FileData.find_by_id_file(session=db, id_file=id)




# @router.get(
#     '/status/{id}',
#     status_code=status.HTTP_200_OK,
#     response_model=FileDetail
# )
# def add_file(id: int, response: Response, db: Session = Depends(get_db)):
#     """List all logs"""
#     return File.find_by_id(session=db, id=id)



# @router.put(
#     '/update/{id}',
#     status_code=status.HTTP_200_OK,
#     response_model=FileDetail
# )
# def add_file(id: int, data: FileStatusUpdate, response: Response, db: Session = Depends(get_db)):
#     """List all logs"""
#     return File.update(session=db, id=id, data=data)