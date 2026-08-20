# 🐂 Sistema de Recria e Terminação Bovino

## 📌 Sobre o Projeto
O Sistema de Recria e Terminação Bovino é uma solução para o agronegócio focada no gerenciamento financeiro e zootécnico da pecuária de corte. O sistema resolve a falta de previsibilidade do produtor rural, permitindo o controle preciso do custo por arroba (@) produzida e ajudando a evitar a comercialização de lotes no prejuízo.

## 🚀 Funcionalidades Principais
* Gestão de Lotes: Cadastro de lotes, datas e acompanhamento da fase atual.
* Controle de Despesas: Lançamento e categorização de custos segregados por fase (Recria e Terminação).
* Acompanhamento de Pesagens: Histórico de pesagens com cálculo automático de Ganho Médio Diário (GMD).
* Painel de Viabilidade: Indicador em tempo real do custo da arroba ganha e projeção de lucratividade com base na cotação do mercado.

## 🛠️ Tecnologias Utilizadas
* Linguagem: Python 3 e JavaScript
* Framework Web: Flask
* Banco de Dados: SQLite
* Frontend: HTML5, CSS3, Jinja2

## 👥 Integrantes do Grupo
* Tiago Sabaini - (GitHub: @tiagosabaini)
* Jhenifer Alves - (GitHub: @jheniiiialvesss)
* Pedro Bueno - (GitHub: @pedronosrinsk)
* Júllia Ketrin - (GitHub: @JeiKeiRambo)
* Lucas Daniel - (GitHub: @KourtneK)

## 📐 Arquitetura do Sistema e Fluxos
O projeto conta com diagramas PlantUML (`.puml`) para documentação visual do banco de dados e das regras de negócio:

* **Modelagem do Banco de Dados (`banco_dados.puml`):** Mapeamento e relacionamento das tabelas SQLite (`lotes`, `despesas`, `pesagens`).
 <img width="590" height="297" alt="image" src="https://github.com/user-attachments/assets/3fc52491-e772-42d8-9936-7dc8b96b2cc7" />

* **Fluxo de Cálculo (`fluxo_custo_arroba.puml`):** Diagrama de atividades detalhando a lógica de processamento do custo por arroba e projeção de lucro.
 <img width="515" height="650" alt="image" src="https://github.com/user-attachments/assets/d09c8c52-37fc-4be0-9f4d-ce039c9b541c" />

