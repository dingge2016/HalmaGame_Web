import copy
import queue
import timeit
import numpy
from ipython_genutils.py3compat import xrange
import profile

class Board:
    chessNum = 19

    def __init__(self, size, player_num):
        self.size = size
        self.playerNum = player_num
        self.boardMatrix = [['.' for x in xrange(self.size)] for y in xrange(self.size)]

    def print(self):
        for i in self.boardMatrix:
            print(i)

    def random(self):

        b = 19
        while b:
            random_x = numpy.random.randint(0, 15)
            random_y = numpy.random.randint(0, 15)
            if self.boardMatrix[random_x][random_y] == '.':
                b -= 1
                self.boardMatrix[random_x][random_y] = 'B'
        w = 19
        while w:
            random_x = numpy.random.randint(0, 15)
            random_y = numpy.random.randint(0, 15)
            if self.boardMatrix[random_x][random_y] == '.':
                w -= 1
                self.boardMatrix[random_x][random_y] = 'W'
        return self.boardMatrix

    def initialize(self):
        if self.playerNum is 1:
            pass
        elif self.playerNum is 2:
            # Build black pieces on the top-left
            for i in xrange(0, 5):
                for j in xrange(0, 6 - i):
                    self.boardMatrix[i][j] = 'B'
            self.boardMatrix[0][5] = '.'

            # Build black pieces on the bottom-left
            for i in xrange(self.size - 5, self.size):
                for j in xrange(2 * self.size - 7 - i, self.size):
                    self.boardMatrix[i][j] = 'W'
            self.boardMatrix[-1][-6] = '.'
        return self.boardMatrix


class Action:
    def __init__(self, behavior, start, end):
        self.behavior = behavior
        self.start = start
        self.end = end

    def get_list(self):
        return [self.behavior, self.start, self.end]

    def print(self):
        return self.behavior + " " + self.start[0] + "," + self.start[1] + " " + self.end[0] + "," + self.end[1]


# static function

def empty(i, j, state):
    board_size = len(state)
    if i < 0 or j < 0 or i >= board_size or j >= board_size:
        return False
    if state[i][j] != '.':
        return False
    return True

def distance(p1_x, p1_y, p2_x, p2_y):
    return (p1_x - p2_x) ** 2 + (p1_y - p2_y) ** 2


def filled(i, j, state):
    board_size = len(state)
    if i < 0 or j < 0 or i >= board_size or j >= board_size:
        return False
    if state[i][j] != '.':
        return True
    return False


class Halma:
    dirs = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

    def __init__(self, board_size):
        self.boardSize = board_size
        self.leftTopConnor = set()
        self.rightBottomConnor = set()
        self.leftTopCamp = set()
        self.rightBottomCamp = set()
        for i in xrange(0, 5):
            for j in xrange(0, 6 - i):
                self.leftTopConnor.add((i, j))
        self.leftTopConnor.remove((0, 5))

        for i in xrange(self.boardSize - 5, self.boardSize):
            for j in xrange(2 * self.boardSize - 7 - i, self.boardSize):
                self.rightBottomConnor.add((i, j))
        self.rightBottomConnor.remove((self.boardSize - 1, self.boardSize - 6))

    def next_neibour(self, i, j, dir):
        x_next = i + dir[0]
        y_next = j + dir[1]
        return [x_next, y_next]

    def next_jump_neibour(self, i, j, dir):
        x_next = i + 2 * dir[0]
        y_next = j + 2 * dir[1]
        return [x_next, y_next]

    def check_legal(self, x: int, y: int, x_next: int, y_next: int, state: list, color: str) -> bool:
        if color is 'B':
            if (x, y) not in self.leftTopConnor and (x_next, y_next) in self.leftTopConnor:
                return False
            return True
        elif color is 'W':
            if (x, y) not in self.rightBottomConnor and (x_next, y_next) in self.rightBottomConnor:
                return False
            return True

    def search_actions_with_move(self, i, j, state, color):
        action_list = []
        for dir in self.dirs:
            [x_next, y_next] = self.next_neibour(i, j, dir)
            if empty(x_next, y_next, state) and self.check_legal(i, j, x_next, y_next, state, color):
                tmp = Action('E', [i, j], [x_next, y_next])
                action_list.append([tmp.get_list()])
        return action_list

    def search_actions_with_jump(self, i, j, state, color):
        jump_queue = queue.Queue()
        visited = [[False for x in xrange(self.boardSize)] for y in xrange(self.boardSize)]
        visited[i][j] = True
        action_id = 0
        jump_queue.put([i, j, -1])
        action_list = {}
        while not jump_queue.empty():
            [x, y, last_action_id] = jump_queue.get()
            for dir in self.dirs:
                [x_nei, y_nei] = self.next_neibour(x, y, dir)
                [x_next, y_next] = self.next_jump_neibour(x, y, dir)
                if empty(x_next, y_next, state) and filled(x_nei, y_nei, state) and visited[x_next][y_next] is False:
                    if self.check_legal(i, j, x_next, y_next, state, color):
                        visited[x_next][y_next] = True
                        tmp = Action('J', [x, y], [x_next, y_next])
                        jump_queue.put([x_next, y_next, action_id])
                        if last_action_id == -1:
                            action_list[action_id] = [tmp.get_list()]
                        else:
                            action_list[action_id] = action_list[last_action_id] + [tmp.get_list()]
                        action_id += 1

        return list(action_list.values())

    def camp_black(self, state):
        for (i, j) in self.leftTopConnor:
            if state[i][j] == 'B':
                return True
        return False

    def camp_white(self, state):
        for (i, j) in self.rightBottomConnor:
            if state[i][j] == 'W':
                return True
        return False

    def check_win(self, state):
        count_filled_w: int = 0
        exist_w = False
        for (i, j) in self.leftTopConnor:
            if state[i][j] == 'W':
                count_filled_w += 1
                exist_w = True
            elif state[i][j] == 'B':
                count_filled_w += 1

        count_filled_b = 0
        exist_b = False
        for (i, j) in self.rightBottomConnor:
            if state[i][j] == 'B':
                count_filled_b += 1
                exist_b = True
            elif state[i][j] == 'W':
                count_filled_b += 1
        return [count_filled_w == 19 and exist_w, count_filled_b == 19 and exist_b]


