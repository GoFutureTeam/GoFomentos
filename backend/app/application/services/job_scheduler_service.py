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
from .paraiba_gov_scraper_service import ParaibaGovScraperService
from .confap_scraper_service import ConfapScraperService
from .capes_scraper_service import CapesScraperService
from .finep_scraper_service import FinepScraperService
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
        paraiba_gov_scraper_service: ParaibaGovScraperService,
        confap_scraper_service: ConfapScraperService,
        capes_scraper_service: CapesScraperService,
        finep_scraper_service: FinepScraperService,
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
            paraiba_gov_scraper_service: Serviço de raspagem Paraíba Gov
            confap_scraper_service: Serviço de raspagem CONFAP
            capes_scraper_service: Serviço de raspagem CAPES
            finep_scraper_service: Serviço de raspagem FINEP
            openai_service: Serviço de extração OpenAI
            pdf_processing_delay_ms: Delay entre processamento de PDFs
        """
        self.scheduler = AsyncIOScheduler()
        self.job_repo = job_repository
        self.edital_repo = edital_repository
        self.cnpq_scraper = cnpq_scraper_service
        self.fapesq_scraper = fapesq_scraper_service
        self.paraiba_gov_scraper = paraiba_gov_scraper_service
        self.confap_scraper = confap_scraper_service
        self.capes_scraper = capes_scraper_service
        self.finep_scraper = finep_scraper_service
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

    async def execute_paraiba_gov_job_now(self, filter_by_date: bool = True) -> str:
        """
        Executa o job de raspagem Paraíba Gov AGORA (manualmente).

        Args:
            filter_by_date: Se True, filtra apenas editais com prazo >= hoje. Se False, retorna todos.

        Returns:
            str: ID do job criado
        """
        job_id = str(uuid.uuid4())

        # Criar execução no MongoDB
        execution = JobExecution.create(job_name="paraiba_gov_scraping_manual")
        execution.id = job_id
        await self.job_repo.create(execution)

        # Executar em background
        asyncio.create_task(self._execute_paraiba_gov_job(job_id, filter_by_date))

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Job Paraíba Gov manual iniciado: {job_id} (filter_by_date={filter_by_date})")
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

    async def _execute_paraiba_gov_job(self, job_id: str, filter_by_date: bool = True):
        """
        Executa job de scraping Paraíba Gov em background.

        Args:
            job_id: ID do job
            filter_by_date: Se True, filtra apenas editais com prazo >= hoje
        """
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Job Paraíba Gov iniciado: {job_id}")

            # Buscar job do banco
            job = await self.job_repo.find_by_id(job_id)
            if not job:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Job não encontrado: {job_id}")
                return

            # Iniciar job
            job.start()
            await self.job_repo.update(job)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ▶️ Iniciando raspagem Paraíba Gov (filter_by_date={filter_by_date})...")

            # 1. Raspar Paraíba Gov
            editais_info = await self.paraiba_gov_scraper.scrape_paraiba_gov_editais(filter_by_date=filter_by_date)

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
                    texto = await self.paraiba_gov_scraper.download_and_extract_pdf(pdf_url)

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

                    # Adicionar metadata extra do Paraíba Gov ao MongoDB
                    paraiba_gov_metadata = {
                        'apelido_edital': titulo,
                        'descricao': edital_info.get('descricao'),
                        'data_limite': edital_info.get('data_limite').isoformat() if edital_info.get('data_limite') else None,
                        'financiador_1': 'Governo da Paraíba - SECTIES',
                        'origem': 'Paraíba Gov'
                    }

                    # Merge metadata extra e salvar novamente
                    merged_vars = {**extracted, **paraiba_gov_metadata}
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

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Job Paraíba Gov concluído: {job_id}")
            print(f"    Processados: {job.processed_editais}/{job.total_editais}")
            print(f"    Erros: {job.failed_editais}")

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro crítico no job Paraíba Gov: {e}")

            job = await self.job_repo.find_by_id(job_id)
            if job:
                job.fail(str(e))
                await self.job_repo.update(job)

        finally:
            # Remover do dicionário de jobs rodando
            self.running_jobs.pop(job_id, None)

    async def execute_confap_job_now(self, filter_by_date: bool = True) -> str:
        """
        Executa o job de raspagem CONFAP AGORA (manualmente).

        Args:
            filter_by_date: Se True, filtra apenas editais com ano >= ano atual. Se False, retorna todos.

        Returns:
            str: ID do job criado
        """
        job_id = str(uuid.uuid4())

        # Criar execução no MongoDB
        execution = JobExecution.create(job_name="confap_scraping_manual")
        execution.id = job_id
        await self.job_repo.create(execution)

        # Executar em background
        asyncio.create_task(self._execute_confap_job(job_id, filter_by_date))

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Job CONFAP manual iniciado: {job_id} (filter_by_date={filter_by_date})")
        return job_id

    async def _execute_confap_job(self, job_id: str, filter_by_date: bool = True):
        """
        Executa job de scraping CONFAP em background.

        Args:
            job_id: ID do job
            filter_by_date: Se True, filtra apenas editais com ano >= ano atual
        """
        # Marcar como rodando
        self.running_jobs[job_id] = True

        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Job CONFAP iniciado: {job_id}")

            # Buscar job do banco
            job = await self.job_repo.find_by_id(job_id)
            if not job:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Job não encontrado: {job_id}")
                return

            # Iniciar job
            job.start()
            await self.job_repo.update(job)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ▶️ Iniciando raspagem CONFAP (filter_by_date={filter_by_date})...")

            # 1. Raspar CONFAP (obter lista de editais)
            editais_info = await self.confap_scraper.scrape_confap_editais(filter_by_date=filter_by_date)

            # Contador de PDFs totais (será atualizado conforme encontramos PDFs)
            total_pdfs = 0
            processed_pdfs = 0

            # 2. Para cada edital, extrair links de download
            for i, edital_info in enumerate(editais_info, 1):
                # Verificar cancelamento
                if not self.running_jobs.get(job_id, True):
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏸️ Job cancelado pelo usuário")
                    break

                detail_url = edital_info['url']
                titulo = edital_info['titulo']

                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📋 Processando edital {i}/{len(editais_info)}: {titulo[:60]}...")

                try:
                    # Extrair links de download da página de detalhes
                    download_links = await self.confap_scraper.extract_download_links(detail_url)

                    if not download_links:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Nenhum link de download encontrado para este edital")
                        job.add_error(detail_url, "Nenhum link de download encontrado", 0)
                        await self.job_repo.update(job)
                        continue

                    # Atualizar total de PDFs
                    total_pdfs += len(download_links)
                    job.update_progress(processed_pdfs, total_pdfs)
                    await self.job_repo.update(job)

                    # 3. Processar cada PDF encontrado
                    for pdf_idx, pdf_url in enumerate(download_links, 1):
                        # Verificar cancelamento
                        if not self.running_jobs.get(job_id, True):
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏸️ Job cancelado pelo usuário")
                            break

                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📄 Baixando PDF {pdf_idx}/{len(download_links)}: {pdf_url}")

                        try:
                            # Baixar e extrair PDF
                            texto = await self.confap_scraper.download_and_extract_pdf(pdf_url)

                            if not texto:
                                job.add_error(pdf_url, "Não foi possível extrair texto do PDF", 0)
                                await self.job_repo.update(job)
                                processed_pdfs += 1
                                job.update_progress(processed_pdfs, total_pdfs)
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

                            # Adicionar metadata extra do CONFAP ao MongoDB
                            confap_metadata = {
                                'apelido_edital': titulo,
                                'url_detalhes': detail_url,
                                'status': edital_info.get('status', 'Em andamento'),
                                'ano': edital_info.get('ano'),
                                'financiador_1': 'CONFAP',
                                'origem': 'CONFAP'
                            }

                            # Merge metadata extra e salvar novamente
                            merged_vars = {**extracted, **confap_metadata}
                            await self.edital_repo.save_final_extraction(
                                edital_uuid=edital_uuid,
                                consolidated_variables=merged_vars,
                                status="completed"
                            )

                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ PDF processado com sucesso")

                        except Exception as e:
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao processar PDF: {e}")
                            job.add_error(pdf_url, str(e), 0)
                            await self.job_repo.update(job)

                        # Atualizar progresso
                        processed_pdfs += 1
                        job.update_progress(processed_pdfs, total_pdfs)
                        await self.job_repo.update(job)

                        # ⏱️ Delay entre PDFs para não sobrecarregar a event loop da API
                        await asyncio.sleep(self.pdf_processing_delay_ms / 1000.0)

                except Exception as e:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao processar edital: {e}")
                    job.add_error(detail_url, str(e), 0)
                    await self.job_repo.update(job)

            # 4. Finalizar job
            job.complete()
            await self.job_repo.update(job)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Job CONFAP concluído: {job_id}")
            print(f"    Processados: {job.processed_editais}/{job.total_editais}")
            print(f"    Erros: {job.failed_editais}")

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro crítico no job CONFAP: {e}")

            job = await self.job_repo.find_by_id(job_id)
            if job:
                job.fail(str(e))
                await self.job_repo.update(job)

        finally:
            # Remover do dicionário de jobs rodando
            self.running_jobs.pop(job_id, None)

    async def execute_capes_job_now(self, filter_by_date: bool = True) -> str:
        """
        Executa o job de raspagem CAPES AGORA (manualmente).

        Args:
            filter_by_date: Se True, filtra apenas chamadas com ano >= ano atual. Se False, retorna todos.

        Returns:
            str: ID do job criado
        """
        job_id = str(uuid.uuid4())

        # Criar execução no MongoDB
        execution = JobExecution.create(job_name="capes_scraping_manual")
        execution.id = job_id
        await self.job_repo.create(execution)

        # Executar em background
        asyncio.create_task(self._execute_capes_job(job_id, filter_by_date))

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Job CAPES manual iniciado: {job_id} (filter_by_date={filter_by_date})")
        return job_id

    async def _execute_capes_job(self, job_id: str, filter_by_date: bool = True):
        """
        Executa job de scraping CAPES em background.

        Args:
            job_id: ID do job
            filter_by_date: Se True, filtra apenas chamadas com ano >= ano atual
        """
        # Marcar como rodando
        self.running_jobs[job_id] = True

        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Job CAPES iniciado: {job_id}")

            # Buscar job do banco
            job = await self.job_repo.find_by_id(job_id)
            if not job:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Job não encontrado: {job_id}")
                return

            # Iniciar job
            job.start()
            await self.job_repo.update(job)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ▶️ Iniciando raspagem CAPES (filter_by_date={filter_by_date})...")

            # 1. Raspar CAPES (obter lista de chamadas com PDFs)
            chamadas_info = await self.capes_scraper.scrape_capes_chamadas(filter_by_date=filter_by_date)

            # Contador de PDFs totais
            total_pdfs = sum(len(chamada['pdf_urls']) for chamada in chamadas_info)
            processed_pdfs = 0

            job.update_progress(processed_pdfs, total_pdfs)
            await self.job_repo.update(job)

            # 2. Para cada chamada, processar seus PDFs
            for i, chamada_info in enumerate(chamadas_info, 1):
                # Verificar cancelamento
                if not self.running_jobs.get(job_id, True):
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏸️ Job cancelado pelo usuário")
                    break

                titulo = chamada_info['titulo']
                pdf_urls = chamada_info['pdf_urls']
                ano = chamada_info['ano']

                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📋 Processando chamada {i}/{len(chamadas_info)}: {titulo[:60]}... ({len(pdf_urls)} PDFs)")

                # 3. Processar cada PDF da chamada
                for pdf_idx, pdf_url in enumerate(pdf_urls, 1):
                    # Verificar cancelamento
                    if not self.running_jobs.get(job_id, True):
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏸️ Job cancelado pelo usuário")
                        break

                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📄 Baixando PDF {pdf_idx}/{len(pdf_urls)}: {pdf_url}")

                    try:
                        # Baixar e extrair PDF
                        texto = await self.capes_scraper.download_and_extract_pdf(pdf_url)

                        if not texto:
                            job.add_error(pdf_url, "Não foi possível extrair texto do PDF", 0)
                            await self.job_repo.update(job)
                            processed_pdfs += 1
                            job.update_progress(processed_pdfs, total_pdfs)
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

                        # Adicionar metadata extra da CAPES ao MongoDB
                        capes_metadata = {
                            'apelido_edital': titulo,
                            'ano': ano,
                            'financiador_1': 'CAPES',
                            'origem': 'CAPES'
                        }

                        # Merge metadata extra e salvar novamente
                        merged_vars = {**extracted, **capes_metadata}
                        await self.edital_repo.save_final_extraction(
                            edital_uuid=edital_uuid,
                            consolidated_variables=merged_vars,
                            status="completed"
                        )

                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ PDF processado com sucesso")

                    except Exception as e:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao processar PDF: {e}")
                        job.add_error(pdf_url, str(e), 0)
                        await self.job_repo.update(job)

                    # Atualizar progresso
                    processed_pdfs += 1
                    job.update_progress(processed_pdfs, total_pdfs)
                    await self.job_repo.update(job)

                    # ⏱️ Delay entre PDFs para não sobrecarregar a event loop da API
                    await asyncio.sleep(self.pdf_processing_delay_ms / 1000.0)

            # 4. Finalizar job
            job.complete()
            await self.job_repo.update(job)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Job CAPES concluído: {job_id}")
            print(f"    Processados: {job.processed_editais}/{job.total_editais}")
            print(f"    Erros: {job.failed_editais}")

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro crítico no job CAPES: {e}")

            job = await self.job_repo.find_by_id(job_id)
            if job:
                job.fail(str(e))
                await self.job_repo.update(job)

        finally:
            # Remover do dicionário de jobs rodando
            self.running_jobs.pop(job_id, None)

    async def execute_finep_job_now(self, filter_by_date: bool = True) -> str:
        """
        Executa o job de raspagem FINEP AGORA (manualmente).

        Args:
            filter_by_date: Se True, filtra apenas chamadas com data >= hoje. Se False, retorna todos.

        Returns:
            str: ID do job criado
        """
        job_id = str(uuid.uuid4())

        # Criar execução no MongoDB
        execution = JobExecution.create(job_name="finep_scraping_manual")
        execution.id = job_id
        await self.job_repo.create(execution)

        # Executar em background
        asyncio.create_task(self._execute_finep_job(job_id, filter_by_date))

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Job FINEP manual iniciado: {job_id} (filter_by_date={filter_by_date})")
        return job_id

    async def _execute_finep_job(self, job_id: str, filter_by_date: bool = True):
        """
        Executa job de scraping FINEP em background.

        Args:
            job_id: ID do job
            filter_by_date: Se True, filtra apenas chamadas com data >= hoje
        """
        # Marcar como rodando
        self.running_jobs[job_id] = True

        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Job FINEP iniciado: {job_id}")

            # Buscar job do banco
            job = await self.job_repo.find_by_id(job_id)
            if not job:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Job não encontrado: {job_id}")
                return

            # Iniciar job
            job.start()
            await self.job_repo.update(job)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ▶️ Iniciando raspagem FINEP (filter_by_date={filter_by_date})...")

            # 1. Raspar FINEP (obter lista de chamadas abertas)
            chamadas_info = await self.finep_scraper.scrape_finep_chamadas(filter_by_date=filter_by_date)

            # Contador de PDFs totais (será atualizado conforme encontramos PDFs)
            total_pdfs = 0
            processed_pdfs = 0

            # 2. Para cada chamada, extrair links de PDFs
            for i, chamada_info in enumerate(chamadas_info, 1):
                # Verificar cancelamento
                if not self.running_jobs.get(job_id, True):
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏸️ Job cancelado pelo usuário")
                    break

                detail_url = chamada_info['url']
                titulo = chamada_info['titulo']

                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📋 Processando chamada {i}/{len(chamadas_info)}: {titulo[:60]}...")

                try:
                    # Extrair links de PDFs da página de detalhes
                    pdf_links = await self.finep_scraper.extract_pdf_links(detail_url)

                    if not pdf_links:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Nenhum PDF encontrado para esta chamada")
                        job.add_error(detail_url, "Nenhum PDF encontrado", 0)
                        await self.job_repo.update(job)
                        continue

                    # Atualizar total de PDFs
                    total_pdfs += len(pdf_links)
                    job.update_progress(processed_pdfs, total_pdfs)
                    await self.job_repo.update(job)

                    # 3. Processar cada PDF encontrado
                    for pdf_idx, pdf_url in enumerate(pdf_links, 1):
                        # Verificar cancelamento
                        if not self.running_jobs.get(job_id, True):
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏸️ Job cancelado pelo usuário")
                            break

                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📄 Baixando PDF {pdf_idx}/{len(pdf_links)}: {pdf_url}")

                        try:
                            # Baixar e extrair PDF
                            texto = await self.finep_scraper.download_and_extract_pdf(pdf_url)

                            if not texto:
                                job.add_error(pdf_url, "Não foi possível extrair texto do PDF", 0)
                                await self.job_repo.update(job)
                                processed_pdfs += 1
                                job.update_progress(processed_pdfs, total_pdfs)
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

                            # Adicionar metadata extra da FINEP ao MongoDB
                            finep_metadata = {
                                'apelido_edital': titulo,
                                'url_detalhes': detail_url,
                                'data_limite': chamada_info.get('data_limite').isoformat() if chamada_info.get('data_limite') else None,
                                'financiador_1': 'FINEP',
                                'origem': 'FINEP'
                            }

                            # Merge metadata extra e salvar novamente
                            merged_vars = {**extracted, **finep_metadata}
                            await self.edital_repo.save_final_extraction(
                                edital_uuid=edital_uuid,
                                consolidated_variables=merged_vars,
                                status="completed"
                            )

                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ PDF processado com sucesso")

                        except Exception as e:
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao processar PDF: {e}")
                            job.add_error(pdf_url, str(e), 0)
                            await self.job_repo.update(job)

                        # Atualizar progresso
                        processed_pdfs += 1
                        job.update_progress(processed_pdfs, total_pdfs)
                        await self.job_repo.update(job)

                        # ⏱️ Delay entre PDFs para não sobrecarregar a event loop da API
                        await asyncio.sleep(self.pdf_processing_delay_ms / 1000.0)

                except Exception as e:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao processar chamada: {e}")
                    job.add_error(detail_url, str(e), 0)
                    await self.job_repo.update(job)

            # 4. Finalizar job
            job.complete()
            await self.job_repo.update(job)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Job FINEP concluído: {job_id}")
            print(f"    Processados: {job.processed_editais}/{job.total_editais}")
            print(f"    Erros: {job.failed_editais}")

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro crítico no job FINEP: {e}")

            job = await self.job_repo.find_by_id(job_id)
            if job:
                job.fail(str(e))
                await self.job_repo.update(job)

        finally:
            # Remover do dicionário de jobs rodando
            self.running_jobs.pop(job_id, None)
