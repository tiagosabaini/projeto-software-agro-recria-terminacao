# 🐂 Sistema de Recria e Terminação Bovino

## 📌 Sobre o Projeto
O **Sistema de Recria e Terminação Bovino** é uma aplicação web desenvolvida em Flask/SQLite para a gestão zootécnica e financeira da pecuária de corte. Ele centraliza o fluxo produtivo: desde a aquisição e manejo nutricional de lotes até o ganho médio diário (GMD), simulação de cotações em frigoríficos e aferição de lucratividade real após o abate.

---

## 🛡️ Segurança da Informação (Tríade CID)

A aplicação implementa controles de segurança cobrindo os três pilares fundamentais da segurança da informação:

### 1. Confidencialidade
* **Criptografia de Senhas (Hashing):** As senhas dos usuários nunca são armazenadas em texto simples. Utiliza-se a biblioteca `werkzeug.security` com algoritmos de derivação de chaves seguros (scrypt/PBKDF2) com *salt* dinâmico.
* **Controle de Acesso Baseado em Papéis (RBAC):**
  * Perfil `comum` (Produtor Rural): Acesso operacional aos lotes, despesas, pesagens e painel financeiro.
  * Perfil `sysadmin` (Administrador): Acesso exclusivo à configuração e atualização de preços dos frigoríficos (`/admin_cotacoes`).
* **Proteção de Sessão:** Cookies de sessão configurados com `HttpOnly=True` e `SameSite=Lax` para mitigar ataques de sequestro de sessão (*Session Hijacking*).

### 2. Integridade
* **Proteção contra CSRF (Cross-Site Request Forgery):** Todas as requisições de alteração de estado (`POST`) exigem e validam um *token* criptográfico pseudo-aleatório gerado por sessão, rejeitando requisições forjadas de terceiros.
* **Validação de Entrada Server-Side:** Tratamento de tipos de dados numéricos (valores mínimos de arroba, cabeças e preços) em todas as rotas no backend antes da persistência.
* **Chaves Estrangeiras com Exclusão em Cascata (`PRAGMA foreign_keys = ON`):** Garantia de integridade referencial relacional entre lotes e seus registros filhos (despesas, pesagens e consumo).

### 3. Disponibilidade
* **Rotina de Backup Transacional (`gerar_dump.py`):** Script automatizado de geração de dump SQL da base de dados com carimbo temporal (`YYYYMMDD_HHMMSS`) e armazenamento versionado na pasta `backups/`, garantindo rápida recuperação em caso de falha operacional (*Disaster Recovery*).
* **Mitigação de Ataques de Força Bruta (Rate Limiting de Autenticação):** Bloqueio temporário de 5 minutos após 5 tentativas consecutivas de senha incorreta para prevenir ataques de dicionário.

### 🌐 Interoperabilidade da API (`/api/cotacoes`)
* **Decisão Arquitetural Consciente:** O endpoint `/api/cotacoes` foi propositalmente configurado como público para permitir a integração e consumo por sistemas de campo, balanças eletrônicas e painéis da fazenda sem necessidade de autenticação complexa, mantendo a proteção restrita à rota administrativa de gravação (`/admin_cotacoes`).

---

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3
* **Framework Web:** Flask 3.1.3
* **Banco de Dados:** SQLite3 (Relacional)
* **Frontend:** HTML5, CSS3 moderno, JavaScript (ES6)
* **Segurança:** Werkzeug Security, Secrets

---

## 👥 Integrantes
* Tiago Sabaini
* Jhenifer Alves
* Pedro Bueno
* Júllia Ketrin
* Lucas Daniel