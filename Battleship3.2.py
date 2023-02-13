import os
from random import randrange
from random import choice

menu_of_game = ["Запустить игру", "Правила игры", "Об игре", "Завершить игру"]


class FieldPart:
    main = 'board'
    location = 'location'
    value = 'value'


class Cell:
    def set_cell(self):
        return self

    empty_cell = set_cell('.')
    ship_cell = set_cell('8')
    destroyed_ship = set_cell('X')
    damaged_ship = set_cell('+')
    miss_cell = set_cell(' ')


class Field:

    def __init__(self, size):
        self.size = size
        self.board = [[Cell.empty_cell for x in range(size)] for x in range(size)]
        self.location = [[Cell.empty_cell for x in range(size)] for x in range(size)]

    def get_field_part(self, element):
        if element == FieldPart.main:
            return self.board
        if element == FieldPart.location:
            return self.location
        if element == FieldPart.value:
            return self.value

    def draw_field(self, element):

        field = self.get_field_part(element)
        values = self.get_max_value_cells()

        for x in range(-1, self.size):
            for y in range(-1, self.size):
                if x == -1 and y == -1:
                    print("  ", end="")
                    continue
                if x == -1 and y >= 0:
                    print(y + 1, end=" ")
                    continue
                if x >= 0 and y == -1:
                    print(Game.row[x], end='')
                    continue
                print(" " + str(field[x][y]), end='')
            print("")
        print("")

    def check_ship_fits(self, ship, element):

        field = self.get_field_part(element)

        if ship.x + ship.height - 1 >= self.size or ship.x < 0 or \
                ship.y + ship.width - 1 >= self.size or ship.y < 0:
            return False

        x = ship.x
        y = ship.y
        width = ship.width
        height = ship.height

        for p_x in range(x, x + height):
            for p_y in range(y, y + width):
                if str(field[p_x][p_y]) == Cell.miss_cell:
                    return False

        for p_x in range(x - 1, x + height + 1):
            for p_y in range(y - 1, y + width + 1):
                if p_x < 0 or p_x >= len(field) or p_y < 0 or p_y >= len(field):
                    continue
                if str(field[p_x][p_y]) in (Cell.ship_cell, Cell.destroyed_ship):
                    return False

        return True

    def mark_destroyed_ship(self, ship, element):

        field = self.get_field_part(element)

        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        for p_x in range(x - 1, x + height + 1):
            for p_y in range(y - 1, y + width + 1):
                if p_x < 0 or p_x >= len(field) or p_y < 0 or p_y >= len(field):
                    continue
                field[p_x][p_y] = Cell.miss_cell

        for p_x in range(x, x + height):
            for p_y in range(y, y + width):
                field[p_x][p_y] = Cell.destroyed_ship

    def add_ship_to_field(self, ship, element):

        field = self.get_field_part(element)

        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        for p_x in range(x, x + height):
            for p_y in range(y, y + width):
                field[p_x][p_y] = ship

    def get_max_value_cells(self):
        values = {}
        max_value = 0
        for x in range(self.size):
            for y in range(self.size):
                if self.value[x][y] > max_value:
                    max_value = self.value[x][y]
                values.setdefault(self.value[x][y], []).append((x, y))

        return values[max_value]

    def count_value_board(self, available_ships):
        self.value = [[1 for x in range(self.size)] for x in range(self.size)]
        # Если раскомментировать код ниже, победить компьютер будет намного сложнее,
        # В этом случае логика ходов будет просчитываться за счет проставления баллов.
        # Т.к. логику хода мне помогли написать, считаю нечестным использовать его. В основном коде
        # так же присутствуют взаимосвязи с этой частью, но они не мешают выполнению всего кода.
        # for x in range(self.size):
        #     for y in range(self.size):
        #         if self.location[x][y] == Cell.damaged_ship:
        #
        #             self.value[x][y] = 0
        #
        #             if x - 1 >= 0:
        #                 if y - 1 >= 0:
        #                     self.value[x - 1][y - 1] = 0
        #                 self.value[x - 1][y] *= 50
        #                 if y + 1 < self.size:
        #                     self.value[x - 1][y + 1] = 0
        #
        #             if y - 1 >= 0:
        #                 self.value[x][y - 1] *= 50
        #             if y + 1 < self.size:
        #                 self.value[x][y + 1] *= 50
        #
        #             if x + 1 < self.size:
        #                 if y - 1 >= 0:
        #                     self.value[x + 1][y - 1] = 0
        #                 self.value[x + 1][y] *= 50
        #                 if y + 1 < self.size:
        #                     self.value[x + 1][y + 1] = 0
        #
        # for ship_size in available_ships:
        #
        #     ship = Ship(ship_size, 1, 1, 0)
        #     for x in range(self.size):
        #         for y in range(self.size):
        #             if self.location[x][y] in (Cell.destroyed_ship, Cell.damaged_ship, Cell.miss_cell) \
        #                     or self.value[x][y] == 0:
        #                 self.value[x][y] = 0
        #                 continue
        #             for rotation in range(0, 4):
        #                 ship.set_position(x, y, rotation)
        #                 if self.check_ship_fits(ship, FieldPart.location):
        #                     self.value[x][y] += 1


