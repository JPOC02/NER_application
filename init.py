import os
import json
import spacy
import itertools
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import itertools
from spacy.matcher import Matcher
from pdfminer.high_level import extract_text
from pathlib import Path

input_folder = 'documents'
nodes_folder = 'nodes'
edges_folder = 'edges'

os.makedirs(input_folder, exist_ok=True)
os.makedirs(nodes_folder, exist_ok=True)
os.makedirs(edges_folder, exist_ok=True)

# Carregar spaCy
nlp = spacy.load('pt_core_news_lg')

# Dicionários de Suporte Atualizados com novos termos
temas_tcc = {
  'LINGUAGEM': ['Python', 'JavaScript', 'Java', 'C++', 'SQL', 'NumPy', 'Pandas', 'HTML', 'CSS', 'CSV', 'Linguagem de consulta estruturada'],
  'FRAMEWORK': ['Django', 'FastAPI', 'React', 'Vue', 'Angular', 'Spring', 'Selenium', 'JPA', 'JWT', 'SDK', 'KEDA', 'HPA', 'YOLO', 'YOLOv11'],
  'INFRAESTRUTURA': ['Docker', 'Kubernetes', 'AWS', 'Azure', 'PostgreSQL', 'MySQL', 'Container', 'Git', 'Google', 'REST', 'Email', 'S3', 'DNS', 'VPN', 'SSL',
           'TLS', 'IaaS', 'PaaS', 'SaaS', 'VM', 'InfiniBand', 'SSD', 'DDR4', 'GPU', 'TPU', 'CPU', 'NKE'],
  'TECH_CONCEITO': [
    'RPA', 'Automação Robótica de Processos', 'Bot', 'APIs', 'Machine Learning', 'Deep Learning', 'Robô', 'Web', 'Robots', 'DTE', 'DTO', 'GCP', 'HTTP', 'Logs', 'Escalabilidade',
    'Hypertext Transfer Protocol', 'ORM', 'Código', 'retry', 'Script', 'Inteligência Artificial', 'Framework', 'Nuvem', 'Cloud', 'Requisito', 'BERT', 'BPM', 'GPT', 'LLMs', 'LSTMs',
    'NLP', 'PJe', 'PLN', 'RAG', 'RNNs', 'LLM', 'AI', 'MOTA', 'MOTP', 'IoU', 'mAP', 'FPS', 'F1-score', 'CRUD', 'GitOps', 'DAG', 'CI/CD', 'POC', 'BI', 'BI Business Intelligence',
    'ZTNA', 'SESE', 'EDR', 'XDR', 'MFA', 'SSO', 'IAM', 'GDPR', 'LGPD', 'Cybersecurity', 'DDoS', 'SIEM', 'SOAR'
  ],
  'FINANCEIRO_GESTAO': [
    'Tributação', 'Produto Mínimo Viável', 'Contabilidade', 'Unidade Virtual de Tributação', 'UVT', 'PMEs', 'SINGEP', 'CIK', 'UANs', 'MVP', 'KPI', 'ROI', 'CISO', 'PDCA'
  ],
  'ORGANIZACAO_LOCAL': ['UFRN', 'TJPE', 'ANVISA', 'RDC', 'Sigaa', 'ECT', 'FIOCRUZ', 'ABNT', 'TRE-RN', 'NPAD', 'Brasil Júnior', 'EJ'],
  'CURSO_GRADUAÇÃO': ['Engenharia de Computação', 'Engenharia Elétrica', 'Engenharia Mecânica']
}

