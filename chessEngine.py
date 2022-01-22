# This class will be responsible for storing current and previous states of a chess game. 
# It will also determine the validity of a move

class GameState:
    def __init__(self):  # constructor
        # Board is an 8x8 2d list
        # First value 'b' or 'w' represent colour
        # Second value is piece type
        # '--' represents an empty

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--", ],
            ["--", "--", "--", "--", "--", "--", "--", "--", ],
            ["--", "--", "--", "--", "--", "--", "--", "--", ],
            ["--", "--", "--", "--", "--", "--", "--", "--", ],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLoc = (7, 4)
        self.blackKingLoc = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enPassantPoss = () # coordinates of square where en passant is possible
        self.currentCastlingRights = CastleRights(True,True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    def makeMove(self, move):
        self.board[move.startRow][move.startColumn] = "--"  # replaces piece moved with empty space
        self.board[move.endRow][move.endColumn] = move.pieceMoved  # puts piece moved in new position on board
        self.moveLog.append(move)  # log the move
        self.whiteToMove = not self.whiteToMove  # oppositions go
        # if king moves, update location
        if move.pieceMoved == "wK":
            self.whiteKingLoc = (move.endRow, move.endColumn)
        elif move.pieceMoved == "bK":
            self.blackKingLoc = (move.endRow, move.endColumn)

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endColumn] = move.pieceMoved[0] + 'Q'

        # en passant
        if move.isEnPassantMove:
            self.board[move.startRow][move.endColumn] = "--" # captures pawn
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # if pawn advances two squares
            self.enPassantPoss = ((move.startRow + move.endRow) // 2, move.startColumn)
        else:
            self.enPassantPoss = ()

        # castle move
        if move.isCastleMove:
            if move.endColumn - move.startColumn == 2:  # kingside castle
                self.board[move.endRow][move.endColumn - 1] = self.board[move.endRow][move.endColumn + 1]  # moves rook
                self.board[move.endRow][move.endColumn + 1] = '--'  # erase old rook
            else:  # queenside castle
                self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 2]  # moves rook
                self.board[move.endRow][move.endColumn - 2] = '--'  # erase old rook

        # update castling rights, when a rook or king moves
        self.updateCastleRight(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))


    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()  # stores last move and removes it from moveLog
            self.board[move.startRow][move.startColumn] = move.pieceMoved  # moves piece back
            self.board[move.endRow][move.endColumn] = move.pieceCaptured  # puts captured piece back on board
            self.whiteToMove = not self.whiteToMove
            # if king moves, update location
            if move.pieceMoved == "wK":
                self.whiteKingLoc = (move.startRow, move.startColumn)
            elif move.pieceMoved == "bK":
                self.blackKingLoc = (move.startRow, move.startColumn)
            # undo en passant
            if move.isEnPassantMove:
                self.board[move.endRow][move.endColumn] = '--'
                self.board[move.startRow][move.endColumn] = move.pieceCaptured
                self.enPassantPoss = (move.endRow, move.endColumn)
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enPassantPoss = ()
            # undo castle rights
            self.castleRightsLog.pop() # remove latest castle rights
            newRights = self.castleRightsLog[-1] # set current rights to last rights
            self.currentCastlingRights = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            # undo castle move
            if move.isCastleMove:
                if move.endColumn - move.startColumn == 2: # kingside
                    self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 1]
                    self.board[move.endRow][move.endColumn - 1] = '--'
                else: # queenside
                    self.board[move.endRow][move.endColumn - 2] = self.board[move.endRow][move.endColumn +1]
                    self.board[move.endRow][move.endColumn + 1] = '--'
            self.checkMate = False
            self.staleMate = False


    def updateCastleRight(self,move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bk':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startColumn == 0: # left rook
                    self.currentCastlingRights.wqs = False
                elif move.startColumn == 7: # right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startColumn == 0: # left rook
                    self.currentCastlingRights.bqs = False
                elif move.startColumn == 7: # right rook
                    self.currentCastlingRights.bks = False

    # moves considering checks
    def getValidMoves(self):
        tempEnPassantPoss = self.enPassantPoss
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        # 1. generate all possible moves
        # 2. for each move, make the move
        # 3. generate all opponent's moves
        # 4. for each of opponent's move check if king is being attacked
        # 5. if they attack your king, not valid move
        moves = self.allPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLoc[0],self.whiteKingLoc[1], moves)
        else:
            self.getCastleMoves(self.blackKingLoc[0],self.blackKingLoc[1], moves)
        for i in range(len(moves) - 1, -1, -1):  # when removing from a list, iterate backwards
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: # either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        self.enPassantPoss = tempEnPassantPoss
        self.currentCastlingRights = tempCastleRights
        return moves

    # determine if current player is in check
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLoc[0], self.whiteKingLoc[1])
        else:
            return self.squareUnderAttack(self.blackKingLoc[0], self.blackKingLoc[1])

    # determine if enemy can attack the square r, c
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove # switch to opponent's turn
        oppMoves = self.allPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turn back
        for move in oppMoves:
            if move.endRow == r and move.endColumn == c: # square is under attack
                return True
        return False

    def allPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of columns in r
                colourOfPiece = self.board[r][c][0]  # 1st letter in appropriate square indicates colour of piece
                if (colourOfPiece == 'w' and self.whiteToMove) or (colourOfPiece == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]  # 2nd letter in piece name indicates type
                    self.moveFunctions[piece](r, c, moves)
        return moves

    # Gets all valid pawn moves for the pawn located at row, column and add to list of valid moves
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # white's move
            if self.board[r - 1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c >= 1:
                if self.board[r - 1][c - 1][0] == 'b':  # diagonal capture (left)
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r-1,c-1) == self.enPassantPoss:
                    moves.append(Move((r,c),(r-1,c-1),self.board, isEnPassantMove=True))
            if c <= 6:
                if self.board[r - 1][c + 1][0] == 'b':  # diagonal capture (right)
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r-1,c+1) == self.enPassantPoss:
                    moves.append(Move((r,c),(r-1,c+1),self.board, isEnPassantMove=True))

        else:  # black's move
                if self.board[r + 1][c] == "--":  # 1 square pawn advance
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn advance
                        moves.append(Move((r, c), (r + 2, c), self.board))
                if c >= 1:
                    if self.board[r + 1][c - 1][0] == 'w':  # diagonal capture (left)
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                    elif (r + 1, c - 1) == self.enPassantPoss:
                        moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnPassantMove=True))
                if c <= 6:
                    if self.board[r + 1][c + 1][0] == 'w':  # diagonal capture (right)
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                    elif (r + 1, c + 1) == self.enPassantPoss:
                        moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnPassantMove=True))

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # nested tuple of directions (up, left, down, right)
        enemyPiece = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i  # where d[i] is the row of ith direction tuple
                endColumn = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endColumn < 8:  # if on board
                    endPiece = self.board[endRow][endColumn]
                    if endPiece == "--":  # if end position is empty, valid move
                        moves.append(Move((r, c), (endRow, endColumn), self.board))
                    elif endPiece[0] == enemyPiece:  # if end position is enemy, valid move and break
                        moves.append(Move((r, c), (endRow, endColumn), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        directions = ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2))
        allyColour = 'w' if self.whiteToMove else 'b'
        for d in directions:
            endRow = r + d[0]
            endColumn = c + d[1]
            if 0 <= endRow < 8 and 0 <= endColumn < 8:
                if self.board[endRow][endColumn][0] != allyColour:
                    moves.append(Move((r, c), (endRow, endColumn), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))
        enemyPiece = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + i * d[0]
                endColumn = c + i * d[1]
                if 0 <= endRow < 8 and 0 <= endColumn < 8:
                    endPiece = self.board[endRow][endColumn]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endColumn), self.board))
                    elif endPiece[0] == enemyPiece:
                        moves.append(Move((r, c), (endRow, endColumn), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, 1), (1, -1))
        allyColour = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endColumn = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endColumn < 8:
                endPiece = self.board[endRow][endColumn]
                if endPiece[0] != allyColour:
                    moves.append(Move((r, c), (endRow, endColumn), self.board))

    def getCastleMoves(self, r, c, moves):
        # can't castle in check
        if self.squareUnderAttack(r,c):
            return
        # king side castling
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        # queen side castling
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(r, c, moves)


    def getKingsideCastleMoves(self, r, c, moves): # todo index error on self.board line
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board, isCastleMove = True))


    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board, isCastleMove = True))


