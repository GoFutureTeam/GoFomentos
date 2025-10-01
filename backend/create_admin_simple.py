import asyncio
import sys
import os
sys.path.append('/app')

from app.api.services.mongo_service import MongoService
from app.api.models.user import UserCreate

async def create_admin():
    """Cria usuário administrador diretamente no banco"""
    try:
        # Dados do usuário admin
        admin_data = UserCreate(
            email="admin@gofomentos.com",
            name="Administrador GoFomentos",
            password="admin123"
        )
        
        # Criar usuário
        user = await MongoService.create_user(admin_data)
        
        print("✅ Usuário administrador criado com sucesso!")
        print(f"📧 Email: {user.email}")
        print(f"👤 Nome: {user.name}")
        print(f"🆔 ID: {user.id}")
        print(f"🔑 Senha: admin123")
        
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            print("ℹ️  Usuário administrador já existe!")
            print("📧 Email: admin@gofomentos.com")
            print("🔑 Senha: admin123")
        else:
            print(f"❌ Erro ao criar usuário: {e}")

if __name__ == "__main__":
    asyncio.run(create_admin())
