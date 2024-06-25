from sqlalchemy.orm import Session

from . import models, schemas
import json
import datetime
import uuid
from .database import SessionLocal





def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    with SessionLocal() as session:
        return session.query(models.CDE_User).filter(models.CDE_User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_projects(db: Session, project_id: str, user_uuid: str, limit: int = 1000, skip: int = 0):

    with SessionLocal() as session:
        user = session.query(models.CDE_User).filter(models.CDE_User.uuid == user_uuid).first()
        if user is None:
            print("user is none")
            return None
        else:
            projects = json.loads(user.projects)
            if project_id is not None:
                return session.query(models.CDE_Projects).filter(models.CDE_Projects.project_id == project_id).first()
            else:
                return session.query(models.CDE_Projects).filter(models.CDE_Projects.project_id.in_(projects)).offset(skip).limit(limit).all()
    

          
def update_project(db: Session, project_id: str, user_uuid: str, project: schemas.project):
    with SessionLocal() as session:
        user = session.query(models.CDE_User).filter(models.CDE_User.uuid == user_uuid).first()
        if user is None:
            return None
        else:
            projects = json.loads(user.projects)
            if project_id in projects:
                project = session.query(models.CDE_Projects).filter(models.CDE_Projects.project_id == project_id).first()
                project.name = project.name
                project.description = project.description
                session.commit()
                return project
            else:
                return None
            
def get_project_extensions(db: Session, project_id : str, user_uuid : str, limit: int = 1000, skip: int = 0):
    with SessionLocal() as session:
        user = session.query(models.CDE_User).filter(models.CDE_User.uuid == user_uuid).first()
        if user is None:
            return None
        else:
            projects = json.loads(user.projects)
            if project_id in projects:
                return session.query(models.CDE_Extensions).filter(models.CDE_Extensions.project_id == project_id).offset(skip).limit(limit).all()
            else:
                return None




    