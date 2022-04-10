import io
import re
import sys
import uuid
import chess
import argparse
import textwrap
import requests
import chess.pgn
import chess.svg
from io import BytesIO
from cairosvg import svg2png
from PIL import Image, ImageDraw, ImageFont

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
parser.add_argument('-i', 
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
                    default="false")
parser.add_argument('-o', 
                    '--output', 
                    dest='output',
                    help='Specify the output filename.',
                    default=None)

args = parser.parse_args()

def extractPGN(text):
    pgn = ''
    pgn_regex = r"(1\..*)$"
    for match in re.finditer(pgn_regex, text, re.MULTILINE):
        return match.group()
    return pgn

def getListOfFEN(game):
    data = []
    board = game.board()
    for move in game.mainline_moves():
        data.append(str(board.fen()))
        board.push(move)
    return data

def generateFilename():
    return str(uuid.uuid4().hex)

def draw_multiple_line_text(img, text, font, text_color=(255,255,255), text_start_height=0, offset=(0,0), text_area=(None, None), step=None):
    if(text_area==(None, None)):
        text_area = img.size
    text_area_width, _ = text_area
    draw = ImageDraw.Draw(img)
    offset_x, offset_y = offset
    image_width, _ = img.size
    y_text = text_start_height
    lines = textwrap.wrap(text, width=text_area_width)
    for line in lines:
        line_width, line_height = font.getsize(line)
        draw.text(((image_width - line_width)/2+offset_x, y_text+offset_y), 
                  line, font=font, fill=text_color)
        y_text += line_height

def outputSequence(sequence, args):
    if(args.output is None):
        filename = generateFilename()
    else:
        filename = re.sub(r"[^A-Za-z0-9._]+", "", args.output)
    filename += ".gif"
    sequence[0].save(filename,
        save_all = True, append_images = sequence[1:], 
        optimize = True, duration = 1000)

def createBackground(width=500, 
                     height=500, 
                     color=(0,0,0), 
                     fontsize=16,
                     pgn="sample_text",
                     font=(ImageFont.truetype("arial.ttf", 16)),
                     padding=10,
                     ):
    # create a base layer
    base = Image.new(mode="RGBA", size=(width*2,height), color=color)
    # calculate the text wrap size
    text_width_max = base.size[0]/fontsize
    draw_multiple_line_text(img=base, 
                                text=pgn,
                                font=font, 
                                text_start_height=padding, 
                                offset=(width/2,0), 
                                text_area=(text_width_max,0),
                            )
    return base

def FEN_to_GIF(fen, 
               pgn="sample_text", 
               metadata="",
               base_color=(0,0,0), 
               fontsize=16, 
               font=(ImageFont.truetype("arial.ttf", 16)), 
               padding=10, 
               boardsize=500,
               coordinates=True):

    base = createBackground(pgn=pgn, 
                            color=base_color, 
                            fontsize=fontsize,
                            font=font,
                            padding=padding,
                            width=boardsize,
                            height=boardsize)


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
        
        # create board from position
        board = chess.Board(position)
        # create image of the board
        board_img = Image.open(
            BytesIO(
                svg2png(
                    chess.svg.board(board,
                                    size=boardsize,
                                    coordinates=coordinates,
        ))))
        base.paste(board_img, (0,0))
        # add this frame to the gif sequence
        sequence.append(base)
    return sequence

def extractText(args):   
    if (args.filename is not None):
        pgn_file_location = args.filename
        f = open(pgn_file_location, "r")
        return f.read()
    elif (args.website is not None):
        response = requests.get(args.website)
        return response.text
    elif (args.id is not None):
        url = "https://lichess.org/game/export/"+args.id+"?"
        url += "&clocks="+args.clocks
        url += "&evals="+args.evals
        url += "&literate="+args.literate
        print(url)
        response = requests.get(url)
        if (response.status_code != 200):
            print("Unable to make request")
            print("Status Code: " + str(response.status_code))
            exit()
        return response.text
    else:
        print("Invalid input, use --help")
        exit()

def extractMetadata(text):
    metadata = ""
    metadata_regex = r"^\[.+"
    matches = re.finditer(metadata_regex, text, re.MULTILINE)
    for match in matches:
        metadata += match.group()+"\n"
    return metadata

# Take pgn from commandline argument
text = extractText(args)
#metadata_text = extractMetadata(text)
#print(metadata_text)
pgn_string = extractPGN(text)
pgn_ = io.StringIO(pgn_string)
game = chess.pgn.read_game(pgn_)
FEN = getListOfFEN(game)
PGN = pgn_string
#sequence = FEN_to_GIF(FEN, pgn=PGN, metadata=metadata_text)
sequence = FEN_to_GIF(FEN, pgn=PGN)
sys.stdout.write("\r\n")
sys.stdout.flush()
outputSequence(sequence, args)