class Game:
    row = ['1', '2', '3', '4', '5', '6']
    ships_size = [3, 2, 2, 1, 1, 1]
    field_size = len(range(6))

    def __init__(self):

        self.players = []
        self.current_player = None
        self.next_player = None
        self.status = 'get_ready'

    def start_game(self):

        self.current_player = self.players[0]
        self.next_player = self.players[1]

    def status_check(self):
        if self.status == 'get_ready' and len(self.players) >= 2:
            self.status = 'action'
            self.start_game()
            return True
        if self.status == 'action' and len(self.next_player.ships) == 0:
            self.status = 'game over'
            return True

    def add_player(self, player):
        player.field = Field(Game.field_size)
        player.enemy_ships = list(Game.ships_size)
        self.ships_setup(player)
        player.field.count_value_board(player.enemy_ships)
        self.players.append(player)

    def ships_setup(self, player):
        for ship in Game.ships_size:
            retry_count = 30
            ship = Ship(ship, 0, 0, 0)

            while True:
                
                player.message.clear()

                x, y, r = player.get_input('ship_setup')
                if x + y + r == 0:
                    continue
                ship.set_position(x, y, r)

                if player.field.check_ship_fits(ship, FieldPart.main):
                    player.field.add_ship_to_field(ship, FieldPart.main)
                    player.ships.append(ship)
                    break

                retry_count -= 1
                if retry_count < 0:
                    player.field.board = [[Cell.empty_cell for x in range(Game.field_size)] for x in
                                          range(Game.field_size)]
                    player.ships = []
                    self.ships_setup(player)
                    return True

    def draw(self):
        if not self.current_player.is_ai:
            print('Поле с Вашими кораблями:')
            self.current_player.field.draw_field(FieldPart.main)
            print('Поле с кораблями соперника:')
            self.current_player.field.draw_field(FieldPart.location)
        for line in self.current_player.message:
            print(line)

    def switch_players(self):
        self.current_player, self.next_player = self.next_player, self.current_player


class Player:

    def __init__(self, name, is_ai, skill, auto_ship):
        self.name = name
        self.is_ai = is_ai
        self.auto_ship_setup = auto_ship
        self.skill = skill
        self.message = []
        self.ships = []
        self.enemy_ships = []
        self.field = None

    def get_input(self, input_type):

        if input_type == "ship_setup":

            if self.is_ai or self.auto_ship_setup:
                user_input = str(choice(Game.row)) + str(randrange(0, self.field.size)) + choice(["H", "V"])
            if len(user_input) < 3:
                return 0, 0, 0
            x, y, r = user_input[0], user_input[1:-1], user_input[-1]
            return Game.row.index(x), int(y) - 1, 0 if r == 'H' else 1

        if input_type == "shot":
            if self.is_ai:
                if self.skill == 1:
                    x, y = choice(self.field.get_max_value_cells())
                if self.skill == 0:
                    x, y = randrange(0, self.field.size), randrange(0, self.field.size)
            else:
                user_input = input().upper().replace(" ", "")
                x, y = user_input[0].upper(), user_input[1:]
                if x not in Game.row or not y.isdigit() or int(y) not in range(1, Game.field_size + 1):
                    self.message.append(f'Внимательнее {game.current_player.name}!')
                    return 500, 0
                x = Game.row.index(x)
                y = int(y) - 1
            return x, y

    def make_shot(self, target_player):

        sx, sy = self.get_input('shot')

        if sx + sy == 500 or self.field.location[sx][sy] != Cell.empty_cell:
            return 'retry'
        shot_res = target_player.receive_shot((sx, sy))

        if shot_res == 'miss':
            self.field.location[sx][sy] = Cell.miss_cell

        if shot_res == 'damage':
            self.field.location[sx][sy] = Cell.damaged_ship

        if type(shot_res) == Ship:
            destroyed_ship = shot_res
            self.field.mark_destroyed_ship(destroyed_ship, FieldPart.location)
            self.enemy_ships.remove(destroyed_ship.size)
            shot_res = 'kill'

        self.field.count_value_board(self.enemy_ships)
        return shot_res

    def receive_shot(self, shot):

        sx, sy = shot

        if type(self.field.board[sx][sy]) == Ship:
            ship = self.field.board[sx][sy]
            ship.hp -= 1

            if ship.hp <= 0:
                self.field.mark_destroyed_ship(ship, FieldPart.main)
                self.ships.remove(ship)
                return ship

            self.field.board[sx][sy] = Cell.damaged_ship
            return 'damage'

        else:
            self.field.board[sx][sy] = Cell.miss_cell
            return 'miss'


