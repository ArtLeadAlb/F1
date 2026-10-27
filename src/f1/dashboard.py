
import pandas as pd
import plotly.express as px
import streamlit as st

from f1.domain.services import F1DashboardService
from f1.ingestion.http_client import HttpClient
from f1.ingestion.openf1_client import (
    OpenF1DriverRepository,
    OpenF1LapRepository,
    OpenF1MeetingRepository,
    OpenF1SessionRepository,
)
from f1.utils.config import DEFAULT_YEAR


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="F1 Dashboard",
    page_icon="🏎️",
    layout="wide",
)

ANOS_DISPONIVEIS = [2023, 2024, 2025, 2026]

COUNTRY_CONTINENT = {
    "Australia": "Oceania",
    "Austria": "Europa",
    "Azerbaijan": "Ásia",
    "Bahrain": "Ásia",
    "Belgium": "Europa",
    "Brazil": "América do Sul",
    "Canada": "América do Norte",
    "China": "Ásia",
    "France": "Europa",
    "Germany": "Europa",
    "Hungary": "Europa",
    "India": "Ásia",
    "Italy": "Europa",
    "Japan": "Ásia",
    "Malaysia": "Ásia",
    "Mexico": "América do Norte",
    "Monaco": "Europa",
    "Netherlands": "Europa",
    "Portugal": "Europa",
    "Qatar": "Ásia",
    "Russia": "Europa",
    "Saudi Arabia": "Ásia",
    "Singapore": "Ásia",
    "South Africa": "África",
    "South Korea": "Ásia",
    "Spain": "Europa",
    "Turkey": "Europa",
    "United Arab Emirates": "Ásia",
    "United Kingdom": "Europa",
    "United States": "América do Norte",
    "Argentina": "América do Sul",
    "Sweden": "Europa",
    "Switzerland": "Europa",
    "Thailand": "Ásia",
}


# ============================================================
# SERVIÇOS ORIGINAIS
# ============================================================

@st.cache_resource
def get_service() -> F1DashboardService:
    client = HttpClient()

    return F1DashboardService(
        meeting_repo=OpenF1MeetingRepository(client),
        session_repo=OpenF1SessionRepository(client),
        lap_repo=OpenF1LapRepository(client),
        driver_repo=OpenF1DriverRepository(client),
    )


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_meetings(year: int) -> list[dict]:
    service = get_service()
    meetings = service.get_meetings_for_year(year)
    return [meeting.model_dump() for meeting in meetings]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_top_laps(
    meeting_key: int,
    session_name: str,
) -> list[dict]:
    service = get_service()

    entries = service.get_top_laps_for_meeting(
        meeting_key,
        session_name,
    )

    return [entry.model_dump() for entry in entries]


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def format_lap_time(seconds):
    if pd.isna(seconds):
        return "-"

    seconds = float(seconds)
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    return f"{minutes}:{remaining_seconds:06.3f}"


def normalize_color(value):
    if pd.isna(value):
        return "#808080"

    color = str(value).replace("#", "").strip()

    if len(color) != 6:
        return "#808080"

    try:
        int(color, 16)
    except ValueError:
        return "#808080"

    return f"#{color}"


def ensure_columns(dataframe, defaults):
    """Garante que as colunas necessárias existam."""
    result = dataframe.copy()

    for column, default_value in defaults.items():
        if column not in result.columns:
            result[column] = default_value

    return result


def make_bar_chart(
    dataframe,
    x,
    y,
    title,
    x_label,
    y_label,
):
    """Cria um gráfico de barras com validação básica."""
    if dataframe.empty or x not in dataframe or y not in dataframe:
        st.info("Não há dados suficientes para gerar este gráfico.")
        return

    chart_data = dataframe[[x, y]].dropna().copy()

    if chart_data.empty:
        st.info("Não há dados suficientes para gerar este gráfico.")
        return

    fig = px.bar(
        chart_data,
        x=x,
        y=y,
        title=title,
        labels={x: x_label, y: y_label},
        text=y,
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=55, b=10),
        xaxis_title=x_label,
        yaxis_title=y_label,
    )

    fig.update_traces(textposition="outside", cliponaxis=False)

    st.plotly_chart(fig, use_container_width=True)


