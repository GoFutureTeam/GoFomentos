# Convenções de Nomenclatura - Projeto GoFomentos

Este documento estabelece as convenções de nomenclatura para o projeto GoFomentos, visando padronizar o código e torná-lo mais didático e compreensível.

## Princípios Gerais

1. **Idioma**: Todo o código de domínio será escrito em português
2. **Consistência**: Seguir os mesmos padrões em todo o projeto
3. **Clareza**: Nomes devem ser descritivos e autoexplicativos

## Convenções Específicas

### Arquivos e Componentes

- **Componentes**: PascalCase em português
  - Exemplo: `CardEdital.tsx`, `SecaoFiltro.tsx`, `BotaoPrimario.tsx`

#### Exemplo Prático de Componente

```tsx
// CardEdital.tsx
import React from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Edital } from '../types/edital';

// Interface de props em português com prefixo descritivo
interface PropsCardEdital {
  edital: Edital;
  aoClicar?: (id: number) => void;
  destacado?: boolean;
}

const CardEdital: React.FC<PropsCardEdital> = ({ 
  edital, 
  aoClicar, 
  destacado = false 
}) => {
  // Variáveis em português
  const { id, titulo, descricao_resumida, categoria, data_fim_submissao } = edital;
  
  // Funções em português
  const formatarData = (data: string) => {
    return new Date(data).toLocaleDateString('pt-BR');
  };
  
  const manipularClique = () => {
    if (aoClicar) {
      aoClicar(id);
    }
  };
  
  return (
    <Card 
      className={`cursor-pointer hover:shadow-md transition-shadow ${destacado ? 'border-primary' : ''}`}
      onClick={manipularClique}
    >
      <CardHeader>
        <CardTitle className="text-lg font-bold">{titulo}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-600 line-clamp-2">{descricao_resumida}</p>
        <div className="mt-2 flex items-center">
          <span className="bg-primary/10 text-primary text-xs px-2 py-1 rounded">
            {categoria || 'Sem categoria'}
          </span>
        </div>
      </CardContent>
      <CardFooter className="flex justify-between">
        <p className="text-xs text-gray-500">
          Prazo: {data_fim_submissao ? formatarData(data_fim_submissao) : 'Não informado'}
        </p>
        <Button size="sm" variant="outline">Ver detalhes</Button>
      </CardFooter>
    </Card>
  );
};

export default CardEdital;
```

#### Uso do Componente

```tsx
import CardEdital from '../components/CardEdital';
import { useEditaisPortugues } from '../hooks/useEditaisPortugues';

const ListaEditais = () => {
  const { editais, carregando } = useEditaisPortugues();
  const [idSelecionado, setIdSelecionado] = useState<number | null>(null);
  
  const aoSelecionarEdital = (id: number) => {
    setIdSelecionado(id);
  };
  
  if (carregando) {
    return <p>Carregando editais...</p>;
  }
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {editais.map(edital => (
        <CardEdital 
          key={edital.id}
          edital={edital}
          aoClicar={aoSelecionarEdital}
          destacado={edital.id === idSelecionado}
        />
      ))}
    </div>
  );
};
```

### Hooks

#### Compatibilidade com React

O React exige que todos os hooks comecem com o prefixo `use`. Para manter a compatibilidade com o React e seguir as convenções em português, temos duas opções:

1. **Opção Recomendada**: Manter o prefixo `use` e adicionar o sufixo `Portugues`
   - Exemplo: `useEditaisPortugues`, `useFiltersPortugues`
   - Esta abordagem evita erros de lint e mantém a compatibilidade com o React

2. **Alternativa (não recomendada para hooks)**: Usar o prefixo "usar"
   - Exemplo: `usarEditais`, `usarFiltros`
   - **Atenção**: Esta abordagem causa erros de lint, pois o React não reconhece estes como hooks válidos

#### Exemplo Prático de Hook Compatível

