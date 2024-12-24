import socket
import json
import mysql.connector
from mysql.connector import pooling
from urllib.parse import urlparse, parse_qs
import threading
import datetime
import ssl
import hashlib
import os

class VisitorTrackingServer:
    def __init__(self, host='localhost', port=8000, db_config=None, secret_key=None):
        """
        Initialize the server with host, port, database configuration, and a secret key.
        """
        self.host = host
        self.port = port
        self.secret_key = secret_key or hashlib.sha256(os.urandom(60)).hexdigest()

        self.db_config = db_config or {
            'host': 'localhost',
            'user': 'your_username',
            'password': 'your_password',
            'database': 'visitor_tracking_db'
        }

        # Initialize the database connection pool
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="visitor_pool",
            pool_size=5,
            **self.db_config
        )

    def create_database_table(self):
        """
        Ensure the visitors table exists in the database.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS visitors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                page_url VARCHAR(255) UNIQUE,
                visit_count INT DEFAULT 1,
                last_visited TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        self.execute_query(query)

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """
        Execute a database query with proper connection handling.
        """
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(query, params)
            connection.commit()
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
        except mysql.connector.Error as err:
            connection.rollback()
            print(f"Database error: {err}")
            raise
        finally:
            cursor.close()
            connection.close()

    def validate_request(self, page_url):
        """
        Validate the provided page URL.
        """
        if not page_url or not page_url.startswith(('http://', 'https://')):
            raise ValueError("Invalid URL")

    def generate_token(self, page_url):
        """
        Generate a secure token for the given page URL.
        """
        return hashlib.sha256(
            f"{page_url}{self.secret_key}{datetime.datetime.now()}".encode()
        ).hexdigest()

    def update_visitor_count(self, page_url):
        """
        Increment or insert the visitor count for the given page URL.
        """
        self.validate_request(page_url)
        query = '''
            INSERT INTO visitors (page_url, visit_count) 
            VALUES (%s, 1) 
            ON DUPLICATE KEY UPDATE visit_count = visit_count + 1
        '''
        result_query = 'SELECT * FROM visitors WHERE page_url = %s'
        self.execute_query(query, (page_url,))
        result = self.execute_query(result_query, (page_url,), fetch_one=True)
        result['security_token'] = self.generate_token(page_url)
        return result

    def get_visitor_count(self, page_url=None):
        """
        Retrieve visitor counts. Optionally filter by a specific page URL.
        """
        if page_url:
            self.validate_request(page_url)
            query = 'SELECT * FROM visitors WHERE page_url = %s'
            return self.execute_query(query, (page_url,), fetch_one=True)
        query = 'SELECT * FROM visitors'
        return self.execute_query(query, fetch_all=True)

    def setup_ssl(self):
        """
        Configure SSL for secure connections.
        """
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile='server.crt', keyfile='server.key')
        return ssl_context

    def handle_request(self, client_socket):
        """
        Handle incoming client requests and send appropriate responses.
        """
        try:
            request = client_socket.recv(1024).decode()
            headers = request.split('\n')
            request_line = headers[0]
            method, path, _ = request_line.split()

            parsed_path = urlparse(path)
            query_params = parse_qs(parsed_path.query)

            response_data = {}
            status_code = 200

            if method == 'GET':
                if parsed_path.path == '/update':
                    url = query_params.get('url', [''])[0]
                    response_data = self.update_visitor_count(url)
                elif parsed_path.path == '/count':
                    url = query_params.get('url', [None])[0]
                    response_data = self.get_visitor_count(url)

            response_body = json.dumps(response_data)
            response = (
                f"HTTP/1.1 {status_code} OK\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Access-Control-Allow-Methods: GET\r\n"
                "Access-Control-Allow-Headers: Content-Type\r\n\r\n"
                f"{response_body}"
            )
        except ValueError as ve:
            response = f"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\n{str(ve)}"
        except Exception as e:
            response = f"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\n{str(e)}"
        finally:
            client_socket.send(response.encode())
            client_socket.close()

    def start_server(self):
        """
        Start the server to listen for incoming requests.
        """
        self.create_database_table()

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=self.handle_request, args=(client_socket,)).start()


if __name__ == "__main__":
    server = VisitorTrackingServer()
    server.start_server()
