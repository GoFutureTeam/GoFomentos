import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { EditaisProvider } from "./contexts/EditaisContext";
import { ProvedorAutenticacao } from "./contexts/ContextoAutenticacao";
import RotaProtegida from "./components/RotaProtegida";
import { ToastProvider } from "@/components/ui/toast-provider";
import Index from "./pages/Index";
import EditalDetails from "./pages/EditalDetails";
import Matchs from "./pages/Matchs";
import MatchResults from "./pages/MatchResults";
import EmailSignup from "./pages/EmailSignup";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login";
import Registro from "./pages/Registro";
import EsqueciSenha from "./pages/EsqueciSenha";
import MeusProjetos from "./pages/MeusProjetos";

const queryClient = new QueryClient();

const App = () => {
  // console.log('🚀 App iniciando...');

  try {
    return (
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <ProvedorAutenticacao>
            <EditaisProvider>
              <BrowserRouter>
                <Routes>
                  {/* Rotas Públicas - Apenas Login, Cadastro e Esqueci Senha */}
                  <Route path="/login" element={<Login />} />
                  <Route path="/registro" element={<Registro />} />
                  <Route path="/esqueci-senha" element={<EsqueciSenha />} />
                  <Route path="/recuperar-senha" element={<EsqueciSenha />} />
                  
                  {/* Rotas Protegidas (requerem autenticação) */}
                  <Route element={<RotaProtegida />}>
                    <Route path="/" element={<Index />} />
                    <Route path="/edital/:id" element={<EditalDetails />} />
                    <Route path="/meus-projetos" element={<MeusProjetos />} />
                    <Route path="/matchs" element={<Matchs />} />
                    <Route path="/match-results" element={<MatchResults />} />
                    <Route path="/email-signup" element={<EmailSignup />} />
                  </Route>
                  
                  {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </BrowserRouter>
            </EditaisProvider>
          </ProvedorAutenticacao>
        </ToastProvider>
      </QueryClientProvider>
    );
  } catch (error) {
    console.error('❌ Erro no App:', error);
    return <div>Erro ao carregar aplicação: {String(error)}</div>;
  }
};

export default App;
