import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { map, take } from 'rxjs/operators';

export const authGuard: CanActivateFn = (route, state) => {
  // Injetamos os serviços que precisamos
  const authService = inject(AuthService);
  const router = inject(Router);

  // Usamos o Observable isLoggedIn$ do nosso serviço
  return authService.isLoggedIn.pipe(
    take(1), // Pega apenas o valor mais recente do status de login e encerra
    map(isLoggedIn => {
      if (isLoggedIn) {
        return true; // Se o usuário está logado, permite o acesso à rota
      }

      // Se não estiver logado, redireciona para a página de login
      router.navigate(['/login']);
      return false; // E bloqueia o acesso à rota
    })
  );
};
