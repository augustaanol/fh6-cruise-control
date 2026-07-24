import socket

UDP_IP = "0.0.0.0"  # Nasłuchuj ze wszystkich źródeł
UDP_PORT = 8000

print(f"Rozpoczynam nasłuchiwanie na porcie {UDP_PORT}...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024)
    print(f"✅ Otrzymano {len(data)} bajtów od {addr}!")