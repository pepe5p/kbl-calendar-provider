import requests
from icalendar.cal import Calendar
from loguru import logger
from requests import Response

from game_event import GameEvent

SUBTOURNAMENT_URL = "https://api.turniej-generator.pl/tournament/getSubtournamentData"


class CannotFetchDataError(Exception):
    pass


class NoGamesForTeamError(Exception):
    pass


def create_calendar(
    tournament_id: int,
    subtournament_id: int,
    team_id: int,
) -> Calendar:
    try:
        response = fetch_subtournament_data(tournament_id=tournament_id, subtournament_id=subtournament_id)
    except requests.exceptions.RequestException as e:
        raise CannotFetchDataError() from e

    response_json = response.json()
    team_name = get_team_name(response_json=response_json, team_id=team_id)
    game_events = construct_game_events(response_json=response_json, team_id=team_id)
    if not game_events:
        raise NoGamesForTeamError()

    return create_ical(game_events=game_events, team_name=team_name)


def fetch_subtournament_data(tournament_id: int, subtournament_id: int) -> Response:
    data = {
        "tournament_id": tournament_id,
        "subtournament_id": subtournament_id,
    }
    return requests.post(
        url=SUBTOURNAMENT_URL,
        json=data,
        headers={"Content-Type": "application/json"},
    )


def get_team_name(response_json: dict, team_id: int) -> str:
    for member in response_json["members"]:
        if member["member_id"] == team_id:
            return member["name"]

    logger.error(f"Team with ID {team_id} not found in the response.")
    return "<unknown>"


def construct_game_events(response_json: dict, team_id: int) -> list[GameEvent]:
    game_events = []

    for round_ in response_json["tournament_json"]:
        for match in round_["matches"]:
            home_team_id = match["member1_id"]
            away_team_id = match["member2_id"]
            if team_id not in (home_team_id, away_team_id):
                continue

            match_date = match["match_date"]
            if not match_date:
                continue

            home_team_name = match["member1_name"]
            away_team_name = match["member2_name"]
            home_team_score = match["member1_score"]
            away_team_score = match["member2_score"]
            match_info = match["match_info"]
            match_location = match_info["match_place"]["value"]
            match_video = match_info["match_video"]["value"]
            google_photo = match_info["google_photo"]["value"]
            match_report = match_info["match_report"]["value"]

            game_event_data = GameEvent(
                home_team_name=home_team_name,
                away_team_name=away_team_name,
                match_datetime_raw=match_date,
                home_team_score=home_team_score,
                away_team_score=away_team_score,
                match_location=match_location,
                match_video=match_video,
                google_photo=google_photo,
                match_report=match_report,
            )
            game_events.append(game_event_data)

    return game_events


def create_ical(game_events: list[GameEvent], team_name: str) -> Calendar:
    cal = Calendar()
    cal.add("PRODID", "-//Piotr Karaś//KBL Calendar Provider//1.0.0")
    cal.add("VERSION", "2.0")
    cal.add("X-WR-CALNAME", f"KBL {team_name}")
    cal.add("X-WR-TIMEZONE", "Europe/Warsaw")
    cal.add("CALSCALE", "GREGORIAN")
    cal.add("X-PUBLISHED-TTL", "PT12H")

    for game_event in game_events:
        ical_event = game_event.to_ical_event()
        cal.add_component(component=ical_event)

    return cal
