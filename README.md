# Tech Challenge Fase 4 - Observabilidade de Credit Scoring

Projeto end-to-end para sustentar um classificador de risco de crédito com contratos de qualidade, simulação de data/concept drift, monitoramento e documentação de governança. O cenário usa o dataset Home Credit Default Risk, conforme uma das fontes indicadas no enunciado.

> **Uso acadêmico:** os dados de produção e a mudança de conceito são simulados. Este modelo não deve apoiar decisões reais de crédito.

## O que o projeto demonstra

- Baseline de classificação com Scikit-Learn.
- Contrato Pandera que bloqueia valores ausentes, idade fora do intervalo, valores monetários inválidos e campos fora do domínio.
- Separação entre população de referência e lote de produção simulado.
- Alteração controlada de renda, crédito e anuidade para simular data drift.
- Mudança da relação entre características e inadimplência para simular concept drift.
- Comparação estatística via Kolmogorov-Smirnov e PSI, além de relatório HTML do Evidently.
- Métricas de qualidade do modelo, volume, duração, status e eventos registrados em JSON.
- Painel Streamlit local para acompanhar resultados.
- Documentação de privacidade, limites de uso e governança.

## Stack

- Python 3.11 ou 3.12
- Pandas, NumPy, SciPy e Scikit-Learn
- Pandera para data contracts
- Evidently para relatório de drift
- Streamlit para o painel local
- Kaggle API para obter o arquivo oficial (requer aceite das regras da competição)

## Estrutura

```text
.
|-- data/raw/                 # arquivo do Kaggle, fora do Git
|-- data/processed/           # reservado para dados derivados, fora do Git
|-- data/artifacts/           # reservado para modelo serializado, fora do Git
|-- docs/                     # fonte de dados e governança
|-- logs/                     # eventos JSONL, fora do Git
|-- monitoring/               # painel Streamlit
|-- reports/generated/        # HTML, estatísticas e métricas, fora do Git
|-- scripts/                  # setup, download e execução no Windows
|-- src/credit_drift/         # pipeline, contrato, modelo e detecção
`-- pyproject.toml
```

## 1. Preparar o ambiente no Windows

Na raiz do projeto:

```powershell
.\scripts\setup_windows.ps1
```

O script cria `.venv` e instala as dependências do projeto, do painel e do cliente Kaggle. Se o PowerShell bloquear scripts nesta sessão, rode:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 2. Obter o dataset

O arquivo usado é `application_train.csv`, da competição [Home Credit Default Risk no Kaggle](https://www.kaggle.com/competitions/home-credit-default-risk/data). É necessário entrar na conta Kaggle e aceitar as regras da competição antes do download. Siga o guia [docs/DATASET.md](docs/DATASET.md).

Com as credenciais da sua própria conta Kaggle configuradas:

```powershell
.\scripts\download_data.ps1
```

Também é possível baixar o arquivo pela interface web e salvá-lo em `data/raw/application_train.csv`. O arquivo bruto e as credenciais são ignorados pelo Git. Não os publique.

## 3. Executar a demonstração do contrato

O lote de exemplo inclui idade inválida, renda negativa e anuidade nula. Pandera deve rejeitá-lo:

```powershell
.\scripts\demo_contract.ps1
```

## 4. Rodar treino, simulação e monitoramento

```powershell
.\scripts\run_pipeline.ps1
```

O padrão usa até 60.000 linhas limpas para manter o experimento leve. Para alterar o limite:

```powershell
.\scripts\run_pipeline.ps1 -Rows 100000
```

Arquivos gerados em `reports/generated/`:

- `evidently_data_drift.html`: comparação interativa da distribuição das features.
- `drift_statistics.csv`: estatística KS e PSI por variável numérica.
- `metrics.json`: métricas de classificação, tamanho dos lotes, taxa do alvo, quantidade de alertas e duração.

Eventos de execução, rejeições do contrato e falhas ficam em `logs/pipeline_events.jsonl`.

## 5. Abrir o painel

Depois de executar o pipeline:

```powershell
.\monitoring\run_dashboard.ps1
```

O Streamlit imprime um endereço local (normalmente `http://localhost:8501`). O painel exibe volumes, duração, número de testes com drift, taxas do alvo e métricas ROC AUC/Brier de referência e produção.

## Como interpretar os alertas

- KS marca mudança quando `p_value < 0.05`.
- PSI usa `0.2` como limiar didático de mudança relevante.
- O relatório Evidently aplica testes conforme os tipos de coluna e apresenta a comparação gráfica.
- A degradação de performance é comparada entre holdout de referência e lote de produção simulado.
- `TARGET` não entra no treino como feature. Ele só serve para medir o modelo e ilustrar o concept drift retrospectivamente.

Os limites são demonstrativos e dependem de tamanho de amostra, frequência de monitoramento e custo de falsos alertas. Em produção, deveriam ser calibrados com validação de negócio.

## Reprodutibilidade e histórico

Use commits pequenos, com mensagens convencionais, por exemplo:

```text
feat: add pandera data contract
feat: simulate production drift
feat: generate evidently monitoring report
docs: document privacy and model limitations
```

Com a mesma versão de Python, dataset, dependências e seed (`42`), a preparação e a simulação são reproduzíveis. O relatório HTML contém data/hora da execução e as estatísticas também são salvas em CSV/JSON.

## Governança e LGPD

Consulte [docs/GOVERNANCE.md](docs/GOVERNANCE.md) para finalidade, minimização, retenção, limites de privacidade, vieses e pontos que exigiriam análise jurídica numa operação real. A origem e os limites do dataset estão em [docs/DATASET.md](docs/DATASET.md).

## Roteiro sugerido para o vídeo STAR (até 5 minutos)

1. **Situation (40 s):** degradação silenciosa de um modelo de crédito e impacto potencial.
2. **Task (40 s):** validar entradas, detectar drift, registrar saúde e documentar privacidade.
3. **Action (2 min 20 s):** mostrar o contrato rejeitando o lote; explicar baseline e separação de referência/produção; rodar a simulação e abrir HTML/painel.
4. **Result (1 min 20 s):** apontar features alteradas, alertas KS/PSI, mudança de métricas e limitações da simulação.

## Limitações conhecidas

- A tabela do Kaggle não traz uma série temporal adequada para observar drift real; as duas populações são criadas por simulação controlada.
- O conceito de produção é ressampleado para fins didáticos e não é um resultado real futuro.
- A seleção de features é intencionalmente pequena para manter o baseline e a explicação gerenciáveis.
- A métrica agregada não avalia justiça por grupo nem torna o modelo apto para uso real.
