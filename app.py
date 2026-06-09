import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Premier League Dashboard",
    page_icon="⚽",
    layout="wide"
)

with st.expander("About this dashboard"):
    st.write("""
    This dashboard analyses Premier League team performance across multiple seasons.
    It uses match result data to calculate league tables, win rates, goal trends,
    home/away performance, form, and club history.
    """)

season_files = {}

for start_year in range(1993, 2026):
    end_year = start_year + 1

    label = f"{start_year}/{str(end_year)[-2:]}"
    file_name = f"data/matches_{start_year}_{str(end_year)[-2:]}.csv"

    season_files[label] = file_name

season = st.sidebar.selectbox(
    "Choose a season",
    list(season_files.keys())[::-1]
)

df = pd.read_csv(
    season_files[season],
    encoding="latin1",
    on_bad_lines="skip"
)

df = df.dropna(subset=["HomeTeam", "AwayTeam"])

df["HomeTeam"] = df["HomeTeam"].astype(str)
df["AwayTeam"] = df["AwayTeam"].astype(str)

teams = sorted(set(df["HomeTeam"]).union(set(df["AwayTeam"])))

TEAM_BADGES = {
    "Arsenal": "arsenal.png",
    "Chelsea": "chelsea.png",
    "Aston Villa": "aston_villa.png",
    "Bournemouth": "bournemouth.png",
    "Brentford": "brentford.png",
    "Brighton": "brighton.png",
    "Burnley": "burnley.png",
    "Everton": "everton.png",
    "Fulham": "fulham.png",
    "Liverpool": "liverpool.png",
    "Leeds": "leeds.png",
    "Sunderland": "sunderland.png",
    "Man City": "manchester_city.png",
    "Man United": "manchester_united.png",
    "Crystal Palace": "crystal_palace.png",
    "Nott'm Forest": "nottingham_forest.png",
    "Spurs": "tottenham.png",
    "Newcastle": "newcastle.png",
    "West Ham": "west_ham.png",
    "Wolves": "wolves.png",
}

def build_league_table(matches_data, teams_list):
    table = []

    for club in teams_list:
        club_matches = matches_data[
            (matches_data["HomeTeam"] == club) |
            (matches_data["AwayTeam"] == club)
        ]

        played = len(club_matches)
        wins = 0
        draws = 0
        losses = 0
        goals_for = 0
        goals_against = 0

        for _, row in club_matches.iterrows():
            if row["HomeTeam"] == club:
                goals_for += row["FTHG"]
                goals_against += row["FTAG"]

                if row["FTR"] == "H":
                    wins += 1
                elif row["FTR"] == "D":
                    draws += 1
                else:
                    losses += 1
            else:
                goals_for += row["FTAG"]
                goals_against += row["FTHG"]

                if row["FTR"] == "A":
                    wins += 1
                elif row["FTR"] == "D":
                    draws += 1
                else:
                    losses += 1

        goal_difference = goals_for - goals_against
        points = wins * 3 + draws

        table.append({
            "Team": club,
            "P": played,
            "W": wins,
            "D": draws,
            "L": losses,
            "GF": goals_for,
            "GA": goals_against,
            "GD": goal_difference,
            "Pts": points
        })

    league_table = pd.DataFrame(table)

    league_table = league_table.sort_values(
        by=["Pts", "GD", "GF"],
        ascending=[False, False, False]
    ).reset_index(drop=True)

    league_table.insert(0, "Pos", league_table.index + 1)

    return league_table

st.markdown(
    f"""
# ⚽ Premier League Performance Dashboard
Analyze team performance, results, goals, form, and league position for the {season} Premier League Season.
""")

st.caption(f"Season: {season}")

st.sidebar.header("Filters")
team = st.sidebar.selectbox("Choose a team", teams)

sidebar_badge_file = TEAM_BADGES.get(
    team,
    f"{team.lower().replace(' ', '_')}.png"
)
sidebar_badge_path = f"assets/{sidebar_badge_file}"

