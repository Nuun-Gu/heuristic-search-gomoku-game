import sys
import random
import pygame
from pygame.locals import *
import pygame.gfxdraw
from collections import namedtuple

chesspiece = namedtuple('chesspiece', 'Name Value Color')
Point = namedtuple('Point', 'X Y')
PLAYER_TURN_CNT = 0
BLACK_chesspiece = chesspiece('黑子', 1, (0, 0, 0))
WHITE_chesspiece = chesspiece('白子', 2, (225, 225, 225))
chess_box = [[0 for x in range(19)] for y in range(19)]
direction = [(1, 0), (0, 1), (1, 1), (1, -1)]

class Checkerboard:
    def __init__(self, linecounts):
        self._linecounts = linecounts
        self._checkerboard = [[0] * linecounts for _ in range(linecounts)]

    def get_checkerboard(self):
        return self._checkerboard

    checkerboard = property(get_checkerboard)

    # 判断是否可落子
    def can_drop(self, point):
        return self._checkerboard[point.Y][point.X] == 0

    def drop(self, chesspiece, point):
        print(f'{chesspiece.Name} ({point.X}, {point.Y})')
        self._checkerboard[point.Y][point.X] = chesspiece.Value

        if self._win(point):
            print(f'{chesspiece.Name}WIN!')
            return chesspiece

    # 判断是否分出胜负
    def _win(self, point):
        cur_value = self._checkerboard[point.Y][point.X]
        for os in direction:
            if self._getenemy_count_on_direction(point, cur_value, os[0], os[1]):
                return True

    def _getenemy_count_on_direction(self, point, value, x_direction, y_direction):
        count = 1
        for step in range(1, 5):
            x = point.X + step * x_direction
            y = point.Y + step * y_direction
            if 0 <= x < self._linecounts and 0 <= y < self._linecounts and self._checkerboard[y][x] == value:
                count += 1
            else:
                break
        for step in range(1, 5):
            x = point.X - step * x_direction
            y = point.Y - step * y_direction
            if 0 <= x < self._linecounts and 0 <= y < self._linecounts and self._checkerboard[y][x] == value:
                count += 1
            else:
                break

        return count >= 5


SIZE = 30
linecounts = 19
Boxwid = 4
Border_Length = SIZE * (linecounts - 1) + 4 * 2 + Boxwid
Start_X = Start_Y = 40 + int(Boxwid / 2) + 4
screenH = SIZE * (linecounts - 1) + 40 * 2 + Boxwid + 4 * 2
screenwid = screenH

Stone_Radius = SIZE // 2 - 3  # 棋子半径
Stone_Radius2 = SIZE // 2 + 3
Checkerboard_Color = (222, 173, 55)  # 棋盘RGB
BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
RED_COLOR = (200, 30, 30)
BLUE_COLOR = (30, 30, 200)
RIGHT_INFO_POS_X = screenH + Stone_Radius2 * 2 + 10


