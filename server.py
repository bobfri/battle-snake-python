import os
import random

import cherrypy

"""
This is a simple Battlesnake server written in Python and was based on the starter snake from battlesnake official
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""
class Board(object):
    def __init__(self, maxx, maxy):
      self.board=[[{"visited":False,"snake":False,"tail":False,"head_move":False} for i in range(maxy)] for j in range(maxx)]
      self.maxx=maxx
      self.maxy=maxy
      self.turn=0
      return

    def clean(self,turn):
      self.turn=turn
      self.board=[[{"visited":False,"snake":False,"tail":False,"head_move":False} for i in range(self.maxy)] for j in range(self.maxx)]

      return
    def snake(self,snake_piece):
      self.board[snake_piece["x"]][snake_piece["y"]]["snake"]=True
      return
    def tail(self,tail):
      self.board[tail["x"]][tail["y"]]["tail"]=True
    def head(self,head):
      moves_ressult = {
          "up":{"x":0,"y":1},
         "down":{"x":0,"y":-1}, 
         "left":{"x":-1,"y":0}, 
         "right":{"x":1,"y":0}}
      for move in moves_ressult:
        temp={"x":(moves_ressult.get(move)["x"]+head["x"]),"y":(moves_ressult.get(move)["y"]+head["y"])}
        if temp["x"]>=0 and temp["x"]<self.maxx and temp["y"]>=0 and temp["y"]<self.maxy:
          if not self.board[temp["x"]][temp["y"]]["snake"]:
            self.board[head["x"]][head["y"]]["head_move"]=True

    def check(self,move,head,length):
      moves_ressult = {
          "up":{"x":0,"y":1},
         "down":{"x":0,"y":-1}, 
         "left":{"x":-1,"y":0}, 
         "right":{"x":1,"y":0}}
      to_visite=[{"x":(moves_ressult.get(move)["x"]+head["x"]),"y":(moves_ressult.get(move)["y"]+head["y"])}]
      board=self.board.copy()
      board[to_visite[0]["x"]][to_visite[0]["y"]]["visited"]= False
      visited_stack=[]
      head_move=False
      tail=False
      while len(visited_stack)<=length:
        if len(to_visite)==0:
          return {"wontTrap":False,"visited":len(visited_stack), "move":move, "tail":tail, "head_move":head_move}
        tempPlace=to_visite.pop(0)
        visited_stack.append(tempPlace)
        if (tempPlace["y"]+1)<self.maxy:
          if not board[tempPlace["x"]][tempPlace["y"]+1]["visited"] and not board[tempPlace["x"]][tempPlace["y"]+1]["snake"] and not board[tempPlace["x"]][tempPlace["y"]+1]["head_move"]:
            board[tempPlace["x"]][tempPlace["y"]+1]["visited"]= True
            to_visite.append({"x":tempPlace["x"],"y":tempPlace["y"]+1})
          if board[tempPlace["x"]][tempPlace["y"]+1]["head_move"]:
            head_move=True
          if board[tempPlace["x"]][tempPlace["y"]+1]["tail"]:
            tail=True
        if (tempPlace["y"]-1)>=0:
          if not board[tempPlace["x"]][tempPlace["y"]-1]["visited"] and not board[tempPlace["x"]][tempPlace["y"]-1]["snake"] and not board[tempPlace["x"]][tempPlace["y"]-1]["head_move"]:
            board[tempPlace["x"]][tempPlace["y"]-1]["visited"]= True
            to_visite.append({"x":tempPlace["x"],"y":tempPlace["y"]-1})
          if board[tempPlace["x"]][tempPlace["y"]-1]["head_move"]:
            head_move=True
          if board[tempPlace["x"]][tempPlace["y"]-1]["tail"]:
            tail=True
        if (tempPlace["x"]+1)<self.maxx:
          if not board[tempPlace["x"]+1][tempPlace["y"]]["visited"] and not board[tempPlace["x"]+1][tempPlace["y"]]["snake"] and not board[tempPlace["x"]+1][tempPlace["y"]]["head_move"]:
            board[tempPlace["x"]+1][tempPlace["y"]]["visited"]= True
            to_visite.append({"x":tempPlace["x"]+1,"y":tempPlace["y"]})
          if board[tempPlace["x"]+1][tempPlace["y"]]["head_move"]:
            head_move=True
          if board[tempPlace["x"]+1][tempPlace["y"]]["tail"]:
            tail=True
        if (tempPlace["x"]-1)>=0:
          if not board[tempPlace["x"]-1][tempPlace["y"]]["visited"] and not board[tempPlace["x"]-1][tempPlace["y"]]["snake"] and not board[tempPlace["x"]-1][tempPlace["y"]]["head_move"]:
            board[tempPlace["x"]-1][tempPlace["y"]]["visited"]= True
            to_visite.append({"x":tempPlace["x"]-1,"y":tempPlace["y"]})
          if board[tempPlace["x"]-1][tempPlace["y"]]["head_move"]:
            head_move=True
          if board[tempPlace["x"]-1][tempPlace["y"]]["tail"]:
            tail=True
      return {"wontTrap":True,"visited":0, "move":move, "tail":tail, "head_move":head_move}


    def printboard(self):
      print(self.board)
      return

class Battlesnake(object):
    boards= {}
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "bobfrit",  
            "color": "#80c1ff", 
            "head": "silly",  
            "tail": "bolt", 
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json
        self.boards.update({data["game"]["id"]: Board(data["board"]["width"],data["board"]["height"])})
        print("START")
        return "ok"
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        data = cherrypy.request.json
        board=self.boards[data["game"]["id"]]
        if board.turn!= data["turn"]:
          board.clean(data["turn"])
        head = data["you"]["head"]
        possible_moves = ["up", "down", "left", "right"]
        tryMoves=possible_moves.copy()
        board_sanke_death_move=self.clashWithHead(head)
        remove_move=self.outOfBoardMove()+self.crashIntoSnake(head)
        remove_move.extend(board_sanke_death_move.copy())
        #self.board.printboard()
        tryMoves=[temp for temp in possible_moves if temp not in remove_move]
        print(f"trymove 1:{tryMoves}")
        try :
          if len(tryMoves)==0:
            tryMoves.extend(board_sanke_death_move)
          if len(tryMoves)==1 and len(board_sanke_death_move)==0:
            move= tryMoves[0]
          else:
            print(f"trymove 2:{tryMoves}")
            #if len(data["board"]["snakes"])==2:
              #123ertjC XtryMovesNearest = self.kill(tryMoves.copy(),head,[data["board"]["snakes"]]);
              #print(data["board"]["snakes"])
            tryMovesNearest = self.nearest_food(tryMoves.copy(),head,data["board"]["food"])
            move = random.choice(tryMovesNearest)

            trapMove=[]
            trapMove.append(board.check(move,data["you"]["head"],data["you"]["length"]))
            print(f"trymove 3:{tryMoves}")
            print(f"trymovenearest 1:{tryMovesNearest}")
            print(f"trapmove 1:{trapMove}")
            if not trapMove[-1]["wontTrap"]:
              
              tryMovesNearest.remove(move)
              print(f"trymove 4:{tryMoves}")
              print(f"trymovenearest 2:{tryMovesNearest}")
              print(f"trapmove 2:{trapMove}")
              if len(tryMovesNearest) == 1:
                tryMoves.remove(move)
                move=tryMovesNearest[0]
                trapMove.append(board.check(move,data["you"]["head"],data["you"]["length"]))
              count=0
              while len(tryMoves)>0:
                count+=1
                if count>6:
                  raise Exception("stuck in loop")
                print(f"trymove 5:{tryMoves}")
                print(f"trymovenearest 3:{tryMovesNearest}")
                print(f"trapmove 3:{trapMove}")
                print(f"move 1:{move}")
                tryMoves.remove(move)
                print(len(tryMoves))
                print(f"trymove 6:{tryMoves}")
                print(f"trymovenearest 4:{tryMovesNearest}")
                print(f"trapmove 4:{trapMove}")
                if not trapMove[-1]["wontTrap"]:
                  if len(tryMoves)==0:
                    trapMove.sort(key=lambda x:x["tail"])
                    move=trapMove[-1]["move"]
                    if not trapMove[-1]["tail"]:
                      trapMove.sort(key=lambda x:x["visited"])
                      move=trapMove[-1]["move"]
                    if len(board_sanke_death_move)<=0:
                      break
                    else:
                      tryMoves.extend(board_sanke_death_move)
                      move=tryMoves[0]
                      board_sanke_death_move.clear()

                  else:
                    move=tryMoves[0]
                    trapMove.append(board.check(move,data["you"]["head"],data["you"]["length"]))
                else:
                  break


        except IndexError as e:
          print(e)
          print("random")
          move = random.choice(possible_moves)
        print(f"MOVE: {move}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        print("END")
        return "ok"
        

    #return a list of moves that would kill the snake by crashing into and other snake
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def crashIntoSnake(self,head):
        moves_ressult = {
          "up":{"x":0,"y":1},
         "down":{"x":0,"y":-1}, 
         "left":{"x":-1,"y":0}, 
         "right":{"x":1,"y":0}}
        move_return=[]
        data = cherrypy.request.json
        #head = data["you"]["head"]
        snake_block=[]
        #for peice in  data["you"]["body"]:
         # snake_block.append(peice)
        board= self.boards[data["game"]["id"]]
        for snake in data["board"]["snakes"]:
          for peice in snake["body"]:
            snake_block.append(peice)
            board.snake(peice)
          #TODO check if the other snake will eat
          board.tail(snake_block.pop())
          board.head(snake["head"])
        for pos_move in moves_ressult:
          temp={"x":(moves_ressult.get(pos_move)["x"]+head["x"]),"y":(moves_ressult.get(pos_move)["y"]+head["y"])}
          if temp in snake_block:
            move_return.append(pos_move)
        return move_return

    #return list of moves that will be out of the board
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def outOfBoardMove(self):
        moves_ressult = {
          "up":{"x":0,"y":1},
         "down":{"x":0,"y":-1}, 
         "left":{"x":-1,"y":0}, 
         "right":{"x":1,"y":0}}
        move_return=[]
        data = cherrypy.request.json
        max_y=data["board"]["height"]
        max_x=data["board"]["width"]
        head = data["you"]["head"]
        for pos_move in moves_ressult:
          temp={"x":(moves_ressult.get(pos_move)["x"]+head["x"]),"y":(moves_ressult.get(pos_move)["y"]+head["y"])}
          if temp["x"]>=max_x or temp["y"]>=max_y or temp["x"]<0 or temp["y"]<0:
            move_return.append(pos_move)
        return move_return
    
    #reutn move that could crash with an other head that would kill
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def clashWithHead(self,head):
        moves_ressult = {
          "up":{"x":0,"y":1},
         "down":{"x":0,"y":-1}, 
         "left":{"x":-1,"y":0}, 
         "right":{"x":1,"y":0}}
        move_return=[]
        data = cherrypy.request.json
        #head = data["you"]["head"]
        length = data["you"]["length"]
        snake_head=[]
        snake_prediction=[]
        for snake in data["board"]["snakes"]:
          if length <= snake["length"] and snake["head"] != head:
            snake_head.append(snake["head"])
        for snakehead in snake_head:
          for pos_move in moves_ressult:
            snake_prediction.append({"x":(moves_ressult.get(pos_move)["x"]+snakehead["x"]),"y":(moves_ressult.get(pos_move)["y"]+snakehead["y"])})
        for pos_move in moves_ressult:
          temp={"x":(moves_ressult.get(pos_move)["x"]+head["x"]),"y":(moves_ressult.get(pos_move)["y"]+head["y"])}
          if temp in snake_prediction:
            move_return.append(pos_move)
        #print(move_return)
        return move_return

    #return the move that would bring you closes to a food node
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def nearest_food(self, move, head, food):
        moves_ressult = {
          "up":{"x":0,"y":1},
         "down":{"x":0,"y":-1}, 
         "left":{"x":-1,"y":0}, 
         "right":{"x":1,"y":0}}
        move_return =[]
        snake_head=[]
        head_moves=[]
        data = cherrypy.request.json
        for s in data["board"]["snakes"]:
          if s["head"]!=head:
            snake_head.append(s["head"])
        
        if len(food) >0:
          food.sort(key=lambda x:abs(x["x"]-head["x"])+abs(x["y"]-head["y"]))
          nearestFood=food[0]
          #closest
          #print(nearestFood)
          for pos_move in move:
            tempDistance=abs(nearestFood["x"]-head["x"]-moves_ressult.get(pos_move)["x"])+abs(nearestFood["y"]-head["y"]-moves_ressult.get(pos_move)["y"])
            tempDistanceOpissite=abs(nearestFood["x"]-head["x"]+moves_ressult.get(pos_move)["x"])+abs(nearestFood["y"]-head["y"]+moves_ressult.get(pos_move)["y"])
            if tempDistanceOpissite>tempDistance:
              move_return.append(pos_move)
          
          if len(move_return)>0:
            #print(move_return)
            return move_return

          else:
            return move
        return move
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def kill(self, move, head, food):
        moves_ressult = {
          "up":{"x":0,"y":1},
         "down":{"x":0,"y":-1}, 
         "left":{"x":-1,"y":0}, 
         "right":{"x":1,"y":0}}
        move_return =[]
        
        if len(food) >0:
          food.sort(key=lambda x:abs(x["x"]-head["x"])+abs(x["y"]-head["y"]))
          nearestFood=food[0]
          #closest
          #print(nearestFood)
          for pos_move in move:
            tempDistance=abs(nearestFood["x"]-head["x"]-moves_ressult.get(pos_move)["x"])+abs(nearestFood["y"]-head["y"]-moves_ressult.get(pos_move)["y"])
            tempDistanceOpissite=abs(nearestFood["x"]-head["x"]+moves_ressult.get(pos_move)["x"])+abs(nearestFood["y"]-head["y"]+moves_ressult.get(pos_move)["y"])
            if tempDistanceOpissite>tempDistance:
              move_return.append(pos_move)
          
          if len(move_return)>0:
            #print(move_return)
            return move_return

          else:
            return move
        return move

if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)