# test = Board(16, 2)
#
# state = test.boardMatrix
# state[0][0] = '.'
# a = Halma(16)
# for i in state:
#     print(i)
# ans = a.check_win(state)
# print(ans)


# actually I do not need the action units, I only want to know the node that I can visited


class GameAgent(Halma):


    def __init__(self, mode, color, remain_time, initial_state):
        """
        :string mode: SINGLE or GAME indicating game mode
        :string color: BlACK or WHITE indicating color you play
        :float remaining time: Total amount of remaining time for your agent
        :list board: current state of checker board
        """
        self.mode = mode
        self.color = color[0]
        self.opponentColor = 'W' if self.color == 'B' else 'B'
        self.remainTime = remain_time
        self.initialState = initial_state
        self.boardSize = len(initial_state)
        if remain_time <= 20:
            self.depthNum = 1
        else:
            self.depthNum = 2

        self.distance = {}
        for x1 in xrange(self.boardSize):
            for y1 in xrange(self.boardSize):
                for x2 in xrange(self.boardSize):
                    for y2 in xrange(self.boardSize):
                        self.distance[(x1, y1, x2, y2)] = (x1 - x2) ** 2 + (y1 - y2) ** 2

        Halma.__init__(self, len(initial_state))

    def terminal_test(self, state, depth):
        if self.remainTime < 0.001 or depth == self.depthNum:
            return True
        return False

    # in the future, write it
    def utility(self, state):
        winCheck = self.check_win(state)

        if self.color == 'B':
            if winCheck[1]:
                return float('inf')
            #if winCheck[0]:
            #    return float('-inf')

        if self.color == 'W':
            if winCheck[0]:
                return float('inf')
            #if winCheck[1]:
            #    return float('-inf')

        value_b = 0.0001
        value_w = 0.0001
        b_goals = [goal for goal in self.rightBottomConnor if state[goal[0]][goal[1]] =='.']
        w_goals = [goal for goal in self.leftTopConnor if state[goal[0]][goal[1]] =='.']
        for i in xrange(self.boardSize):
            for j in xrange(self.boardSize):
                if state[i][j] == 'B':
                    distanceList = [self.distance[(i, j, goal[0], goal[1])] for goal in b_goals]
                    value_b += max(distanceList) if len(distanceList) else -1 if self.camp_white(state) else 0

                elif state[i][j] == 'W':
                    distanceList = [self.distance[(i, j, goal[0], goal[1])] for goal in w_goals]
                    value_w += max(distanceList) if len(distanceList) else -1 if self.camp_black(state) else 0
        if self.color == 'B':
            return value_w / value_b
        elif self.color == 'W':
            return value_b / value_w

    def search_actions(self, state, color):
        action_list = []
        for i in xrange(self.boardSize):
            for j in xrange(self.boardSize):
                if state[i][j] == color:
                    action_list += self.search_actions_with_jump(i, j, state, color)

        for i in xrange(self.boardSize):
            for j in xrange(self.boardSize):
                if state[i][j] == color:
                    action_list += self.search_actions_with_move(i, j, state, color)

        return self.check_outer(action_list, state, color)

    def check_outer(self, action_list, state, color):
        found = 0
        action_list_move_out = []
        action_list_move_away = []
        if color == 'B':
            if self.camp_black(state):
                for action in action_list:
                    [x, y] = [action[0][1][0], action[0][1][1]]
                    [x_next, y_next] = [action[-1][2][0], action[-1][2][1]]
                    if (x, y) in self.leftTopConnor:
                        if (x_next, y_next) not in self.leftTopConnor:
                            found += 1
                            action_list_move_out.append(action)
                        elif x_next >= x and y_next >= y:
                            action_list_move_away.append(action)

        if color == 'W':
            if self.camp_white(state):

                for action in action_list:
                    [x, y] = [action[0][1][0], action[0][1][1]]
                    [x_next, y_next] = [action[-1][2][0], action[-1][2][1]]
                    if (x, y) in self.rightBottomConnor:
                        if (x_next, y_next) not in self.rightBottomConnor:
                            found += 1
                            action_list_move_out.append(action)
                        elif x_next <= x and y_next <= y:
                            action_list_move_away.append(action)


        if len(action_list_move_out) != 0:
            return action_list_move_out
        elif len(action_list_move_away) != 0:
            return action_list_move_away
        else:
            return action_list

    def result(self, state, action, color):
        new_state = numpy.copy(state)
        new_state[action[0][1][0]][action[0][1][1]] = '.'
        new_state[action[-1][2][0]][action[-1][2][1]] = color

        return new_state


