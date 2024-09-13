import json
import argparse
import tkinter

def parseInput():
    parser = argparse.ArgumentParser("json_parser")
    parser.add_argument("input_file", help="This file will be used to generate the jeopardy board",type=str)
    args = parser.parse_args()
    if args.input_file == "":
        return ""
    return open(args.input_file,encoding="utf-8")

def parseJson(fp):
    data = json.load(fp)
    return data

class Game:
    def __init__(self,data):
        self.board = data["board"]
        self.config = data["config"]
        self.grid = {}
        self.board_to_grid()
        self.questions = data["questions"]
        self.isOver = False
        self.state = 0
        self.answer_id = 0
        self.answer = ""
        self.question_id = 0
        self.question = ""
        # 0 = board
        # 1 = answer
        # 2 = question
        self.window = tkinter.Tk()
        self.window.bind("<Button-1>", self.get_mouseposition)
        self.canvas = tkinter.Canvas(self.window, height=1200, width=1200,bg=self.config["background_color"])
        self.canvas.pack()
        self.draw()

    def board_to_grid(self):
        for idx,row in enumerate(self.board):
            for idy,answer in enumerate(row["answers"]):
                self.grid[idx,idy]=answer

    def get_mouseposition(self,event):
        self.mouse_x = event.x
        self.mouse_y = event.y
        if self.state!=0 or self.process_mouseposition():
            self.state = (self.state + 1) % 3
            if self.state == 2:
                self.mark_done()
            self.draw()

    def check_square(self,row,column):
        for idx,board_row in enumerate(self.board):
            for idy,answer in enumerate(board_row["answers"]):
                if idx==column and idy==row:
                    if "done" in answer.keys():
                        return False
                    else:
                        return True
        return False

    def mark_done(self):
        for board_row in self.board:
            for answer in board_row["answers"]:
                if self.answer_id==answer["id"]:
                    answer["done"]=True

    def get_question(self, id):
        for question in self.questions:
            if id == question["id"]:
                return question["text"]

    def process_mouseposition(self):
        if self.mouse_x > 100 and self.mouse_y > 100 and self.mouse_x < 1100 and self.mouse_y < 1100:
            # 0 100-300, 1 300-500, 2 500-700, 3 700-900, 4 900-1100
            column = (self.mouse_x-100)//200
            row = (self.mouse_y-100)//200
            valid = self.check_square(row,column)
            if valid:
                self.answer = self.grid[column,row]["text"]
                self.answer_id = self.grid[column,row]["id"]
                self.question_id = self.grid[column,row]["question_id"]
                self.question = self.get_question(self.question_id)
                return True
            return False
        else:
            return False

    def draw_board(self):
        for i in range(6):
            self.canvas.create_line((100+200*i,100,100+200*i,1100),width=1,fill=self.config["grid_color"])
            self.canvas.create_line((100,100+200*i,1100,100+200*i),width=1,fill=self.config["grid_color"])

    def draw(self):
        self.canvas.delete("all")
        if self.state == 0:
            self.draw_board()
            for idx,category in enumerate(self.board):
                self.canvas.create_text(200+idx*200,100,text=category["category_name"],width=200,font=('Times','18','bold'),anchor="s",justify="center",fill=self.config["text_color"])
                for row,answer in enumerate(category["answers"]):
                    number_color=self.config["done_color"] if "done" in answer.keys() else self.config["text_color"]
                    self.canvas.create_text(200+idx*200,200+200*row,text=answer["value"],font=('Times','30','bold'),fill=number_color)
        elif self.state == 1:
            self.canvas.create_text(600,600,text=self.answer,font=('Times','60'),width=1200,justify="center",fill=self.config["text_color"])
        elif self.state == 2:
            self.canvas.create_text(600,600,text=self.question,font=('Times','60'),width=1200,justify="center",fill=self.config["text_color"])

    def gameloop(self):
        self.window.mainloop()

def main():
    #parse input
    file_in = parseInput()
    if file_in == "":
        print("No input given")
        quit
    #parse file
    data = parseJson(file_in)
    file_in.close()
    #gameloop
    game = Game(data)
    game.gameloop()

if __name__=="__main__":
    main()