# kbl-calendar-provider

AWS Lambda code that fetches schedule from KBL League and returns .ics calendar with games.

1. Build docker image:
    ```
    docker compose build kbl-calendar-provider
    ```

2. Run docker container:
    ```
    docker compose kbl-calendar-provider run bash
    ```
    or with make
    ```
    make dc_bash
    ```

3. Run tests:
    ```
    make test
    ```
