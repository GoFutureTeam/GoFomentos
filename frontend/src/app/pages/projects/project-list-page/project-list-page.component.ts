import { Component, OnInit, inject } from '@angular/core';
import { CommonModule, CurrencyPipe } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Observable } from 'rxjs';
import { Projeto } from '../../../core/models/projeto';
import { ProjetosService } from '../../../core/services/projetos.service';

@Component({
  selector: 'app-project-list-page',
  standalone: true,
  // Adicionamos RouterModule para o futuro link do botão e CurrencyPipe para formatar o valor
  imports: [CommonModule, RouterModule, CurrencyPipe],
  templateUrl: './project-list-page.component.html',
  styleUrl: './project-list-page.component.scss'
})
export class ProjectListPageComponent implements OnInit {
  private projetosService = inject(ProjetosService);

  // Criamos um Observable para receber a lista de projetos
  public projetos$!: Observable<Projeto[]>;

  ngOnInit(): void {
    // MOCK: Em um app real, o ID do usuário viria do AuthService após o login.
    // Usamos o ID 'usr-abc-123' do nosso usuário de teste "Ana Silva" do arquivo usuarios.json.
    const usuarioLogadoId = 'usr-abc-123';

    // Chamamos o serviço para buscar os projetos deste usuário
    this.projetos$ = this.projetosService.getProjetosPorUsuario(usuarioLogadoId);
  }
}
