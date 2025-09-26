import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map, of } from 'rxjs';
import { Projeto } from '../models/projeto'; 

@Injectable({
  providedIn: 'root'
})
export class ProjetosService {
  private http = inject(HttpClient);
  private mockApiUrl = 'assets/dataFAKE/projetos.json';

  constructor() { }

  /**
   * Busca os projetos pertencentes a um usuário específico.
   */
  getProjetosPorUsuario(usuarioId: string): Observable<Projeto[]> {
    return this.http.get<Projeto[]>(this.mockApiUrl).pipe(
      map(todosOsProjetos =>
        todosOsProjetos.filter(projeto => projeto.usuarioId === usuarioId)
      )
    );
  }

  /**
   * Simula a criação de um novo projeto.
   */
  criarProjeto(novoProjeto: Omit<Projeto, 'id'>): Observable<Projeto> {
    console.log('NOVO PROJETO (MOCK):', novoProjeto);
    const projetoCriado: Projeto = {
      id: `proj-${Math.random().toString(36).substring(2, 9)}`,
      ...novoProjeto
    };
    return of(projetoCriado);
  }
}
