import pyxel
import copy
import random
import json


directions = [
    {"y": -1, "x": -1},
    {"y": -1, "x": 0},
    {"y": -1, "x": 1},
    {"y": 0, "x": -1},
    {"y": 0, "x": 1},
    {"y": 1, "x": -1},
    {"y": 1, "x": 0},
    {"y": 1, "x": 1},
]
HUMAN = "YOU"
COM = "COM"


def pos2yx(pos):
    return (pos // 8, pos % 8)


def yx2pos(y, x):
    return None if y < 0 or y >= 8 or x < 0 or x >= 8 else y * 8 + x


# 石の数をカウント
def count_stone(state, stone):
    return len(list(filter(lambda b: b == stone, state)))


def get_color(p):
    return 7 if p == 1 else 0


def draw_small_stone(x, y, p):
    pyxel.circ(x + 2, y + 2, 3, get_color(p))


# Boardクラス
class Board:
    def __init__(self, player, state=None):
        self.animations = [None] * 64
        if state is None:
            state = []
            for pos in range(64):
                y, x = pos2yx(pos)
                if (y == 3 and x == 3) or (y == 4 and x == 4):
                    state.append(-1)
                elif (y == 3 and x == 4) or (y == 4 and x == 3):
                    state.append(1)
                else:
                    state.append(0)
        self.set_board(player, state)

    def set_board(self, player, state):
        def sign(target_player):
            return 1 if self.player == target_player else -1

        self.player = player
        self.state = state
        self.score = [0] * 64
        self.next_state = [None] * 64
        self.next_animations = [None] * 64
        for pos in range(64):
            if self.state[pos] != 0:
                continue
            tmp_state = None
            animations = [None] * 64
            y, x = pos2yx(pos)
            for direction in directions:
                tmp_y = y
                tmp_x = x
                success = 0
                while True:
                    tmp_y += direction["y"]
                    tmp_x += direction["x"]
                    tmp_pos = yx2pos(tmp_y, tmp_x)
                    if tmp_pos is None:
                        break
                    tmp_player = self.state[tmp_pos]
                    if tmp_player == -player:
                        success += 1
                    else:
                        if success and tmp_player == player:
                            if tmp_state is None:
                                tmp_state = copy.copy(self.state)
                                tmp_state[pos] = player
                            for i in range(1, success + 1):
                                tmp_y = y + direction["y"] * i
                                tmp_x = x + direction["x"] * i
                                tmp_pos = yx2pos(tmp_y, tmp_x)
                                tmp_state[tmp_pos] = player
                                animations[tmp_pos] = -i * 2
                        break
            # スコア算出
            score = 0
            if not tmp_state is None:
                score = 10000
                remain = count_stone(tmp_state, 0)
                is_early = (max(32, remain) * (1 - random.random() * 0.2)) / 32
                for tmp_pos in range(64):
                    y, x = pos2yx(tmp_pos)
                    base_player = tmp_state[tmp_pos]
                    if base_player != 0:
                        base_score = (1 - is_early) * 2
                        if (
                            (y == 0 and x == 0)
                            or (y == 0 and x == 7)
                            or (y == 7 and x == 0)
                            or (y == 7 and x == 7)
                        ):
                            base_score = 160 * is_early
                        elif (
                            (y == 1 and x == 1)
                            or (y == 1 and x == 6)
                            or (y == 6 and x == 1)
                            or (y == 6 and x == 6)
                        ):
                            base_score = -60 * is_early
                        elif ((y == 1 or y == 6) and (x == 0 or x == 7)) or (
                            (y == 0 or y == 7) and (x == 1 or x == 6)
                        ):
                            base_score = -20 * is_early
                        score += base_score * sign(base_player)
                        for direction in directions:
                            tmp_y = y + direction["y"]
                            tmp_x = x + direction["x"]
                            tmp_pos = yx2pos(tmp_y, tmp_x)
                            if tmp_pos is None:
                                score += is_early * sign(base_player)
                            else:
                                score += is_early * sign(tmp_state[tmp_pos])
            self.next_state[pos] = tmp_state
            self.score[pos] = score
            self.next_animations[pos] = animations

    def counts(self):
        state = self.state
        return count_stone(state, -1), count_stone(state, 1)

    def winner(self):
        cntBlack, cntWhite = self.counts()
        if cntBlack > cntWhite:
            return -1
        elif cntBlack < cntWhite:
            return 1
        else:
            return 0

    def draw(self, operator):
        cntBlack, cntWhite = self.counts()
        draw_small_stone(8, 144, -1)
        pyxel.text(16, 144, ":" + str(cntBlack), 7)
        pyxel.text(32, 144, operator["-1"], 7)
        draw_small_stone(72, 144, 1)
        pyxel.text(80, 144, ":" + str(cntWhite), 7)
        pyxel.text(96, 144, operator["1"], 7)
        for pos in range(64):
            y, x = pos2yx(pos)
            cx = x * 16 + 8
            cy = y * 16 + 8
            pyxel.rect(cx, cy, 15, 15, 3)
            if self.state[pos] != 0:
                a = self.animations[pos]
                p = self.state[pos]
                if a is None:
                    pyxel.circ(cx + 7, cy + 7, 6, get_color(p))
                else:
                    self.animations[pos] += 1
                    if a == 0:
                        pyxel.elli(cx + 3, cy - 2, 8, 12, get_color(-p))
                    elif a == 1:
                        pyxel.elli(cx + 5, cy - 5, 4, 12, get_color(-p))
                    elif a == 2:
                        pyxel.elli(cx + 6, cy - 7, 2, 12, get_color(-p))
                    elif a == 4:
                        pyxel.elli(cx + 6, cy - 7, 2, 12, get_color(p))
                    elif a == 5:
                        pyxel.elli(cx + 5, cy - 5, 4, 12, get_color(p))
                    elif a == 6:
                        pyxel.elli(cx + 3, cy - 2, 8, 12, get_color(p))
                        self.animations[pos] = None
            elif not self.next_state[pos] is None:
                pyxel.circ(cx + 7, cy + 7, 1, 13)
                # pyxel.text(cx + 1, cy + 1, str(int(self.score[pos] / 100)), 1)


class App:
    def __init__(self):
        pyxel.init(144, 168, title="Pyxel Reversi")
        # pyxel.mouse(True)
        self.scene = 0  # 0:title 1:main 2:end
        self.counter = 0
        self.board = None
        with open("./bgm.json", "rt") as fin:
            bgm = json.loads(fin.read())
        for ch, sound in enumerate(bgm):
            if sound is None:
                continue
            pyxel.sound(ch).set(
                sound["notes"], sound["tones"], sound["volumes"], sound["effects"], 1
            )
        pyxel.sound(3).set("c4", "n", "5", "f", 12)
        pyxel.run(self.update, self.draw)

    def update(self):
        pressed = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        if self.counter > 0:
            self.counter -= 1
        elif self.scene == 0:
            if pressed:
                x = pyxel.mouse_x
                y = pyxel.mouse_y
                clicked = False
                if x >= 12 and x < 68 and y >= 68 and y < 98:
                    clicked = True
                    self.operator = {"-1": HUMAN, "1": COM}
                if x >= 76 and x < 132 and y >= 68 and y < 98:
                    clicked = True
                    self.operator = {"-1": COM, "1": HUMAN}
                if clicked:
                    if pyxel.play_pos(0) is None:
                        for ch in range(3):
                            pyxel.play(ch, [ch], loop=True)
                    self.board = Board(-1)
                    self.passed = 0
                    self.scene = 1
        elif self.scene == 1:
            board = self.board
            player = board.player
            if len(list(filter(lambda b: not b is None, board.next_state))) == 0:
                if self.passed == -player:
                    # パス処理
                    self.scene = 2
                self.passed = player
                board.set_board(-player, board.state)
            elif self.operator[str(player)] == HUMAN:
                if pressed:
                    y = (pyxel.mouse_y - 8) // 16
                    x = (pyxel.mouse_x - 8) // 16
                    pos = yx2pos(y, x)
                    self.set_stone(pos)
            else:
                next_pos = None
                min_score = None
                for pos, state in enumerate(board.next_state):
                    if state is None:
                        continue
                    tmp_score = 0
                    tmp_board = Board(-player, state)
                    for tmp_pos in range(64):
                        score = tmp_board.score[tmp_pos]
                        if score > tmp_score:
                            tmp_score = score
                    if min_score is None or min_score > tmp_score:
                        next_pos = pos
                        min_score = tmp_score
                self.set_stone(next_pos)
        elif self.scene == 2:
            if pressed:
                self.scene = 0

    def draw(self):
        if self.scene == 0:
            pyxel.cls(13)
            pyxel.text(46, 57, "Pyxel Reversi", 11)
            pyxel.text(46, 56, "Pyxel Reversi", 3)
            pyxel.rectb(12, 68, 56, 30, 3)
            pyxel.text(16, 72, "You (first) ", 0)
            pyxel.text(16, 80, "     vs     ", 3)
            pyxel.text(16, 88, "Com (Second)", 7)
            pyxel.rectb(76, 68, 56, 30, 3)
            pyxel.text(80, 72, "Com (first) ", 0)
            pyxel.text(80, 80, "     vs     ", 3)
            pyxel.text(80, 88, "You (Second)", 7)
        else:
            pyxel.cls(13)
            board = self.board
            board.draw(self.operator)
            if self.scene == 1:
                if self.passed != 0:
                    draw_small_stone(8, 152, self.passed)
                    pyxel.text(16, 152, "passed.", 7)
                elif self.operator[str(board.player)] == HUMAN:
                    pyxel.text(8, 152, "Your turn.", 7)
            if self.scene == 2:
                winner = board.winner()
                if winner == 0:
                    pyxel.text(8, 152, "draw...", 7)
                else:
                    draw_small_stone(8, 152, winner)
                    pyxel.text(16, 152, "win!", 7)

    def set_stone(self, pos):
        if pos is None:
            return
        board = self.board
        next_state = board.next_state[pos]
        if not next_state is None:
            pyxel.play(3, [3])
            board.animations = board.next_animations[pos]
            board.set_board(-board.player, next_state)
            self.passed = 0
            if self.operator[str(board.player)] == COM:
                self.counter = 10


App()
