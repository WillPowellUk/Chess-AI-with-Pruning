# This is the main file.
# It will handle user input and display the current GameState object

import pygame as p  # import pygame library
import chessEngine, smartMoveFinder  # import chessEngine.py

p.init()  # initialise pygame
width = height = 512  # pixels
dimension = 8  # dimension of a chess board
sqSize = height // dimension
maxFps = 15  # for animations
images = {}  # dictionary of images
sqSelected = ()  # keeps track of last click of user (row,column)


# initialise global directory of images only once
# loads and scales the images for all the pieces
# access image using images['wp'] etc.
def loadImages(folder="images"):
    pieces = ["wR", "wN", "wB", "wQ", "wK", "wB", "wp", "bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR", "bp"]
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load(folder + "/" + piece + ".png"), (sqSize, sqSize))


# main module for chess, handling user input and updating graphics
def main():
    global sqSelected, undoMove, flip
    undoMove = False

    screen = p.display.set_mode((width, height))  # sets dimensions of console/canvas
    p.display.set_caption('Chess Match')  # console title
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chessEngine.GameState()
    validMoves = gs.getValidMoves()  # gets valid moves from chessEngine
    moveMade = False  # flag for when valid move is made
    loadImages("images2")
    running = True
    playerClicks = []  # keep track of player clicks (two tuples [(x1,y1),(x2,y2)
    gameOver = False

    '''
    Settings
    '''
    playerOne = True # true when human playing white
    playerTwo = False # true when human playing black
    flip = False  # Flip Board
    animateMoves = True
    '''
    End of Settings
    '''

    while running:
        humanTurn = (gs.whiteToMove and playerOne ) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:  # if user closes console, stop playing
                running = False

            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:  # if mouse click
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # gets (x,y) coordinates of mouse
                    if not gs.whiteToMove and flip:
                        column = 7 - location[0] // sqSize  # finds square which mouse is selecting
                        row = 7 - location[1] // sqSize
                    else:
                        column = location[0] // sqSize  # finds square which mouse is selecting
                        row = location[1] // sqSize
                    if sqSelected == (row, column):  # if user clicks same square twice
                        sqSelected = ()  # deselects clicks
                        playerClicks = []  # clear player clicks
                    else:
                        sqSelected = (row, column)
                        playerClicks.append(sqSelected)  # append for both 1st and 2nd clicks
                    if len(playerClicks) == 2:  # after 2nd click
                        move = chessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                undoMove = False
                                sqSelected = ()  # reset user click
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            # keyboard handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:  # undo move when left arrow pressed
                    gs.undoMove()
                    undoMove = True
                    moveMade = True
                    animate = False
                    gameOver = False


        # AI move finder
        if not gameOver and not humanTurn:
            AIMove = smartMoveFinder.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = smartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True


        #  valid moves can be updated for next go
        if moveMade:
            if animate and animateMoves:
                animateMove(gs.moveLog[-1], screen, gs.board, clock, gs.whiteToMove)
            if gs.inCheck():
                colour = "White" if gs.whiteToMove else "Black"
                print(colour + " is in check")
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, validMoves, gs)
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'StaleMate')
        clock.tick(maxFps)
        p.display.flip()


# graphics module
def drawGameState(screen, validMoves, gs):
    drawBoard(screen)  # draw squares on board
    highlightSq(sqSelected, screen, gs)
    drawPieces(screen, gs.board, gs.whiteToMove)  # draw pieces ontop of squares
    highlightMoves(sqSelected, screen, validMoves, gs)  # draw moves ontop of pieces


def drawBoard(screen):
    global colours
    colours = [p.Color("white"), p.Color("light grey")]
    for row in range(dimension):
        for column in range(dimension):
            colour = colours[((row + column) % 2)]
            p.draw.rect(screen, colour, p.Rect(column * sqSize, row * sqSize, sqSize, sqSize))


