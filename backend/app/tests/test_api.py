import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

def test_read_main():
    """
    Testa a rota raiz da API
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bem-vindo à API de Editais"}

def test_health_check():
    """
    Testa a rota de health check
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "mongodb_status" in response.json()
    assert "chromadb_status" in response.json()

# Testes que requerem autenticação
@pytest.fixture
def token():
    """
    Fixture para obter token de autenticação para testes
    """
    # Criar um usuário de teste
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword"
    }
    
    # Tentar criar o usuário (pode falhar se já existir)
    client.post("/api/users", json=user_data)
    
    # Fazer login
    response = client.post(
        "/token",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    
    assert response.status_code == 200
    return response.json()["access_token"]

def test_read_users_me(token):
    """
    Testa a rota para obter o usuário atual
    """
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