```typescript
// useEditaisPortugues.ts
import { useState, useEffect, useCallback } from 'react';
import { apiEdital } from '../services/apiEdital';

export const useEditaisPortugues = (filtrosIniciais = {}) => {
  // Variáveis em português
  const [editais, setEditais] = useState([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState(null);
  
  // Funções em português
  const buscarEditais = useCallback(async () => {
    setCarregando(true);
    try {
      const resposta = await apiEdital.listarEditais(filtrosIniciais);
      setEditais(resposta.data);
    } catch (err) {
      setErro('Erro ao buscar editais');
    } finally {
      setCarregando(false);
    }
  }, [filtrosIniciais]);
  
  useEffect(() => {
    buscarEditais();
  }, [buscarEditais]);
  
  return {
    editais,
    carregando,
    erro,
    buscarEditais
  };
};
```

#### Uso do Hook em Componentes

```tsx
// No componente
import { useEditaisPortugues } from '../hooks/useEditaisPortugues';

const MeuComponente = () => {
  // Uso direto com nomes em português
  const { editais, carregando, erro } = useEditaisPortugues();
  
  // OU mapeando para nomes em inglês se necessário
  const { 
    editais: items, 
    carregando: loading, 
    erro: error 
  } = useEditaisPortugues();
  
  // Resto do componente...
};
```

### Contextos

- **Arquivos de Contexto**: Prefixo "Contexto" + nome em PascalCase
  - Exemplo: `ContextoEditais.tsx`, `ContextoUsuario.tsx`
- **Provedores de Contexto**: Prefixo "Provedor" + nome em PascalCase
  - Exemplo: `ProvedorEditais`, `ProvedorAutenticacao`

#### Exemplo Prático de Contexto

```typescript
// ContextoEditais.tsx
import React, { createContext, useState } from 'react';
import { Edital } from '../types/edital';

// Definir o tipo do contexto
type ValorContextoEditais = {
  editais: Edital[];
  carregando: boolean;
  erro: string | null;
  atualizarFiltros: (filtros: any) => void;
};

// Criar o contexto
export const ContextoEditais = createContext<ValorContextoEditais | undefined>(undefined);

// Criar o provedor
export const ProvedorEditais: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [editais, setEditais] = useState<Edital[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  
  const atualizarFiltros = (filtros: any) => {
    // Lógica para atualizar filtros
  };
  
  const valor = {
    editais,
    carregando,
    erro,
    atualizarFiltros
  };
  
  return (
    <ContextoEditais.Provider value={valor}>
      {children}
    </ContextoEditais.Provider>
  );
};
```

#### Uso do Contexto

```tsx
// Hook para acessar o contexto
import { useContext } from 'react';
import { ContextoEditais } from '../contexts/ContextoEditais';

export const useContextoEditaisPortugues = () => {
  const contexto = useContext(ContextoEditais);
  if (!contexto) {
    throw new Error('useContextoEditaisPortugues deve ser usado dentro de um ProvedorEditais');
  }
  return contexto;
};

// Uso no componente
const MeuComponente = () => {
  const { editais, carregando } = useContextoEditaisPortugues();
  // Resto do componente...
};
```

### Serviços e APIs

- **Arquivos de Serviço**: Prefixo do tipo + nome em camelCase
  - Exemplo: `apiEdital.ts`, `servicoAutenticacao.ts`
- **Classes de Serviço**: Prefixo "Servico" + nome em PascalCase
  - Exemplo: `ServicoApiEdital`, `ServicoAutenticacao`

#### Exemplo Prático de Serviço de API