def drawPieces(screen, board, whiteToMove):
    for r in range(dimension):
        for c in range(dimension):
            if not whiteToMove and flip:
                piece = board[7 - r][7 - c]  # piece is equal to a particular part in the 8x8 list in gameState
            else:
                piece = board[r][c]  # piece is equal to a particular part in the 8x8 list in gameState
            if piece != "--":  # not empty square
                screen.blit(images[piece],
                            p.Rect(c * sqSize, r * sqSize, sqSize, sqSize))  # overlays image over board


def animateMove(move, screen, board, clock, whiteToMove):
    global colours
    dR = move.endRow - move.startRow
    dC = move.endColumn - move.startColumn
    framesPerSquare = 10  # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        # increments r and c from start to end of animation
        r, c = (move.startRow + dR * frame / frameCount, move.startColumn + dC * frame / frameCount)
        drawBoard(screen)  # draws board and pieces normally
        drawPieces(screen, board, whiteToMove)
        # draws over end square whilst animation is occurring, otherwise piece already visible
        colour = colours[(move.endRow + move.endColumn) % 2]
        if not whiteToMove and flip:
            endSquare = p.Rect((7 - move.endColumn) * sqSize, (7 - move.endRow) * sqSize, sqSize, sqSize)
        else:
            endSquare = p.Rect(move.endColumn * sqSize, move.endRow * sqSize, sqSize, sqSize)
        p.draw.rect(screen, colour, endSquare)
        # if piece is captured, keep piece on board whilst doing the animation
        if move.pieceCaptured != '--':
            screen.blit(images[move.pieceCaptured], endSquare)
        if not whiteToMove and flip:
            screen.blit(images[move.pieceMoved], p.Rect((7 - c) * sqSize, (7 - r) * sqSize, sqSize, sqSize))
        else:
            screen.blit(images[move.pieceMoved], p.Rect(c * sqSize, r * sqSize, sqSize, sqSize))
        p.display.flip()  # update display
        clock.tick(120)  # limits time taken for each frame


def highlightSq(square, screen, gs):
    if square != ():  # if square selected
        r, c = square
        rUsr, cUsr = square
        if not gs.whiteToMove and flip:
            rUsr = 7 - r
            cUsr = 7 - c
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # nested if statement, if piece is own, highlight
            p.draw.rect(screen, "yellow", p.Rect(cUsr * sqSize, rUsr * sqSize, sqSize, sqSize))


def highlightMoves(square, screen, validMoves, gs):
    if square != ():  # if square selected
        r, c = square
        for move in validMoves:
            if move.startRow == r and move.startColumn == c:
                if move.pieceCaptured == '--':
                    if not gs.whiteToMove and flip:
                        p.draw.circle(screen, "red", (((7 * sqSize) - (move.endColumn * sqSize) + sqSize // 2),
                                                      ((7 * sqSize) - (move.endRow * sqSize) + sqSize // 2)),
                                      sqSize // 5)
                    else:
                        p.draw.circle(screen, "red", ((move.endColumn * sqSize) + sqSize // 2,
                                                      (move.endRow * sqSize) + sqSize // 2), sqSize // 5)

                else:
                    if not gs.whiteToMove and flip:
                        p.draw.circle(screen, "blue", (((7 * sqSize) - (move.endColumn * sqSize) + sqSize // 2),
                                                       ((7 * sqSize) - (move.endRow * sqSize) + sqSize // 2)),
                                      sqSize // 5)
                    else:
                        p.draw.circle(screen, "blue", ((move.endColumn * sqSize) + sqSize // 2,
                                                       (move.endRow * sqSize) + sqSize // 2), sqSize // 5)


def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 42, True, False)  # bold, 32 font
    textObject = font.render(text, False, p.Color('Gray'))
    textLocation = p.Rect(0, 0, width, height).move(width / 2 - textObject.get_width() / 2,
                                                    height / 2 - textObject.get_height() / 2)  # adds shadow
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":  # convention if chessMain is imported elsewhere
    main()
