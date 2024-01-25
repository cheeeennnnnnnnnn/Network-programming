import socket
import threading

class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '127.0.0.1'
        self.port = 12345
        self.rooms = {f"Room {i+1}": {'players': [], 'game_active': False} for i in range(40)}  # 初始化房间字典
        self.lock = threading.Lock()  # 添加锁对象
        
        self.init_server()

    def init_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"服务器正在监听 {self.host}:{self.port}...")

        while True:
            client_socket, client_address = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            
    def broadcast_to_room_players(self, room, message, sender_socket):
        for player_socket, _ in room['players']:
            if player_socket != sender_socket:
                try:
                    player_socket.send(message.encode())
                except Exception as e:
                    print("向玩家发送消息时出错:", e)

    def get_room_by_socket(self, client_socket):
        for room in self.rooms.values():
            for player_socket, _ in room['players']:
                if id(client_socket) == id(player_socket):
                    return room
        return None

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode()

                if not data:
                    break

                if data.startswith("加入了房间"):
                    room_number = data.split()[-1]
                    room_id = f"Room {room_number}"  # 转换为房间标识
                    
                    with self.lock:  # 使用锁确保线程安全性
                        room = self.rooms[room_id]
                        if len(room['players']) == 0:  # 如果房间内没有玩家，则加入为第一个玩家
                            room['players'].append((client_socket, 'Player X'))
                            client_socket.send("等待其他玩家加入".encode())
                        elif len(room['players']) == 1:  # 如果房间内已有一个玩家，则加入为第二个玩家
                            room['players'].append((client_socket, 'Player O'))
                            # 向房间内两名玩家发送游戏开始信号
                            for player_socket, _ in room['players']:
                                player_socket.send("游戏开始".encode())
                            # 在这里设置 room['game_active'] 为 True，表示游戏已经开始    
                            room['game_active'] = True
                            #print("1111111")
                            # 启动五子棋游戏逻辑
                            threading.Thread(target=self.start_game, args=(room['players'],)).start()
                        else:
                            client_socket.send("房间已满，无法加入".encode())

                # 处理客户端发送的落子信息并广播给同一房间内的其他玩家
                elif data.startswith("MOVE"):
                    
                    move_info = data.split()
                    row = int(move_info[1])
                    col = int(move_info[2])
                    room = self.get_room_by_socket(client_socket)
                    #print("22222222")
                    #print(room['game_active'])
                    #print(data.split()[-1])
                    with self.lock:  # 使用锁确保线程安全性.
                        
                        if room and room['game_active']:
                            #print("22222222")
                            self.broadcast_to_room_players(room, data, client_socket)
            except Exception as e:
                print("处理客户端消息时出错:", e)
                break

    def start_game(self, players):
        player1_socket, player1_symbol = players[0]
        player2_socket, player2_symbol = players[1]

        player1_socket.send(player1_symbol.encode())
        player2_socket.send(player2_symbol.encode())

# 启动服务器
if __name__ == "__main__":
    server = Server()
