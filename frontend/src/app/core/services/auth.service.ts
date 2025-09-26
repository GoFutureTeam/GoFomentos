import { Injectable, inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common'; // <-- 1. Importe a função
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, of, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private loggedIn: BehaviorSubject<boolean>;

  // 2. Injete o PLATFORM_ID para saber onde o código está rodando
  private platformId = inject(PLATFORM_ID);
  private router = inject(Router);

  constructor() {
    // 3. Inicialize o BehaviorSubject com o valor correto
    this.loggedIn = new BehaviorSubject<boolean>(this.hasToken());
  }

  /**
   * Verifica o token, mas apenas se estiver no navegador.
   */
  private hasToken(): boolean {
    if (isPlatformBrowser(this.platformId)) {
      // Se estiver no navegador, verifique o localStorage
      return !!localStorage.getItem('authToken');
    }
    // Se estiver no servidor, retorne 'false' por padrão
    return false;
  }

  get isLoggedIn(): Observable<boolean> {
    return this.loggedIn.asObservable();
  }

  /**
   * Pega o token do localStorage.
   */
  getToken(): string | null {
    if (isPlatformBrowser(this.platformId)) {
      return localStorage.getItem('authToken');
    }
    return null;
  }

  /**
   * Simula o processo de login.
   */
  login(email: string, password: string): Observable<any> {
    // Lógica de backend FAKE:
    if (email === 'teste@gofomentos.com' && password === '123456') {
      const fakeToken = 'meu-token-fake-123456';
      if (isPlatformBrowser(this.platformId)) {
        localStorage.setItem('authToken', fakeToken);
      }
      this.loggedIn.next(true);
      return of({ success: true, token: fakeToken });
    }
    return throwError(() => new Error('E-mail ou senha inválidos'));
  }

  /**
   * Simula o processo de registro.
   */
  register(name: string, email: string, password: string): Observable<any> {
    console.log('Usuário registrado (MOCK):', { name, email, password });
    return of({ success: true, message: 'Registro realizado com sucesso!' });
  }

  /**
   * Realiza o logout do usuário.
   */
  logout(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('authToken');
    }
    this.loggedIn.next(false);
    this.router.navigate(['/login']);
  }
}
// O auth.service.ts Conectado a um Backend Real
/*
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment'; // Para a URL da API

// Interfaces para tipagem forte das requisições e respostas
export interface AuthResponse {
  token: string;
  // Opcional: pode vir também com dados do usuário
  user?: {
    id: string;
    name: string;
    email: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  // 1. URL da nossa API (configurada nos environments)
  private apiUrl = environment.apiUrl + '/auth';

  private loggedIn = new BehaviorSubject<boolean>(this.hasToken());

  // 2. Injetamos o HttpClient para fazer as chamadas HTTP
  private http = inject(HttpClient);
  private router = inject(Router);

  constructor() { }

  private hasToken(): boolean {
    return !!localStorage.getItem('authToken');
  }

  get isLoggedIn(): Observable<boolean> {
    return this.loggedIn.asObservable();
  }

  /**
   * Pega o token do localStorage. Útil para o HttpInterceptor.

  getToken(): string | null {
    return localStorage.getItem('authToken');
  }

  /**
   * Realiza o login fazendo uma chamada POST para a API.

  login(email: string, password: string): Observable<AuthResponse> {
    // 3. Fazemos a chamada POST para o endpoint de login
    return this.http.post<AuthResponse>(`${this.apiUrl}/login`, { email, password }).pipe(
      // 4. Usamos o operador 'tap' para executar uma ação "paralela" quando a resposta chega
      tap(response => {
        if (response && response.token) {
          // Se a API retornar um token, nós o salvamos e atualizamos o estado
          localStorage.setItem('authToken', response.token);
          this.loggedIn.next(true);
        }
      })
    );
  }

  /**
   * Realiza o registro fazendo uma chamada POST para a API.

  register(name: string, email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, { name, email, password });
  }

  /**
   * A lógica de logout não muda, pois é uma operação do lado do cliente.

  logout(): void {
    localStorage.removeItem('authToken');
    this.loggedIn.next(false);
    this.router.navigate(['/login']);
  }
}
*/