```typescript
// apiEdital.ts
import { Edital, FiltrosEdital } from '../types/edital';

// Interface para resposta da API
interface RespostaApi<T> {
  dados: T;
  sucesso: boolean;
  mensagem: string;
}

class ServicoApiEdital {
  private urlBase = '/api/v1';
  
  // Métodos em português
  async listarEditais(filtros: FiltrosEdital = {}): Promise<RespostaApi<Edital[]>> {
    try {
      const params = new URLSearchParams();
      
      // Adicionar filtros como parâmetros
      if (filtros.categoria) {
        params.append('categoria', filtros.categoria);
      }
      
      const resposta = await fetch(`${this.urlBase}/editais?${params}`);
      const dados = await resposta.json();
      
      return {
        dados: dados.editais,
        sucesso: true,
        mensagem: 'Editais carregados com sucesso'
      };
    } catch (erro) {
      return {
        dados: [],
        sucesso: false,
        mensagem: `Erro ao carregar editais: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }
  
  async obterEdital(id: number): Promise<RespostaApi<Edital>> {
    try {
      const resposta = await fetch(`${this.urlBase}/editais/${id}`);
      const dados = await resposta.json();
      
      return {
        dados,
        sucesso: true,
        mensagem: 'Edital encontrado'
      };
    } catch (erro) {
      return {
        dados: null as unknown as Edital,
        sucesso: false,
        mensagem: `Erro ao buscar edital: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }
  
  async criarEdital(dados: Partial<Edital>): Promise<RespostaApi<Edital>> {
    try {
      const resposta = await fetch(`${this.urlBase}/editais`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
      });
      
      const editalCriado = await resposta.json();
      
      return {
        dados: editalCriado,
        sucesso: true,
        mensagem: 'Edital criado com sucesso'
      };
    } catch (erro) {
      return {
        dados: null as unknown as Edital,
        sucesso: false,
        mensagem: `Erro ao criar edital: ${erro instanceof Error ? erro.message : 'Erro desconhecido'}`
      };
    }
  }
}

// Exportar uma instância única do serviço
export const apiEdital = new ServicoApiEdital();
```

#### Uso do Serviço

```typescript
import { apiEdital } from '../services/apiEdital';

// Em um componente ou hook
const buscarDados = async () => {
  try {
    const resposta = await apiEdital.listarEditais({ categoria: 'Tecnologia' });
    if (resposta.sucesso) {
      console.log('Editais carregados:', resposta.dados);
    } else {
      console.error('Erro:', resposta.mensagem);
    }
  } catch (erro) {
    console.error('Erro na requisição:', erro);
  }
};
```

### Variáveis e Propriedades

- **Variáveis e Propriedades**: camelCase em português
  - Exemplo: `termoBusca`, `filtrosAtivos`, `tipoRecurso`
- **Constantes**: UPPER_SNAKE_CASE em português
  - Exemplo: `URL_BASE_API`, `TEMPO_LIMITE_SESSAO`

### Interfaces e Types

- **Interfaces/Types**: Prefixo descritivo + PascalCase
  - Exemplo: `PropsCardEdital`, `FiltrosEdital`, `EstadoAplicacao`
  - Prefixos comuns: `Props`, `Estado`, `Resposta`, `Filtros`

### Funções e Métodos

- **Funções e Métodos**: camelCase com verbo + substantivo
  - Exemplo: `buscarEditais()`, `atualizarFiltros()`, `formatarData()`

## Exemplos de Refatoração

### Antes:
```typescript
// EditalCard.tsx
const EditalCard: React.FC<EditalCardProps> = ({ id, nome }) => { ... }

// useEditais.ts
export const useEditais = (initialFilters: EditalFilters = {}) => { ... }

// editalApi.ts
class EditalApiService { async listEditais() { ... } }
```

### Depois:
```typescript
// CardEdital.tsx
const CardEdital: React.FC<PropsCardEdital> = ({ id, nome }) => { ... }

// usarEditais.ts
export const usarEditais = (filtrosIniciais: FiltrosEdital = {}) => { ... }

// apiEdital.ts
class ServicoApiEdital { async listarEditais() { ... } }
```

## Implementação

A implementação destas convenções será feita gradualmente, começando pelos componentes principais e expandindo para todo o projeto.
