migration = """
CREATE TABLE IF NOT EXISTS speed_test_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    download_speed FLOAT NOT NULL,
    upload_speed FLOAT NOT NULL,
    ping FLOAT NOT NULL,
    server_url VARCHAR(255) NOT NULL,
    server_lat FLOAT NOT NULL,
    server_lon FLOAT NOT NULL,
    server_name VARCHAR(255) NOT NULL,
    server_country VARCHAR(255) NOT NULL,
    server_cc VARCHAR(10) NOT NULL,
    server_sponsor VARCHAR(255) NOT NULL,
    server_id VARCHAR(255) NOT NULL,
    server_host VARCHAR(255) NOT NULL,
    server_distance FLOAT NOT NULL,
    server_latency FLOAT NOT NULL,
    bytes_sent BIGINT NOT NULL,
    bytes_received BIGINT NOT NULL,
    client_ip VARCHAR(255) NOT NULL,
    client_lat FLOAT NOT NULL,
    client_lon FLOAT NOT NULL,
    client_isp VARCHAR(255) NOT NULL,
    client_isprating FLOAT NOT NULL,
    client_rating FLOAT NOT NULL,
    client_ispdlavg FLOAT NOT NULL,
    client_ispulavg FLOAT NOT NULL,
    client_loggedin BOOLEAN NOT NULL,
    client_country VARCHAR(255) NOT NULL
);
"""


__all__ = ['migration']