st.sidebar.image(sidebar_badge_path, width=120)

team_matches = df[
    (df["HomeTeam"] == team) | (df["AwayTeam"] == team)
]

wins = 0
draws = 0
losses = 0
goals_for = 0
goals_against = 0

for _, row in team_matches.iterrows():
    if row["HomeTeam"] == team:
        goals_for += row["FTHG"]
        goals_against += row["FTAG"]

        if row["FTR"] == "H":
            wins += 1
        elif row["FTR"] == "D":
            draws += 1
        else:
            losses += 1
    else:
        goals_for += row["FTAG"]
        goals_against += row["FTHG"]

        if row["FTR"] == "A":
            wins += 1
        elif row["FTR"] == "D":
            draws += 1
        else:
            losses += 1

matches_played = wins + draws + losses
win_rate = round((wins / matches_played) * 100, 1) if matches_played > 0 else 0
goal_difference = goals_for - goals_against
points = wins * 3 + draws

st.divider()

badge_file = TEAM_BADGES.get(
    team,
    f"{team.lower().replace(' ', '_')}.png"
)
badge_path = f"assets/{badge_file}"

left, right = st.columns([1, 6])

with left:
    try:
        st.image(badge_path, width=100)
    except:
        st.write("")

with right:
    st.subheader(f"{team} Overview")

league_table = build_league_table(df, teams)

position = league_table.loc[
    league_table["Team"] == team,
    "Pos"
].iloc[0]

if position == 1:
    season_status = "Champions"
elif position <= 4:
    season_status = "Champions League"
elif position <= 6:
    season_status = "European Places"
elif position >= 18:
    season_status = "Relegated"
else:
    season_status = "Mid Table"

col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

col1.metric("Position", position)
col2.metric("Matches", matches_played)
col3.metric("Points", points)
col4.metric("Win Rate", f"{win_rate}%")
col5.metric("Goals Scored", goals_for)
col6.metric("Goals Conceded", goals_against)
col7.metric("Goal Difference", goal_difference)
col8.metric("Season Outcome", season_status)

st.divider()

st.subheader("📊 Performance Breakdown")

results_df = pd.DataFrame({
    "Result": ["Wins", "Draws", "Losses"],
    "Count": [wins, draws, losses]
})

fig = px.bar(
    results_df,
    x="Result",
    y="Count",
    title=f"{team} Results Breakdown"
)

pie_fig = px.pie(
    results_df,
    names="Result",
    values="Count",
    title=f"{team} Result Distribution"
)

left, right = st.columns(2)

with left:
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.plotly_chart(pie_fig, use_container_width=True)

home_matches = df[df["HomeTeam"] == team]
away_matches = df[df["AwayTeam"] == team]

home_wins = len(home_matches[home_matches["FTR"] == "H"])
away_wins = len(away_matches[away_matches["FTR"] == "A"])

home_win_pct = (
    round((home_wins / len(home_matches)) * 100, 1)
    if len(home_matches) > 0 else 0
)

away_win_pct = (
    round((away_wins / len(away_matches)) * 100, 1)
    if len(away_matches) > 0 else 0
)

home_away_df = pd.DataFrame({
    "Location": ["Home", "Away"],
    "Win Rate": [home_win_pct, away_win_pct]
})

home_away_fig = px.bar(
    home_away_df,
    x="Location",
    y="Win Rate",
    title=f"{team} Home vs Away Win Rate",
    text="Win Rate"
)

home_away_fig.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

home_away_fig.update_yaxes(
    title="Win Percentage",
    range=[0, 100]
)

col1, col2 = st.columns(2)

col1.metric("Home Win %", f"{home_win_pct}%")
col2.metric("Away Win %", f"{away_win_pct}%")

st.plotly_chart(home_away_fig, use_container_width=True)

st.divider()

st.divider()

st.subheader(f"{team} Premier League History")

