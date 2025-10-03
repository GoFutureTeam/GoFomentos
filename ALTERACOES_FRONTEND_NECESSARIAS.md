# 🔧 ALTERAÇÕES NECESSÁRIAS NO FRONTEND

## 🚨 PROBLEMA CRÍTICO #1: PROXY DO VITE

**Arquivo:** `frontend/vite.config.ts`

**Problema:** O proxy está interceptando todas as chamadas `/api` e redirecionando para um servidor externo.

**Solução:**
```typescript
// ANTES
server: {
  host: "::",
  port: 8080,
  proxy: {
    '/api': {
      target: 'https://api-editais.gofuture.cc',
      changeOrigin: true,
      secure: true,
      rewrite: (path) => path.replace(/^\/api/, '/api')
    },
    // ...
  }
},

// DEPOIS
server: {
  host: "::",
  port: 8080,
  // PROXY DESABILITADO - Usando backend local (Docker) na porta 8002
  // O proxy estava interceptando as chamadas /api e redirecionando para servidor externo
  /*
  proxy: {
    '/api': {
      target: 'https://api-editais.gofuture.cc',
      changeOrigin: true,
      secure: true,
      rewrite: (path) => path.replace(/^\/api/, '/api')
    },
    // ...
  }
  */
},
```

**Fazer o mesmo para a seção `preview` no mesmo arquivo.**

---

## 🚨 PROBLEMA #2: ARQUIVO .ENV

**Arquivo:** `frontend/.env`

**Problema:** O arquivo `.env` pode estar ausente ou desatualizado.

**Solução:**
```
VITE_API_BASE_URL=http://localhost:8002
```

**Comando para criar:**
```bash
echo VITE_API_BASE_URL=http://localhost:8002 > frontend/.env
```

---

## 🚨 PROBLEMA #3: CAMPOS ANTIGOS EM COMPONENTES

### 3.1. MeusProjetos.tsx

**Arquivo:** `frontend/src/pages/MeusProjetos.tsx`

**Problema:** Usando campos antigos (`nomeProjeto`, `descricao`, `areaProjeto`) em vez dos novos campos do backend.

**Solução:**
```typescript
// ANTES
<h4 className="font-bold text-2xl text-[rgba(67,80,88,1)] mb-3">
  {projeto.nomeProjeto}
</h4>
<p className="text-base text-[rgba(67,80,88,1)] mb-4 line-clamp-3">
  {projeto.descricao}
</p>
<span className="text-sm text-[rgba(67,80,88,1)] font-medium">
  {projeto.areaProjeto || 'Geral'}
</span>

// DEPOIS
<h4 className="font-bold text-2xl text-[rgba(67,80,88,1)] mb-3">
  {projeto.titulo_projeto}
</h4>
<p className="text-base text-[rgba(67,80,88,1)] mb-4 line-clamp-3">
  {projeto.resumo_atividades}
</p>
<span className="text-sm text-[rgba(67,80,88,1)] font-medium">
  {projeto.nome_empresa}
</span>
```

**Também mudar:**
```typescript
// ANTES
const confirmarExclusao = (projetoId: string, nomeProjeto: string) => {
  if (window.confirm(`Tem certeza que deseja excluir o projeto "${nomeProjeto}"?`)) {
    excluirProjeto(projetoId);
  }
};

// DEPOIS
const confirmarExclusao = (projetoId: string, tituloProjeto: string) => {
  if (window.confirm(`Tem certeza que deseja excluir o projeto "${tituloProjeto}"?`)) {
    excluirProjeto(projetoId);
  }
};
```

**E na chamada da função:**
```typescript
// ANTES
onClick={() => confirmarExclusao(projeto.id!, projeto.nomeProjeto)}

// DEPOIS
onClick={() => confirmarExclusao(projeto.id!, projeto.titulo_projeto)}
```

---

### 3.2. ProjetosSalvos.tsx

**Arquivo:** `frontend/src/components/match/ProjetosSalvos.tsx`

**Problema:** Usando campos antigos (`nomeProjeto`, `descricao`, `areaProjeto`).

**Solução:**
```typescript
// ANTES
<h4 className="font-bold text-lg text-[rgba(67,80,88,1)] mb-2 line-clamp-2">
  {projeto.nomeProjeto}
</h4>
<p className="text-sm text-[rgba(67,80,88,1)] mb-3 line-clamp-3">
  {projeto.descricao}
</p>
<span className="text-xs text-[rgba(67,80,88,1)] font-medium">
  {projeto.areaProjeto || 'Geral'}
</span>

// DEPOIS
<h4 className="font-bold text-lg text-[rgba(67,80,88,1)] mb-2 line-clamp-2">
  {projeto.titulo_projeto}
</h4>
<p className="text-sm text-[rgba(67,80,88,1)] mb-3 line-clamp-3">
  {projeto.resumo_atividades}
</p>
<span className="text-xs text-[rgba(67,80,88,1)] font-medium">
  {projeto.nome_empresa}
</span>
```

---

## 📋 RESUMO DAS ALTERAÇÕES

1. ✅ **vite.config.ts** - Comentar proxy para evitar redirecionamento
2. ✅ **frontend/.env** - Criar/atualizar com URL do backend local
3. ✅ **MeusProjetos.tsx** - Atualizar campos para novo formato
4. ✅ **ProjetosSalvos.tsx** - Atualizar campos para novo formato

---

## 🚀 APÓS ALTERAÇÕES

1. **Reiniciar o frontend:**
```bash
cd frontend
npm run dev
```

2. **Acessar:**
```
http://localhost:8080
```

3. **Testar registro e login**

---

## 📝 MAPEAMENTO DE CAMPOS

| Campo Antigo | Campo Novo |
|-------------|------------|
| `nomeProjeto` | `titulo_projeto` |
| `descricao` | `resumo_atividades` |
| `objetivoPrincipal` | `objetivo_principal` |
| `areaProjeto` | `nome_empresa` |
| `dataCriacao` | `created_at` |
| `dataAtualizacao` | `updated_at` |
