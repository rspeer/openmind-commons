from django.shortcuts import render_to_response
from django.http import HttpResponse
from csc.concepttools.colors import *
from csc.nl import get_nl
from context import respond_with
import re
en_nl = get_nl('en')
import nltk.data
sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

def tokenize_by_sentences(x):
    return sent_tokenizer.tokenize(x,realign_boundaries=True)

def tokenize_by_lines(x):
    return x.split('\n')

def sentences_or_lines(x):
    sentences = tokenize_by_sentences(x)
    lines = tokenize_by_lines(x)
    if len(lines) >= 2*len(sentences):
        # this is probably line-based
        return lines
    else:
        return sentences

tokenizers = []
paragraphpattern = re.compile('''\s*\n(\s*\n)+''')
tokenizers.append(lambda x: paragraphpattern.split(x))
tokenizers.append(sentences_or_lines)
tokenizers.append(lambda x: x.split())
names = ['paragraphs','sentences','words','characters']
#tokenizers is an array of 2-tuples of the form ('name of tokens', tokenizer)
#output is a dictionary of form {'name of tokens':[tokens], 'color':color} and so is each token except for word.

def HTMLColor(rgb_tuple):
    return '#%02x%02x%02x' % rgb_tuple

#kind of arbitrary weightings, but make the range (0, 1)
def linearizeColorfulness(howcolorful):
    if howcolorful < 0:
        return 0
    if howcolorful > 1:
        return 1
    return howcolorful

def mergeColors(color1, color2, weight1):
    result = tuple(int(color1[i]*weight1 + color2[i]*(1-weight1)) for i in range(3))
    return result

def deepColorTokenize(text, maxdepth):
    return deepColorTokenizeHelper(text, tokenizers, names, maxdepth, (255,255,255))

def deepColorTokenizeHelper(text, tokenizers, names, maxdepth, bgcolor):
    color = text_color(text)
    try:
        howcolorful = linearizeColorfulness(how_colorful(text,thesvd))
    except KeyError:
        if (color == (128,128,128)):
            howcolorful = 0
        else:
            howcolorful = 0.5
    transcolor = mergeColors(color, bgcolor, howcolorful)
    if transcolor[0] + transcolor[1]*2 + transcolor[2] > 512:
        fontcolor = "#000000"
    else:
        fontcolor = "#ffffff"
    if maxdepth == 0:
        stopword = en_nl.is_stopword(text.strip("""''""().?!;: \t\n\r"""))
        return {'color':HTMLColor(transcolor), 'colored':(not stopword), 'bordercolor': HTMLColor(color), names[0]:[text], 'fontcolor':fontcolor}
    else:
        textcolor = {}
        textcolor['color'] = HTMLColor(transcolor)
        textcolor['fontcolor'] = fontcolor
        textcolor['bordercolor'] = HTMLColor(color)
        textcolor['colored'] = not en_nl.is_stopword(text.strip("""''""().?!;: \t\n\r"""))
        textcolor[names[0]] = [deepColorTokenizeHelper(token, tokenizers[1:], names[1:], maxdepth-1, transcolor) for token in tokenizers[0](text) if token.strip() != '']
        return textcolor

def splitparagraphs(text):
    return None

def startpage(request, lang='en'):
    if 'text' in request.POST and request.POST['text'].strip()!='':
        text = request.POST['text']
        colordepth = 3
        if request.POST['colordepth']:
            if request.POST['colordepth'] == 'wholetext':
                colordepth = 0
            elif request.POST['colordepth'] == 'paragraph':
                colordepth = 1
            elif request.POST['colordepth'] == 'sentence':
                colordepth = 2
        colorized = deepColorTokenize(text,colordepth)
        return respond_with('colorizer/index.html', request, {'coloredtext':colorized, 'originaltext':text, 'MEDIA_ROOT':'/site_media/static'})
    else:
        return respond_with('colorizer/index.html',request,{'MEDIA_ROOT':'/site_media/static'})

def display_meta(request):
    values = request.META.items()
    values.sort()
    html = []
    for k,v in values:
        html.append('<tr><td>%s</td><td>%s</td></tr>' % (k,v))
    return HttpResponse('<table>%s</table>' % '\n'.join(html))