history_rows = []

for label, file_path in season_files.items():
    try:
        season_df = pd.read_csv(
            file_path,
            encoding="latin1",
            on_bad_lines="skip"
        )

        season_df = season_df.dropna(subset=["HomeTeam", "AwayTeam"])

        season_df["HomeTeam"] = season_df["HomeTeam"].astype(str)
        season_df["AwayTeam"] = season_df["AwayTeam"].astype(str)

        season_teams = sorted(
            set(season_df["HomeTeam"]).union(set(season_df["AwayTeam"]))
        )

        if team not in season_teams:
            continue

        season_table = build_league_table(season_df, season_teams)

        team_row = season_table[season_table["Team"] == team].iloc[0]

        history_rows.append({
            "Season": label,
            "Position": team_row["Pos"],
            "Points": team_row["Pts"],
            "Wins": team_row["W"],
            "Goals For": team_row["GF"],
            "Goals Against": team_row["GA"],
            "Goal Difference": team_row["GD"]
        })

    except:
        continue

history_df = pd.DataFrame(history_rows)

if not history_df.empty:
    seasons_played = len(history_df)
    highest_finish = history_df["Position"].min()
    lowest_finish = history_df["Position"].max()
    average_finish = round(history_df["Position"].mean(), 1)
    total_wins = history_df["Wins"].sum()
    total_goals = history_df["Goals For"].sum()

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("PL Seasons", seasons_played)
    col2.metric("Highest Finish", highest_finish)
    col3.metric("Lowest Finish", lowest_finish)
    col4.metric("Average Finish", average_finish)
    col5.metric("Total Wins", total_wins)
    col6.metric("Total Goals", total_goals)

    best_season = history_df.loc[history_df["Points"].idxmax()]
    worst_season = history_df.loc[history_df["Position"].idxmax()]

    col1, col2 = st.columns(2)

    col1.metric(
    "Best PL Season",
    f"{best_season['Season']} - {best_season['Points']} pts"
)


    col2.metric(
    "Worst PL Season",
    f"{worst_season['Season']} - {worst_season['Position']} place"
)

    points_fig = px.line(
    history_df.sort_values("Season"),
    x="Season",
    y="Points",
    markers=True,
    title=f"{team} Points by Season"
)

    points_fig.update_layout(
    xaxis_tickangle=-45
)

    st.plotly_chart(points_fig, use_container_width=True)

    history_fig = px.line(
        history_df.sort_values("Season"),
        x="Season",
        y="Position",
        markers=True,
        title=f"League Finish by Season"
    )

    history_fig.update_layout(
    xaxis_tickangle=-45
    )

    history_fig.update_yaxes(
        autorange="reversed",
        dtick=1
    )

    st.plotly_chart(history_fig, use_container_width=True)

    with st.expander("View full club history"):
        st.dataframe(
            history_df.sort_values("Season", ascending=False),
            use_container_width=True,
            hide_index=True
        )
else:
    st.info(f"No Premier League history found for {team}.")

st.divider()

st.subheader("📈 Position History")

position_data = df.copy()

position_data["ParsedDate"] = pd.to_datetime(
    position_data["Date"],
    dayfirst=True,
    errors="coerce"
)

position_data = position_data.dropna(subset=["ParsedDate"])
position_data = position_data.sort_values("ParsedDate")

matches_per_gameweek = len(teams) // 2

position_history = []

