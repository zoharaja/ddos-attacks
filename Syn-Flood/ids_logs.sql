CREATE DATABASE ids_logs;
USE ids_logs;

CREATE TABLE syn_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME,
    source_ip VARCHAR(15),
    dest_ip VARCHAR(15),
    protocol VARCHAR(10),
    alert TEXT
);
