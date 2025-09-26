import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { Usuario } from '../models/usuario'; 

@Injectable({
  providedIn: 'root'
})
export class UsuariosService {
  private http = inject(HttpClient);
  private mockApiUrl = 'assets/dataFAKE/usuarios.json';

  constructor() { }

  /**
   * Simula a busca do perfil do usuário atualmente logado.
   */
  getPerfilUsuarioLogado(): Observable<Usuario | undefined> {
    // MOCK: Em um app real, o ID do usuário viria do AuthService após o login.
    // Aqui, estamos fixando o ID de um dos nossos usuários falsos.
    const usuarioLogadoId = 'usr-abc-123';

    return this.http.get<Usuario[]>(this.mockApiUrl).pipe(
      map(usuarios => usuarios.find(u => u.id === usuarioLogadoId))
    );
  }
}
