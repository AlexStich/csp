#!/usr/bin/python

import sys
import queue
import os


class Csp:
    def __init__(self):
        self.sudokus_start = "./sudokus_start.txt"
        self.sudokus_finish = "./sudokus_finish.txt"
        self.outputFile = "./output.txt"
        self.rows = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
        self.columns = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        self.queue_ac3 = queue.Queue(maxsize=0)
        self.initial_domain = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.constrains = {}           # key (e.g. col_1 || row_A || box_1) -> constrain
        self.relations_between_fields_and_constrains = {}       # field -> [constrain_key, ...]

    def start(self, board):
        board = self.normalize_data(board)
        self.setConstrains()
        fields_domains = self.setFieldsDomains(board)
        self.createQueue(fields_domains)

        if self.AC3(board, fields_domains):
            self.writeOutput(self.getResultString(board) + " AC3")
        else:
            result_board = self.backtracking(board, fields_domains)
            self.writeOutput(self.getResultString(result_board) + " BTS")

    def backtracking(self, board, fields_domains):

        if len(fields_domains) == 0:
            return board

        field = self.successorFunction(fields_domains)

        for field_value in fields_domains[field]:
            if self.constrainsWorked(field, field_value, board):
                field_domain = fields_domains[field].copy()
                field_domain.remove(field_value)
                fields_domains[field] = field_domain

                if len(fields_domains.get(field)) == 0:  # domain is empty - no solutions
                    return False
            else:
                new_board = board.copy()
                new_fields_domains = fields_domains.copy()

                new_board[field] = str(field_value)
                del(new_fields_domains[field])

                self.createQueue(new_fields_domains)
                if self.AC3(new_board, new_fields_domains):
                    return new_board

                result_board = self.backtracking(new_board, new_fields_domains)

                if result_board:
                    return result_board

        return False

    def AC3(self, board, fields_domains):
        while self.queue_ac3.qsize():
            field = self.queue_ac3.get()

            if not fields_domains.get(field, False):    # don't process state if it excluded from fields_domain
                continue

            domain_changed = self.applyConstrains(field, board, fields_domains)

            if len(fields_domains.get(field)) == 0:     # domain is empty - no solutions
                return False

            if len(fields_domains[field]) == 1:         # move field on board and remove from fields_domains
                board[field] = str(fields_domains[field][0])
                del (fields_domains[field])

            if domain_changed:
                related_fields = self.getRelatedFields(field, fields_domains)
                self.addToQueue(related_fields)

            if len(fields_domains) == 0:
                return True

        return False

    def successorFunction(self, fields_domains: dict):

        fields_domains_sorted = list(sorted(fields_domains.items(), key=lambda domain: len(domain[1]) + (1 - len(self.getRelatedFields(domain[0], fields_domains))/27)))

        return fields_domains_sorted.pop(0)[0]

    def getRelatedFields(self, field, fields_domains):

        total_fields = []

        for constrain_key in self.relations_between_fields_and_constrains[field]:
            related_fields = self.constrains[constrain_key].copy()
            related_fields.remove(field)
            total_fields += related_fields

        fields_to_queue = list(set(total_fields).intersection(set(map(lambda x: x[0], fields_domains.items()))))

        return fields_to_queue

    def createQueue(self, fields_domains):

        self.queue_ac3 = queue.Queue(maxsize=0)

        for field, field_domain in fields_domains.items():
            self.queue_ac3.put(field)

    def addToQueue(self, fields):

        for field in fields:
            self.queue_ac3.put(field)

    def applyConstrains(self, field, board, fields_domains):

        domain_change = False
        values_for_remove = []

        if not fields_domains.get(field, False):
            return False

        for field_value in fields_domains[field]:
            if self.constrainsWorked(field, field_value, board):
                values_for_remove.append(field_value)
                domain_change = True

        if values_for_remove:
            domain = fields_domains[field].copy()
            for value in values_for_remove:
                domain.remove(value)
            fields_domains[field] = domain

        return domain_change

    def constrainsWorked(self, field, field_value, board_):

        has_similar_fields = False
        end_loops = False

        board = board_.copy()
        board[field] = str(field_value)

        for constrain_key in self.relations_between_fields_and_constrains[field]:

            for field1 in self.constrains[constrain_key]:
                checked_fields = []

                for field2 in self.constrains[constrain_key]:

                    if (field2 not in checked_fields) and (field1 != field2) and \
                        board[field1] != "0" and board[field2] != "0" \
                            and board[field1] == board[field2]:

                        has_similar_fields = True

                        end_loops = True
                        break

                if end_loops:
                    break

                checked_fields.append(field1)

            if end_loops:
                break

        return has_similar_fields

    def setFieldsDomains(self, board):

        fields_domains = {}
        for field, value in board.items():
            if value == "0":
                fields_domains[field] = self.initial_domain

        return fields_domains

    def setConstrains(self):

        # row constrain
        for row in self.rows:
            row_constrain = []
            for column in self.columns:
                row_constrain.append(row + column)

                # fill relations between fields and constrains
                self.fillRelationsBetweenFieldsAndConstrains(row + column, "row_" + row)

            self.constrains.update({"row_" + row: row_constrain})

        # column constrain
        for column in self.columns:
            column_constrain = []
            for row in self.rows:
                column_constrain.append(row + column)

                # fill relations between fields and constrains
                self.fillRelationsBetweenFieldsAndConstrains(row + column, "col_" + column)

            self.constrains.update({"col_" + column: column_constrain})

        # box constrain
        axis_range = [[0, 3],[3, 6],[6, 9]]
        i = 0
        for x_col, y_col in axis_range:
            for x_row, y_row in axis_range:
                i = i + 1
                box_constrain = []
                for column in self.columns[x_col:y_col]:
                    for row in self.rows[x_row:y_row]:
                        box_constrain.append(row + column)

                        # fill relations between fields and constrains
                        self.fillRelationsBetweenFieldsAndConstrains(row + column, "box_" + str(i))

                self.constrains.update({"box_" + str(i): box_constrain})

    def fillRelationsBetweenFieldsAndConstrains(self, field, constrain_key):

        if self.relations_between_fields_and_constrains.get(field, False):
            old_value = self.relations_between_fields_and_constrains[field]
            self.relations_between_fields_and_constrains[field] = old_value + [constrain_key]
        else:
            self.relations_between_fields_and_constrains[field] = [constrain_key]

    def getResultString(self, board):
        return "".join(map(lambda x: str(x[1]), board.items()))

    def writeOutput(self, row):

        file = open(self.outputFile, "a")
        file.write(row)
        file.close()

    def normalize_data(self, input_data):

        board = {}
        i = 0

        for row in self.rows:
            for column in self.columns:
                board[row + column] = input_data[i]
                i = i + 1

        return board


def main(input_data=None):

    board = {}

    csp = Csp()

    if os.path.isfile(csp.outputFile):
        os.remove(csp.outputFile)

    if input_data:
        board = input_data
    else:

        file = open(csp.sudokus_start)

        for line in file:
            csp.__init__()
            board = line
            csp.start(board)

        file.close()

        exit(3)

    csp.start(board)


if __name__ == '__main__':

    input_data = None

    if len(sys.argv) > 1:
        input_data = sys.argv[1]

    main(input_data)
