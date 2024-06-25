from typing import Union
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status, Request, Security, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, MetaData, text
from sqlalchemy.orm import Session
from pydantic import BaseModel, ValidationError, validator
import json
from sql_mod import models
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt, sha256_crypt, sha512_crypt, scrypt
from sql_mod.schemas import Token, TokenData, UserInDB, CompleteUploadResponse, InitiateUploadResponse
import os



SECRET_KEY = "d9d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Directory to save uploaded files
UPLOAD_DIRECTORY = "./uploads"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

MAX_SIZE_IN_BYTES = 1073741824  # 1 GB
EXPIRES_IN = 60  # minutes



from sql_mod import models, schemas


from sql_mod import crud
from sql_mod.database import SessionLocal, engine




app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#if tables empty, create tables from models
if not models.Base.metadata.tables:
    models.Base.metadata.create_all(bind=engine)






class User:
    
    def sleep(seconds):
        import time
        time.sleep(seconds)

    def authenticate_user(db ,email: str, password: str):

        user = crud.get_user_by_email(db, email)
        print("user: " + str(user))
 
        if user is None:
            print("user is none")
  
            return None
       
        if not user.type == "api":
        
   
            return None
        if not check_password_hash(user.password, password):
            print("passwords do not match")
      
            return None
        return user
   






def verify_password(plain_password, hashed_password):
    return scrypt.verify(plain_password, hashed_password)

def get_password_hash(password):
    return scrypt.hash(password)

def get_user(db, username: str):
        user = crud.get_user_by_email(db, username)
        if user is None:
            return None
        else:
            user_dict = {
                "hashed_password": user.password,
                "username": user.email,
                "email": user.email,
                "disabled": False,
                "full_name": "Daniel Sivertsen",
                "uuid": user.uuid,
                "scopes": "api user"
            }
        return UserInDB(**user_dict)

        
 

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "api":"user",
        })

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
    , db: Session = Depends(get_db)
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
        print("authenticate_value: " + str(authenticate_value))
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            print("scope not in token_data.scopes")
            print(token_data.scopes)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user

