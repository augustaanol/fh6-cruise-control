import socket
import struct
import math

class TelemetryReceiver:
    def __init__(self, config):
        self.config = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.ioctl(socket.SIO_UDP_CONNRESET, False)
        except:
            pass
        self.sock.bind((config['net_listen_ip'], config['net_listen_port']))
        self.sock.setblocking(False)
        
        self.forward_sock = None
        if config['net_forward_enabled']:
            self.forward_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def receive(self):
        latest_data = None
        while True:
            try:
                data, _ = self.sock.recvfrom(1024)
                if self.forward_sock:
                    try:
                        self.forward_sock.sendto(data, (self.config['net_forward_ip'], self.config['net_forward_port']))
                    except Exception:
                        pass
                latest_data = data
            except BlockingIOError:
                break
            except Exception:
                break
                
        return latest_data

    @staticmethod
    def parse_speed(data: bytes) -> float | None:
        if not data or len(data) < 311:
            return None
        try:
            vx = struct.unpack_from('<f', data, 32)[0]
            vy = struct.unpack_from('<f', data, 36)[0]
            vz = struct.unpack_from('<f', data, 40)[0]
            return math.sqrt(vx**2 + vy**2 + vz**2) * 3.6
        except Exception:
            return None

    def close(self):
        self.sock.close()
        if self.forward_sock:
            self.forward_sock.close()