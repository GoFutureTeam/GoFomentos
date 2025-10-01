# Solução para Nomenclatura de Hooks em Português no React

## Problema

O React exige que todos os hooks comecem com o prefixo `use`. Quando tentamos usar o prefixo `usar` em português (como em `usarEditais`), o linter do React detecta isso como um erro porque não reconhece essas funções como hooks válidos.

## Solução Implementada

Para resolver este problema e manter a padronização da nomenclatura em português, implementamos a seguinte solução:

### 1. Hooks com Nomenclatura Compatível

Criamos hooks com o prefixo `use` (exigido pelo React) e adicionamos o sufixo `Portugues` para indicar que usam nomenclatura em português internamente:

```typescript
// ✅ Correto: Mantém o prefixo "use" exigido pelo React
export const useEditaisPortugues = (filtrosIniciais: EditalFilters = {}) => {
  // Implementação com nomes em português
};
```

### 2. Nomes Internos em Português

Dentro dos hooks, usamos nomenclatura totalmente em português para variáveis e funções:

```typescript
// Variáveis em português
const [editais, setEditais] = useState<Edital[]>([]);
const [carregando, setCarregando] = useState(false);
const [erro, setErro] = useState<string | null>(null);

// Funções em português
const buscarEditais = useCallback(() => { /* ... */ }, []);
const atualizarFiltros = useCallback(() => { /* ... */ }, []);
```

### 3. Mapeamento nos Componentes

Nos componentes que usam os hooks, fazemos um mapeamento dos nomes em português para os nomes que o componente espera:

```typescript
// Componente usando o hook
const {
  editais,
  carregando: loading,  // Mapeamento para nome esperado pelo componente
  erro: error           // Mapeamento para nome esperado pelo componente
} = useEditaisPortugues();
```

## Arquivos Atualizados

1. **Hooks**:
   - `useEditaisPortugues.ts` (substituindo `useEditais.ts`)
   - `useEditalPortugues.ts` (substituindo `useEdital.ts`)
   - `useEditaisAvancadoPortugues.ts` (substituindo `useEditaisAdvanced.ts`)
   - `useContextoEditaisPortugues.ts` (substituindo `useEditaisContext.ts`)

2. **Componentes**:
   - `FilterSection.tsx` - Atualizado para usar `useContextoEditaisPortugues`
   - `Index.tsx` - Atualizado para usar `useContextoEditaisPortugues`
   - `EditalDetails.tsx` - Atualizado para usar `useEditalPortugues`
   - `ProjectForm.tsx` - Atualizado para usar `useEditaisPortugues`

3. **Contextos**:
   - `EditaisContext.tsx` - Atualizado para usar `useEditaisAvancadoPortugues`

## Benefícios

1. **Compatibilidade com React**: Mantém a compatibilidade com as regras do React para hooks
2. **Padronização em Português**: Preserva a nomenclatura em português para maior clareza
3. **Sem Erros de Lint**: Evita os erros de lint relacionados a hooks
4. **Consistência**: Mantém um padrão consistente em todo o projeto

## Próximos Passos

Para continuar a padronização do projeto:

1. Usar o script `refatorar-nomenclatura.js` para automatizar a refatoração de outros arquivos
2. Atualizar a documentação do projeto para refletir as novas convenções
3. Implementar revisões de código para garantir que as novas convenções sejam seguidas

## Exemplo de Uso

```tsx
// Componente usando o hook com nomenclatura correta
import { useEditaisPortugues } from '../hooks/useEditaisPortugues';

const MeuComponente = () => {
  const {
    editais,
    carregando,
    erro,
    atualizarFiltros
  } = useEditaisPortugues();
  
  // Resto do componente...
};
```
