#!/usr/bin/python

import sys
import csv
import statistics as st


class Csp:
    def __init__(self):
        self.sudoku_start = "./sudoku_start.txt"
        self.sudoku_finish = "./sudoku_finish.txt"
        self.outputFile = "./output.txt"
        self.init_board = {}
        self.domains = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.constrains = []
        self.rows = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
        self.columns = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

    def start(self):

        self.init_board = self.normalize_data(self.init_board)
        self.setConstrains()

        result = self.AC3()

        if result:
            self.writeOutput(result + " AC3")
        else:
            result = self.backtracking()
            self.writeOutput(result + " BTS")

    def AC3(self):

        result = ""
        board = self.init_board.copy()
        set_ = self.getOptimalSet(board)

        # Compute by set. Set is row, column or box has minimum empty fields
        while set_:

            for field in board:
                set_ = self.getOptimalSet(board)


        return result

    def backtracking(self):

        result = ""
        while not True:
            return result

    def getOptimalSet(self, board):

        # Take constrains lists as base of set
        result_set = []
        min_zero_count = 9
        for set in self.constrains:
            zero_count = 0
            for field, value in board:
                if value == "0":
                    zero_count += 1
            if zero_count > min_zero_count:
                min_zero_count = zero_count
                result_set = set

        return result_set

    def checkConstrains(self, board, insert_pos):

        has_similar_fields = False
        end_loops = False

        for constrain in self.constrains:
            if next(iter(insert_pos)) in constrain:

                for field1 in constrain:
                    checked_fields = []
                    for field2 in constrain:

                        if (not field2 in checked_fields) and \
                        board.index(field1) != 0 and board.index(field2) != 0 \
                        and board.index(field1) == board.index(field2):

                            has_similar_fields = True

                            end_loops = True
                            break

                    if end_loops:
                        break
                    checked_fields.append(field1)

                if end_loops:
                    break

        return has_similar_fields

    def setConstrains(self):

        # row constrain
        for row in self.rows:
            column_constrain = []
            for column in self.columns:
                column_constrain.append(row + column)

            self.constrains.append(column_constrain)

        # column constrain
        for column in self.columns:
            column_constrain = []
            for row in self.rows:
                column_constrain.append(row + column)

            self.constrains.append(column_constrain)

        # box constrain
        axis_range = [[0, 3],[3, 6],[6, 9]]
        for x_col, y_col in axis_range:
            box_constrain = []
            for x_row, y_row in axis_range:
                for column in self.columns[x_col:y_col]:
                    for row in self.rows[x_row:y_row]:
                        box_constrain.append(row + column)

                self.constrains.append(box_constrain)

    def writeOutput(self, row):
        file = open(self.outputFile, "w")
        file.write(row)
        file.close()

    def normalize_data(self, input_data):

        board = {}

        for row in self.rows:
            i = 0
            for column in self.columns:
                i = i + 1
                board[row + column] = input_data[i]

        return board


def main(input_data=None):

    csp = Csp()

    if input_data:
        csp.init_board = input_data
    else:
        file = open(csp.sudoku_start)
        csp.init_board = file.readline()
        file.close()

    csp.start()


if __name__ == '__main__':

    input_data = None

    if sys.argv[1]:
        input_data = sys.argv[1]

    main(input_data)