consolidation_mapping = {
  'api': 'api', 'application programming interface': 'api', 'interface de programação de aplicações': 'api', 'cnpj': 'cnpj',
  'cadastro de pessoa física': 'cpf', 'cadastro de pessoa fisica': 'cpf','cpf': 'cpf', 'crud': 'crud', 'dry': 'dry', "don't repeat yourself": 'dry', 'não se repita': 'dry',
  'nao se repita': 'dry', 'dte': 'dte', 'domicílio tributário eletrônico': 'dte', 'domicilio tributario eletronico': 'dte', 'dto': 'dto', 'data transfer object': 'dto', 'gcp': 'gcp',
  'http': 'http', 'Hypertext Transfer Protocol': 'http', 'protocolo de transferência de hipertexto': 'http', 'protocolo de transferencia de hipertexto': 'http',
  'ia': 'ia', 'mvp': 'mvp', 'minimum viable product': 'mvp', 'produto mínimo viável': 'mvp', 'produto minimo viavel': 'mvp',
  'orm': 'orm', 'mapeamento objeto-relacional': 'orm', 'object-relational mapping': 'orm',
  'ram': 'ram', 'random Access Memory': 'ram', 'memória de acesso aleatório': 'ram', 'memoria de acesso aleatorio': 'ram',
  'rest': 'rest', 'rf': 'rf', 'rn': 'rn', 'rio grande do norte': 'rn', 'tcc': 'tcc', 'trabalho de conclusão de curso': 'tcc', 'trabalho de conclusao de curso': 'tcc',
  'rnf': 'rnf', 'requisitos não funcionais': 'rnf', 'requisitos nao funcionais': 'rnf', 'roi': 'roi', 'retorno sobre o investimento': 'roi', 'rpa': 'rpa', 'recibo de pagamento autônomo' : 'rpa', 'recibo de pagamento autonomo' : 'rpa',
  'sefip': 'sefip', 'sistema empresa de recolhimento do fgts e informações à previdência social': 'sefip', 'sistema empresa de recolhimento do fgts e informações a previdencia social': 'sefip',
  'siap': 'siap', 'sistema de apoio a processos de segurança contra incêndio e pânico': 'siap', 'sistema de apoio a processos de segurança contra incendio e panico': 'siap',
  'sigaa': 'sigaa', 'sistema integrado de gestão de atividades academicas': 'sigaa', 'sistema integrado de gestao de atividades academicas': 'sigaa',
  'ufrn': 'ufrn', 'universidade federal do rio grande do norte': 'ufrn', 'unidade virtual de tributação': 'uvt', 'unidade virtual de tributacao': 'uvt',
  'vcpu': 'vcpu', 'virtual central processing unit': 'vcpu', 'unidade central de processamento virtual': 'vcpu',
  'bert': 'bert', 'representações codificadoras bidirecionais de transformadores': 'bert', 'representacoes codificadoras bidirecionais de transformadores': 'bert',
  'bidirectional encoder representations from transformers': 'bert', 'bpm': 'bpm', 'gerenciamento de processos de negócio': 'bpm', 'gerenciamento de processos de negocio': 'bpm',
  'Business Process Management': 'bpm', 'gpt': 'gpt', 'llms': 'llm', 'llms': 'llm', 'large language model': 'llm', 'grande modelo de linguagem': 'llm',
  'pln': 'pln', 'nlp': 'pln', 'processamento de linguagem natural': 'pln', 'pmes': 'pmes', 'rag': 'rag',
  'rnns': 'rnns', 'rdc': 'rdc', 'llm': 'llm', 'ai': 'ia', 'inteligência artificial': 'ia', 'inteligencia artificial': 'ia',
  'abnt': 'abnt', 'associação brasileira de normas técnicas': 'abnt', 'ad': 'árvore de decisão', 'ml': 'machine learning',
  'mlp': 'multi layer perceptron', 'sgbd': 'sgbd', 'sistema gerenciador de banco de dados': 'sgbd', 'aed': 'aed', 'análise exploratória de dados': 'aed', 'dag': 'dag',
  'ci/cd': 'ci/cd', 'poc': 'poc', 'bi': 'bi', 'aws': 'aws', 'json': 'json', 'sql': 'sql', 'vm': 'vm', 'dns': 'dns', 'cpu': 'cpu', 'gpu': 'gpu', 'tpu': 'tpu', 'lgpd': 'lgpd', 'gdpr': 'gdpr',
  'vpn': 'vpn', 'sso': 'sso', 'mfa': 'mfa', 'ux': 'ux', 'ui': 'ui', 'uml': 'uml',
  'zero trust': 'ztna', 'ZTA': 'ztna', 'ztna': 'ztna'
}

# Loop de Processamento
pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
print(f'Arquivos encontrados: {len(pdf_files)}')

