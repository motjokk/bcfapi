from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import relationship


from .database import Base
import sqlalchemy as db



class CDE_User(Base):
    __bind_key__ = 'bcf'
    __tablename__ = 'cde__user' 
    id = Column(Integer, primary_key=True)
    oid = Column(String(150))
    email = Column(String(150), unique=True)
    password = Column(String(150))
    first_name = Column(String(150))
    type = Column(String(150))
    client_id = Column(Integer)
    authorizations = Column(Text)
    token = Column(String(150))
    token_expiration = Column(String(150))
    remote_ip = Column(String(150))
    uuid = Column(String(150))
    projects = Column(Text)
    scopes = Column(Text)
    last_login_date = Column(String(150))
    last_login_ip = Column(String(150))
   

class CDE_Projects(Base):
    __bind_key__ = 'bcf'
    __tablename__ = 'cde__projects'
    project_id= Column(String(150))
    id = Column(Integer, primary_key=True)
    description = Column(String(150))
    name = Column(String(150))
    uuid = Column(String(150))
    users = Column(Text)
    lat = Column(Float)
    lon = Column(Float)
    address = Column(Text)
    projectNumber = Column(String(150))
    client_id = Column(Integer)
    archive_path = Column(String(150))
  

class CDE_Extensions(Base):
    __tablename__ = 'extensions'
    __bind_key__ = 'bcf'
    project_id = Column(Integer, ForeignKey('cde__projects.id'))
    id = Column(Integer, primary_key=True)
    topic_type = Column(String(150))
    topic_status = Column(String(150))
    topic_label = Column(String(150))
    snippet_type = Column(String(150))
    priority = Column(String(150))
    users = Column(Text)
    stage = Column(String(150))
    project_actions = Column(Text)
    topic_actions = Column(Text)
    comment_actions = Column(Text)
    view_setup = Column(Text)



class CDE_Documents(Base):
    __tablename__ = 'documents'
    __bind_key__ = 'bcf'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    document_name = Column(String(150))
    version = Column(String(150))
    display_information = Column(Text)
    uri = Column(String(150))
    project_id = Column(Integer, ForeignKey('cde__projects.id'))

    
class Note(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    data = Column(String(10000))
    date = Column(String(150))
    user_id = Column(Integer)


class Files(Base):
    __bind_key__ = 'bcf'
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    Status = db.Column(db.Integer)
    Version = db.Column(db.Integer)
    FileName = db.Column(db.String(150))
    MD5 = db.Column(db.String(150))
    Floor = db.Column(db.Integer)
    uuid = db.Column(db.String(150))
    parent_folder = db.Column(db.String(150))
    uri = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('cde__user.id'))
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'))
    upload_time = db.Column(db.String(150))
    project_id = db.Column(db.Integer, db.ForeignKey('cde__projects.id'))

class Folders(Base):
    __bind_key__ = 'bcf'
    __tablename__ = 'folders'
    id = db.Column(db.Integer, primary_key=True)
    FolderName = db.Column(db.String(150))
    uuid = db.Column(db.String(150))
    uri = db.Column(db.String(150))
    parent_folder_id = db.Column(String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('cde__user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('cde__projects.id'))
    subfolders = db.Column(db.Integer, db.ForeignKey('folders.id'))

class IFCModels(Base):
    __bind_key__ = 'bcf'
    __tablename__ = 'ifcmodels'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(150))
    uri = db.Column(db.String(150))
    uuid = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('cde__user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('cde__projects.id'))

class FileVersions(Base):
    __bind_key__ = 'bcf'
    __tablename__ = 'versions'
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(150))
    upload_time = db.Column(db.String(150))
    uri = db.Column(db.String(150))
    file_uuid = db.Column(db.String(150))
    uuid = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('cde__user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('cde__projects.id'))