import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import socket
import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN
import threading
import asyncio

class ChessGame:
    def __init__(self, client_socket):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 600))
        pygame.display.set_caption('playerO')
        self.board = [[' ' for _ in range(15)] for _ in range(15)]
        self.current_player = 'O'

        self.game_over = False
        self.client_socket = client_socket

    def draw_board(self):
        self.screen.fill((255, 255, 255))  # 设置背景颜色

        # 绘制棋盘网格线
        for i in range(15):
            pygame.draw.line(self.screen, (0, 0, 0), (40, 40 * i + 40), (560, 40 * i + 40), 2)
            pygame.draw.line(self.screen, (0, 0, 0), (40 * i + 40, 40), (40 * i + 40, 560), 2)

        # 绘制棋子
        for row in range(15):
            for col in range(15):
                if self.board[row][col] == 'X':
                    pygame.draw.circle(self.screen, (0, 0, 0), (40 * (col + 1), 40 * (row + 1)), 18)
                elif self.board[row][col] == 'O':
                    pygame.draw.circle(self.screen, (255, 255, 255), (40 * (col + 1), 40 * (row + 1)), 18)
                    pygame.draw.circle(self.screen, (0, 0, 0), (40 * (col + 1), 40 * (row + 1)), 18, 2)
                    
        # 添加五子棋游戏逻辑和界面绘制部分

    def check_winner(self, row, col):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 横向、纵向、右斜、左斜四个方向
        player = self.board[row][col]

        for dr, dc in directions:
            count = 1  # 初始为1，因为当前落子算一颗
            # 检查当前位置四个方向上的连续棋子数量
            for i in range(1, 5):  # 检查连续的四颗棋子
                r, c = row + i * dr, col + i * dc
                if 0 <= r < 15 and 0 <= c < 15 and self.board[r][c] == player:
                    count += 1
                else:
                    break

            for i in range(1, 5):  # 检查连续的四颗棋子
                r, c = row - i * dr, col - i * dc
                if 0 <= r < 15 and 0 <= c < 15 and self.board[r][c] == player:
                    count += 1
                else:
                    break

            if count >= 5:  # 如果达到了五颗连续棋子，玩家获胜
                return True
        return False
    

        
    def update_board(self, row, col, player):
        if player == 'X':
            self.board[row][col] = 'X'
        else:
            self.board[row][col] = 'O'

    def redraw_board(self):
        self.screen.fill((255, 255, 255))  # 设置背景颜色

        # 重新绘制棋盘网格线
        for i in range(15):
            pygame.draw.line(self.screen, (0, 0, 0), (40, 40 * i + 40), (560, 40 * i + 40), 2)
            pygame.draw.line(self.screen, (0, 0, 0), (40 * i + 40, 40), (40 * i + 40, 560), 2)

        # 绘制棋子
        for row in range(15):
            for col in range(15):
                if self.board[row][col] == 'X':
                    pygame.draw.circle(self.screen, (0, 0, 0), (40 * (col + 1), 40 * (row + 1)), 18)
                elif self.board[row][col] == 'O':
                    pygame.draw.circle(self.screen, (255, 255, 255), (40 * (col + 1), 40 * (row + 1)), 18)
                    pygame.draw.circle(self.screen, (0, 0, 0), (40 * (col + 1), 40 * (row + 1)), 18, 2)

        pygame.display.flip()  # 刷新显示
        
 #   def handle_server_message(self, message):
   #     if message.startswith("MOVE"):
   #         move_info = message.split()
    #        row, col, player = map(int, move_info[1:4])
     #       self.update_board(row, col, player)
      #      self.redraw_board()
            

    def handle_mouse_click(self, row, col):
        if 0 <= row < 15 and 0 <= col < 15 and self.board[row][col] == ' ':
            self.board[row][col] = self.current_player
            move_data = f"MOVE {row} {col}"
            try:
                #print("11111111")
                print
                self.client_socket.send(move_data.encode())
            except Exception as e:
                print("向服务器发送移动数据时出错:", e)
            
 #           if(self.current_player == 'X'):
 #               data = self.client_socket.recv(1024).decode()
 #           elif(self.current_player == 'O'):
  #              data = self.client_socket.recv(1024).decode()
            # 传入当前棋手的下棋信息到对手，并在对手游戏界面做出相应绘制

            
        if self.check_winner(row, col):
            print(f"Player {self.current_player} wins!")
            self.game_over = True
