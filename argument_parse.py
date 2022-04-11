import argparse
def getParser():
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
    return parser