
# F1
Projeto com dados da API de fórmula 1
=======
# 🏎️ Dashboard de Fórmula 1

Dashboard interativo desenvolvido em **Python** e **Streamlit** para explorar dados de etapas e voltas da Fórmula 1. O projeto permite filtrar a temporada por continente, país e circuito, além de visualizar tabelas e gráficos nas páginas de corridas, pilotos, equipes, voltas e resultados.

> **Observação sobre os dados:** as análises de pilotos, equipes e resultados são calculadas a partir das voltas retornadas pelo serviço utilizado no projeto. Elas não representam, necessariamente, a classificação oficial completa do campeonato.

## ✨ Funcionalidades

- **🏁 Corridas:** lista as etapas que correspondem aos filtros selecionados e apresenta um resumo da quantidade de etapas por país.
- **👤 Pilotos:** compara pilotos com base nas voltas disponíveis, incluindo melhor tempo, quantidade de voltas retornadas e etapas com dados.
- **👥 Equipes:** resume as voltas retornadas por equipe, os pilotos identificados, as etapas e a melhor volta.
- **⏱️ Voltas:** exibe os tempos de volta disponíveis e destaca os melhores tempos do recorte selecionado.
- **📊 Resultados:** apresenta um comparativo de pilotos ordenado pelo melhor tempo de volta no conjunto de dados filtrado.
- **Filtros:** temporada, tipo de sessão, continente, país e circuito.
- **Gráficos interativos:** visualizações criadas com Plotly.
- **Cache:** uso de cache do Streamlit para reduzir consultas repetidas e acelerar o carregamento.

## 🧰 Tecnologias utilizadas

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly Express](https://plotly.com/python/plotly-express/)
- API OpenF1, por meio dos módulos de integração presentes no projeto.

## 📁 Estrutura do projeto

A estrutura abaixo representa os módulos referenciados pelo dashboard. Ajuste os nomes ou caminhos caso o seu repositório esteja organizado de outra forma.

```text
.
├── src/
│   └── f1/
│       ├── dashboard.py
│       ├── domain/
│       │   └── services.py
│       ├── ingestion/
│       │   ├── http_client.py
│       │   └── openf1_client.py
│       └── utils/
│           └── config.py
├── requirements.txt
└── README.md
```

## 🚀 Como executar localmente

### 1. Pré-requisitos

- Python instalado e disponível no terminal.
- Git, caso queira clonar o repositório.
- Acesso à internet para consultar os dados fornecidos pela API.

### 2. Clone o repositório

Substitua `<URL_DO_REPOSITORIO>` pelo endereço do seu repositório no GitHub:

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_REPOSITORIO>
```

### 3. Crie e ative um ambiente virtual

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (Prompt de Comando):**

```bat
python -m venv .venv
.venv\Scripts\activate
```

**Linux ou macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instale as dependências

Se o projeto já tiver um arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Se ainda não tiver esse arquivo, instale as dependências principais:

```bash
pip install streamlit pandas plotly
```

O projeto também precisa dos módulos internos `f1` presentes no repositório. Execute o comando a partir da raiz do projeto e mantenha a estrutura de pastas esperada pelo código.

### 5. Inicie o dashboard

Se o arquivo estiver em `src/f1/dashboard.py`, execute:

```bash
streamlit run src/f1/dashboard.py
```

O Streamlit exibirá no terminal o endereço local para abrir o dashboard no navegador.

## 🔎 Como utilizar

1. Escolha a página desejada no menu lateral.
2. Selecione a temporada.
3. Escolha o tipo de sessão: **Corrida** ou **Classificação**.
4. Filtre por continente, país e circuito.
5. Consulte a tabela e o gráfico gerados para os filtros atuais.

Os filtros geográficos são dependentes: a seleção de continente restringe os países disponíveis, e a seleção de países restringe os circuitos.

## 📊 Interpretação dos resultados

Os dados exibidos nas páginas de pilotos, equipes, voltas e resultados dependem das voltas que o serviço do projeto retorna para cada etapa e sessão selecionadas. Por isso:

- “Voltas retornadas” significa a quantidade de registros de volta disponíveis no conjunto consultado.
- “Melhor volta” é o menor tempo válido encontrado no recorte atual.
- A posição mostrada em **Resultados** é uma ordenação analítica pelo melhor tempo de volta, não uma posição oficial no campeonato.
- A página de corridas lista as etapas retornadas para a temporada e os filtros selecionados.

## ⚡ Desempenho

O projeto utiliza mecanismos de cache do Streamlit para reaproveitar dados já consultados. A primeira consulta de uma combinação de temporada, sessão e etapas pode demorar mais; consultas repetidas podem ser mais rápidas enquanto os dados estiverem no cache.

## 🛠️ Solução de problemas

**O comando `streamlit` não foi encontrado**

Confirme se o ambiente virtual está ativado e instale o Streamlit:

```bash
python -m pip install streamlit
```

**Erro ao importar o pacote `f1`**

Execute o comando na raiz do repositório e confira se a estrutura de diretórios corresponde aos imports do código. Se necessário, configure o projeto como pacote Python.

**Não aparecem voltas para os filtros selecionados**

Experimente outra temporada, sessão, país ou circuito. A disponibilidade depende dos dados retornados pela API e das consultas implementadas no projeto.

**Erro de conexão**

Verifique a conexão com a internet e tente novamente. A disponibilidade e o formato dos dados dependem do serviço externo consultado.

## 🗺️ Próximas melhorias

Possíveis evoluções para o projeto:

- Adicionar dados de classificação oficial de pilotos e construtores.
- Comparar pontos e posições no campeonato ao longo de várias temporadas.
- Incluir evolução dos tempos de volta por piloto e circuito.
- Melhorar os testes automatizados e o tratamento de erros da API.
- Publicar uma versão acessível pela web.

## 📄 Licença

Adicione uma licença ao repositório caso queira definir formalmente como outras pessoas podem utilizar, modificar e distribuir o projeto.

---

Desenvolvido como projeto de análise e visualização de dados de Fórmula 1 com Python.
