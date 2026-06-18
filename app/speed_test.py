import logging
import os
import re
import socket
import time
from datetime import datetime, timedelta, timezone

import mysql.connector
import speedtest
from migrations import migration


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

logger = logging.getLogger(__name__)
gmt_minus_3 = timezone(timedelta(hours=-3))


def get_external_ip():
    logger.info("Getting external IP address...")
    try:
        ip = socket.gethostbyname(socket.gethostname())
        logger.info("External IP address: %s", ip)
        return ip
    except Exception:
        logger.exception("Could not get external IP address")
        return None


def test_speed():
    st = speedtest.Speedtest()
    st.download()
    st.upload()
    return st.results.dict()


def parse_speedtest_timestamp(value: str) -> datetime:
    try:
        dt_utc = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        dt_utc = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")

    return dt_utc.replace(tzinfo=timezone.utc).astimezone(gmt_minus_3)


def store_results(result, cursor, cnx):
    logger.info("Storing results in database...")

    server = result["server"]
    client = result["client"]

    query = (
        "INSERT INTO speed_tests "
        "(timestamp, download_speed, upload_speed, ping, "
        "server_url, server_lat, server_lon, server_name, server_country, "
        "server_cc, server_sponsor, server_id, server_host, "
        "server_distance, server_latency, bytes_sent, bytes_received, "
        "client_ip, client_lat, client_lon, client_isp, client_isprating, "
        "client_rating, client_ispdlavg, client_ispulavg, client_loggedin, "
        "client_country) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
        "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )

    data = (
        parse_speedtest_timestamp(result["timestamp"]),
        result["download"] / 1_000_000,
        result["upload"] / 1_000_000,
        result["ping"],
        server["url"],
        server["lat"],
        server["lon"],
        server["name"],
        server["country"],
        server["cc"],
        server["sponsor"],
        server["id"],
        server["host"],
        server["d"],
        server["latency"],
        result["bytes_sent"],
        result["bytes_received"],
        client["ip"],
        client["lat"],
        client["lon"],
        client["isp"],
        client["isprating"],
        client["rating"],
        client["ispdlavg"],
        client["ispulavg"],
        client["loggedin"],
        client["country"],
    )

    cursor.execute(query, data)
    cnx.commit()


def quote_identifier(identifier: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_]+", identifier):
        raise ValueError(f"Invalid MySQL identifier: {identifier!r}")

    return f"`{identifier}`"


def get_cnx(database: str | None = None, retries: int = 30, delay: int = 2):
    logger.info("Connecting to MySQL database...")

    kwargs = {
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "root"),
        "host": os.getenv("DB_HOST", "db"),
        "port": int(os.getenv("DB_PORT", "3306")),
    }

    if database:
        kwargs["database"] = database

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            return mysql.connector.connect(**kwargs)
        except mysql.connector.Error as exc:
            last_error = exc
            logger.warning(
                "MySQL is not ready yet, attempt %s/%s: %s",
                attempt,
                retries,
                exc,
            )
            time.sleep(delay)

    raise last_error


def migrate():
    logger.info("Migrating database...")

    db_name = os.getenv("DB_NAME", "db_internet_monitoring")

    cnx = get_cnx(database=None)
    cursor = cnx.cursor()

    try:
        quoted_db_name = quote_identifier(db_name)
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {quoted_db_name}")
        cursor.execute(f"USE {quoted_db_name}")
        cursor.execute(migration)
        cnx.commit()
        logger.info("Database migration completed.")
    finally:
        cursor.close()
        cnx.close()


def main():
    logger.info("Starting database setup...")
    migrate()

    db_name = os.getenv("DB_NAME", "db_internet_monitoring")
    cnx = get_cnx(database=db_name)
    cursor = cnx.cursor()

    logger.info("Running speed test and storing results...")

    try:
        while True:
            try:
                result = test_speed()
                logger.info("%s\n%s", result, "=" * 100)
                store_results(result, cursor, cnx)
                time.sleep(60**1)
            except mysql.connector.Error:
                logger.exception("Database error. Reconnecting...")
                try:
                    cursor.close()
                    cnx.close()
                except mysql.connector.Error:
                    pass

                cnx = get_cnx(database=db_name)
                cursor = cnx.cursor()
                time.sleep(10)
            except Exception:
                logger.exception("Error while running speed test")
                time.sleep(10)
    finally:
        cursor.close()
        cnx.close()


if __name__ == "__main__":
    logger.info("Starting internet monitoring service...")
    main()
