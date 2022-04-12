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
from extractInfo import extractClock,extractEval,extractMetadata,extractPGN,extractText

## TODO add metadata to be included in the additional information
# metadata dictionary is created now, just need to use the information from it to draw to the base

parser = getParser()

def getListOfFEN(game):
    data = []
    board = game.board()
    for move in game.mainline_moves():
        data.append(str(board.fen()))
        board.push(move)
    return data

def generateFilename():
    return str(uuid.uuid4().hex)

def multiblock_text(img, text, font, text_color=(255,255,255), text_start_height=0, offset=(0,0), text_area=(None, None), align='left'):
    if(text_area==(None, None)):
        text_area = img.size
    draw = ImageDraw.Draw(img)
    offset_x, offset_y = offset
    image_width, _ = img.size
    y_text = text_start_height
    draw.multiline_text(((image_width/2)+offset_x, (y_text+offset_y)),
                        text=text, 
                        font=font,
                        align=align,
                        fill=text_color)

def draw_multiple_line_text(img, text, font, text_color=(255,255,255), text_start_height=0, offset=(0,0), text_area=(None, None), step=None):
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

def drawline(base, 
            shape,
            width=500, 
            height=500,
            ):
    img = ImageDraw.Draw(base)  
    img.line(shape, fill ="red", width = 10)
    return base

def createEval(width=500, 
               height=500, 
               color=(0,0,0), 
               fontsize=16,
               eval=0,
               font=(ImageFont.truetype("arial.ttf", 16)),
               padding=10,):
    pixels = ((width/2) + (eval*10),0)
    shape = [pixels, (width/2,0)]

    # create a base layer
    base = Image.new(mode="RGBA", size=(width,height), color=(0,0,0))
    # calculate the text wrap size
    text_width_max = base.size[0]/fontsize
    
    base_ = drawline(base, shape)
    e = str(eval)
    multiblock_text(img=base, 
                            text=e,
                            font=font, 
                            text_start_height=padding, 
                            offset=(0,0), 
                            text_area=(text_width_max,0),
                            )
    return base_

def createClk(width=500, 
              height=500, 
               color=(0,0,0), 
               fontsize=16,
               clk="NA",
               font=(ImageFont.truetype("arial.ttf", 16)),
               padding=10,):

    # create a base layer
    base = Image.new(mode="RGBA", size=(width,height), color=(255,255,255))
    # calculate the text wrap size
    text_width_max = base.size[0]/fontsize
    
    multiblock_text(img=base, 
                            text=clk[0],
                            font=font, 
                            text_start_height=padding, 
                            offset=(150,0), 
                            text_area=(text_width_max,0),
                            text_color=(100,100,100)
                            )
    multiblock_text(img=base, 
                            text=clk[1],
                            font=font, 
                            text_start_height=padding, 
                            offset=(-150,0), 
                            text_area=(text_width_max,0),
                            text_color=(0,0,0)
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
    text += "White: "+meta['white']+" ("+meta['whiteelo']+")"+"["+meta['whiteratingdiff']+"]\n"
    text += "Black: "+meta['black']+" ("+meta['blackelo']+")"+"["+meta['blackratingdiff']+"]\n"

    multiblock_text(img=base, 
                            text=text,
                            font=font, 
                            text_start_height=padding, 
                            offset=(10,0), 
                            text_area=(text_width_max,0),
                            )
    return base
    
def FEN_to_GIF(fen, 
               evals=[],
               clks=[],
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
    isWhite = True
    white_clock, black_clock = clks[0], clks[1]
    sequence = []
    step = 0
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
        board_img = Image.open(BytesIO(svg2png(chess.svg.board(board,size=boardsize,coordinates=coordinates))))
        new_base = base.copy()
        e = evals.pop(0)
        eval_img = createEval(eval=e,
                              color=base_color,
                              fontsize=fontsize,
                              font=font,
                              padding=padding,
                              width=boardsize,
                              height=(int)(boardsize/2))

        if isWhite:
            white_clock = clks.pop(0)
        else:
            black_clock = clks.pop(0)
        isWhite = not isWhite
        
        clk_img = createClk(clk=(white_clock, black_clock),
                             color=base_color,
                             fontsize=fontsize,
                             font=font,
                             padding=padding,
                             width=boardsize,
                             height=(int)(boardsize))

        new_base.paste(meta, (0,(int)(boardsize/2)))
        new_base.paste(clk_img, ((int)(boardsize),((int)(boardsize/100)*85)))
        new_base.paste(eval_img, ((int)(boardsize),((int)(boardsize/100)*90)))
        new_base.paste(board_img, (0,0))

        
        # add this frame to the gif sequence
        sequence.append(new_base)
    return sequence

#  pgn from commandline argument
args = parser.parse_args()
text = extractText(args)
metadata_text, meta_dictionary = extractMetadata(text)
pgn_string = extractPGN(text)
game = chess.pgn.read_game(io.StringIO(pgn_string))
FEN = getListOfFEN(game)
PGN = pgn_string

EVALS = extractEval(PGN)
CLKS = extractClock(PGN)

sequence = FEN_to_GIF(fen=FEN, 
                      pgn=PGN, 
                      metadata=meta_dictionary,
                      evals=EVALS,
                      clks=CLKS)
sys.stdout.write("\r\n")
sys.stdout.flush()
outputSequence(sequence, args)