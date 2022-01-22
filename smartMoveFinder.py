import random
import chessEngine

# gs = chessEngine.GameState()

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3.25, "N": 3, "p": 1}
checkMate = 1000
staleMate = 0
maxDepth = 2
# returns a random move
def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


# helper method to make first recursive call
def findBestMove(gs, validMoves):
    global nextMove
    nextMove = None
    # return greedyAlgorithm(gs, validMoves)
    # return minimaxNonRecursive(gs,validMoves)
    # return minimaxRecursive(gs, validMoves, maxDepth, gs.whiteToMove)
    # negaMax(gs, validMoves, maxDepth, 1 if gs.whiteToMove else -1)
    negaMaxAlphaBeta(gs, validMoves, maxDepth, -checkMate, checkMate, 1 if gs.whiteToMove else -1)
    return nextMove


def greedyAlgorithm(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    maxScore = -checkMate  # lowest theoretical score
    bestMove = None
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        if gs.checkMate:
            score = checkMate
        elif gs.staleMate:
            score = staleMate
        score = turnMultiplier * scoreMaterial(gs.board)
        if score > maxScore:
            maxScore = score
            bestMove = playerMove
        gs.undoMove()
    return bestMove


def minimaxNonRecursive(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = checkMate  # lowest theoretical score
    bestPlayerMove = None
    random.shuffle(validMoves)
    # finds best move by minimising the opponents maximum score
    for playerMove in validMoves:
        gs.makeMove(playerMove)  # get player moves
        opponentsMoves = gs.getValidMoves()  # get opponents move
        if gs.checkMate:
            opponentsMaxScore = -checkMate
        elif gs.staleMate:
            opponentsMaxScore = staleMate
        else:
            opponentsMaxScore = -checkMate  # set to low value
            # finds best move from opponent
            for opponentsMoves in opponentsMoves:
                gs.makeMove(opponentsMoves)
                gs.getValidMoves()  # required to check for checkmate
                if gs.checkMate:
                    score = checkMate
                elif gs.staleMate:
                    score = staleMate
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                if opponentsMaxScore < score:  # update best score
                    opponentsMaxScore = score
                gs.undoMove()
            if opponentsMaxScore < opponentMinMaxScore:  # if opponents max score is lower with this move, make that move
                opponentMinMaxScore = opponentsMaxScore
                bestPlayerMove = playerMove
            gs.undoMove()
    return bestPlayerMove


def minimaxRecursive(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:  # at terminal/leaf depth, no more children, go back up tree
        return scoreMaterial(gs.board)

    # alternates between white and black moves
    if whiteToMove:
        maxScore = - checkMate  # worst possible outcome
        for move in validMoves:
            gs.makeMove(move) # make the move
            nextMoves = gs.getValidMoves() # find next moves
            # moves up from terminal/leaf node with all possible moves by calling its own function recursively
            score = minimaxRecursive(gs, nextMoves, depth - 1, False)
            if score > maxScore:  # new best score
                maxScore = score
                if depth == maxDepth:  # if at surface level, no parents, move to other possible moves and go down
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = checkMate  # worst possible outcome
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = minimaxRecursive(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == maxDepth:
                    nextMove = move
            gs.undoMove()
        return minScore


def negaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -checkMate
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -negaMax(gs, nextMoves, (depth - 1), (-1 * turnMultiplier))
        if score > maxScore:
            maxScore = score
            if depth == maxDepth:
                nextMove = move
        gs.undoMove()
    return maxScore


def negaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    # todo ordering moves e.g. start with a check
    maxScore = -checkMate
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -negaMaxAlphaBeta(gs, nextMoves, (depth - 1), -beta, -alpha, (-1 * turnMultiplier))
        if score > maxScore:
            maxScore = score
            if depth == maxDepth:
                nextMove = move
        gs.undoMove()
        # pruning
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


# Score the board based on material
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score


# Positive score is good for white, negative for black
def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -checkMate  # black wins
        else:
            return checkMate  # white wins
    elif gs.staleMate:
        return staleMate
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score

