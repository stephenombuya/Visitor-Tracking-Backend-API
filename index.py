import socket
import json
import mysql.connector
from urllib.parse import urlparse, parse_qs
import threading
import datetime
import ssl
import hashlib
import os
from mysql.connector import pooling

class VisitorTrackingServer:
    def __init__(self, host='localhost', port=8000, db_config=None, secret_key=None):
        self.host = host
        self.port = port
        self.secret_key = secret_key or hashlib.sha256(os.urandom(60)).hexdigest()
        
        self.db_config = db_config or {
            'host': 'localhost',
            'user': 'your_username',
            'password': 'your_password',
            'database': 'visitor_tracking_db'
        }
        
        # Create connection pool
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="visitor_pool",
            pool_size=5,
            **self.db_config
        )

    def create_database_table(self):
        """Create visitors table if not exists"""
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visitors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                page_url VARCHAR(255) UNIQUE,
                visit_count INT DEFAULT 1,
                last_visited TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        connection.commit()
        cursor.close()
        connection.close()

    def validate_request(self, page_url):
        """Basic request validation"""
        if not page_url or not page_url.startswith(('http://', 'https://')):
            raise ValueError("Invalid URL")

    def generate_token(self, page_url):
        """Generate a secure token for the request"""
        return hashlib.sha256(
            f"{page_url}{self.secret_key}{datetime.datetime.now()}".encode()
        ).hexdigest()

    def update_visitor_count(self, page_url):
        """Update visitor count with enhanced security"""
        self.validate_request(page_url)
        
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            # Atomic upsert operation
            cursor.execute('''
                INSERT INTO visitors (page_url, visit_count) 
                VALUES (%s, 1) 
                ON DUPLICATE KEY UPDATE visit_count = visit_count + 1
            ''', (page_url,))
            
            connection.commit()
            cursor.execute('SELECT * FROM visitors WHERE page_url = %s', (page_url,))
            result = cursor.fetchone()
            result['security_token'] = self.generate_token(page_url)
            return result
        
        except mysql.connector.Error as err:
            connection.rollback()
            raise err
        finally:
            cursor.close()
            connection.close()

    def get_visitor_count(self, page_url=None):
        """Retrieve visitor counts with optional filtering"""
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            if page_url:
                self.validate_request(page_url)
                cursor.execute('SELECT * FROM visitors WHERE page_url = %s', (page_url,))
                result = cursor.fetchone()
            else:
                cursor.execute('SELECT * FROM visitors')
                result = cursor.fetchall()
            
            return result
        
        finally:
            cursor.close()
            connection.close()

    def setup_ssl(self):
        """Configure SSL context"""
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(
            certfile='server.crt', 
            keyfile='server.key'
        )
        return ssl_context

    def handle_request(self, client_socket):
        """Enhanced request handling with error management"""
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
            response = (
                "HTTP/1.1 400 Bad Request\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {len(str(ve))}\r\n\r\n"
                f"{str(ve)}"
            )
        
        except Exception as e:
            response = (
                "HTTP/1.1 500 Internal Server Error\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {len(str(e))}\r\n\r\n"
                f"{str(e)}"
            )
        
        client_socket.send(response.encode())
        client_socket.close()

    def start_server(self):
        """Start the secure socket server"""
        self.create_database_table()
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        # Optional SSL setup
        # ssl_context = self.setup_ssl()
        # server_socket = ssl_context.wrap_socket(server_socket, server_side=True)
        
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            client_socket, addr = server_socket.accept()
            client_thread = threading.Thread(target=self.handle_request, args=(client_socket,))
            client_thread.start()

if __name__ == "__main__":
    server = VisitorTrackingServer()
    server.start_server()
