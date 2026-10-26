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

O enunciado solicita que a equipe discuta base legal, retenção e privacidade. Para este trabalho, descrevemos princípios e controles hipotéticos; não há tratamento de dados de clientes próprios e este README não constitui parecer jurídico. Em uma operação real, a hipótese legal aplicável a decisões de crédito deve ser avaliada pelo controlador com jurídico/encarregado, finalidade, necessidade, transparência e salvaguardas pertinentes, incluindo análise de vieses e mecanismos de revisão.

## Retenção e segurança

Manter arquivos locais apenas pelo tempo necessário à atividade acadêmica; remover credenciais e dados ao concluir. Restringir acesso à máquina e não publicar dados em issues, notebooks ou artefatos. Os scripts não enviam dados a serviços externos além do download iniciado pelo usuário na Kaggle.

## Vieses e explicabilidade

O dataset contém atributos demográficos e proxies socioeconômicos. Eles podem produzir disparidades. O baseline é apenas didático, não foi aprovado para uso real, e suas métricas globais não demonstram equidade. Uma implantação exigiria avaliação de impacto por grupos, explicabilidade, governança humana, contestação e monitoramento continuado.

## Retenção do projeto

`data/raw/`, resultados intermediários e logs locais são ignorados pelo Git. O README e este documento registram finalidade, campos, processamento e limitações para que a avaliação seja reproduzível sem publicar registros individuais.
