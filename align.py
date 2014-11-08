import sys


# Get all alignments
def printGroups(line1, line2, result, outcomes):

	if len(line1) == len(line2) or len(line1) == 1:
		if len(line1) == 1:
			result.append(" ".join(line2))
		else:
			result = result + line2[::-1]
		outcomes.append(result[::-1])
		return

	for i in range(len(line2)-len(line1)+1,0,-1):
		newResult = list(result)
		newResult.append(" ".join(line2[len(line2)-i:len(line2)]))
		temp = printGroups(line1[0:len(line1)-1],line2[0:len(line2)-i], newResult, outcomes)


def initializeProb(lines, prob, count):

	for i in range(0,len(lines),3):
		word = lines[i].split()
		translation = lines[i+1].split()
		alignments = []

		# Computing all alignments
		printGroups(word, translation, [], alignments)

		# Initializing probability and count matrix
		for j in range(len(alignments)):
			for k in range(len(word)):
				if not prob.has_key(word[k]):
					prob[word[k]] = dict()
					count[word[k]] = dict()
				if not prob[word[k]].has_key(alignments[j][k]):
					prob[word[k]][alignments[j][k]] = 0.0
					count[word[k]][alignments[j][k]] = 0.0

# EM Inplementation
def em(corpus, iterations):

	fobject = open(corpus)
	lines = fobject.readlines()
	fobject.close()
	prob = dict()
	count = dict()

	#Initializing P(J|e)
	initializeProb(lines, prob, count)
	

	for iteration in range(iterations+1):
		

		for i in range(0,len(lines),3):
			word = lines[i].split()
			translation = lines[i+1].split()
			alignments = []
			# Computing all alignments
			printGroups(word, translation, [], alignments)
			aprob = [1.0] * len(alignments)
			# Computing alignment probabilities

			if iteration == 0:
				aprob = [1.0/len(alignments)] * len(alignments)
			else:
				for j in range(len(aprob)):
					aprob[j] = 1
					for k in range(len(word)):
						aprob[j] *= prob[word[k]][alignments[j][k]]
				
				total = 0

				for j in range(len(aprob)):
					total += aprob[j]

				for j in range(len(aprob)):
					aprob[j] /= total

			# Collect fractional counts
			for p in range(len(alignments)):
				for q in range(len(word)):
					count[word[q]][alignments[p][q]] += aprob[p]

		
		for key in count.keys():
			total = 0
			for subkey in count[key].keys():
				if count[key][subkey] > 0:
					total += count[key][subkey]
			for subkey in count[key].keys():
				if count[key][subkey] > 0:
					prob[key][subkey] = count[key][subkey]*1.0 / total


		for key in count.keys():
				for subkey in count[key].keys():
					count[key][subkey] = 0

	return prob

def generateAlignment(corpus, iterations, answers):

	correct = 0
	count = 0

	fobject = open(corpus)
	lines = fobject.readlines()
	fobject.close()
	if answers <> -1:
		fobject = open(answers)
		answers = fobject.readlines()
		fobject.close()

	oobject = open('epron-jpron.alignment','w')

	probMap = em(corpus,iterations)

	for i in range(0,len(lines),3):
		word = lines[i].split()
		jword = lines[i+1].split()
		
		jalign = []
		printGroups(word,jword,[],jalign)
		jprob = [1] * len(jalign)
		for j in range(len(jalign)):
			for k in range(len(word)):
				jprob[j] *=  probMap[word[k]][jalign[j][k]]

		maxalign = jprob.index(max(jprob))
		alignment = ''
		for p in range(len(jalign[maxalign])):
			for q in range(len(jalign[maxalign][p].split(' '))):
				alignment += str(p+1) + ' '

		oobject.write(' '.join(word)+'\n')
		oobject.write(' '.join(jalign[maxalign])+'\n')
		oobject.write(alignment+'\n')

		if answers <> -1:
			truealignment = answers[i+2].split()
			obtainedalignment = alignment.split()
			for al in range(len(obtainedalignment)):
				if obtainedalignment[al] == truealignment[al]:
					correct += 1
				count +=1

	if answers <> -1:
		print 'Accuracy: ', correct*1.0/count , ' ', correct, '/', count
	oobject.close()


	# Generate WFSA
	wobject = open('epron-jpron-unsupervised.wfst','w')
	startState = 0
	endState = 0
	stateCount = 1
	parentState = 0

	wobject.write(str(endState) + '\n')
	for keys in probMap.keys():
	
		wobject.write("(" + str(startState) + " (" + str(stateCount) + " " + keys + " *e* 1))\n")
		parentState = stateCount
		stateCount += 1

		for subkey in probMap[keys].keys():
			
			path = subkey.split()
			if probMap[keys][subkey] < 0.01:
				continue
			if len(path)>1:
				wobject.write("(" + str(parentState) + " (" + str(stateCount) + ' *e* ' + path[0] + ' ' + str(probMap[keys][subkey]) + '))\n')
			else:
				wobject.write("(" + str(parentState) + " (" + str(endState) + ' *e* ' + path[0] + ' ' + str(probMap[keys][subkey]) + '))\n')
				continue

			prevState = stateCount
			stateCount += 1

			for i in range(1,len(path)-1):
				
				wobject.write("(" + str(prevState) + " (" + str(stateCount) + ' *e* ' + path[i] + ' 1))\n')
				prevState = stateCount
				stateCount += 1			

			wobject.write("(" + str(prevState) + " (" + str(endState) + ' *e* ' + path[len(path)-1] + ' 1))\n')
	wobject.close()



def main():
	iterations = int(sys.argv[2])	
	datafile = sys.argv[4]
	if len(sys.argv) ==7:
		checkfile = sys.argv[6]
	else:
		checkfile = -1
	
	generateAlignment(datafile, iterations, checkfile)

main()