class CastleRights():
    def __init__(self,wks,bks,wqs,bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

# this class converts from matrix to chess notation and back
class Move:
    # converts chess notation of ranks to rows
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    # flips ranksToRows dictionary
    rowToRanks = {v: k for k, v in ranksToRows.items()}
    # convert notation for columns
    filesToColumns = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    columnsToFiles = {v: k for k, v in filesToColumns.items()}

    def __init__(self, startSq, endSq, board, isEnPassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startColumn = startSq[1]
        self.endRow = endSq[0]
        self.endColumn = endSq[1]
        self.pieceMoved = board[self.startRow][self.startColumn]  # stores piece that was moved
        self.pieceCaptured = board[self.endRow][self.endColumn]  # stores piece that was captured
        # pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        # en passant
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        # castle move
        self.isCastleMove = isCastleMove
        # stores unique ID for each move (like a hash function)
        self.moveID = self.startRow * 1000 + self.startColumn * 100 + self.endRow * 10 + self.endColumn

    # since move objects are different, overriding the equals method checks if same move for different objects
    def __eq__(self, other):  # checks if object is equal to another object
        if isinstance(other, Move):  # checks if other object is an instance of the Move Class
            return self.moveID == other.moveID  # return true if moveID is equal to other moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startColumn) + self.getRankFile(self.endRow, self.endColumn)

    def getRankFile(self, r, c):
        return self.columnsToFiles[c] + self.rowToRanks[r]
