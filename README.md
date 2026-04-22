# Análise de Tendências Tecnológicas em TCCs via NER e Grafos

Este projeto aplica técnicas de Processamento de Linguagem Natural (PLN) e Teoria dos Grafos para identificar e analisar as principais tecnologias, frameworks e conceitos citados em Trabalhos de Conclusão de Curso (TCCs) de computação e engenharia.

## 1. Integrantes do Grupo
* João Paulo de Oliveira Cabral (Responsável pelo código da extração das entidade e conexões e organização do repositório)
* Gustavo Quezado Gurgel Magalhaes (Responsável pela gravação do vídeo e código da análise dos gráfos)

## 2. Descrição Detalhada das Atividades
O projeto foi dividido em quatro fases principais de processamento de dados:

### A. Preparação e Extração (ETL)
* **Gestão de Documentos:** Implementação de um fluxo de entrada para arquivos PDF na pasta `documents/`.
* **Extração de Texto:** Utilização da biblioteca `pdfminer` para converter o conteúdo bruto dos PDFs em texto processável, com filtros específicos para focar no conteúdo entre o "Resumo" e as "Referências".

### B. Processamento de Linguagem Natural (NER)
* **Modelo spaCy:** Utilização do modelo `pt_core_news_lg` para processamento em português.
* **Dicionário Customizado:** Criação de um léxico de tecnologia (`temas_tcc`) abrangendo categorias como Linguagens, Frameworks, Infraestrutura e Conceitos Financeiros/Gestão.
* **Consolidação de Entidades:** Implementação de um mapeamento de sinonímia (`consolidation_mapping`) para agrupar variações (ex: "ia", "inteligência artificial" e "ai" consolidados como "ia").
* **Extração Híbrida:** Uso conjunto do `Matcher` do spaCy (regras) e do modelo de NER estatístico para garantir alta cobertura.

### C. Geração de Redes de Conhecimento
* **Mapeamento de Co-ocorrência:** Identificação de entidades que aparecem no mesmo parágrafo, gerando arquivos de conexões (`edges/`).
* **Cálculo de Estatísticas:** Geração de resumos individuais (`nodes/`) com contagem de ocorrências e categorização.

### D. Visualização e Análise de Grafos
* **Modelagem com NetworkX:** Construção de um grafo global onde o tamanho dos nós representa a frequência de citações e as arestas representam a força da conexão (co-ocorrência).
* **Centralidade:** Cálculo de *Degree* (conexões únicas) e *Betweenness Centrality* (influência como ponte entre áreas).
* **Exportação:** Visualização gerada via `Matplotlib` com layout de mola (*spring layout*) para evidenciar clusters.

## 3. Apresentação dos Resultados

### Estatísticas Gerais do Grafo
* **Nós:** 392
* **Conexões:** 357
* **Densidade:** 0.0047
* **Diâmetro do maior componente:** 6

### Principais Entidades

| Top 5 Mais Citadas | Citações | Top 5 Mais Influentes (Pontes) | Betweenness |
| :--- | :--- | :--- | :--- |
| código | 152 | código | 0.0153 |
| web | 145 | framework | 0.0069 |
| llm | 120 | cloud | 0.0049 |
| python | 119 | postgresql | 0.0041 |
| prisma | 84 | nuvem | 0.0040 |

### Conexões Mais Fortes (Co-ocorrência)
As tecnologias que mais "caminham juntas" nos parágrafos analisados:
1.  **llm ↔ rag** (Peso: 24)
2.  **ia ↔ llm** (Peso: 18)
3.  **spring ↔ framework** (Peso: 14)
4.  **código ↔ python** (Peso: 13)
5.  **cloud ↔ http** (Peso: 11)

### Visualização do Grafo
*(A imagem abaixo representa a rede de tecnologias extraídas dos 19 documentos)*

![Grafo de Entidades](grafo_entidades.png)

## 4. Análise e Discussão dos Achados

### Dominância da IA Generativa
A conexão mais forte do grafo (**LLM ↔ RAG**) e a alta posição de **IA** e **LLM** nas citações confirmam uma forte tendência nos TCCs atuais: o uso de modelos de linguagem de grande porte combinados com técnicas de recuperação de dados. Isso indica uma transição de trabalhos puramente teóricos para implementações práticas de IA aplicada.

### Estrutura de Conhecimento
O termo **"código"** lidera tanto em citações quanto em influência (*betweenness*). Isso ocorre porque ele atua como o principal "hub" que conecta diferentes stacks tecnológicas: desde o desenvolvimento **Web/Python** até automações em **Nuvem**.

### Clusters de Desenvolvimento Web e Backend
A forte co-ocorrência entre **Spring ↔ Framework** e a presença de **PostgreSQL** como uma das principais pontes mostra que o ecossistema de desenvolvimento corporativo robusto (Java/Spring) ainda é um pilar fundamental na formação acadêmica, servindo de base para projetos de diversas naturezas.

### O Caso de Ferramentas de Nicho (Prisma)
A entidade **Prisma** aparece no Top 5 de citações, mas possui **0 conexões únicas**. Isso sugere a presença de um trabalho altamente especializado que utiliza essa ferramenta de forma exaustiva, mas cujos termos de suporte não coincidiram com o dicionário global ou a ferramenta não foi citada em conjunto com outras tecnologias nos mesmos parágrafos, caracterizando-se como um "nó de nicho".


## 5. Link do Vídeo
Como orientado pelo professor aqui está o link do vídeo hospedado na plataforma Loom

https://www.loom.com/share/752cd98474f849bcafb298e308b447b4
