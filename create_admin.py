#!/usr/bin/env python3
import requests
import json

# Dados do usuário administrador
admin_user = {
    "email": "admin@gofomentos.com",
    "name": "Administrador GoFomentos",
    "password": "admin123"
}

def create_admin_user():
    """Cria o usuário administrador via API"""
    try:
        # URL da API
        url = "http://localhost:8000/api/users"
        
        # Headers
        headers = {
            "Content-Type": "application/json"
        }
        
        # Fazer requisição POST
        response = requests.post(url, json=admin_user, headers=headers)
        
        if response.status_code == 200:
            print("✅ Usuário administrador criado com sucesso!")
            print(f"📧 Email: {admin_user['email']}")
            print(f"🔑 Senha: {admin_user['password']}")
            print(f"👤 Nome: {admin_user['name']}")
            print("\nResposta da API:")
            print(json.dumps(response.json(), indent=2))
        elif response.status_code == 400:
            error_detail = response.json().get("detail", "Erro desconhecido")
            if "already registered" in error_detail.lower():
                print("ℹ️  Usuário administrador já existe!")
                print(f"📧 Email: {admin_user['email']}")
                print(f"🔑 Senha: {admin_user['password']}")
            else:
                print(f"❌ Erro ao criar usuário: {error_detail}")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar à API. Verifique se o servidor está rodando.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def test_login():
    """Testa o login do usuário administrador"""
    try:
        # URL do token
        url = "http://localhost:8000/token"
        
        # Dados do login
        login_data = {
            "username": admin_user["email"],
            "password": admin_user["password"]
        }
        
        # Headers para form data
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Fazer requisição POST
        response = requests.post(url, data=login_data, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            print("\n✅ Login realizado com sucesso!")
            print(f"🎫 Token: {token_data['access_token'][:50]}...")
            return token_data['access_token']
        else:
            print(f"\n❌ Erro no login: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n❌ Erro no teste de login: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Criando usuário administrador para GoFomentos...")
    print("=" * 50)
    
    # Criar usuário
    create_admin_user()
    
    # Testar login
    token = test_login()
    
    print("\n" + "=" * 50)
    print("✅ Processo concluído!")
    print("\n📋 CREDENCIAIS DO ADMINISTRADOR:")
    print(f"   Email: {admin_user['email']}")
    print(f"   Senha: {admin_user['password']}")
    print(f"   Nome: {admin_user['name']}")
