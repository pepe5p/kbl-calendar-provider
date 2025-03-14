from calendar_creating import create_calendar

TOURNAMENT_ID = 1588
SUBTOURNAMENT_ID = 3093
TEAM_ID = 8204  # CTF White Mambas

calendar = create_calendar(
    tournament_id=TOURNAMENT_ID,
    subtournament_id=SUBTOURNAMENT_ID,
    team_id=TEAM_ID,
)

with open("white_mambas.ics", "wb") as f:
    f.write(calendar.to_ical())
