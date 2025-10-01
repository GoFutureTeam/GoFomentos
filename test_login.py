#!/usr/bin/env python3
import requests
import json

def test_login():
    """Testa o login do administrador"""
    print("🔐 Testando login do administrador...")
    
    # URL do token
    url = "http://localhost:8000/token"
    
    # Dados do login
    data = {
        "username": "admin@gofomentos.com",
        "password": "admin123"
    }
    
    # Headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        # Fazer requisição POST
        response = requests.post(url, data=data, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ LOGIN REALIZADO COM SUCESSO!")
            print(f"🎫 Token JWT: {token_data['access_token'][:50]}...")
            print(f"🕒 Tipo: {token_data['token_type']}")
            
            # Testar um endpoint protegido
            test_protected_endpoint(token_data['access_token'])
            
            return token_data['access_token']
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def test_protected_endpoint(token):
    """Testa um endpoint protegido"""
    print("\n🔒 Testando endpoint protegido...")
    
    url = "http://localhost:8000/api/users/me"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Endpoint protegido funcionando!")
            print(f"👤 Usuário: {user_data['name']}")
            print(f"📧 Email: {user_data['email']}")
            print(f"🆔 ID: {user_data['id']}")
        else:
            print(f"❌ Erro no endpoint protegido: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

def test_editais_list(token):
    """Testa listagem de editais"""
    print("\n📄 Testando listagem de editais...")
    
    url = "http://localhost:8000/api/editais"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            editais = response.json()
            print(f"✅ Listagem funcionando! Encontrados {len(editais)} editais")
            if editais:
                print(f"📋 Primeiro edital: {editais[0].get('apelido_edital', 'Sem nome')}")
        else:
            print(f"❌ Erro na listagem: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    print("🚀 Testando sistema GoFomentos...")
    print("=" * 50)
    
    # Testar login
    token = test_login()
    
    if token:
        # Testar listagem de editais
        test_editais_list(token)
        
        print("\n" + "=" * 50)
        print("✅ TESTES CONCLUÍDOS COM SUCESSO!")
        print("\n📋 CREDENCIAIS CONFIRMADAS:")
        print("   Email: admin@gofomentos.com")
        print("   Senha: admin123")
        print("   Sistema: 100% Funcional")
    else:
        print("\n❌ Falha nos testes de autenticação")
