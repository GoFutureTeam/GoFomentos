import React, { Component, ErrorInfo, ReactNode } from 'react';

/**
 * Error Boundary para capturar erros não tratados
 * 
 * Previne que toda a aplicação quebre por causa de um erro
 */

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('❌ Erro capturado pelo Error Boundary:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo,
    });

    // Aqui você pode enviar o erro para um serviço de monitoramento
    // Ex: Sentry, LogRocket, etc.
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
    
    // Recarregar a página
    window.location.href = '/';
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
            {/* Ícone de erro */}
            <div className="flex justify-center mb-4">
              <div className="bg-red-100 rounded-full p-3">
                <svg
                  className="w-12 h-12 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
            </div>

            {/* Mensagem */}
            <h2 className="text-2xl font-bold text-gray-900 text-center mb-2">
              Ops! Algo deu errado
            </h2>
            
            <p className="text-gray-600 text-center mb-6">
              Ocorreu um erro inesperado. Não se preocupe, já estamos trabalhando para resolver.
            </p>

            {/* Detalhes do erro (apenas em desenvolvimento) */}
            {import.meta.env.DEV && this.state.error && (
              <details className="mb-6 bg-gray-100 rounded p-4">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 mb-2">
                  Detalhes técnicos (dev)
                </summary>
                <pre className="text-xs text-red-600 overflow-auto max-h-40">
                  {this.state.error.toString()}
                  {'\n\n'}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}

            {/* Botão de reset */}
            <button
              onClick={this.handleReset}
              className="w-full px-6 py-3 bg-[#DCF763] text-[rgba(67,80,88,1)] rounded-lg hover:bg-[#DCF763]/90 transition-colors font-bold"
            >
              Voltar para o início
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
