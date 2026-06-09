import requests

for start_year in range(1993, 2026):
    end_year = start_year + 1

    season_code = f"{str(start_year)[-2:]}{str(end_year)[-2:]}"
    season_name = f"{start_year}_{str(end_year)[-2:]}"

    url = f"https://www.football-data.co.uk/mmz4281/{season_code}/E0.csv"
    file_path = f"data/matches_{season_name}.csv"

    response = requests.get(url)

    if response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)

        print(f"Downloaded {season_name}")
    else:
        print(f"Failed: {season_name}")