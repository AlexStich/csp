#!/usr/bin/python

import sys
import queue


class Csp:
    def __init__(self):
        self.sudokus_start = "./sudokus_start.txt"
        self.sudokus_finish = "./sudokus_finish.txt"
        self.outputFile = "./output.txt"
        self.board = {}
        self.initial_domain = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.fieldsDomains = {}        # e.g. {field1: [1,2,3], , ... } contains fields with zero and more than one value
        self.constrains = {}           # key (e.g. col_1 || row_A || box_1) -> constrain
        self.relations_between_fields_and_constrains = {}       # field -> [constrain_key, ...]
        self.rows = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
        self.columns = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        self.queue_ = queue.Queue(maxsize=0)

    def start(self):
        self.board = self.normalize_data(self.board)
        self.setConstrains()
        self.setFieldsDomains(self.board)
        self.createQueue()

        if self.csp():
            self.writeOutput(self.getResult() + " AC3")
            print(self.getResult())
        else:
            self.backtracking()
            self.writeOutput(self.getResult() + " BTS")

    def getResult(self):
        return "".join(map(lambda x: str(x[1]), self.board.items()))

    def csp(self):
        while self.queue_.qsize():
            field = self.queue_.get()

            if not self.fieldsDomains.get(field, False):    # don't process state if it excluded from fields_domain
                continue

            domain_changed = self.applyConstrains(field)

            if len(self.fieldsDomains.get(field)) == 0:     # domain is empty - no solutions
                return False

            if len(self.fieldsDomains[field]) == 1:         # move field on board and remove from fields_domains
                self.board[field] = str(self.fieldsDomains[field][0])
                del (self.fieldsDomains[field])

            if domain_changed:
                related_fields = self.getRelatedFields(field)
                self.addToQueue(related_fields)

            if len(self.fieldsDomains) == 0:
                return True

        return False

    def backtracking(self):

        result = ""
        return result

    def getRelatedFields(self, field):

        total_fields = []

        for constrain_key in self.relations_between_fields_and_constrains[field]:
            related_fields = self.constrains[constrain_key].copy()
            related_fields.remove(field)
            total_fields += related_fields

        return list(set(total_fields))

    def createQueue(self):

        self.queue_ = queue.Queue(maxsize=0)
        for field, field_domain in self.fieldsDomains.items():
            self.queue_.put(field)

    def addToQueue(self, fields):

        for field in fields:
            self.queue_.put(field)

    def applyConstrains(self, field):

        domain_change = False
        values_for_remove = []

        if not self.fieldsDomains.get(field, False):
            return False

        for field_domain in self.fieldsDomains[field]:
            if self.hasConstrains(field, field_domain):
                values_for_remove.append(field_domain)
                domain_change = True

        if values_for_remove:
            domain = self.fieldsDomains[field].copy()
            for value in values_for_remove:
                domain.remove(value)
            self.fieldsDomains[field] = domain

        return domain_change

    def hasConstrains(self, field, field_domain):

        has_similar_fields = False
        end_loops = False

        board = self.board.copy()
        board[field] = str(field_domain)

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

        for field, value in board.items():
            if value == "0":
                self.fieldsDomains[field] = self.initial_domain

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

    csp = Csp()

    if input_data:
        csp.board = input_data
    else:

        file = open(csp.sudokus_start)

        for line in file:
            csp.__init__()
            csp.board = line
            csp.start()

        file.close()

        exit(3)

    csp.start()


if __name__ == '__main__':

    input_data = None

    if len(sys.argv) > 1:
        input_data = sys.argv[1]

    main(input_data)