def add_geography(dataframe):
    """Adiciona continente sem alterar os dados originais."""
    result = dataframe.copy()

    if "country_name" not in result.columns:
        result["country_name"] = "Não informado"

    result["country_name"] = (
        result["country_name"]
        .fillna("Não informado")
        .astype(str)
    )

    result["continent"] = (
        result["country_name"]
        .map(COUNTRY_CONTINENT)
        .fillna("Outros")
    )

    return result


def load_laps_for_meetings(meetings_dataframe, session_name):
    """Carrega as voltas das etapas selecionadas."""
    entries = []

    if meetings_dataframe.empty:
        return pd.DataFrame()

    total = len(meetings_dataframe)
    progress = st.progress(0, text="Carregando voltas...")

    try:
        for index, (_, meeting) in enumerate(
            meetings_dataframe.iterrows(),
            start=1,
        ):
            try:
                meeting_key = int(meeting["meeting_key"])
                meeting_laps = fetch_top_laps(
                    meeting_key,
                    session_name,
                )

                for lap in meeting_laps:
                    lap["meeting_key"] = meeting_key
                    lap["meeting_name"] = meeting.get(
                        "meeting_name",
                        "Etapa não informada",
                    )
                    lap["circuit_short_name"] = meeting.get(
                        "circuit_short_name",
                        "Não informado",
                    )
                    lap["country_name"] = meeting.get(
                        "country_name",
                        "Não informado",
                    )
                    lap["continent"] = meeting.get(
                        "continent",
                        "Outros",
                    )

                entries.extend(meeting_laps)

            except Exception as error:
                st.warning(
                    f"Não foi possível carregar a etapa "
                    f"{meeting.get('meeting_name', 'desconhecida')}: "
                    f"{error}"
                )

            progress.progress(
                index / total,
                text=f"Etapa {index} de {total}",
            )
    finally:
        progress.empty()

    if not entries:
        return pd.DataFrame()

    dataframe = pd.DataFrame(entries)

    dataframe = ensure_columns(
        dataframe,
        {
            "meeting_key": pd.NA,
            "meeting_name": "Não informado",
            "circuit_short_name": "Não informado",
            "country_name": "Não informado",
            "continent": "Outros",
            "driver_name": "Não informado",
            "driver_acronym": "N/D",
            "team_name": "Não informado",
            "team_colour": "#808080",
            "lap_number": pd.NA,
            "lap_duration": pd.NA,
            "rank": pd.NA,
        },
    )

    dataframe["lap_duration"] = pd.to_numeric(
        dataframe["lap_duration"],
        errors="coerce",
    )

    dataframe = dataframe.dropna(subset=["lap_duration"]).copy()
    dataframe = dataframe[dataframe["lap_duration"] > 0].copy()

    dataframe["lap_duration_fmt"] = dataframe[
        "lap_duration"
    ].apply(format_lap_time)

    dataframe["team_colour"] = dataframe["team_colour"].apply(
        normalize_color
    )

    return dataframe


# ============================================================
# TABELAS E GRÁFICOS POR PÁGINA
# ============================================================

