from importlib.metadata import metadata
import io
import re
import sys
import uuid
import chess
import textwrap
import requests
import chess.pgn
import chess.svg
from io import BytesIO
from cairosvg import svg2png
from PIL import Image, ImageDraw, ImageFont
from argument_parse import getParser

## TODO add metadata to be included in the additional information
# metadata dictionary is created now, just need to use the information from it to draw to the base

parser = getParser()

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

def drawer(font, img, texts):
    print(texts)
    lines = textwrap.wrap(texts, width=40)
    print(lines)
    draw = ImageDraw.Draw(img)
    y_text = 0
    for line in lines:
        width, height = font.getsize(line)
        draw.text((0, y_text), line, font=font)
        y_text += height
    return draw

def multiblock_text(img, text, font, text_color=(255,255,255), text_start_height=0, offset=(0,0), text_area=(None, None), step=None):
    if(text_area==(None, None)):
        text_area = img.size
    draw = ImageDraw.Draw(img)
    offset_x, offset_y = offset
    image_width, _ = img.size
    y_text = text_start_height
    draw.multiline_text(((image_width/2)+offset_x, (y_text+offset_y)),
                        text=text, 
                        font=font,
                        align='left',
                        fill=text_color  )

def draw_multiple_line_text(img, text, font, text_color=(255,255,255), text_start_height=0, offset=(0,0), text_area=(None, None), step=None):
    print(text)
    if(text_area==(None, None)):
        text_area = img.size
    text_area_width, _ = text_area
    draw = ImageDraw.Draw(img)
    offset_x, offset_y = offset
    image_width, _ = img.size
    y_text = text_start_height
    lines = (textwrap.wrap(text, width=text_area_width))
    for line in lines:
        line_width, line_height = font.getsize(line)
        draw.text(((image_width - line_width)/2+offset_x, y_text+offset_y), 
                  line, font=font, fill=text_color, align='left')
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

def createStaticMetaInfo(width=500, 
                        height=500, 
                        color=(0,0,0), 
                        fontsize=16,
                        meta="sample_text",
                        font=(ImageFont.truetype("arial.ttf", 16)),
                        padding=10,
                        ):
    # create a base layer
    base = Image.new(mode="RGBA", size=(width*2,height), color=(0,0,0))
    # calculate the text wrap size
    text_width_max = base.size[0]/fontsize

    text = meta['event']+"\n("+meta['timecontrol']+")\n"+meta['opening']+"\n"
    text += meta['white']+" ("+meta['whiteelo']+")"+"["+meta['whiteratingdiff']+"]\n"
    text += meta['black']+" ("+meta['blackelo']+")"+"["+meta['blackratingdiff']+"]\n"

    multiblock_text(img=base, 
                            text=text,
                            font=font, 
                            text_start_height=padding, 
                            offset=(0,0), 
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

    meta = createStaticMetaInfo(meta=metadata,
                                color=base_color,
                                fontsize=fontsize,
                                font=font,
                                padding=padding,
                                width=boardsize,
                                height=(int)(boardsize/2)
                                )

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
        new_base = base.copy()
        new_base.paste(meta, (0,(int)(boardsize/2)))
        new_base.paste(board_img, (0,0))
        # add this frame to the gif sequence
        sequence.append(new_base)
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
    quote_regex = r"\"(.*)\""
    metadata_regex = r"^\[.+"
    Eventregex = r"\[Event.*"
    Siteregex = r"\[Site.*"
    Dateregex = r"\[Date.*"
    Whiteregex = r"\[White.*"
    Blackregex = r"\[Black.*"
    Resultregex = r"\[Result.*"
    WhiteEloregex = r"\[WhiteElo.*"
    BlackEloregex = r"\[BlackElo.*"
    WhiteRatingDiffregex = r"\[WhiteRatingDiff.*"
    BlackRatingDiffregex = r"\[BlackRatingDiff.*"
    Variantregex = r"\[Variant.*"
    TimeControlregex = r"\[TimeControl.*"
    ECOregex = r"\[ECO.*"
    Openingregex = r"\[Opening.*"
    Terminationregex = r"\[Termination.*"
    
    matches = re.finditer(metadata_regex, text, re.MULTILINE)
    for match in matches:
        metadata += match.group()+'\n'

    date =  re.search(quote_regex, (re.search(Dateregex, metadata, re.MULTILINE)).group(), re.MULTILINE).group(1)
    event = re.search(quote_regex, (re.search(Eventregex, metadata, re.MULTILINE)).group(), re.MULTILINE).group(1)
    site =  re.search(quote_regex, (re.search(Siteregex, metadata, re.MULTILINE)).group(), re.MULTILINE).group(1)
    result =re.search(quote_regex, (re.search(Resultregex, metadata, re.MULTILINE)).group(), re.MULTILINE).group(1)
    white = re.search(quote_regex, (re.search(Whiteregex, metadata, re.MULTILINE)).group(), re.MULTILINE).group(1)
    black = re.search(quote_regex, (re.search(Blackregex, metadata, re.MULTILINE)).group(), re.MULTILINE).group(1)
    whiteelo = re.search(quote_regex, (re.search(WhiteEloregex, metadata, re.MULTILINE)).group(), re.MULTILINE).group(1)
    blackelo = re.search(quote_regex, (re.search(BlackEloregex, metadata, re.MULTILINE)).group(), re.MULTILINE).group(1)
    whiteratingdiff =re.search(quote_regex, (re.search(WhiteRatingDiffregex, metadata, re.MULTILINE)).group(), re.MULTILINE).group(1)
    blackratingdiff = re.search(quote_regex, (re.search(BlackRatingDiffregex, metadata, re.MULTILINE)).group(), re.MULTILINE).group(1)
    variant = re.search(quote_regex, (re.search(Variantregex, metadata, re.MULTILINE)).group(), re.MULTILINE).group(1)
    timecontrol =re.search(quote_regex, (re.search(TimeControlregex, metadata, re.MULTILINE)).group(), re.MULTILINE).group(1)
    eco = re.search(quote_regex, (re.search(ECOregex, metadata, re.MULTILINE)).group(), re.MULTILINE).group(1)
    opening = re.search(quote_regex, (re.search(Openingregex, metadata, re.MULTILINE)).group(), re.MULTILINE).group(1)
    termination =   re.search(quote_regex, (re.search(Terminationregex, metadata, re.MULTILINE)).group(), re.MULTILINE).group(1)
    
    meta ={
        "date": date,
        "event": event,
        "site": site,
        "result": result,
        "white": white,
        "black": black,
        "whiteelo": whiteelo,
        "blackelo": blackelo,
        "whiteratingdiff": whiteratingdiff,
        "blackratingdiff": blackratingdiff,
        "variant": variant,
        "timecontrol": timecontrol,
        "eco": eco,
        "opening": opening,
        "termination": termination
    }
    return metadata, meta

#  pgn from commandline argument
args = parser.parse_args()
text = extractText(args)
metadata_text, meta_dictionary = extractMetadata(text)
pgn_string = extractPGN(text)
game = chess.pgn.read_game(io.StringIO(pgn_string))
FEN = getListOfFEN(game)
PGN = pgn_string
sequence = FEN_to_GIF(FEN, pgn=PGN, metadata=meta_dictionary)
sys.stdout.write("\r\n")
sys.stdout.flush()
outputSequence(sequence, args)