export interface Edital {
  id: string;
  titulo: string;
  orgaoFomento: string;
  descricao: string;
  areaFoco: string;
  dataEncerramento: string; // Formato ISO: "AAAA-MM-DDTHH:mm:ssZ"
  valorDisponivel: number;
}
