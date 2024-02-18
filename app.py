from math import log10
import time

import streamlit as st

from table import FixturesTable, TeamNames


st.set_page_config(page_title="UWSU FIFA Tournament", page_icon="🎮", layout="wide")

if "table" not in st.session_state:
    st.session_state["table"] = None

if "teams" not in st.session_state:
    st.session_state["teams"] = TeamNames()


st.title("UWSU FIFA Tournament")


def get_css(table):

    return f"""
    <style>
        .fixture-container {{
            display: flex;
            background-color: rgb(180, 180, 210);
            border-radius: 5px;
            padding: 4px;
            line-hieght: 1;
        }}
        .fixture-teams {{
            width: 70%;
            line-height: 1;
        }}
        .fixture-id {{
            width: 30%;
            color: black;
            background-color: rgb(200, 200, 230);
            font-size: 2.3rem;
            display: flex;
            justify-content: center;
            align-items: center;    
        }}

        .fixtures-col {{
            height: {90 * len(table.graph_data["cols"][0])}px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
        }}
    </style>
    """


def get_fixture_img(fixture):
    t1score = fixture.team1_score
    t2score = fixture.team2_score

    if t1score is None or t2score is None or t1score == t2score:
        pipe2_color = pipe1_color = "rgb(200, 200, 230)"
    elif t1score > t2score:
        pipe1_color = "green"
        pipe2_color = "red"
    else:
        pipe1_color = "red"
        pipe2_color = "green"

    return f"""
            <div class="fixture-container">
                <div class="fixture-teams">
                    <span>{fixture.team1 if fixture.team1 else '😎'} <span style="color: {pipe1_color}">|</span> {t1score if t1score is not None else '-'}</span>
                    <br>
                    <span>vs</span>
                    <br>
                    <span>{fixture.team2 if fixture.team2 else '😎'} <span style="color: {pipe2_color}">|</span> {t2score if t2score is not None else '-'}</span>
                </div>
                <div class="fixture-id">
                    {fixture.id}
                </div>
            </div>
            """


def get_fixtures_display(fixtures):
    fixtures = "".join([get_fixture_img(f) for f in fixtures])

    return f"""
            <div class="fixtures-col">{fixtures}</div>
            """


team_names_tab, team_tables_tab = st.tabs(["Team Names", "Table"])

with team_names_tab:
    cols = st.columns(2)
    with cols[0]:
        st.header("Teams Details")
    with cols[1]:
        with st.columns(2)[-1]:
            number_of_teams = st.number_input(
                "Number of teams", min_value=2, max_value=512, value=16
            )
            if log10(number_of_teams) / log10(2) % 1 != 0:
                st.error("Number of teams must be a whole power of 2!", icon="🚫")
                st.stop()

            table = st.session_state["table"]
            if table is None or table.no_of_teams != number_of_teams:
                table = FixturesTable(number_of_teams)
                st.session_state["table"] = table

    name_input_col, teams_col = st.columns((2, 3))
    with name_input_col:
        if st.session_state["teams"].num_names < number_of_teams:

            def add_team():
                st.session_state["teams"].add_name(st.session_state["team_to_add"])

            st.text_input(
                "Team name",
                placeholder="Enter team name...",
                label_visibility="hidden",
                key="team_to_add",
                on_change=add_team,
            )
        else:

            def full_msg():
                msg = "All teams have been entered. Click on any to edit. 😊"
                for m in msg.split(" "):
                    yield m + " "
                    time.sleep(0.05)

            st.write_stream(full_msg())

        def delete_name():
            st.session_state["teams"].delete_name(st.session_state["to_delete"])

        with st.form("Delete form", clear_on_submit=False):
            st.number_input(
                "Team to delete",
                min_value=0 if st.session_state["teams"].num_names == 0 else 1,
                max_value=st.session_state["teams"].num_names,
                placeholder="Enter a team number to delete",
                label_visibility="collapsed",
                key="to_delete",
            )
            st.form_submit_button("Delete", on_click=delete_name)

    with teams_col:
        st.write(" || ".join(st.session_state["teams"].names))


with team_tables_tab:
    st.markdown(get_css(table), unsafe_allow_html=True)
    if (
        st.session_state["teams"] is None
        or st.session_state["teams"].num_names < number_of_teams
    ):
        st.info(f"Enter all {number_of_teams} teams names to randomise table...")
        st.session_state["table"].reset_table()
    else:

        def reset_table():
            table.reset_table()

        def randomise_table():
            table.randomise_table(
                [TeamNames.strip_name(name) for name in st.session_state["teams"].names]
            )
            st.balloons()

        set_table_col, set_match_col = st.columns(2)
        with set_table_col:
            if st.session_state["table"].game_started:
                st.button("Reset Table", on_click=reset_table)
            else:
                st.button("Randomise/Recreate Table", on_click=randomise_table)
        with set_match_col:
            fixture_id_col, team1_score_col, team2_score_col, set_btn = st.columns(4)
            with fixture_id_col:
                st.selectbox(
                    "Fixture ID",
                    options=[i for i in range(1, table.no_of_fixtures + 1)],
                    key="fixture_id",
                )
            with team1_score_col:
                st.number_input("Team 1 Score", min_value=0, key="team1_score")
            with team2_score_col:
                st.number_input("Team 2 Score", min_value=0, key="team2_score")
            with set_btn:
                st.write("")
                st.button(
                    "Set Match",
                    on_click=table.set_match,
                    args=(
                        st.session_state["fixture_id"],
                        st.session_state["team1_score"],
                        st.session_state["team2_score"],
                    ),
                )

    st_cols = st.columns(table.graph_data["no_cols"])
    for idx, fixtures in enumerate(table.graph_data["cols"]):
        with st_cols[idx]:
            fixtures_display = get_fixtures_display(fixtures)
            st.markdown(fixtures_display, unsafe_allow_html=True)