for pdf_name in pdf_files:
  print(f'\nProcessando: {pdf_name}...')
  file_id = Path(pdf_name).stem
  pdf_path = os.path.join(input_folder, pdf_name)

  try:
    text_content = extract_text(pdf_path)
  except Exception as e:
    print(f'Erro ao ler {pdf_name}: {e}')
    continue

  raw_paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip()]
  start_indices = [i for i, p in enumerate(raw_paragraphs) if 'RESUMO' in p.upper()]
  end_indices = [i for i, p in enumerate(raw_paragraphs) if 'REFERÉNCIAS' in p.upper() or 'REFERENCIAS' in p.upper()]

  start_idx = start_indices[0] if start_indices else -1
  end_idx = end_indices[-1] if end_indices else -1

  if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
    paragraphs = raw_paragraphs[start_idx + 1 : end_idx]
  elif start_idx != -1:
    paragraphs = raw_paragraphs[start_idx + 1:]
  else:
    paragraphs = raw_paragraphs

  paragraphs = [p for p in paragraphs if len(p.split()) >= 10]
  full_filtered_text = '\n\n'.join(paragraphs)

  matcher = Matcher(nlp.vocab)
  for cat, terms in temas_tcc.items():
    for term in terms:
      pattern = [{'LOWER': t.lower()} for t in term.split()]
      matcher.add(cat, [pattern])

  nlp.max_length = len(full_filtered_text) + 100000
  doc = nlp(full_filtered_text)

  summary_map = {}
  counted_tokens = set() 

  # Busca por entidades automáticas do spaCy
  for ent in doc.ents:
    if ent.label_.upper() == 'MISC': continue
    
    # Marca os índices (tokens) dessa entidade como "já contados"
    for i in range(ent.start, ent.end):
      counted_tokens.add(i)

    canon = consolidation_mapping.get(ent.text.lower().strip(), ent.text.lower().strip())
    summary_map.setdefault(canon, {'entidade': canon, 'ocorrencias': 0, 'cats': set()})
    summary_map[canon]['ocorrencias'] += 1
    summary_map[canon]['cats'].add(ent.label_)

  # Busca pelas suas regras do Matcher
  for match_id, start, end in matcher(doc):
    if start in counted_tokens or (end - 1) in counted_tokens:
      continue
      
    # Marca como contada
    for i in range(start, end):
      counted_tokens.add(i)

    canon = consolidation_mapping.get(doc[start:end].text.lower().strip(), doc[start:end].text.lower().strip())
    summary_map.setdefault(canon, {'entidade': canon, 'ocorrencias': 0, 'cats': set()})
    summary_map[canon]['ocorrencias'] += 1
    summary_map[canon]['cats'].add(nlp.vocab.strings[match_id])

  final_summary = [{'entidade': v['entidade'], 'ocorrencias': v['ocorrencias'], 'categorias': ', '.join(v['cats'])} for v in summary_map.values()]
  with open(f'{nodes_folder}/entities_summary_{file_id}.json', 'w', encoding='utf-8') as f:
    json.dump(final_summary, f, ensure_ascii=False, indent=4)

  connections_data = []
  for idx, p_text in enumerate(paragraphs):
    p_doc = nlp(p_text)
    ents_in_p = {}
    for m_id, s, e in matcher(p_doc):
      canon = consolidation_mapping.get(p_doc[s:e].text.lower().strip(), p_doc[s:e].text.lower().strip())
      ents_in_p[canon] = ents_in_p.get(canon, 0) + 1
    if len(ents_in_p) > 1 or (len(ents_in_p) == 1 and list(ents_in_p.values())[0] > 1):
      connections_data.append({'paragraph_index': idx, 'entities_found': ents_in_p})

  with open(f'{edges_folder}/connections_{file_id}.json', 'w', encoding='utf-8') as f:
    json.dump(connections_data, f, ensure_ascii=False, indent=4)

print('\n--- Processamento finalizado com novos termos! ---')


# Carregar e Consolidar Atributos dos Nós (global_entities)
global_entities = {}
for filename in os.listdir(nodes_folder):
  if filename.endswith('.json'):
    with open(os.path.join(nodes_folder, filename), 'r', encoding='utf-8') as f:
      data = json.load(f)
      for entry in data:
        ent = entry['entidade']
        count = entry['ocorrencias']

        # Garante que tratamos categorias novas como set
        new_cats_raw = entry.get('categorias', '')
        new_categories = set(new_cats_raw.split(', ')) if isinstance(new_cats_raw, str) else set(new_cats_raw)

        if ent not in global_entities:
          global_entities[ent] = {'ocorrencias': 0, 'categorias': set()}

        global_entities[ent]['ocorrencias'] += count
        global_entities[ent]['categorias'].update(new_categories)

# Converte sets de volta para strings para o cálculo e exibição
for ent, info in global_entities.items():
  info['categorias'] = ', '.join(sorted(list(info['categorias'])))

# 3. Calcular média global de citações
occurrences_list = [v['ocorrencias'] for v in global_entities.values()]
avg_citations = sum(occurrences_list) / len(occurrences_list) if occurrences_list else 0

