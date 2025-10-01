import React, { useState } from 'react';
import { useEditaisPortugues, useEditalPortugues, useEnumsEdital } from '../hooks/useEditaisPortugues';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Skeleton } from './ui/skeleton';

/**
 * Componente de exemplo que demonstra o uso dos hooks com nomenclatura correta
 * 
 * Este componente mostra como usar os hooks que seguem as convenções de nomenclatura
 * em português, mas mantendo a compatibilidade com o React.
 */
const ExemploUsoHooks: React.FC = () => {
  const [idEditalSelecionado, setIdEditalSelecionado] = useState<number | null>(null);
  
  // Uso do hook useEditaisPortugues (nomenclatura compatível com React)
  const {
    editais,
    carregando: carregandoEditais,
    erro: erroEditais,
    atualizarFiltros
  } = useEditaisPortugues();
  
  // Uso do hook useEditalPortugues para detalhes de um edital específico
  const {
    edital,
    carregando: carregandoEdital,
    erro: erroEdital,
    baixarPdf
  } = useEditalPortugues(idEditalSelecionado || undefined);
  
  // Uso do hook useEnumsEdital para obter enumerações
  const {
    enums,
    carregando: carregandoEnums
  } = useEnumsEdital();
  
  // Função para selecionar um edital
  const selecionarEdital = (id: number) => {
    setIdEditalSelecionado(id);
  };
  
  // Função para filtrar por categoria
  const filtrarPorCategoria = (categoria: string) => {
    atualizarFiltros({ categoria });
  };
  
  // Função para baixar o PDF de um edital
  const handleBaixarPdf = async () => {
    if (idEditalSelecionado) {
      try {
        await baixarPdf(idEditalSelecionado);
      } catch (erro) {
        console.error('Erro ao baixar PDF:', erro);
      }
    }
  };
  
  // Renderização condicional para estado de carregamento
  if (carregandoEditais) {
    return (
      <div className="p-4">
        <h2 className="text-xl font-bold mb-4">Carregando editais...</h2>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      </div>
    );
  }
  
  // Renderização condicional para erro
  if (erroEditais) {
    return (
      <div className="p-4 text-red-500">
        <h2 className="text-xl font-bold mb-2">Erro ao carregar editais</h2>
        <p>{erroEditais}</p>
      </div>
    );
  }
  
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-6">Exemplo de Uso dos Hooks</h1>
      
      {/* Seção de categorias */}
      <div className="mb-6">
        <h2 className="text-xl font-bold mb-2">Categorias</h2>
        <div className="flex flex-wrap gap-2">
          {carregandoEnums ? (
            <Skeleton className="h-10 w-32" />
          ) : (
            enums?.categorias.map((categoria) => (
              <Button 
                key={categoria} 
                variant="outline"
                onClick={() => filtrarPorCategoria(categoria)}
              >
                {categoria}
              </Button>
            ))
          )}
        </div>
      </div>
      
      {/* Lista de editais */}
      <div className="mb-6">
        <h2 className="text-xl font-bold mb-2">Editais</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {editais.map((edital) => (
            <Card 
              key={edital.id} 
              className={`cursor-pointer ${idEditalSelecionado === edital.id ? 'border-primary' : ''}`}
              onClick={() => selecionarEdital(edital.id)}
            >
              <CardHeader>
                <CardTitle>{edital.titulo}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{edital.descricao_resumida}</p>
                <div className="mt-2 flex items-center">
                  <span className="bg-primary/10 text-primary text-xs px-2 py-1 rounded">
                    {edital.categoria || 'Sem categoria'}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
      
      {/* Detalhes do edital selecionado */}
      {idEditalSelecionado && (
        <div className="mt-8">
          <h2 className="text-xl font-bold mb-2">Detalhes do Edital</h2>
          
          {carregandoEdital ? (
            <Skeleton className="h-48 w-full" />
          ) : erroEdital ? (
            <div className="p-4 text-red-500">
              <p>{erroEdital}</p>
            </div>
          ) : edital ? (
            <Card>
              <CardHeader>
                <CardTitle>{edital.titulo}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p>{edital.descricao_completa || edital.descricao}</p>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h3 className="font-semibold">Empresa</h3>
                      <p>{edital.empresa || 'Não informada'}</p>
                    </div>
                    <div>
                      <h3 className="font-semibold">Categoria</h3>
                      <p>{edital.categoria || 'Não informada'}</p>
                    </div>
                    <div>
                      <h3 className="font-semibold">Data de Submissão</h3>
                      <p>{edital.data_fim_submissao || 'Não informada'}</p>
                    </div>
                    <div>
                      <h3 className="font-semibold">Contrapartida</h3>
                      <p>{edital.contrapartida || 'Não informada'}</p>
                    </div>
                  </div>
                  
                  <Button onClick={handleBaixarPdf} disabled={!edital.pdfLink}>
                    Baixar PDF
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <p>Nenhum edital selecionado</p>
          )}
        </div>
      )}
    </div>
  );
};

export default ExemploUsoHooks;
