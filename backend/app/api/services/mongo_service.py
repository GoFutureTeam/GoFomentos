from typing import List, Dict, Any, Optional
from ...db.mongodb import mongodb
from ..models.user import UserCreate, UserInDB, User, UserUpdate
from ..models.edital import EditalCreate, EditalInDB, Edital, EditalUpdate
from ..models.project import ProjectCreate, ProjectInDB, Project, ProjectUpdate
from .auth_service import get_password_hash
from datetime import datetime
import uuid


class MongoService:
    @staticmethod
    async def create_user(user: UserCreate) -> User:
        users_collection = mongodb.get_collection("users")
        
        # Verificar se o usuário já existe
        existing_user = await users_collection.find_one({"email": user.email})
        if existing_user:
            raise ValueError(f"User with email {user.email} already exists")
        
        # Criar usuário no banco
        user_in_db = UserInDB(
            **user.dict(),
            hashed_password=get_password_hash(user.password)
        )
        
        await users_collection.insert_one(user_in_db.dict())
        
        return User(
            id=user_in_db.id,
            email=user_in_db.email,
            name=user_in_db.name,
            is_active=user_in_db.is_active,
            created_at=user_in_db.created_at,
            updated_at=user_in_db.updated_at
        )
    
    @staticmethod
    async def get_user(user_id: str) -> Optional[User]:
        users_collection = mongodb.get_collection("users")
        user = await users_collection.find_one({"id": user_id})
        if user:
            user_in_db = UserInDB(**user)
            return User(
                id=user_in_db.id,
                email=user_in_db.email,
                name=user_in_db.name,
                is_active=user_in_db.is_active,
                created_at=user_in_db.created_at,
                updated_at=user_in_db.updated_at
            )
        return None
    
    @staticmethod
    async def update_user(user_id: str, user_update: UserUpdate) -> Optional[User]:
        users_collection = mongodb.get_collection("users")
        
        # Verificar se o usuário existe
        existing_user = await users_collection.find_one({"id": user_id})
        if not existing_user:
            return None
        
        # Preparar dados para atualização
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Atualizar usuário
        await users_collection.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        # Buscar usuário atualizado
        updated_user = await users_collection.find_one({"id": user_id})
        user_in_db = UserInDB(**updated_user)
        
        return User(
            id=user_in_db.id,
            email=user_in_db.email,
            name=user_in_db.name,
            is_active=user_in_db.is_active,
            created_at=user_in_db.created_at,
            updated_at=user_in_db.updated_at
        )
    
    @staticmethod
    async def delete_user(user_id: str) -> bool:
        users_collection = mongodb.get_collection("users")
        result = await users_collection.delete_one({"id": user_id})
        return result.deleted_count > 0
    
    @staticmethod
    async def create_edital(edital: EditalCreate) -> Edital:
        editais_collection = mongodb.get_collection("editais")
        
        # Criar edital no banco
        edital_in_db = EditalInDB(**edital.dict())
        
        await editais_collection.insert_one(edital_in_db.dict())
        
        return Edital(
            **edital_in_db.dict()
        )
    
    @staticmethod
    async def get_edital(edital_uuid: str) -> Optional[Edital]:
        editais_collection = mongodb.get_collection("editais")
        edital = await editais_collection.find_one({"uuid": edital_uuid})
        if edital:
            return Edital(**edital)
        return None
    
    @staticmethod
    async def get_editais(skip: int = 0, limit: int = 100) -> List[Edital]:
        editais_collection = mongodb.get_collection("editais")
        editais = await editais_collection.find().skip(skip).limit(limit).to_list(length=limit)
        return [Edital(**edital) for edital in editais]
    
    @staticmethod
    async def update_edital(edital_uuid: str, edital_update: EditalUpdate) -> Optional[Edital]:
        editais_collection = mongodb.get_collection("editais")
        
        # Verificar se o edital existe
        existing_edital = await editais_collection.find_one({"uuid": edital_uuid})
        if not existing_edital:
            return None
        
        # Preparar dados para atualização
        update_data = edital_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        # Atualizar edital
        await editais_collection.update_one(
            {"uuid": edital_uuid},
            {"$set": update_data}
        )
        
        # Buscar edital atualizado
        updated_edital = await editais_collection.find_one({"uuid": edital_uuid})
        
        return Edital(**updated_edital)
    
    @staticmethod
    async def delete_edital(edital_uuid: str) -> bool:
        editais_collection = mongodb.get_collection("editais")
        result = await editais_collection.delete_one({"uuid": edital_uuid})
        return result.deleted_count > 0
    
    @staticmethod
    async def create_project(project: ProjectCreate) -> Project:
        projects_collection = mongodb.get_collection("projects")
        
        # Criar projeto no banco
        project_in_db = ProjectInDB(**project.dict())
        
        await projects_collection.insert_one(project_in_db.dict())
        
        return Project(**project_in_db.dict())
    
    @staticmethod
    async def get_project(project_id: str) -> Optional[Project]:
        projects_collection = mongodb.get_collection("projects")
        project = await projects_collection.find_one({"id": project_id})
        if project:
            return Project(**project)
        return None
    
    @staticmethod
    async def get_user_projects(user_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        projects_collection = mongodb.get_collection("projects")
        projects = await projects_collection.find({"user_id": user_id}).skip(skip).limit(limit).to_list(length=limit)
        return [Project(**project) for project in projects]
    
    @staticmethod
    async def update_project(project_id: str, project_update: ProjectUpdate) -> Optional[Project]:
        projects_collection = mongodb.get_collection("projects")
        
        # Verificar se o projeto existe
        existing_project = await projects_collection.find_one({"id": project_id})
        if not existing_project:
            return None
        
        # Preparar dados para atualização
        update_data = project_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        # Atualizar projeto
        await projects_collection.update_one(
            {"id": project_id},
            {"$set": update_data}
        )
        
        # Buscar projeto atualizado
        updated_project = await projects_collection.find_one({"id": project_id})
        
        return Project(**updated_project)
    
    @staticmethod
    async def delete_project(project_id: str) -> bool:
        projects_collection = mongodb.get_collection("projects")
        result = await projects_collection.delete_one({"id": project_id})
        return result.deleted_count > 0