# 4. Identificar entidades com conexões
entities_with_connections = set()
for filename in os.listdir(edges_folder):
  if filename.endswith('.json'):
    with open(os.path.join(edges_folder, filename), 'r', encoding='utf-8') as f:
      connections = json.load(f)
      for conn in connections:
        entities_found = list(conn['entities_found'].keys())
        if len(entities_found) > 1:
          for e in entities_found:
            entities_with_connections.add(e)

# 5. Inicializar Grafo com o filtro: ACIMA DA MÉDIA OU COM CONEXÕES
G_filtered = nx.Graph()

for ent, info in global_entities.items():
  if (info['ocorrencias'] > avg_citations) or (ent in entities_with_connections):
    G_filtered.add_node(ent, size=info['ocorrencias'])

# 6. Adicionar Arestas entre os nós filtrados
for filename in os.listdir(edges_folder):
  if filename.endswith('.json'):
    with open(os.path.join(edges_folder, filename), 'r', encoding='utf-8') as f:
      connections = json.load(f)
      for conn in connections:
        entities_found = list(conn['entities_found'].keys())
        valid_ents = [e for e in entities_found if G_filtered.has_node(e)]
        if len(valid_ents) > 1:
          for u, v in itertools.combinations(sorted(valid_ents), 2):
            if G_filtered.has_edge(u, v):
              G_filtered[u][v]['weight'] += 1
            else:
              G_filtered.add_edge(u, v, weight=1)

# 7. Visualização
plt.figure(figsize=(40, 25))
pos = nx.spring_layout(G_filtered, k=3.5, scale=2.5, iterations=100)

node_sizes = [G_filtered.nodes[n]['size'] * 90 for n in G_filtered.nodes()]
nx.draw_networkx_nodes(G_filtered, pos, node_size=node_sizes, node_color='lightgreen', alpha=0.7)

if G_filtered.number_of_edges() > 0:
  weights = [G_filtered[u][v]['weight'] for u, v in G_filtered.edges()]
  nx.draw_networkx_edges(G_filtered, pos, width=weights, edge_color='gray', alpha=0.3)

nx.draw_networkx_labels(G_filtered, pos, font_size=10, font_weight='bold')

plt.title(f"Grafo: Entidades Acima da Média ({avg_citations:.2f}) ou Com Conexões")
plt.axis('off')
plt.savefig("grafo_entidades.png", dpi=300, bbox_inches='tight')
print("Gráfico salvo como 'grafo_entidades.png'.")

print(f"Grafo gerado com {G_filtered.number_of_nodes()} nós e {G_filtered.number_of_edges()} conexões.")



# 1. Estatísticas de Nós (Entidades)
# Grau (número de conexões diretas)
degree_dict = dict(G_filtered.degree())

# Centralidade de Intermediação (quais termos ligam diferentes 'comunidades' de assuntos)
betweenness_dict = nx.betweenness_centrality(G_filtered, weight='weight')

# Criar DataFrame para análise
nodes_stats = []
for node in G_filtered.nodes():
  nodes_stats.append({
    'Entidade': node,
    'Citações Totais': G_filtered.nodes[node]['size'],
    'Conexões Únicas': degree_dict[node],
    'Influência (Betweenness)': round(betweenness_dict[node], 4)
  })

df_nodes = pd.DataFrame(nodes_stats).sort_values(by='Citações Totais', ascending=False)

# 2. Estatísticas de Arestas (Conexões Mais Fortes)
edges_stats = []
for u, v, data in G_filtered.edges(data=True):
  edges_stats.append({
    'Origem': u,
    'Destino': v,
    'Peso (Co-ocorrência)': data['weight']
  })

df_edges = pd.DataFrame(edges_stats).sort_values(by='Peso (Co-ocorrência)', ascending=False)

# 3. Exibição dos Resultados
print("=== TOP 10 ENTIDADES MAIS CITADAS ===")
print(df_nodes.head(10))

print("\n=== TOP 10 ENTIDADES MAIS INFLUENTES (PONTES NO GRAFO) ===")
print(df_nodes.sort_values(by='Influência (Betweenness)', ascending=False).head(10))

print("\n=== TOP 10 CONEXÕES MAIS FORTES (OCORREM NO MESMO PARÁGRAFO) ===")
print(df_edges.head(10))

# Estatísticas Gerais
print(f"\nResumo do Grafo:")
print(f"- Densidade do Grafo: {nx.density(G_filtered):.4f}")
print(f"- Diâmetro do maior componente: {nx.diameter(G_filtered.subgraph(max(nx.connected_components(G_filtered), key=len)))}")

