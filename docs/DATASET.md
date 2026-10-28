# Fonte e preparação dos dados

## Fonte selecionada

Home Credit Default Risk, competição oficial hospedada pela Kaggle e organizada pelo Home Credit Group: <https://www.kaggle.com/competitions/home-credit-default-risk/data>.

O projeto utiliza somente `application_train.csv`, a tabela principal de solicitações. Ela contém uma linha por solicitação e a coluna `TARGET` com o resultado binário. A página da competição informa que o acesso aos arquivos depende de login e aceite das regras. Use a fonte oficial; não publique o arquivo bruto no GitHub.

## Como obter no Windows

1. Crie/acesse sua conta Kaggle, abra a competição e aceite as regras.
2. Configure a API Kaggle com a credencial da sua própria conta conforme a documentação oficial: <https://github.com/Kaggle/kaggle-api#api-credentials>.
3. Na raiz do projeto, rode `.\scripts\download_data.ps1`.
4. Confirme que `data/raw/application_train.csv` existe. Essa pasta está ignorada pelo Git.

Alternativamente, baixe `application_train.csv` pela interface web do Kaggle e salve em `data/raw/`.

## Recorte usado

O pipeline carrega os campos necessários, deriva idade a partir de `DAYS_BIRTH`, remove linhas sem valores nas features selecionadas e limita a execução local a 60.000 linhas por padrão. O arquivo original supera o mínimo de 5.000 amostras solicitado; o recorte mantém os experimentos leves em um computador pessoal. O argumento `--rows` permite alterar o limite.

Features utilizadas: gênero, renda, valor do crédito, anuidade, idade e tamanho da família. `SK_ID_CURR` serve apenas para identificar duplicatas e não entra no modelo. `TARGET` é usado como rótulo e nunca como feature.

## Limites

Os dados são de uma competição e refletem uma população e contexto próprios. O dataset não deve ser tratado como amostra representativa de clientes brasileiros, nem usado para decisões reais de crédito. A produção e o concept drift deste trabalho são cenários simulados para fins didáticos.
