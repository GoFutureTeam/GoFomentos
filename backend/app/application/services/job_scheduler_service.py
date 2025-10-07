"""
Job Scheduler Service - Agendamento e execução de jobs
"""
import asyncio
import uuid
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ...domain.entities.job_execution import JobExecution
from ...domain.repositories.job_repository import JobRepository
from ...domain.repositories.edital_repository import EditalRepository
from .cnpq_scraper_service import CNPqScraperService
from .fapesq_scraper_service import FapesqScraperService
from .openai_extractor_service import OpenAIExtractorService


class JobSchedulerService:
    """
    Serviço para agendamento e execução de jobs.
    Usa APScheduler para jobs agendados e execução assíncrona.
    """

    def __init__(
        self,
        job_repository: JobRepository,
        edital_repository: EditalRepository,
        cnpq_scraper_service: CNPqScraperService,
        fapesq_scraper_service: FapesqScraperService,
        openai_service: OpenAIExtractorService,
        pdf_processing_delay_ms: int = 1000
    ):
        """
        Inicializa o scheduler.

        Args:
            job_repository: Repositório de jobs
            edital_repository: Repositório de editais
            cnpq_scraper_service: Serviço de raspagem CNPq
            fapesq_scraper_service: Serviço de raspagem FAPESQ
            openai_service: Serviço de extração OpenAI
            pdf_processing_delay_ms: Delay entre processamento de PDFs
        """
        self.scheduler = AsyncIOScheduler()
        self.job_repo = job_repository
        self.edital_repo = edital_repository
        self.cnpq_scraper = cnpq_scraper_service
        self.fapesq_scraper = fapesq_scraper_service
        self.openai_service = openai_service
        self.running_jobs = {}  # Dicionário para controlar jobs em execução
        self.pdf_processing_delay_ms = pdf_processing_delay_ms

    def start(self):
        """
        Inicializa o scheduler e agenda o job diário.
        """
        # Agendar job diário às 01:00 AM
        self.scheduler.add_job(
            self._execute_cnpq_scraping_job,
            trigger=CronTrigger(hour=1, minute=0),
            id='cnpq_daily_scraping',
            name='CNPq Daily Scraping',
            replace_existing=True
        )

        self.scheduler.start()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Scheduler iniciado - Job agendado para 01:00 AM")

    def shutdown(self):
        """Para o scheduler"""
        self.scheduler.shutdown()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🛑 Scheduler encerrado")

    async def execute_cnpq_job_now(self) -> str:
        """
        Executa o job de raspagem CNPq AGORA (manualmente).

        Returns:
            str: ID do job criado
        """
        job_id = str(uuid.uuid4())

        # Criar execução no MongoDB
        execution = JobExecution.create(job_name="cnpq_scraping_manual")
        execution.id = job_id
        await self.job_repo.create(execution)

        # Executar em background
        asyncio.create_task(self._execute_job(job_id))

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Job CNPq manual iniciado: {job_id}")
        return job_id

    async def execute_fapesq_job_now(self, filter_by_date: bool = True) -> str:
        """
        Executa o job de raspagem FAPESQ AGORA (manualmente).

        Args:
            filter_by_date: Se True, filtra apenas editais com prazo >= hoje. Se False, retorna todos.

        Returns:
            str: ID do job criado
        """
        job_id = str(uuid.uuid4())

        # Criar execução no MongoDB
        execution = JobExecution.create(job_name="fapesq_scraping_manual")
        execution.id = job_id
        await self.job_repo.create(execution)

        # Executar em background
        asyncio.create_task(self._execute_fapesq_job(job_id, filter_by_date))

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Job FAPESQ manual iniciado: {job_id} (filter_by_date={filter_by_date})")
        return job_id

    # Manter compatibilidade com código antigo
    async def execute_job_now(self) -> str:
        """Executa job CNPq (alias para execute_cnpq_job_now)"""
        return await self.execute_cnpq_job_now()

    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancela um job em execução.

        Args:
            job_id: ID do job

        Returns:
            bool: True se cancelado com sucesso
        """
        if job_id in self.running_jobs:
            # Marcar para cancelamento
            self.running_jobs[job_id] = False

            # Atualizar no banco
            job = await self.job_repo.find_by_id(job_id)
            if job:
                job.cancel()
                await self.job_repo.update(job)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Job cancelado: {job_id}")
            return True

        return False

    async def _execute_cnpq_scraping_job(self):
        """
        Executa o job agendado (chamado pelo scheduler às 01:00 AM).
        """
        job_id = str(uuid.uuid4())

        # Criar execução no MongoDB
        execution = JobExecution.create(job_name="cnpq_scraping_scheduled")
        execution.id = job_id
        await self.job_repo.create(execution)

        # Executar
        await self._execute_job(job_id)

    async def _execute_job(self, job_id: str):
        """
        Lógica principal de execução do job.

        Args:
            job_id: ID do job
        """
        # Marcar como rodando
        self.running_jobs[job_id] = True

        try:
            # Buscar job
            job = await self.job_repo.find_by_id(job_id)
            if not job:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Job não encontrado: {job_id}")
                return

            # Iniciar job
            job.start()
            await self.job_repo.update(job)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ▶️ Iniciando raspagem CNPq...")

            # 1. Raspar CNPq
            urls = await self.cnpq_scraper.scrape_cnpq_chamadas()

            job.update_progress(0, len(urls))
            await self.job_repo.update(job)

            # 2. Processar cada URL
            for i, url in enumerate(urls, 1):
                # Verificar cancelamento
                if not self.running_jobs.get(job_id, True):
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏸️ Job cancelado pelo usuário")
                    break

                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📄 Processando edital {i}/{len(urls)}: {url}")

                try:
                    # Baixar e extrair PDF
                    texto = await self.cnpq_scraper.download_and_extract_pdf(url)

                    if not texto:
                        job.add_error(url, "Não foi possível extrair texto do PDF", 0)
                        await self.job_repo.update(job)
                        continue

                    # Gerar UUID para o edital
                    edital_uuid = str(uuid.uuid4())

                    # Extrair variáveis com OpenAI (salva progressivamente)
                    await self.openai_service.extract_variables_progressive(
                        text=texto,
                        edital_uuid=edital_uuid,
                        pdf_url=url
                    )

                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Edital processado com sucesso")

                except Exception as e:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao processar edital: {e}")
                    job.add_error(url, str(e), 0)
                    await self.job_repo.update(job)

                # Atualizar progresso
                job.update_progress(i, len(urls))
                await self.job_repo.update(job)

                # ⏱️ Delay entre PDFs para não sobrecarregar a event loop da API
                await asyncio.sleep(self.pdf_processing_delay_ms / 1000.0)

            # 3. Finalizar job
            job.complete()
            await self.job_repo.update(job)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Job concluído: {job_id}")
            print(f"    Processados: {job.processed_editais}/{job.total_editais}")
            print(f"    Erros: {job.failed_editais}")

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro crítico no job: {e}")

            job = await self.job_repo.find_by_id(job_id)
            if job:
                job.fail(str(e))
                await self.job_repo.update(job)

        finally:
            # Remover do dicionário de jobs rodando
            self.running_jobs.pop(job_id, None)

    async def _execute_fapesq_job(self, job_id: str, filter_by_date: bool = True):
        """
        Executa job de scraping FAPESQ em background.

        Args:
            job_id: ID do job
            filter_by_date: Se True, filtra apenas editais com prazo >= hoje
        """
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Job FAPESQ iniciado: {job_id}")

            # Buscar job do banco
            job = await self.job_repo.find_by_id(job_id)
            if not job:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Job não encontrado: {job_id}")
                return

            # Iniciar job
            job.start()
            await self.job_repo.update(job)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ▶️ Iniciando raspagem FAPESQ (filter_by_date={filter_by_date})...")

            # 1. Raspar FAPESQ
            editais_info = await self.fapesq_scraper.scrape_fapesq_editais(filter_by_date=filter_by_date)

            job.update_progress(0, len(editais_info))
            await self.job_repo.update(job)

            # 2. Processar cada edital
            for i, edital_info in enumerate(editais_info, 1):
                # Verificar cancelamento
                if not self.running_jobs.get(job_id, True):
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏸️ Job cancelado pelo usuário")
                    break

                pdf_url = edital_info['pdf_url']
                titulo = edital_info['titulo']

                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📄 Processando edital {i}/{len(editais_info)}: {titulo[:60]}...")

                try:
                    # Baixar e extrair PDF
                    texto = await self.fapesq_scraper.download_and_extract_pdf(pdf_url)

                    if not texto:
                        job.add_error(pdf_url, "Não foi possível extrair texto do PDF", 0)
                        await self.job_repo.update(job)
                        continue

                    # Gerar UUID para o edital
                    edital_uuid = str(uuid.uuid4())

                    # Extrair variáveis com OpenAI (salva progressivamente)
                    extracted = await self.openai_service.extract_variables_progressive(
                        text=texto,
                        edital_uuid=edital_uuid,
                        pdf_url=pdf_url
                    )

                    # Adicionar metadata extra do FAPESQ ao MongoDB
                    fapesq_metadata = {
                        'apelido_edital': titulo,
                        'descricao': edital_info.get('descricao'),
                        'data_limite': edital_info.get('data_limite').isoformat() if edital_info.get('data_limite') else None,
                        'data_publicacao': edital_info.get('data_publicacao').isoformat() if edital_info.get('data_publicacao') else None,
                        'financiador_1': 'FAPESQ-PB',
                        'origem': 'FAPESQ'
                    }

                    # Merge metadata extra e salvar novamente
                    merged_vars = {**extracted, **fapesq_metadata}
                    await self.edital_repo.save_final_extraction(
                        edital_uuid=edital_uuid,
                        consolidated_variables=merged_vars,
                        status="completed"
                    )

                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Edital processado com sucesso")

                except Exception as e:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao processar edital: {e}")
                    job.add_error(pdf_url, str(e), 0)
                    await self.job_repo.update(job)

                # Atualizar progresso
                job.update_progress(i, len(editais_info))
                await self.job_repo.update(job)

                # ⏱️ Delay entre PDFs para não sobrecarregar a event loop da API
                await asyncio.sleep(self.pdf_processing_delay_ms / 1000.0)

            # 3. Finalizar job
            job.complete()
            await self.job_repo.update(job)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Job FAPESQ concluído: {job_id}")
            print(f"    Processados: {job.processed_editais}/{job.total_editais}")
            print(f"    Erros: {job.failed_editais}")

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro crítico no job FAPESQ: {e}")

            job = await self.job_repo.find_by_id(job_id)
            if job:
                job.fail(str(e))
                await self.job_repo.update(job)

        finally:
            # Remover do dicionário de jobs rodando
            self.running_jobs.pop(job_id, None)
