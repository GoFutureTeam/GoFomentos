import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, map } from 'rxjs';
import { Edital } from '../models/edital.model'; // <-- Verifique se ele está importando o modelo

@Injectable({
  providedIn: 'root'
})
export class EditaisService {
  private http = inject(HttpClient);
  private mockApiUrl = 'assets/dataFAKE/editais.json'; // <-- Verifique o caminho do JSON

  private _allEditais$ = new BehaviorSubject<Edital[]>([]);
  public allEditais$: Observable<Edital[]> = this._allEditais$.asObservable();

  constructor() {
    this.fetchAllEditais().subscribe();
  }

  private fetchAllEditais(): Observable<Edital[]> {
    return this.http.get<Edital[]>(this.mockApiUrl).pipe(
      tap(editais => this._allEditais$.next(editais))
    );
  }

  getEditalById(id: string): Observable<Edital | undefined> {
    return this.allEditais$.pipe(
      map(editais => editais.find(e => e.id === id))
    );
  }
}