class AlphaBetaAgent(GameAgent):

    valueAction = {}
    def max_value(self, state, alpha, beta, depth):
        if self.terminal_test(state, depth):
            return self.utility(state)
        max_value = float("-inf")
        action_list = self.search_actions(state, self.color)
        for action in action_list:

            value = self.min_value(self.result(state, action, self.color), alpha, beta, depth + 1)

            max_value = max(value, max_value)
            if depth == 0:
                self.valueAction[value] = action
            if value >= beta:
                return max_value
            alpha = max(alpha, value)
        return max_value

    def min_value(self, state, alpha, beta, depth):
        if self.terminal_test(state, depth):
            return self.utility(state)
        min_value = float("inf")

        action_list = self.search_actions(state, self.opponentColor)

        for action in action_list:
            value = self.max_value(self.result(state, action, self.opponentColor), alpha, beta, depth + 1)
            min_value = min(value, min_value)
            if value <= alpha:
                return min_value
            beta = min(beta, value)
        return value

    def alpha_beta_search(self):
        value = self.max_value(self.initialState, float('-inf'), float('inf'), 0)
        return self.valueAction[value]

#
# test = Board(16, 2)
# state = test.initialize()
# # # state = [['.', '.', '.', '.', '.', 'B', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
# # # ['.', '.', '.', '.', '.', 'B', 'B', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
# # # ['.', '.', '.', '.', 'B', 'B', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
# # # ['.', '.', '.', 'B', 'B', 'B', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
# # # ['.', '.', 'B', 'B', 'B', 'B', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
# # # ['B', 'B', 'B', '.', 'B', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
# # # ['.', 'B', 'B', 'B', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
# # # ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
# # # ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
# # # ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'W', '.', '.'],
# # # ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'W', 'W', '.'],
# # # ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'W', 'W', 'W', 'W', '.', '.'],
# # # ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'W', 'W', '.', '.', '.'],
# # # ['.', '.', '.', '.', '.', '.', '.', '.', '.', 'W', 'W', 'W', '.', '.', '.', 'W'],
# # # ['.', '.', '.', '.', '.', '.', '.', '.', 'W', 'W', 'W', '.', '.', '.', 'W', 'W'],
# # # ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'W']]
# # # for i in state:
# # #     print(i)
# # # OpAction = AlphaBetaAgent("SINGLE", "W", 100, state)
# # # ans = OpAction.search_actions(state, "W")
# # # print("ansforB", ans)
# time = 30
# round = 0
# while time:
#
#     startTime = timeit.default_timer()
#     state = numpy.array(state)
#     myAction = AlphaBetaAgent("SINGLE", "W", 30, state)
#     ans = myAction.alpha_beta_search()
#
#
#     #print("ansforW", ans)
#     state = myAction.result(state, ans, "W")
#
#     print("------------------------")
#     for i in state:
#         print(i)
#     print("------------------------")
#     if myAction.check_win(state)[0] and myAction.check_win(state)[1]:
#         break
#     OpAction = AlphaBetaAgent("SINGLE", "B", 10, state)
#     ans = OpAction.alpha_beta_search()
#     # print("ansforB", ans)
#     state = OpAction.result(state, ans, "B")
#     print("------------------------")
#     for i in state:
#         print(i)
#     print("------------------------")
#     print(OpAction.check_win(state)[0],  OpAction.check_win(state)[1])
#     if OpAction.check_win(state)[0] and OpAction.check_win(state)[1]:
#         break
#     endTime = timeit.default_timer()
#     round += 1
#     print("round", round)
# #     print(endTime - startTime)
#
#
# input = open("input.txt", 'r').read().split('\n')
#
# output = open("output.txt", 'w')
# mode = str(input[0].strip('\r'))
# color = str(input[1][0].strip('\r'))
# remain_time = float(input[2].strip('\r'))
#
# state = [[str(x) for x in input[i].strip('\r')] for i in range(3, 19)]
# state = numpy.array(state)
#
# OpAction = AlphaBetaAgent(mode, color, remain_time, state)
# ans = OpAction.alpha_beta_search()
# state = OpAction.result(state, ans, "W")
# for action in ans:
#     output.write("%s "%action[0])
#     output.write(str(action[1][1]))
#     output.write(",")
#     output.write(str(action[1][0]))
#     output.write(" ")
#     output.write(str(action[2][1]))
#     output.write(",")
#     output.write(str(action[2][0]))
#     output.write("\n")
# output.close()