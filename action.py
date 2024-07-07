class Action():
    def __init__(self, player = 0  , type = 0 , arr = []):
        self.type = type
        self.player = player
        self.arr = arr
    
    #action = {actionType : (0-8) 0-Nothing, 1-TSUMO, 2-RIICHI, 3-CLOSEDKAN, 4-CHAKAN, 4-RON, 5-PON, 6-KAN, 7-CHI
        #, arr : [], player : (0-3)}