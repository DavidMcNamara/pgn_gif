import chess.svg
import uuid
import textwrap
import io
import chess
import chess.pgn
import chess.svg
import argparse
import re
import sys
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from cairosvg import svg2png

parser = argparse.ArgumentParser("PGN to GIF")
parser.add_argument('-f', 
                    '--file', 
                    dest='filename',
                    help='Add file path to a PGN file',
                    default=None)
parser.add_argument('-w', 
                    '--web', 
                    dest='website',
                    help='Add URL path to PGN',
                    default=None)
parser.add_argument('-id', 
                    '--id', 
                    dest='id',
                    help='Add Lichess Game ID',
                    default=None)
parser.add_argument('-c', 
                    '--clocks', 
                    dest='clocks',
                    help='Include clock comments in the PGN moves, when available',
                    default="false")
parser.add_argument('-e', 
                    '--evals', 
                    dest='evals',
                    help='Include analysis evaluation comments in the PGN, when available',
                    default="false")
parser.add_argument('-l', 
                    '--literate', 
                    dest='literate',
                    help='Insert textual annotations in the PGN about the opening, analysis variations, mistakes, and game termination',
                    default="true")

args = parser.parse_args()

def extractPGN(text):
    pgn = ''
    pgn_regex = r"(1\..*)$"
    for match in re.finditer(pgn_regex, text, re.MULTILINE):
        return match.group()
    return pgn

def getListOfFEN(game):
    data = []
    # iterate over the mainline pgn
    board = game.board()
    for move in game.mainline_moves():
        data.append(str(board.fen()))
        board.push(move)
    return data

def generateFilename():
    unique_filename = str(uuid.uuid4().hex)
    return unique_filename

def draw_multiple_line_text(img, text, font, text_color=(255,255,255), text_start_height=0, offset=(0,0), text_area=(None, None), step=None):
    if(text_area==(None, None)):
        text_area = img.size
    text_area_width, text_area_height = text_area
    draw = ImageDraw.Draw(img)
    offset_x, offset_y = offset
    image_width, image_height = img.size
    y_text = text_start_height
    lines = textwrap.wrap(text, width=text_area_width)
    for line in lines:
        line_width, line_height = font.getsize(line)
        draw.text(((image_width - line_width)/2+offset_x, y_text+offset_y), 
                  line, font=font, fill=text_color)
        y_text += line_height

def outputSequence(sequence):
    #filename = generateFilename()+".gif"
    filename = "test.gif"
    print(filename)
    sequence[0].save(filename,
        save_all = True, append_images = sequence[1:], 
        optimize = True, duration = 1000)

def FEN_to_GIF(fen, 
               pgn="sample_text", 
               base_color=(0,0,0), 
               fontsize=16, 
               font=(ImageFont.truetype("arial.ttf", 16)), 
               padding=10, 
               boardsize=500,
               coordinates=True):
    sys.stdout.flush()
    step = 0
    sequence = []
    for position in fen:
        step+=1
        sys.stdout.write("\r")
        sys.stdout.flush()
        percent = (int)((step/len(fen))*100)
        sys.stdout.write("Converting to GIF: %s" %(str(percent)+"%")) 
        sys.stdout.flush()
        # board information
        board = chess.Board(position)
        #  first image
        source_img = Image.open(
            BytesIO(
                svg2png(
                    chess.svg.board(board,
                                    size=boardsize,
                                    coordinates=coordinates,
                    #arrows=[chess.svg.Arrow(chess.E4, chess.F6, color="#0000cccc")],
                    #squares=chess.SquareSet(chess.BB_DARK_SQUARES & chess.BB_FILE_B),
        ))))
        # information about the first image
        width, height = source_img.size
        # create a base layer
        base = Image.new(mode="RGBA", size=(width*2,height), color=base_color)
        base.paste(source_img, (0,0))

        # calculate the text wrap size
        text_width_max = base.size[0]/fontsize
        draw_multiple_line_text(img=base, 
                                text=pgn, 
                                font=font, 
                                text_start_height=padding, 
                                offset=(width/2,0), 
                                text_area=(text_width_max,0),
                                step=(step-1)
                            )
        # add this frame to the gif sequence
        sequence.append(base)
    return sequence
#######

if (args.filename is not None):
    pgn_file_location = args.filename
    print("Loading file : ", pgn_file_location)
    print("Opening file")
    f = open(pgn_file_location, "r")
    text = f.read()
elif (args.website is not None):
    print("web")
    response = requests.get(args.website)
    print((response.text))
    print(response.headers)
    text = response.text
elif (args.id is not None):
    print("ID")
    url = "https://lichess.org/game/export/"+args.id+"?"
    url += "&clocks="+args.clocks
    url += "&evals="+args.evals
    url += "&literate="+args.literate
    print(url)
    response = requests.get(url)
    text = response.text
    print(text)
else:
    print("Invalid input")
    print("--help")
    exit()



# Take pgn from commandline argument
print("Extracting information")
pgn_string = extractPGN(text)
pgn_ = io.StringIO(pgn_string)
# create a game object
print("Creating game")
game = chess.pgn.read_game(pgn_)
FEN = getListOfFEN(game)
PGN = pgn_string
sequence = FEN_to_GIF(FEN, pgn=PGN)
sys.stdout.write("\r\n")
sys.stdout.flush()
print("Saving GIF")
outputSequence(sequence)