def outtext(screen, font, x, y, text, fcolor=(255, 255, 255)):
    imgText = font.render(text, True, fcolor)
    screen.blit(imgText, (x, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((screenwid, screenH))
    pygame.display.set_caption('五子棋人机博弈')

    font1 = pygame.font.SysFont('SimHei', 32)
    font2 = pygame.font.SysFont('SimHei', 72)
    fwidth, fheight = font2.size('一二三四')

    checkerboard = Checkerboard(linecounts)
    current_player = BLACK_chesspiece
    winner = None
    computer = AI(linecounts, WHITE_chesspiece)

    black_winenemy_count = 0
    white_winenemy_count = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if winner is not None:
                        winner = None
                        current_player = BLACK_chesspiece
                        checkerboard = Checkerboard(linecounts)
                        computer = AI(linecounts, WHITE_chesspiece)
            elif event.type == MOUSEBUTTONDOWN:
                if winner is None:
                    pressed_array = pygame.mouse.get_pressed()
                    if pressed_array[0]:
                        mouse_pos = pygame.mouse.get_pos()
                        click_point = get_mousecheck(mouse_pos)
                        if click_point is not None:
                            if checkerboard.can_drop(click_point):
                                winner = checkerboard.drop(current_player, click_point)
                                global PLAYER_TURN_CNT
                                PLAYER_TURN_CNT = PLAYER_TURN_CNT + 1
                                if winner is None:
                                    current_player = player_turn_change(current_player)
                                    computer.get_opponent_drop(click_point)
                                    AI_point = computer.AI_drop()
                                    winner = checkerboard.drop(current_player, AI_point)
                                    if winner is not None:
                                        white_winenemy_count += 1
                                    current_player = player_turn_change(current_player)
                                else:
                                    black_winenemy_count += 1
                        else:
                            print('Over confines')

        # 画棋盘
        draw_checkbox(screen)

        # 画棋盘上已有的棋子
        for i, row in enumerate(checkerboard.checkerboard):
            for j, cell in enumerate(row):
                if cell == BLACK_chesspiece.Value:
                    draw_pieces(screen, Point(j, i), BLACK_chesspiece.Color)
                    # 打印落子次序
                    # record_turn(screen, Point(j, i), BLACK_chesspiece.Color)
                elif cell == WHITE_chesspiece.Value:
                    draw_pieces(screen, Point(j, i), WHITE_chesspiece.Color)
                    # record_turn(screen, Point(j, i), BLACK_chesspiece.Color)

        if winner:
            outtext(screen, font2, (screenwid - fwidth) // 2, (screenH - fheight) // 2, winner.Name + 'Win!', RED_COLOR)

        pygame.display.flip()


# 落子回合交换
def player_turn_change(current_player):
    if current_player == BLACK_chesspiece:
        return WHITE_chesspiece
    else:
        return BLACK_chesspiece


# 画棋盘
def draw_checkbox(screen):
    # 填充棋盘背景色
    screen.fill(Checkerboard_Color)
    # 画棋盘网格线外的边框
    pygame.draw.rect(screen, BLACK_COLOR, (40, 40, Border_Length, Border_Length), Boxwid)
    # 画网格线
    for i in range(linecounts):
        pygame.draw.line(screen, BLACK_COLOR,
                         (Start_Y, Start_Y + SIZE * i),
                         (Start_Y + SIZE * (linecounts - 1), Start_Y + SIZE * i),
                         1)
    for j in range(linecounts):
        pygame.draw.line(screen, BLACK_COLOR,
                         (Start_X + SIZE * j, Start_X),
                         (Start_X + SIZE * j, Start_X + SIZE * (linecounts - 1)),
                         1)
    # 画星位和天元
    for i in (3, 9, 15):
        for j in (3, 9, 15):
            if i == j == 9:
                radius = 5
            else:
                radius = 3
            # pygame.draw.circle(screen, BLACK, (Start_X + SIZE * i, Start_Y + SIZE * j), radius)
            pygame.gfxdraw.aacircle(screen, Start_X + SIZE * i, Start_Y + SIZE * j, radius, BLACK_COLOR)
            pygame.gfxdraw.filled_circle(screen, Start_X + SIZE * i, Start_Y + SIZE * j, radius, BLACK_COLOR)

    # 标记落子顺序
    for numi in range(1, 19):
        for numj in range(1, 19):
            global chess_box
            # 未标记顺序则不显示
            if chess_box[numi][numj]:
                # 字体使用青叶手写体
                font01 = pygame.font.Font("font.ttf", 20)
                # 写字
                var1 = str(chess_box[numi][numj])
                surface1 = font01.render(var1, True, (255, 0, 0))
                # 显示文字
                screen.blit(surface1, (Start_X + SIZE * numi + 7, Start_Y + SIZE * numj + 5))


# 画棋子
def draw_pieces(screen, point, stone_color):
    # pygame.draw.circle(screen, stone_color, (Start_X + SIZE * point.X, Start_Y + SIZE * point.Y), Stone_Radius)
    pygame.gfxdraw.aacircle(screen, Start_X + SIZE * point.X, Start_Y + SIZE * point.Y, Stone_Radius, stone_color)
    pygame.gfxdraw.filled_circle(screen, Start_X + SIZE * point.X, Start_Y + SIZE * point.Y, Stone_Radius, stone_color)


# 标记落子顺序
def record_turn(screen, point):
    # 加载字体
    font01 = pygame.font.Font("font.ttf", 100)
    # 写字
    var1 = str(PLAYER_TURN_CNT)
    surface1 = font01.render(var1, True, (255, 0, 0))
    # 显示文字
    screen.blit(surface1, (Start_X + SIZE * point.X, Start_Y + SIZE * point.Y))


# 捕捉鼠标点击，决定落子位置
def get_mousecheck(click_pos):
    pos_x = click_pos[0] - Start_X
    pos_y = click_pos[1] - Start_Y
    if pos_x < -4 or pos_y < -4:
        return None
    x = pos_x // SIZE
    y = pos_y // SIZE
    if pos_x % SIZE > Stone_Radius:
        x += 1
    if pos_y % SIZE > Stone_Radius:
        y += 1
    if x >= linecounts or y >= linecounts:
        return None
    global PLAYER_TURN_CNT
    PLAYER_TURN_CNT = PLAYER_TURN_CNT + 1
    global chess_box
    chess_box[x][y] = PLAYER_TURN_CNT
    return Point(x, y)


class AI:
    def __init__(self, linecounts, chesspiece):
        self._linecounts = linecounts
        self._my = chesspiece
        self._opponent = BLACK_chesspiece if chesspiece == WHITE_chesspiece else WHITE_chesspiece
        self._checkerboard = [[0] * linecounts for _ in range(linecounts)]

    def get_opponent_drop(self, point):
        self._checkerboard[point.Y][point.X] = self._opponent.Value

    def AI_drop(self):
        point = None
        score = 0
        for i in range(self._linecounts):
            for j in range(self._linecounts):
                if self._checkerboard[j][i] == 0:
                    _score = self.get_score(Point(i, j))
                    if _score > score:
                        score = _score
                        point = Point(i, j)
                    elif _score == score and _score > 0:
                        r = random.randint(0, 100)
                        if r % 2 == 0:
                            point = Point(i, j)
        self._checkerboard[point.Y][point.X] = self._my.Value
        global PLAYER_TURN_CNT
        chess_box[point.X][point.Y] = PLAYER_TURN_CNT
        return point

    def get_score(self, point):
        score = 0
        for os in direction:
            score += self.line_score(point, os[0], os[1])
        return score

    def line_score(self, point, x_direction, y_direction):
        count = 0  # 落子处我方连续子数
        enemy_count = 0  # 落子处对方连续子数
        space = None  # 我方连续子中有无空格
        enemy_space = None  # 对方连续子中有无空格
        spire = 0  # 我方连续子两端有无阻挡
        enenmy_spire = 0  # 对方连续子两端有无阻挡
        double3 = 0
        three_and_four = 0
        double4 = 0
        # 如果是 1 表示是边上是我方子，2 表示敌方子, 0 表示该位置无落子
        flag = self.get_chess_color(point, x_direction, y_direction, True)
        if flag != 0:
            for step in range(1, 6):
                x = point.X + step * x_direction
                y = point.Y + step * y_direction
                if 0 <= x < self._linecounts and 0 <= y < self._linecounts:
                    # 我方子
                    if flag == 1:
                        if self._checkerboard[y][x] == self._my.Value:
                            count += 1
                            if space is False:
                                space = True
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            enenmy_spire += 1
                            break
                        else:
                            if space is None:
                                space = False
                            else:
                                break  # 空格退出
                    # 敌方子
                    elif flag == 2:
                        if self._checkerboard[y][x] == self._my.Value:
                            enenmy_spire += 1
                            break
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            enemy_count += 1
                            if enemy_space is False:
                                enemy_space = True
                        else:
                            if enemy_space is None:
                                enemy_space = False
                            else:
                                break
                else:
                    # 棋盘边缘阻挡
                    if flag == 1:
                        spire += 1
                    elif flag == 2:
                        enenmy_spire += 1

        if space is False:
            space = None
        if enemy_space is False:
            enemy_space = None

        block_flag = self.get_chess_color(point, -x_direction, -y_direction, True)
        if block_flag != 0:
            for step in range(1, 6):
                x = point.X - step * x_direction
                y = point.Y - step * y_direction
                if 0 <= x < self._linecounts and 0 <= y < self._linecounts:
                    if block_flag == 1:
                        if self._checkerboard[y][x] == self._my.Value:
                            count += 1
                            if space is False:
                                space = True
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            enenmy_spire += 1
                            break
                        else:
                            if space is None:
                                space = False
                            else:
                                break  # 空格退出
                    elif block_flag == 2:
                        if self._checkerboard[y][x] == self._my.Value:
                            enenmy_spire += 1
                            break
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            enemy_count += 1
                            if enemy_space is False:
                                enemy_space = True
                        else:
                            if enemy_space is None:
                                enemy_space = False
                            else:
                                break
                else:
                    # 棋盘边缘阻挡
                    if block_flag == 1:
                        spire += 1
                    elif block_flag == 2:
                        enenmy_spire += 1

        score = 0
        # 己方4连直接冲5
        if count != 0:
            print(count)
        if count == 4:
            score = 10000
        # 对方4连必须堵
        elif enemy_count == 4:
            score = 9000
        # 己方3连分情况
        elif count ==3 and enemy_count==3:
            if spire == 0:
                score = 5000
            elif spire ==1:
                score = 1200
            else:
                score = 800
        elif count == 3:
            #  两端都未被挡
            if spire == 0:
                score = 1000
            # 一端被挡
            elif spire == 1:
                score = 100
            # 两端都被挡 无落子价值
            else:
                score = 0
        # 对方3连分情况
        elif enemy_count == 3:
            # 两端都未被挡
            if enenmy_spire == 0:
                score = 900
            # 一端被挡
            elif enenmy_spire == 1:
                score = 90
            # 两端都被挡 无落子价值
            else:
                score = 0
        # 己方2连分情况
        elif count == 2:
            # 两端都未被挡
            if spire == 0:
                score = 100
            # 一端被挡
            elif spire == 1:
                score = 10
            # 两端都被挡 无落子价值
            else:
                score = 0
        # 敌方2连分情况
        elif enemy_count == 2:
            # 两端都未被挡
            if enenmy_spire == 0:
                score = 90
            # 一端被挡
            elif enenmy_spire == 1:
                score = 9
            # 两端都被挡 无落子价值
            else:
                score = 0
        elif count == 1:
            score = 10
        elif enemy_count == 1:
            score = 9
        else:
            score = 0

        if space and enemy_count:
            score = score * 0.8

        if enemy_space:
            score = score * 0.4

        if space:
            score = score * 0.5

        # if score != 0:
        #     print(score)

        return score

    # 判断指定位置处在指定方向上是我方子、对方子、空
    def get_chess_color(self, point, x_direction, y_direction, next):
        x = point.X + x_direction
        y = point.Y + y_direction
        if 0 <= x < self._linecounts and 0 <= y < self._linecounts:
            if self._checkerboard[y][x] == self._my.Value:
                return 1
            elif self._checkerboard[y][x] == self._opponent.Value:
                return 2
            else:
                if next:
                    return self.get_chess_color(Point(x, y), x_direction, y_direction, False)
                else:
                    return 0
        else:
            return 0


if __name__ == '__main__':
    main()
