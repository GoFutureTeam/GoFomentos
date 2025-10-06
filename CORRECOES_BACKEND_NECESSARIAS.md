# 🔴 CORREÇÕES NECESSÁRIAS NO BACKEND

## RESUMO
O backend está usando **Pydantic V2** mas com sintaxe do **Pydantic V1**, causando crashes ao serializar respostas.

---

## ARQUIVOS COM TODOs ADICIONADOS:

### 1. **Models** (3 arquivos)
- `backend/app/api/models/user.py` - linha 42
- `backend/app/api/models/project.py` - linha 59
- `backend/app/api/models/edital.py` - linha 111

**Buscar por:** `TODO: CORREÇÃO NECESSÁRIA - Pydantic V2`

**Mudar:**
```python
class Config:
    orm_mode = True  # ❌ ERRADO
```

**Para:**
```python
class Config:
    from_attributes = True  # ✅ CORRETO
```

---

### 2. **mongo_service.py**
Arquivo: `backend/app/api/services/mongo_service.py`

**Buscar por:** `TODO: CORREÇÃO`

#### Métodos com correções necessárias:
- `create_user()` - linhas 21-42 (3 TODOs)
- `get_user()` - linhas 58-61
- `create_edital()` - linhas 119-133
- `create_project()` - linhas 187-201
- `get_project()` - linhas 210-213
- `get_user_projects()` - linhas 221-225

**Principais mudanças:**

1. **Substituir `.dict()` por `.model_dump()`**
2. **Excluir password ao criar UserInDB:**
   ```python
   user_data = user.model_dump(exclude={'password'})
   ```
3. **Remover `_id` do MongoDB antes de retornar:**
   ```python
   if '_id' in dict_obj:
       del dict_obj['_id']
   ```

---

### 3. **auth_service.py**
Arquivo: `backend/app/api/services/auth_service.py`

**Buscar por:** `TODO: CORREÇÃO` (linha 38)

Método: `get_user()`

---

## TESTE APÓS CORREÇÕES:

```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@example.com","name":"Teste","password":"senha123"}'
```

Deve retornar **200 OK** com JSON do usuário.

---

## PRIORIDADE: 🔴 CRÍTICA
Sem essas correções, registro/login/projetos NÃO funcionam.
