from csc.concepttools.colors import text_color, how_colorful, thesvd
import nltk.data
import sys

sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

#returns list of sentences, without stripping quotations or whitespace from the sentences
def str_sentences(str):
	return sent_tokenizer.tokenize(str.strip())

def file_sentences(filename):
	file = open(filename)
	totalfile = ""
	for line in file.readlines():
		totalfile += line
	sentences = str_sentences(totalfile)
	return sentences

def main():
	sentences = file_sentences(sys.argv[1])
	for sentence in sentences:
		sentence = sentence.strip(' "\'\n')
		if sentence:
			print sentence
			print '-'*2
			print text_color(sentence)
			print '-'*10
	
if __name__ == '__main__': main()
