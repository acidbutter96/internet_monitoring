import speedtest
import mysql.connector
import time
import socket
from datetime import datetime, timezone, timedelta
from logging import getLogger

# Função para obter o IP externo

logger = getLogger(__name__)
gmt_minus_3 = timezone(timedelta(hours=-3))


def get_external_ip():
    logger.info("Getting external IP address...")
    try:
        ip = socket.gethostbyname(socket.gethostname())
        logger.info(f"External IP address: {ip}")
        return ip
    except Exception as e:  # noqa
        return None


def test_speed():
    st = speedtest.Speedtest()
    st.download()
    st.upload()
    return st.results.dict()


def store_results(result, cursor, cnx):
    logger.info("Storing results in database...")
    dt_utc = datetime.strptime(result['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
    download_speed = result['download'] / 1_000_000  # Convert to Mbps
    upload_speed = result['upload'] / 1_000_000  # Convert to Mbps
    ping = result['ping']
    server = result['server']
    client = result['client']
    timestamp = dt_utc.astimezone(gmt_minus_3)
    bytes_sent = result['bytes_sent']
    bytes_received = result['bytes_received']

    query = ("INSERT INTO speed_tests "
             "(timestamp, download_speed, upload_speed, ping, "
             "server_url, server_lat, server_lon, server_name, server_country,"
             "server_cc, server_sponsor, server_id, server_host"
             ", server_distance, server_latency, bytes_sent, "
             "bytes_received, client_ip, client_lat, client_lon,"
             " client_isp, client_isprating, client_rating,"
             " client_ispdlavg, client_ispulavg,"
             " client_loggedin, client_country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)") # noqa
    data = (timestamp, download_speed, upload_speed, ping, # noqa
            server['url'], server['lat'], server['lon'], server['name'], server['country'], server[ # noqa
                'cc'], server['sponsor'], server['id'], server['host'], server['d'], server['latency'], # noqa
            bytes_sent, bytes_received,
            client['ip'], client['lat'], client['lon'], client['isp'], client['isprating'], client['rating'], client['ispdlavg'], client['ispulavg'], client['loggedin'], client['country']) # noqa

    cursor.execute(query, data)
    cnx.commit()


def main():
    logger.info("connecting to MySQL...")
    cnx = mysql.connector.connect(
        user='root',
        password='root',
        host='db',  # 'localhost',
        port=3306,
        database='db_internet_monitoring',
    )
    cursor = cnx.cursor()

    logger.info("Running speed test and storing results...")
    while True:
        try:
            result = test_speed()
            logger.info(result, "\n", "=" * 100, "\n")
            store_results(result, cursor, cnx)
            time.sleep((60 ** 2) / 8)
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(10)

    cursor.close()
    cnx.close()


if __name__ == "__main__":
    logger.info("Starting internet monitoring service...")
    main()
