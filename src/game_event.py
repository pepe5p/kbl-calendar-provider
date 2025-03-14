from datetime import datetime, timedelta

from icalendar import Event


class GameEvent:
    KBL_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(
        self,
        home_team_name: str,
        away_team_name: str,
        match_datetime_raw: str,
        home_team_score: str | None,
        away_team_score: str | None,
        match_location: str | None,
        match_video: str | None,
        google_photo: str | None,
        match_report: str | None,
    ) -> None:
        self.home_team_name = home_team_name
        self.away_team_name = away_team_name
        self.match_datetime = datetime.strptime(match_datetime_raw, GameEvent.KBL_DATETIME_FORMAT)
        self.home_team_score = home_team_score
        self.away_team_score = away_team_score
        self.match_location = match_location
        self.match_video = match_video
        self.google_photo = google_photo
        self.match_report = match_report

    def to_ical_event(self) -> Event:
        ical_event = Event()
        ical_event.add("SUMMARY", self.summary)
        if self.match_location:
            ical_event.add("LOCATION", self.match_location)
        ical_event.add("DTSTART", self.match_datetime)
        ical_event.add("DTEND", self.end_datetime)
        ical_event.add("DESCRIPTION", self.description)
        return ical_event

    @property
    def summary(self) -> str:
        return f"KBL: {self.home_team_name} vs {self.away_team_name}"

    @property
    def end_datetime(self) -> datetime:
        return self.match_datetime + timedelta(hours=1, minutes=30)

    @property
    def description(self) -> str:
        if self.home_team_score is None and self.away_team_score is None:
            score = f"{self.home_team_name} - {self.away_team_name}"
        else:
            score = f"{self.home_team_name} {self.home_team_score}" f" - {self.away_team_score} {self.away_team_name}"

        video = ""
        if self.match_video:
            video = f"Video: {self.match_video}"

        photos = ""
        if self.google_photo:
            photos = f"Photos: {self.google_photo}"

        report = ""
        if self.match_report:
            report = f"Report: {self.match_report}"

        fields = list(
            filter(
                lambda field: bool(field),
                (score, video, photos, report),
            )
        )
        return "\n".join(fields)
