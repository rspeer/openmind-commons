from colors import how_colorful, thesvd
import os

def main():
	import sys
	try:
		dirname = os.path.abspath(sys.argv[1])
	except IndexError:
		raise ValueError('To run this as a script, please give name of a directory containing text files with comma separated "colorful words"')
	try:
		filelist = os.listdir(dirname)
	except OSError:
		raise ValueError("Directory not found")
	for file in filelist:
		color = file.split('.')[0]
		print(color + ":\n")
		fstream = open(os.path.join(dirname,file))
		lines = [x.strip('\n') for x in fstream.readlines()]
		for line in lines:
			for word in line.split(','):
				print("{0}: {1}".format(word, how_colorful(word.strip(),thesvd)))
			    


if __name__ == '__main__': main()
