/**
 * Script para refatoração automática da nomenclatura do projeto GoFomentos
 * 
 * Este script ajuda a padronizar a nomenclatura do projeto, seguindo as convenções
 * definidas em CONVENÇÕES_NOMENCLATURA.md
 * 
 * Uso: node refatorar-nomenclatura.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Mapeamento de nomes antigos para novos nomes
const MAPEAMENTO_ARQUIVOS = {
  // Componentes
  'EditalCard.tsx': 'CardEdital.tsx',
  'FilterDropdown.tsx': 'DropdownFiltro.tsx',
  'FilterSection.tsx': 'SecaoFiltro.tsx',
  'SearchInput.tsx': 'InputBusca.tsx',
  'SuccessMessage.tsx': 'MensagemSucesso.tsx',
  'HeroSection.tsx': 'SecaoDestaque.tsx',
  'InfoSection.tsx': 'SecaoInfo.tsx',
  
  // Hooks
  'useEditais.ts': 'usarEditais.ts',
  'useEditaisAdvanced.ts': 'usarEditaisAvancado.ts',
  'useEditaisContext.ts': 'usarContextoEditais.ts',
  'useMatching.ts': 'usarCorrespondencia.ts',
  'use-toast.ts': 'usarToast.ts',
  'use-mobile.tsx': 'usarMobile.tsx',
  
  // Serviços
  'editalApi.ts': 'apiEdital.ts',
  
  // Contextos
  'EditaisContext.tsx': 'ContextoEditais.tsx',
  'EditaisContextCreator.ts': 'CriadorContextoEditais.ts',
  'EditaisContextTypes.ts': 'TiposContextoEditais.ts',
  
  // Páginas
  'EditalDetails.tsx': 'DetalhesEdital.tsx',
  'EmailSignup.tsx': 'CadastroEmail.tsx',
  'MatchResults.tsx': 'ResultadosCorrespondencia.tsx',
  'Matchs.tsx': 'Correspondencias.tsx',
};

// Mapeamento de nomes de funções/métodos
const MAPEAMENTO_FUNCOES = {
  // Hooks
  'useEditais': 'usarEditais',
  'useEditaisAdvanced': 'usarEditaisAvancado',
  'useEditaisContext': 'usarContextoEditais',
  'useMatching': 'usarCorrespondencia',
  
  // Métodos de API
  'listEditais': 'listarEditais',
  'getEdital': 'obterEdital',
  'getEditalByApelido': 'obterEditalPorApelido',
  'createEdital': 'criarEdital',
  'updateEdital': 'atualizarEdital',
  'updatePdf': 'atualizarPdf',
  'deleteEdital': 'deletarEdital',
  'checkPdfExists': 'verificarExistenciaPdf',
  'downloadPdf': 'baixarPdf',
  'downloadPdfByApelido': 'baixarPdfPorApelido',
  
  // Componentes
  'EditalCard': 'CardEdital',
  'FilterDropdown': 'DropdownFiltro',
  'FilterSection': 'SecaoFiltro',
  'SearchInput': 'InputBusca',
  'SuccessMessage': 'MensagemSucesso',
  'HeroSection': 'SecaoDestaque',
  'InfoSection': 'SecaoInfo',
  
  // Contextos
  'EditaisContext': 'ContextoEditais',
  'EditaisProvider': 'ProvedorEditais',
};

// Diretório raiz do projeto
const DIR_RAIZ = path.resolve(__dirname, '..');
const DIR_SRC = path.join(DIR_RAIZ, 'src');

/**
 * Renomeia arquivos de acordo com o mapeamento
 */
function renomearArquivos() {
  console.log('Renomeando arquivos...');
  
  Object.entries(MAPEAMENTO_ARQUIVOS).forEach(([nomeAntigo, nomeNovo]) => {
    // Buscar o arquivo em todos os subdiretórios
    const resultado = buscarArquivo(DIR_SRC, nomeAntigo);
    
    if (resultado) {
      const caminhoAntigo = resultado;
      const caminhoNovo = path.join(path.dirname(caminhoAntigo), nomeNovo);
      
      try {
        // Verificar se o arquivo de destino já existe
        if (!fs.existsSync(caminhoNovo)) {
          fs.renameSync(caminhoAntigo, caminhoNovo);
          console.log(`✅ Renomeado: ${caminhoAntigo} -> ${caminhoNovo}`);
        } else {
          console.log(`⚠️ Arquivo já existe: ${caminhoNovo}`);
        }
      } catch (erro) {
        console.error(`❌ Erro ao renomear ${caminhoAntigo}: ${erro.message}`);
      }
    } else {
      console.log(`⚠️ Arquivo não encontrado: ${nomeAntigo}`);
    }
  });
}

/**
 * Busca um arquivo em um diretório e seus subdiretórios
 */
function buscarArquivo(diretorio, nomeArquivo) {
  const arquivos = fs.readdirSync(diretorio);
  
  for (const arquivo of arquivos) {
    const caminhoCompleto = path.join(diretorio, arquivo);
    const stat = fs.statSync(caminhoCompleto);
    
    if (stat.isDirectory()) {
      const resultado = buscarArquivo(caminhoCompleto, nomeArquivo);
      if (resultado) return resultado;
    } else if (arquivo === nomeArquivo) {
      return caminhoCompleto;
    }
  }
  
  return null;
}