for gameweek in range(1, (len(position_data) // matches_per_gameweek) + 1):
    matches_so_far = position_data.iloc[:gameweek * matches_per_gameweek]

    table_so_far = build_league_table(matches_so_far, teams)

    team_position = table_so_far.loc[
        table_so_far["Team"] == team,
        "Pos"
    ].iloc[0]

    position_history.append({
        "Gameweek": gameweek,
        "Position": team_position
    })

position_history_df = pd.DataFrame(position_history)

position_fig = px.line(
    position_history_df,
    x="Gameweek",
    y="Position",
    markers=True,
    title="Position History by Gameweek"
)

position_fig.update_yaxes(
    autorange="reversed",
    dtick=1
)

st.plotly_chart(position_fig, use_container_width=True)

goals_df = pd.DataFrame({
    "Metric": ["Goals For", "Goals Against"],
    "Goals": [goals_for, goals_against]
})

goals_fig = px.bar(
    goals_df,
    x="Metric",
    y="Goals",
    title=f"{team} Goals For vs Goals Against"
)

st.plotly_chart(goals_fig, use_container_width=True)

st.divider()

st.subheader("📅 Recent Form")

last_five = team_matches.tail(5)

form = []

for _, row in last_five.iterrows():
    if row["HomeTeam"] == team:
        if row["FTR"] == "H":
            form.append("🟢 W")
        elif row["FTR"] == "D":
            form.append("🟡 D")
        else:
            form.append("🔴 L")
    else:
        if row["FTR"] == "A":
            form.append("🟢 W")
        elif row["FTR"] == "D":
            form.append("🟡 D")
        else:
            form.append("🔴 L")

st.markdown("### Last 5 Results")
st.write(" ".join(form))

recent_matches = last_five[
    ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]
].copy()

recent_matches["FTR"] = recent_matches["FTR"].replace({
    "H": "Home Win",
    "A": "Away Win",
    "D": "Draw"
})

st.dataframe(
    recent_matches,
    column_config={
        "Date": "Date",
        "HomeTeam": "Home Team",
        "AwayTeam": "Away Team",
        "FTHG": "Home Goals",
        "FTAG": "Away Goals",
        "FTR": "Result"
    },
    use_container_width=True,
    hide_index=True
)

st.divider()

st.subheader("🏆 League  Standings")

league_table = build_league_table(df, teams)

position = league_table.loc[
    league_table["Team"] == team,
    "Pos"
].iloc[0]          

if position == 1:
    season_status = "🏆 Champions"
elif position <= 4:
    season_status = "⭐ Champions League"
elif position <= 6:
    season_status = "🌍 European Places"
elif position >= 18:
    season_status = "⬇️ Relegated"
else:
    season_status = "⚽ Mid Table"

def highlight_team(row):

    if row["Team"] == team:
        return ["background-color: #1E3A5F"] * len(row)

    if row["Pos"] <= 4:
        return ["background-color: #16351A"] * len(row)

    if row["Pos"] >= len(league_table) - 2:
        return ["background-color: #3A1616"] * len(row)

    return [""] * len(row)

styled_table = league_table.style.apply(
    highlight_team,
    axis=1
)

st.dataframe(
    styled_table,
    use_container_width=True,
    hide_index=True
)

st.divider()

display_matches = team_matches[
    ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]
].copy()

display_matches["FTR"] = display_matches["FTR"].replace({
    "H": "Home Win",
    "A": "Away Win",
    "D": "Draw"
})

with st.expander(f"View {team} Match History"):
    st.dataframe(
        display_matches,
        column_config={
            "Date": st.column_config.DateColumn(
                "Date",
                help="Match date"
            ),
            "HomeTeam": st.column_config.TextColumn(
                "Home Team",
                help="Team playing at home"
            ),
            "AwayTeam": st.column_config.TextColumn(
                "Away Team",
                help="Team playing away"
            ),
            "FTHG": st.column_config.NumberColumn(
                "Home Goals",
                help="Full Time Home Goals"
            ),
            "FTAG": st.column_config.NumberColumn(
                "Away Goals",
                help="Full Time Away Goals"
            ),
            "FTR": st.column_config.TextColumn(
                "Result",
                help="Match result"
            )
        },
        hide_index=True,
        use_container_width=True
    )


    st.divider()

    st.caption("Premier League Dashboard | Built with Python, Pandas, Plotly and Streamlit |Data source: Football-Data.co.uk match result CSVs")