def show_races(meetings):
    st.header("🏁 Corridas")
    st.caption("Etapas correspondentes aos filtros selecionados.")

    if meetings.empty:
        st.info("Nenhuma corrida encontrada para os filtros.")
        return

    race_table = ensure_columns(
        meetings,
        {
            "meeting_name": "Não informado",
            "circuit_short_name": "Não informado",
            "country_name": "Não informado",
            "continent": "Outros",
            "date_start": pd.NA,
            "meeting_key": pd.NA,
        },
    )

    race_table = race_table.rename(
        columns={
            "meeting_name": "Etapa",
            "circuit_short_name": "Circuito",
            "country_name": "País",
            "continent": "Continente",
            "date_start": "Data de início",
            "meeting_key": "ID da etapa",
        }
    )

    possible_columns = [
        "Etapa",
        "Circuito",
        "País",
        "Continente",
        "Data de início",
        "ID da etapa",
    ]

    race_table = race_table[
        [column for column in possible_columns if column in race_table]
    ]

    st.metric("Total de etapas", len(meetings))

    chart_data = (
        meetings.groupby("country_name", dropna=False)
        .size()
        .reset_index(name="Quantidade de etapas")
        .sort_values("Quantidade de etapas", ascending=False)
    )

    make_bar_chart(
        chart_data,
        "country_name",
        "Quantidade de etapas",
        "Etapas por país",
        "País",
        "Quantidade de etapas",
    )

    st.subheader("Tabela de corridas")
    st.dataframe(race_table, use_container_width=True, hide_index=True)


