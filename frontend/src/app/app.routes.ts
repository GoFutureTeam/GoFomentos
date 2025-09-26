import { Routes } from '@angular/router';

// Imports dos componentes de página
import { LoginPageComponent } from './pages/auth/login-page/login-page.component';
import { RegisterPageComponent } from './pages/auth/register-page/register-page.component';
import { ForgotPasswordPageComponent } from './pages/auth/forgot-password-page/forgot-password-page.component';
import { EditalSearchPageComponent } from './pages/editais/edital-search-page/edital-search-page.component';
import { DashboardPageComponent } from './pages/dashboard/dashboard-page/dashboard-page.component';
import { ProjectListPageComponent } from './pages/projects/project-list-page/project-list-page.component';

// Import do guardião de rotas
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  // --- Rotas Públicas ---
  { path: 'login', component: LoginPageComponent }, // <-- Rota para o login
  { path: 'registro', component: RegisterPageComponent },
  { path: 'esqueci-minha-senha', component: ForgotPasswordPageComponent },

  // --- Rotas Protegidas ---
  {
    path: 'editais',
    component: EditalSearchPageComponent,
    canActivate: [authGuard]
  },
  {
    path: 'dashboard',
    component: DashboardPageComponent,
    canActivate: [authGuard]
  },
  {
    path: 'meus-projetos',
    component: ProjectListPageComponent,
    canActivate: [authGuard]
  },

  // --- Redirecionamentos ---
  // Se o usuário acessar a raiz do site, redirecione para a página de editais
  { path: '', redirectTo: '/editais', pathMatch: 'full' },

  // Se nenhuma rota for encontrada, redirecione para o login
  { path: '**', redirectTo: '/login' }
];
