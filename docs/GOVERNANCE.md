# Governança, privacidade e uso responsável

## Finalidade e limites

Este repositório é um exercício acadêmico de observabilidade de um classificador de risco. Não é um sistema de concessão de crédito e não deve orientar decisões sobre pessoas reais. O dataset público foi disponibilizado para a competição Home Credit Default Risk; seu uso deve respeitar as regras e atribuições da fonte.

## Privacidade e minimização

- O código seleciona apenas as variáveis necessárias para o exercício.
- O identificador `SK_ID_CURR` é usado somente para checar unicidade e é excluído do modelo.
- O arquivo bruto fica em `data/raw/`, ignorado pelo Git. Não enviar dados brutos, credenciais Kaggle ou segredos ao repositório.
- Os relatórios registram métricas agregadas; não devem incluir linhas identificáveis.
- Este dataset de competição não deve ser confundido com dados pessoais obtidos diretamente de clientes da fintech fictícia.

## Base legal e LGPD

O art. 7º, X, da LGPD prevê o tratamento de dados pessoais para proteção do crédito, observada a legislação pertinente. Em uma operação real de análise de risco ou decisão de crédito, essa hipótese pode ser considerada quando o tratamento for necessário e diretamente ligado à proteção do crédito. A base legal não autoriza qualquer coleta ou uso: continuam aplicáveis os princípios da LGPD, os direitos dos titulares, a transparência, a qualidade e segurança dos dados, e as salvaguardas contra discriminação e decisões inadequadas. O controlador deve documentar finalidade, necessidade, categorias de dados, compartilhamentos e retenção, e avaliar o caso com o encarregado e assessoria jurídica.

Neste projeto acadêmico, o art. 7º, X, é discutido como hipótese para o cenário fictício de análise de crédito, não como fundamento jurídico do tratamento que realizamos. O arquivo é um dataset público de competição, usado localmente para demonstrar modelagem e monitoramento; não recebemos dados de clientes da fintech fictícia nem fazemos decisões reais. O uso do dataset continua sujeito às regras da competição e não torna automaticamente aplicável essa hipótese legal.

## Retenção e segurança

O arquivo bruto `data/raw/application_train.csv` e quaisquer cópias intermediárias ficam somente na máquina local e devem ser removidos até 30 dias após a conclusão da atividade. O mesmo prazo vale para logs de execução em `logs/` e relatórios locais temporários. Ao encerrar o projeto, descarte-os apagando esses arquivos e esvaziando a lixeira; remova também credenciais Kaggle conforme as instruções da plataforma. O prazo é uma regra operacional deste exercício, não uma obrigação legal universal.

O repositório mantém apenas código, documentação e resultados agregados versionados (`metrics.json`, `drift_statistics.csv` e relatório Evidently), sem linhas individuais do dataset. Esses artefatos podem permanecer no repositório acadêmico enquanto ele for necessário para avaliação; ao arquivar ou tornar o repositório privado/removê-lo, apague o histórico e os artefatos se a retenção deixar de ser necessária. Restringir acesso à máquina e não publicar dados ou credenciais em issues, notebooks ou artefatos. O pipeline não envia dados a serviços externos; o download Kaggle é iniciado pelo usuário.

## Vieses e explicabilidade

O dataset contém atributos demográficos e proxies socioeconômicos. Eles podem produzir disparidades. O baseline é apenas didático, não foi aprovado para uso real, e suas métricas globais não demonstram equidade. Uma implantação exigiria avaliação de impacto por grupos, explicabilidade, governança humana, contestação e monitoramento continuado.

## Retenção do projeto

`data/raw/`, resultados intermediários e logs locais são ignorados pelo Git. Apenas o relatório de drift e métricas agregadas ficam versionados; não incluem registros de clientes. Os arquivos locais brutos, intermediários e logs são descartados em até 30 dias após a conclusão da atividade. O README e este documento registram finalidade, campos, processamento e limitações para que a avaliação seja reproduzível sem publicar linhas individuais.