def show_drivers(laps):
    st.header("👤 Pilotos")
    st.caption(
        "Estatísticas dos pilotos presentes nas voltas retornadas "
        "para as etapas filtradas."
    )

    if laps.empty:
        st.info("Não há dados de pilotos para os filtros selecionados.")
        return

    drivers = (
        laps.groupby(
            ["driver_name", "driver_acronym", "team_name"],
            dropna=False,
        )
        .agg(
            Voltas_no_recorte=("lap_duration", "count"),
            Melhor_volta_segundos=("lap_duration", "min"),
            Etapas_com_dados=("meeting_key", "nunique"),
        )
        .reset_index()
        .sort_values("Melhor_volta_segundos")
    )

    drivers["Melhor volta"] = drivers["Melhor_volta_segundos"].apply(
        format_lap_time
    )

    drivers = drivers.rename(
        columns={
            "driver_name": "Piloto",
            "driver_acronym": "Sigla",
            "team_name": "Equipe",
            "Etapas_com_dados": "Etapas",
            "Voltas_no_recorte": "Voltas retornadas",
        }
    )

    st.metric("Pilotos encontrados", len(drivers))

    chart_data = drivers.nlargest(10, "Voltas retornadas")

    make_bar_chart(
        chart_data,
        "Sigla",
        "Voltas retornadas",
        "Pilotos com mais voltas retornadas (Top 10)",
        "Piloto",
        "Quantidade de voltas",
    )

    st.subheader("Tabela de pilotos")
    st.dataframe(
        drivers[
            [
                "Piloto",
                "Sigla",
                "Equipe",
                "Voltas retornadas",
                "Etapas",
                "Melhor volta",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


def show_teams(laps):
    st.header("👥 Equipes")
    st.caption(
        "Comparação baseada nas voltas retornadas para os filtros atuais."
    )

    if laps.empty:
        st.info("Não há dados de equipes para os filtros selecionados.")
        return

    teams = (
        laps.groupby("team_name", dropna=False)
        .agg(
            Voltas_retornadas=("lap_duration", "count"),
            Melhor_volta_segundos=("lap_duration", "min"),
            Pilotos=("driver_name", "nunique"),
            Etapas=("meeting_key", "nunique"),
        )
        .reset_index()
        .sort_values("Melhor_volta_segundos")
    )

    teams["Melhor volta"] = teams["Melhor_volta_segundos"].apply(
        format_lap_time
    )

    teams = teams.rename(
        columns={
            "team_name": "Equipe",
            "Voltas_retornadas": "Voltas retornadas",
        }
    )

    st.metric("Equipes encontradas", len(teams))

    chart_data = teams.sort_values(
        "Voltas retornadas",
        ascending=False,
    )

    make_bar_chart(
        chart_data,
        "Equipe",
        "Voltas retornadas",
        "Voltas retornadas por equipe",
        "Equipe",
        "Quantidade de voltas",
    )

    st.subheader("Tabela de equipes")
    st.dataframe(
        teams[
            [
                "Equipe",
                "Voltas retornadas",
                "Pilotos",
                "Etapas",
                "Melhor volta",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


def show_laps(laps):
    st.header("⏱️ Voltas")
    st.caption("Voltas retornadas pelo serviço para as etapas selecionadas.")

    if laps.empty:
        st.info("Não há voltas para os filtros selecionados.")
        return

    lap_table = laps.sort_values("lap_duration").copy()

    st.metric("Voltas disponíveis", len(lap_table))
    st.metric(
        "Melhor volta no recorte",
        format_lap_time(lap_table["lap_duration"].min()),
    )

    chart_data = lap_table.nsmallest(10, "lap_duration").copy()
    chart_data["Piloto"] = chart_data["driver_acronym"].astype(str)
    chart_data["Identificação"] = (
        chart_data["Piloto"]
        + " — "
        + chart_data["meeting_name"].astype(str)
    )

    make_bar_chart(
        chart_data,
        "Identificação",
        "lap_duration",
        "10 melhores tempos de volta no recorte",
        "Piloto e etapa",
        "Tempo (segundos)",
    )

    st.subheader("Tabela de voltas")

    display = lap_table.rename(
        columns={
            "meeting_name": "Etapa",
            "circuit_short_name": "Circuito",
            "country_name": "País",
            "driver_name": "Piloto",
            "driver_acronym": "Sigla",
            "team_name": "Equipe",
            "lap_number": "Número da volta",
            "lap_duration_fmt": "Tempo",
            "rank": "Posição retornada",
        }
    )

    columns = [
        "Etapa",
        "Circuito",
        "País",
        "Piloto",
        "Sigla",
        "Equipe",
        "Número da volta",
        "Tempo",
        "Posição retornada",
    ]

    display = display[
        [column for column in columns if column in display.columns]
    ]

    st.dataframe(display, use_container_width=True, hide_index=True)


def show_results(laps):
    st.header("📊 Resultados")
    st.caption(
        "Resumo comparativo do recorte filtrado. "
        "Não equivale à classificação oficial do campeonato."
    )

    if laps.empty:
        st.info("Não há resultados para os filtros selecionados.")
        return

    results = (
        laps.groupby(
            ["driver_name", "driver_acronym", "team_name"],
            dropna=False,
        )
        .agg(
            Melhor_volta_segundos=("lap_duration", "min"),
            Voltas_retornadas=("lap_duration", "count"),
            Etapas=("meeting_key", "nunique"),
        )
        .reset_index()
        .sort_values("Melhor_volta_segundos")
    )

    results["Melhor volta"] = results["Melhor_volta_segundos"].apply(
        format_lap_time
    )
    results.insert(
        0,
        "Posição no recorte",
        range(1, len(results) + 1),
    )

    results = results.rename(
        columns={
            "driver_name": "Piloto",
            "driver_acronym": "Sigla",
            "team_name": "Equipe",
            "Voltas_retornadas": "Voltas retornadas",
        }
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Pilotos", results["Piloto"].nunique())
    col2.metric("Equipes", results["Equipe"].nunique())
    col3.metric("Etapas", laps["meeting_key"].nunique())

    chart_data = results.head(10).copy()

    make_bar_chart(
        chart_data,
        "Sigla",
        "Melhor_volta_segundos",
        "Melhores tempos por piloto (Top 10)",
        "Piloto",
        "Melhor volta (segundos)",
    )

    st.subheader("Tabela de resultados")
    st.dataframe(
        results[
            [
                "Posição no recorte",
                "Piloto",
                "Sigla",
                "Equipe",
                "Melhor volta",
                "Voltas retornadas",
                "Etapas",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# APLICAÇÃO PRINCIPAL
# ============================================================

def main():
    st.title("🏎️ Dashboard de Fórmula 1")
    st.caption(
        "Explore corridas, pilotos, equipes, voltas e resultados "
        "usando os filtros da barra lateral."
    )

    with st.sidebar:
        st.header("Filtros")
        st.divider()
        pagina = st.radio(
            "Navegação",
            options=[
                "🏁 Corridas",
                "👥 Equipes",
                "👤 Pilotos",
                "⏱️ Voltas",
                "📊 Resumo Geral",
            ],
            index=0,
            key="pagina_dashboard",
        )

        st.divider()

        ano_inicial = (
            DEFAULT_YEAR
            if DEFAULT_YEAR in ANOS_DISPONIVEIS
            else ANOS_DISPONIVEIS[-1]
        )

        ano = st.selectbox(
            "Temporada",
            options=ANOS_DISPONIVEIS,
            index=ANOS_DISPONIVEIS.index(ano_inicial),
        )
        st.divider()
        session_name = st.selectbox(
            "Tipo de sessão",
            options=["Race", "Qualifying"],
            format_func=lambda value: (
                "Corrida" if value == "Race" else "Classificação"
            ),
        )

    # 1. Carregar etapas para o ano escolhido.
    try:
        meetings_data = fetch_meetings(int(ano))
    except Exception as error:
        st.error(f"Não foi possível carregar as etapas: {error}")
        st.stop()

    if not meetings_data:
        st.warning(f"Nenhuma etapa encontrada para {ano}.")
        st.stop()

    meetings = pd.DataFrame(meetings_data)

    meetings = ensure_columns(
        meetings,
        {
            "meeting_key": pd.NA,
            "meeting_name": "Não informado",
            "circuit_short_name": "Não informado",
            "country_name": "Não informado",
            "date_start": pd.NA,
        },
    )

    meetings = add_geography(meetings)

    # 2. Filtros geográficos dependentes.
    with st.sidebar:
        st.divider()
        st.subheader("🌎 Localização")

        continent_options = ["Todos"] + sorted(
            meetings["continent"].dropna().unique().tolist()
        )

        selected_continent = st.selectbox(
            "Continente",
            options=continent_options,
        )

        if selected_continent == "Todos":
            continent_meetings = meetings.copy()
        else:
            continent_meetings = meetings[
                meetings["continent"] == selected_continent
            ].copy()

        country_options = sorted(
            continent_meetings["country_name"].dropna().unique().tolist()
        )

        selected_countries = st.multiselect(
            "Países",
            options=country_options,
            default=country_options,
        )

        country_meetings = continent_meetings[
            continent_meetings["country_name"].isin(selected_countries)
        ].copy()

        circuit_options = sorted(
            country_meetings["circuit_short_name"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_circuits = st.multiselect(
            "Circuitos",
            options=circuit_options,
            default=circuit_options,
        )

    # 3. Aplicar os filtros à tabela de etapas.
    selected_meetings = country_meetings[
        country_meetings["circuit_short_name"].isin(selected_circuits)
    ].copy()

    if selected_meetings.empty:
        st.warning(
            "Nenhuma etapa corresponde aos filtros. "
            "Altere o continente, os países ou os circuitos."
        )
        st.stop()

    # A página Corridas usa a tabela de etapas diretamente.
    if pagina == "🏁 Corridas":
        show_races(selected_meetings)
        return

    # 4. Carregar as voltas apenas para as etapas selecionadas.
    with st.spinner("Preparando os dados para os filtros selecionados..."):
        laps = load_laps_for_meetings(
            selected_meetings,
            session_name,
        )

    if laps.empty:
        st.warning(
            "Não foram encontradas voltas válidas para esta combinação "
            "de temporada, sessão e filtros geográficos."
        )
        return

    # 5. Mostrar a página escolhida.
    if pagina == "👤 Pilotos":
        show_drivers(laps)

    elif pagina == "👥 Equipes":
        show_teams(laps)

    elif pagina == "⏱️ Voltas":
        show_laps(laps)

    elif pagina == "📊 Resultados":
        show_results(laps)


if __name__ == "__main__":
    main()