async def get_current_active_user(
    current_user: Annotated[User, Security(get_current_user, scopes=["api"])]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user




@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_db) ) -> Token:

    #print(form_data)
 
    user = authenticate_user(get_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/bcf/3.0/projects/{project_id}")
async def get_projects(project_id, request: Request, current_user: Annotated[User, Security(get_current_active_user, scopes=["api"])]
       ,  db: Session = Depends(get_db)):
    
    
    project = crud.get_projects(db, str(project_id), str(current_user.uuid))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project

@app.get("/bcf/3.0/projects/")
async def get_projects(request: Request,
       current_user: Annotated[User, Security(get_current_active_user, scopes=["api"])]
       ,db : Session = Depends(get_db) ) ->list[schemas.project]:    

    projects = crud.get_projects(db, None, str(current_user.uuid))
 
  
    if not projects:
        raise HTTPException(status_code=404, detail="Projects not found")


    return list[schemas.project](projects)

@app.put("/bcf/3.0/projects/{project_id}")
async def update_project(project_id, request: Request, current_user: Annotated[User, Security(get_current_active_user, scopes=["api"])]
                         ,db : Session = Depends(get_db) ) ->schemas.project: 

    np = await request.body()
    np = json.loads(np)  
    project = crud.update_project(db, str(project_id), str(current_user.uuid), np)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.name = np['name']
    project.description = np['description']
    db.commit()

    return project



@app.get("bcf/3.0/projects/{project_id}/extensions")
async def get_extensions(project_id, request: Request, current_user: Annotated[User, Security(get_current_active_user, scopes=["api"])]
       ,  db: Session = Depends(get_db)):
    
    extensions = crud.get_project_extensions(db, str(project_id), str(current_user.uuid))
    if not extensions:
        raise HTTPException(status_code=404, detail="Extensions not found")

    return extensions


#GET /bcf/{version}/projects/{project_id}/files_information
@app.get("/bcf/3.0/projects/{project_id}/files_information")
async def get_files_information(project_id, request: Request, current_user: Annotated[User, Security(get_current_active_user, scopes=["api"])]
       ,  db: Session = Depends(get_db)):
    
    extensions = crud.get_project_extensions(db, str(project_id), str(current_user.uuid))
    if not extensions:
        raise HTTPException(status_code=404, detail="Extensions not found")

    return extensions

'''
#POST /select-documents
@app.post("/select-documents")
async def select_documents(request: Request, current_user: Annotated[User, Security(get_current_active_user, scopes=["api"])]
       ,  db: Session = Depends(get_db)):
    
    np = await request.body()
    np = json.loads(np)  
    project = crud.update_project(db, str(project_id), str(current_user.uuid), np)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.name = np['name']
    project.description = np['description']
    db.commit()

    return project
'''
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/upload.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

#POST /upload-documents
@app.post("/cde/upload-document", response_model=schemas.InitiateUploadResponse)
async def initiate_upload(fileName: str = Form(...)):
    uploadId = str(uuid.uuid4())
    # Generate upload UI URL
    upload_ui_url = f"https://cde.example.com/document-upload?upload_session={uploadId}"
    
    # Create an empty file for the upload
    temp_file_path = os.path.join(UPLOAD_DIRECTORY, f"{uploadId}_{fileName}.part")
    with open(temp_file_path, "wb") as temp_file:
        pass

    return schemas.InitiateUploadResponse(
        upload_ui_url=upload_ui_url,
        expires_in=EXPIRES_IN,
        max_size_in_bytes=MAX_SIZE_IN_BYTES
    )

@app.post("/cde/upload/{uploadId}", response_model=CompleteUploadResponse)
async def upload_file(uploadId: str, file: UploadFile = File(...), metadata: str = Form(...)):
    temp_file_path = os.path.join(UPLOAD_DIRECTORY, f"{uploadId}_{file.filename}.part")
    #temp_file_path = UPLOAD_DIRECTORY + "/" + str(uploadId) + "_" + str(file.filename) + ".part"
    if not os.path.exists(temp_file_path):
        print("File not found!!!!!!!!! "+temp_file_path)
        raise HTTPException(status_code=404, detail="Upload ID not found or expired")

    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)

    # Check file size
    content = await file.read()
    if len(content) > MAX_SIZE_IN_BYTES:
        raise HTTPException(status_code=400, detail="File size exceeds the maximum allowed size")

    # Write the file to the temporary path
    with open(temp_file_path, "wb") as buffer:
        buffer.write(content)

    # Save metadata
    metadata_dict = json.loads(metadata)
    metadata_path = os.path.join(UPLOAD_DIRECTORY, f"{uploadId}_{file.filename}.metadata.json")
    with open(metadata_path, "w") as metadata_file:
        json.dump(metadata_dict, metadata_file)

    # Rename the temp file to the final file name
    os.rename(temp_file_path, file_path)

    return CompleteUploadResponse(
        uploadId=uploadId,
        status="completed",
        fileName=file.filename,
        fileSize=len(content),
        metadata=metadata_dict
    )

@app.get("/cde/upload/status/{uploadId}", response_model=CompleteUploadResponse)
async def get_upload_status(uploadId: str, fileName: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, fileName)
    metadata_path = os.path.join(UPLOAD_DIRECTORY, f"{uploadId}_{fileName}.metadata.json")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    file_size = os.path.getsize(file_path)

    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as metadata_file:
            metadata_dict = json.load(metadata_file)
    else:
        metadata_dict = {}

    return CompleteUploadResponse(
        uploadId=uploadId,
        status="completed",
        fileName=fileName,
        fileSize=file_size,
        metadata=metadata_dict
    )

@app.delete("/cde/upload/{uploadId}", response_model=InitiateUploadResponse)
async def delete_upload(uploadId: str, fileName: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, fileName)
    temp_file_path = os.path.join(UPLOAD_DIRECTORY, f"{uploadId}_{fileName}.part")
    metadata_path = os.path.join(UPLOAD_DIRECTORY, f"{uploadId}_{fileName}.metadata.json")
    
    if os.path.exists(file_path):
        os.remove(file_path)
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        return InitiateUploadResponse(upload_ui_url="deleted", expires_in=0, max_size_in_bytes=0)
    elif os.path.exists(temp_file_path):
        os.remove(temp_file_path)
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        return InitiateUploadResponse(upload_ui_url="deleted", expires_in=0, max_size_in_bytes=0)
    else:
        raise HTTPException(status_code=404, detail="Upload ID not found or file does not exist")

