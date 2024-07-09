class Action():
    def __init__(self, player = 0  , type = 0 , arr = []):
        self.type = type
        self.player = player
        self.arr = arr
    
    #action = {actionType : (0-8) 0-Nothing, 1-TSUMO, 2-RIICHI, 3-CLOSEDKAN, 4-CHAKAN, 5-RON, 6-PON, 7-KAN, 8-CHI
        #, arr : [], player : (0-3)}


    def __str__(self) -> str:
        
        return f"Action:  Type: {str(self.type)} , Player: {str(self.player)} , Arr: {str(self.arr)} "