class Ship:

    def __init__(self, size, x, y, rotation):

        self.width = None
        self.size = size
        self.hp = size
        self.x = x
        self.y = y
        self.rotation = rotation
        self.set_rotation(rotation)

    def __str__(self):
        return Cell.ship_cell

    def set_position(self, x, y, r):
        self.x = x
        self.y = y
        self.set_rotation(r)

    def set_rotation(self, r):

        self.rotation = r

        if self.rotation == 0:
            self.width = self.size
            self.height = 1
        elif self.rotation == 1:
            self.width = 1
            self.height = self.size
        elif self.rotation == 2:
            self.y = self.y - self.size + 1
            self.width = self.size
            self.height = 1
        elif self.rotation == 3:
            self.x = self.x - self.size + 1
            self.width = 1
            self.height = self.size


class Menu:
    while True:

        for menu in menu_of_game:
            print(menu_of_game.index(menu) + 1, '.', menu)
        menu = input("Введите Ваш выбор: ")

        if menu == '1':
            print('Пушки наготове, самое время начать игру! \n'
                  'Но прежде прошу Вас представиться адмирал!')
            break

        elif menu == '2':
            print('_________________\n'
                  'ЦЕЛЬ ИГРЫ:\n'
                  'Разбить флот противника, потопив все его корабли.\n'
                  '\n'
                  'ПРАВИЛА ИГРЫ:\n'
                  'Перед Вами предстанет 2 поля с размерами 6х6, на одном из них размещен Ваш флот,\n'
                  'на втором поле пустые ячейки в которых скрыт вражеский флот состоящий из:\n'
                  '3-х шлюпок (однопалубные), 2-х эсминцев (двухпалубные) и одного крейсера (трехпалубный).\n'
                  'Для того, чтобы совершить выстрел, необходимо ввести координаты,\n'
                  'первая цифра по оси Х (горизонталь), вторая цифра ось У (вертикаль).\n'
                  '\n'
                  'Окунитесь в мир морских сражений. Удачи!\n'
                  '_________________\n')

        elif menu == '3':
            print('_________________\n'
                  '"МОРСКОЙ БОЙ"\n'
                  'Это не игра, это битва.\n'
                  '\n'
                  'В морской баталии принимает участие 1 адмирал (игрок).\n'
                  'Перед мореходом стоит важная задача, потопить вражеский флот.\n'
                  'Вам предстоит сразиться с невероятно сложным противником\n'
                  'по имени J.A.R.V.I.S. - Just A Rather Very Intelligent System \n'
                  '(рус. Просто довольно интеллектуальная система), \n'
                  'который очень любит поиграть в "Морской бой" в перерывах между \n'
                  'тем, чтобы помогать железному человеку в очередной раз спасти мир. \n'
                  'P.s. если повезет, иногда вместо Джарвиса играет сам Тони.\n'
                  '_________________')

        elif menu == '4':
            quit()


if __name__ == '__main__':

    Menu()
    players = [Player(name=input('Введите Ваше имя: '), is_ai=False, auto_ship=True, skill=1),
               Player(name='J.A.R.V.I.S.', is_ai=True, auto_ship=True, skill=1)]

    game = Game()

    while True:
        game.status_check()

        if game.status == 'get_ready':
            game.add_player(players.pop(0))

        if game.status == 'action':
            game.current_player.message.append("Введите координаты для выстрела: ")
            game.draw()
            game.current_player.message.clear()
            shot_result = game.current_player.make_shot(game.next_player)
            if shot_result == 'miss':
                game.next_player.message.append(f'На этот раз {game.current_player.name}, Вы промахнулись!')
                game.next_player.message.append('_' * 10)
                game.next_player.message.append(f'{game.next_player.name}, Ваш ход!')
                game.switch_players()
                continue
            elif shot_result == 'retry':
                game.current_player.message.append('Эти координаты недопустимы. Попробуйте еще раз!')
                continue
            elif shot_result == 'damage':
                game.current_player.message.append(f'Отличный выстрел {game.current_player.name}, продолжайте!')
                game.next_player.message.append('_' * 10)
                game.next_player.message.append(f'{game.next_player.name} ваш корабль под обстрелом!')
                continue
            elif shot_result == 'kill':
                game.current_player.message.append(
                    f'Так держать {game.current_player.name}! Вы потопили корабль противника!')
                game.next_player.message.append('_' * 10)
                game.next_player.message.append(f'Увы {game.next_player.name} ваш корабль был уничтожен.')
                continue

        if game.status == 'game over':
            print(f'Поле с потопленным флотом адмирала {game.next_player.name}:')
            game.next_player.field.draw_field(FieldPart.main)
            print(f'Поле с флотом побеноносного адмирала {game.current_player.name}:')
            game.current_player.field.draw_field(FieldPart.main)
            print(f'{game.next_player.name}, это был Ваш последний корабль')
            print(f'Поздравляю {game.current_player.name} Вы выиграли матч!')
            break