/**
 * Atualiza referências nos arquivos
 */
function atualizarReferencias() {
  console.log('Atualizando referências...');
  
  // Encontrar todos os arquivos .ts e .tsx
  const arquivos = encontrarArquivosPorExtensao(DIR_SRC, ['.ts', '.tsx']);
  
  arquivos.forEach(arquivo => {
    if (arquivo.endsWith('.d.ts')) return; // Pular arquivos de declaração
    
    let conteudo = fs.readFileSync(arquivo, 'utf8');
    let modificado = false;
    
    // Atualizar importações de arquivos
    Object.entries(MAPEAMENTO_ARQUIVOS).forEach(([nomeAntigo, nomeNovo]) => {
      const nomeAntigoSemExt = nomeAntigo.replace(/\.[^/.]+$/, '');
      const nomeNovoSemExt = nomeNovo.replace(/\.[^/.]+$/, '');
      
      // Padrão para importações
      const padraoImport = new RegExp(`from ['"](.*?/${nomeAntigoSemExt})['"]`, 'g');
      const novoImport = (match, p1) => `from '${p1.replace(nomeAntigoSemExt, nomeNovoSemExt)}'`;
      
      const novoConteudo = conteudo.replace(padraoImport, novoImport);
      if (novoConteudo !== conteudo) {
        conteudo = novoConteudo;
        modificado = true;
      }
    });
    
    // Atualizar nomes de funções/métodos
    Object.entries(MAPEAMENTO_FUNCOES).forEach(([nomeAntigo, nomeNovo]) => {
      // Diferentes padrões para capturar o nome da função em diferentes contextos
      const padroes = [
        new RegExp(`\\b${nomeAntigo}\\(`, 'g'), // Chamada de função: nomeAntigo(
        new RegExp(`\\b${nomeAntigo}\\s*=\\s*\\(`, 'g'), // Definição de função: nomeAntigo = (
        new RegExp(`\\bconst\\s+${nomeAntigo}\\s*=`, 'g'), // Declaração de constante: const nomeAntigo =
        new RegExp(`\\bfunction\\s+${nomeAntigo}\\s*\\(`, 'g'), // Declaração de função: function nomeAntigo(
        new RegExp(`\\bimport\\s+{[^}]*\\b${nomeAntigo}\\b[^}]*}\\s+from`, 'g'), // Import: import { nomeAntigo } from
        new RegExp(`\\bexport\\s+const\\s+${nomeAntigo}\\s*=`, 'g'), // Export const: export const nomeAntigo =
        new RegExp(`\\bexport\\s+function\\s+${nomeAntigo}\\s*\\(`, 'g'), // Export function: export function nomeAntigo(
      ];
      
      padroes.forEach(padrao => {
        const novoConteudo = conteudo.replace(padrao, match => match.replace(nomeAntigo, nomeNovo));
        if (novoConteudo !== conteudo) {
          conteudo = novoConteudo;
          modificado = true;
        }
      });
    });
    
    // Salvar arquivo se foi modificado
    if (modificado) {
      fs.writeFileSync(arquivo, conteudo, 'utf8');
      console.log(`✅ Atualizado: ${arquivo}`);
    }
  });
}

/**
 * Encontra arquivos com determinadas extensões em um diretório e seus subdiretórios
 */
function encontrarArquivosPorExtensao(diretorio, extensoes) {
  let resultado = [];
  
  const arquivos = fs.readdirSync(diretorio);
  
  for (const arquivo of arquivos) {
    const caminhoCompleto = path.join(diretorio, arquivo);
    const stat = fs.statSync(caminhoCompleto);
    
    if (stat.isDirectory()) {
      resultado = resultado.concat(encontrarArquivosPorExtensao(caminhoCompleto, extensoes));
    } else if (extensoes.some(ext => arquivo.endsWith(ext))) {
      resultado.push(caminhoCompleto);
    }
  }
  
  return resultado;
}

/**
 * Função principal
 */
function main() {
  console.log('Iniciando refatoração de nomenclatura...');
  
  // Criar backup antes de começar
  console.log('Criando backup...');
  const dataHora = new Date().toISOString().replace(/[:.]/g, '-');
  const backupDir = path.join(DIR_RAIZ, `backup-${dataHora}`);
  
  try {
    fs.mkdirSync(backupDir);
    execSync(`xcopy "${DIR_SRC}" "${backupDir}\\src\\" /E /I /H`);
    console.log(`✅ Backup criado em: ${backupDir}`);
  } catch (erro) {
    console.error(`❌ Erro ao criar backup: ${erro.message}`);
    return;
  }
  
  // Executar refatoração
  try {
    atualizarReferencias();
    renomearArquivos();
    console.log('✅ Refatoração concluída com sucesso!');
  } catch (erro) {
    console.error(`❌ Erro durante a refatoração: ${erro.message}`);
    console.log(`Você pode restaurar o backup de: ${backupDir}`);
  }
}

// Executar o script
main();
