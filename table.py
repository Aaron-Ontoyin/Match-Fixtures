from math import log
from random import shuffle


class TeamNames:
    def __init__(self) -> None:
        self.names = []
        self.num_names = 0

    @staticmethod
    def strip_name(name):
        return name.split(".")[1].strip()
    
    def add_name(self, name):
        if name:
            self.names.append(f"{self.num_names + 1}. {name.title()}")
            self.num_names += 1

    def delete_name(self, name_num):
        if name_num > self.num_names:
            return

        self.names.pop(name_num - 1)
        for idx, name in enumerate(self.names[name_num - 1 :], name_num - 1):
            num, name = self.names[idx].split(".")
            self.names[idx] = f"{int(num) - 1}. {name}"

        self.num_names -= 1


class Fixture:
    def __init__(self, id, next_fixture, previous_fixtures, team1=None, team2=None):
        self.id = id
        self.team1 = team1
        self.team2 = team2
        self.team1_score = None
        self.team2_score = None
        self.next = next_fixture
        self.prev = previous_fixtures

    def __str__(self) -> str:
        return f"{self.id}: {self.team1} vs {self.team2}, Mapping: From {self.prev} to {self.next}"

    def __repr__(self) -> str:
        return self.__str__()


class FixturesTable:

    def __init__(self, no_of_teams):
        no_of_stages = log(no_of_teams, 10) / log(2, 10)
        self.no_of_stages = int(no_of_stages)
        assert (
            no_of_stages % 1 == 0 and no_of_teams > 1
        ), "Number of teams must be a power of 2"

        no_of_boxes = int(2 * (2**no_of_stages - 1))

        self.no_of_teams = no_of_teams
        self.no_of_fixtures = int(no_of_boxes / 2)
        self.fixtures = {}

        for i in range(1, self.no_of_fixtures + 1):
            if i == 1:
                f = Fixture(i, None, [2, 3])
                self.fixtures[i] = f
            else:
                next_fixture = i // 2
                num_outter_fixtures = self.no_of_teams / 2
                num_inner_fixtures = self.no_of_fixtures - num_outter_fixtures
                pre_fixtures = [i * 2, i * 2 + 1] if i <= num_inner_fixtures else None
                f = Fixture(i, next_fixture, pre_fixtures)
                self.fixtures[i] = f

        self.graph_data = self.cal_graph_data()

        self.game_started = False

    def cal_graph_data(self):
        num_cols = 2 * self.no_of_stages - 1
        cols = []

        num_outter_fixtures = int(self.no_of_teams / 4)
        temp_fixtures = sorted(self.fixtures.keys(), reverse=True)

        while True:
            middle_idx = int(len(cols) // 2)
            cols.insert(
                middle_idx,
                [self.fixtures[i] for i in temp_fixtures[:num_outter_fixtures]],
            )
            temp_fixtures = temp_fixtures[num_outter_fixtures:]

            middle_idx = int(len(cols) // 2)
            cols.insert(
                middle_idx,
                [self.fixtures[i] for i in temp_fixtures[:num_outter_fixtures]],
            )
            temp_fixtures = temp_fixtures[num_outter_fixtures:]

            if len(temp_fixtures) == 1:
                middle_idx = int(len(cols) // 2)
                cols.insert(middle_idx, [self.fixtures[temp_fixtures[0]]])
                break

            if len(temp_fixtures) <= 3:
                num_outter_fixtures = 1
            else:
                num_outter_fixtures = int(num_outter_fixtures / 2)

        return {"no_cols": num_cols, "cols": cols}

    def set_match(self, fixture_id, team1_score, team2_score):

        if team1_score == team2_score:
            return

        fixture = self.fixtures[fixture_id]
        if fixture.team1 is None or fixture.team2 is None:
            return

        fixture.team1_score = team1_score
        fixture.team2_score = team2_score
        winner = fixture.team1 if team1_score > team2_score else fixture.team2
        if fixture.next is None:
            return
        next_fixture = self.fixtures[fixture.next]
        if next_fixture.team1 is None:
            next_fixture.team1 = winner
        else:
            if next_fixture.team1 != winner:
                next_fixture.team2 = winner

        self.game_started = True

    def randomise_table(self, names):

        if self.no_of_teams != len(names):
            return f"Number of teams in the table is {self.no_of_teams} but {len(names)} names were provided"

        if self.game_started:
            return "Game has already started"

        shuffle(names)
        num_outter_fixtures = int(self.no_of_teams / 2)
        outer_fixtures_ids = sorted(self.fixtures.keys(), reverse=True)[
            :num_outter_fixtures
        ]

        for i in outer_fixtures_ids:
            fixture = self.fixtures[i]
            fixture.team1 = names.pop()
            fixture.team2 = names.pop()

    def reset_table(self):

        for i in range(1, self.no_of_fixtures + 1):
            fixture = self.fixtures[i]
            fixture.team1 = None
            fixture.team2 = None
            fixture.team1_score = None
            fixture.team2_score = None
        
        self.game_started = False
