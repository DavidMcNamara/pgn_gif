import re
import requests

def extractPGN(text):
    pgn = ''
    pgn_regex = r"(1\..*)$"
    for match in re.finditer(pgn_regex, text, re.MULTILINE):
        return match.group()
    return pgn

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

def extractEval(text):
    evals = []
    eval_regex = r"\[%eval ((?:\\.|[^\]\\])*)]"
    matches = re.finditer(eval_regex, text, re.MULTILINE)
    for match in matches:
        try:
            evals.append(float(match.group(1)))
        except:
            evals.append(match.group(1))
    return evals

def extractClock(text):
    evals = []
    clock_regex = r"\[%clk ((?:\\.|[^\]\\])*)]"
    matches = re.finditer(clock_regex, text, re.MULTILINE)
    for match in matches:
        evals.append(str(match.group(1)))
    return evals