#        else:
#            self.current_player = 'O' if self.current_player == 'X' else 'X'
            
        self.redraw_board()
    def charge_game(self):        
        try:
            self.client_socket.settimeout(0.5)  # 设置超时时间为5秒
            data = self.client_socket.recv(1024).decode()
            if data.startswith("MOVE"):
                move_info = data.split()
                opponent_row = int(move_info[1])
                opponent_col = int(move_info[2])
                self.board[opponent_row][opponent_col] = 'O' if self.current_player == 'X' else 'X'   
                #print("aaaaaaaaaaaaaaaaaaaaa")
        except socket.timeout:
            print("请进行您的操作")
        except Exception as e:
            print("接收数据时出错:", e)
            
  
            
        self.redraw_board()  # 重新绘制棋盘和棋子            

    def start_game(self):
        # 创建五子棋游戏实例并保存为属性

        self.chess_game = ChessGame(self.client_socket)
        self.chess_game.start_game_loop()  # 启动 Pygame 的事件循环
                
    def start_game_loop(self):
        # 游戏事件循环
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    col = (x - 20) // 40
                    row = (y - 20) // 40
                    self.handle_mouse_click(row, col)  # 处理玩家点击事件
                    
                    
            # 绘制棋盘、棋子等
            self.draw_board()
            pygame.display.flip()
            clock.tick(60)
            self.charge_game()
                        
        
        
class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

        # 创建客户端 socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '127.0.0.1'
        self.port = 12345
        self.game_in_progress = False
        self.room_number = None  # 记录玩家所在的房间号
        self.player_symbol = None  # 记录玩家的标识


    def init_ui(self):
        self.setWindowTitle("Game Lobby")
        self.setGeometry(100, 100, 800, 600)

        # 创建主窗口部件和垂直布局
        main_widget = QWidget()
        layout = QVBoxLayout()

        # 设置游戏大厅背景颜色
        main_widget.setStyleSheet("background-color: #f0f0f0;")

        # 创建游戏卓布局的网格布局
        grid_layout = QGridLayout()

        # 创建游戏卓按钮
        self.rooms = []
        for i in range(5):
            for j in range(8):
                room_btn = QPushButton(f"Room {i * 8 + j + 1}")
                room_btn.setFixedSize(100, 100)  # 设置按钮大小
                room_btn.setStyleSheet("background-color: #3498db; color: white; border-radius: 10px;")  # 设置按钮样式
                room_btn.setFont(QFont("Arial", 12, QFont.Bold))  # 设置按钮字体样式
                room_btn.clicked.connect(lambda _, idx=i*8+j+1: self.join_room(idx))  # 绑定按钮点击事件
                grid_layout.addWidget(room_btn, i, j)  # 将按钮添加到网格布局中
                self.rooms.append(room_btn)

        layout.addLayout(grid_layout)  # 将网格布局添加到垂直布局中
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        
    def start_receive_thread(self):
        threading.Thread(target=self.receive_server_message).start()

    def join_room(self, room_number):
        if not self.game_in_progress or self.room_number != room_number:
            try:
                if self.game_in_progress:
                    self.client_socket.send("退出房间".encode())
                    self.game_in_progress = False

                self.client_socket.connect((self.host, self.port))
                self.client_socket.send(f"加入了房间 {room_number}".encode())
                data = self.client_socket.recv(1024).decode()

                if data == "等待其他玩家加入":
                    print("等待其他玩家加入房间...")
                    self.game_in_progress = False
                elif data == "游戏开始":
                    print("游戏开始！")
                    self.game_in_progress = True
                    self.room_number = room_number
                    

               # 接收服务器发送的玩家标识信息
                self.player_symbol = self.client_socket.recv(1024).decode()
                print(f"你的标识为: {self.player_symbol}")
              # 启动五子棋游戏界面
                self.start_game()

            except Exception as e:
                print("与服务器通信出现异常:", e)

    def start_game(self):
        # 创建五子棋游戏实例
        self.chess_game = ChessGame(self.client_socket)
        self.chess_game.start_game_loop()  # 启动 Pygame 的事件循环


                    
    def receive_server_message(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, message=data))
            except Exception as e:
                print("接收服务器消息时出错:", e)
        
    def closeEvent(self, event):
        if self.game_in_progress:
            try:
                self.client_socket.send("退出房间".encode())
            except Exception as e:
                print("与服务器通信出现异常:", e)

            # 在退出房间时释放资源
            self.release_resources()

        event.accept()
                
        
    def handle_game_over(self):
        # 关闭五子棋游戏界面
        if hasattr(self, 'chess_game') and self.chess_game is not None:
            self.chess_game.handle_game_over("X")  # 或者传入胜利的玩家标识

        # 关闭 Pygame 界面
        pygame.quit()
        sys.exit()

    def show_game_lobby(self):
        # 关闭游戏界面
        # self.hide()  # 如果窗口只是隐藏，不会真正关闭游戏界面
        if hasattr(self, 'chess_game') and self.chess_game is not None:
            self.chess_game = None  # 清空游戏对象

        # 显示游戏大厅界面
        self.show()
        
def main():
    app = QApplication(sys.argv)
    window = ClientWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

