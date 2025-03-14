import http
from typing import Any

from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from loguru import logger

from calendar_creating import CannotFetchDataError, create_calendar, NoGamesForTeamError

app = APIGatewayHttpResolver()


def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict:
    """
    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc:
        https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    return app.resolve(event, context)


@app.exception_handler(NoGamesForTeamError)
def handle_no_games_for_team_error(_: NoGamesForTeamError) -> Response[str]:
    logger.error("No games found for the given team.")
    return Response(
        status_code=http.HTTPStatus.BAD_REQUEST,
        content_type="text/plain",
        body="No games found for the given team.",
    )


@app.exception_handler(CannotFetchDataError)
def handle_cannot_fetch_data_error(error: CannotFetchDataError) -> Response[str]:
    logger.error(f"Failed to fetch KBL data: {error}")
    return Response(
        status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
        content_type="text/plain",
        body=f"Failed to fetch KBL data: {error}",
    )


@app.get("/")
def main() -> Response[str]:
    TOURNAMENT_ID = 1588  # KBL
    subtournament_id_raw = app.current_event.get_query_string_value(name="subtournament_id")
    member_id_raw = app.current_event.get_query_string_value(name="member_id")
    if not subtournament_id_raw or not member_id_raw:
        return Response(
            status_code=http.HTTPStatus.BAD_REQUEST,
            content_type="text/plain",
            body="Query string parameters 'subtournament_id' and 'member_id' are required.",
        )

    subtournament_id = int(subtournament_id_raw)
    member_id = int(member_id_raw)

    calendar = create_calendar(
        tournament_id=TOURNAMENT_ID,
        subtournament_id=int(subtournament_id),
        team_id=member_id,
    )

    return Response(
        status_code=http.HTTPStatus.OK,
        content_type="text/plain; charset=utf-8",
        body=calendar.to_ical().decode("utf-8"),
    )
