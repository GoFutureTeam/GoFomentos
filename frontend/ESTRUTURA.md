# Estrutura Completa do Projeto

/frontend
├── .editorconfig                                            # Configurações do editor
├── .gitignore                                               # Arquivos ignorados pelo Git
├── angular.json                                             # Configurações do Angular CLI
├── package.json                                             # Dependências do projeto
├── README.md                                                # Documentação do projeto
├── tsconfig.app.json                                        # Configurações TypeScript para app
├── tsconfig.json                                            # Configurações TypeScript principais
├── tsconfig.spec.json                                       # Configurações TypeScript para testes
├── .vscode/
│   ├── extensions.json                                      # Extensões recomendadas VS Code
│   ├── launch.json                                          # Configurações de debug
│   └── tasks.json                                           # Tarefas VS Code
├── public/
│   └── favicon.ico                                          # Ícone da aplicação
└── src/
    ├── index.html                                           # Template HTML principal
    ├── main.server.ts                                       # Entrada do servidor (SSR)
    ├── main.ts                                              # Entrada principal da aplicação
    ├── server.ts                                            # Configuração do servidor
    ├── styles.scss                                          # Estilos globais da aplicação
    └── app/
        ├── app.component.html                               # Template do componente raiz
        ├── app.component.scss                               # Estilos do componente raiz
        ├── app.component.spec.ts                            # Testes do componente raiz
        ├── app.component.ts                                 # Componente raiz da aplicação
        ├── app.config.server.ts                             # Configuração do servidor
        ├── app.config.ts                                    # Configuração principal da app
        ├── app.routes.ts                                    # Definição das rotas
        ├── core/                                            # 🔧 CORE - Serviços Singleton, Models, Guards
        │   └── services/
        │       ├── auth.service.ts                          # ✅ Serviço de autenticação
        │       ├── editais.service.ts                       # ✅ Serviço de gestão de editais
        │       └── notification.service.ts                  # ✅ Serviço de notificações
        ├── pages/                                           # 📄 PAGES - Telas/Features principais
        │   ├── account/
        │   │   └── profile-page/
        │   │       ├── profile-page.component.html          # ✅ Template perfil usuário
        │   │       ├── profile-page.component.scss          # ✅ Estilos perfil usuário
        │   │       └── profile-page.component.ts            # ✅ Lógica perfil usuário
        │   ├── auth/
        │   │   ├── forgot-password-page/
        │   │   │   ├── forgot-password-page.component.html  # ✅ Template esqueci senha
        │   │   │   ├── forgot-password-page.component.scss  # ✅ Estilos esqueci senha
        │   │   │   └── forgot-password-page.component.ts    # ✅ Lógica esqueci senha
        │   │   ├── login-page/
        │   │   │   ├── login-page.component.html            # ✅ Template login
        │   │   │   ├── login-page.component.scss            # ✅ Estilos login
        │   │   │   └── login-page.component.ts              # ✅ Lógica login
        │   │   └── register-page/
        │   │       ├── register-page.component.html         # ✅ Template registro
        │   │       ├── register-page.component.scss         # ✅ Estilos registro
        │   │       └── register-page.component.ts           # ✅ Lógica registro
        │   ├── dashboard/
        │   │   └── dashboard-page/
        │   │       ├── dashboard-page.component.html        # ✅ Template dashboard
        │   │       ├── dashboard-page.component.scss        # ✅ Estilos dashboard
        │   │       └── dashboard-page.component.ts          # ✅ Lógica dashboard
        │   ├── editais/
        │   │   └── edital-search-page/
        │   │       ├── edital-search-page.component.html    # ✅ Template busca editais
        │   │       ├── edital-search-page.component.scss    # ✅ Estilos busca editais
        │   │       └── edital-search-page.component.ts      # ✅ Lógica busca editais
        │   └── projects/
        │       ├── project-form/
        │       │   ├── project-form.component.html          # ✅ Template formulário projeto
        │       │   ├── project-form.component.scss          # ✅ Estilos formulário projeto
        │       │   └── project-form.component.ts            # ✅ Lógica formulário projeto
        │       └── project-list-page/
        │           ├── project-list-page.component.html     # ✅ Template lista projetos
        │           ├── project-list-page.component.scss     # ✅ Estilos lista projetos
        │           └── project-list-page.component.ts       # ✅ Lógica lista projetos
        └── shared/                                          # 🔄 SHARED - Componentes Reutilizáveis
            ├── components/
            │   ├── button/
            │   │   ├── button.component.html               # ✅ Template botão reutilizável
            │   │   ├── button.component.scss               # ✅ Estilos botão reutilizável
            │   │   └── button.component.ts                 # ✅ Lógica botão reutilizável
            │   ├── edital-card/
            │   │   ├── edital-card.component.html          # ✅ Template card de edital
            │   │   ├── edital-card.component.scss          # ✅ Estilos card de edital
            │   │   └── edital-card.component.ts            # ✅ Lógica card de edital
            │   ├── filter-dropdown/
            │   │   ├── filter-dropdown.component.html      # ✅ Template dropdown filtros
            │   │   ├── filter-dropdown.component.scss      # ✅ Estilos dropdown filtros
            │   │   └── filter-dropdown.component.ts        # ✅ Lógica dropdown filtros
            │   ├── search-input/                           # ✅ Componente input de busca
            │   └── spinner/                                # ✅ Componente loading spinner
            └── layout/
                ├── footer/                                 # ✅ Pasta footer criada
                └── header/                                 # ✅ Pasta header criada
