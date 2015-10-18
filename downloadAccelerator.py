#!/usr/bin/env python
import requests
from requests import Request
import threading
import argparse
import time


"""Debug Class"""
class Debug:
	debugState = False
	printTol = 11

	@staticmethod
	def dprint(stringToPrint, tol):
		if((Debug.debugState == True) and (tol >= Debug.printTol)):
			print '\t' + str(stringToPrint)



"""Shared Objects"""
class Shared:
	def __init__(self):
		self.chunkSem = threading.Semaphore()
		self.dictSem = threading.Semaphore()
		self.stateSem = threading.Semaphore()
		self.urlSem = threading.Semaphore()
		self.compileSem = threading.Semaphore(0)

		self.totalByte = 0;
		self.fileName = ""
		self.chunk = 0
		self.chunkSize = 1000000
		self.totalChunk = 0
		self.chunksRemain = True
		self.url = ""
		self.fileDict = {}

	def getChunk(self):
		self.chunkSem.acquire()
		rt = self.chunk
		self.chunk = self.chunk + 1
		if(self.chunk >= self.totalChunk):
			Debug.dprint("NO CHUNKS REMAIN", 11)
			self.chunksRemain = False
		self.chunkSem.release()
		return rt

	def setState(self, newState):
		self.stateSem.acquire()
		Debug.dprint("*** SETTING chunksRemain STATE *** - " + str(newState), 3)
		self.chunksRemain = newState
		self.stateSem.release()

	def checkState(self):
		self.stateSem.acquire()
		Debug.dprint("*** CHECKING chunksRemain STATE *** - " + str(self.chunksRemain), 3)
		rt = self.chunksRemain
		self.stateSem.release()
		return rt

	def getURL(self):
		self.urlSem.acquire()
		rt = self.url
		self.urlSem.release()
		return rt

	def addChunk(self, chunk, chunkText):
		Debug.dprint(str(chunk) + " is waiting for the dictSem", 11)
		self.dictSem.acquire()

		self.fileDict[chunk] = chunkText

		Debug.dprint("Added " + str(chunk) + " to dictionary", 11)

		if(len(self.fileDict) >= self.totalChunk):
			Debug.dprint("COMPILE SEM RELEASED", 11)

			self.compileSem.release()
		self.dictSem.release()

	def compile(self):
		Debug.dprint("*** RUNNING compile ***", 5)
		rt = ""

		self.dictSem.acquire()

		keys = self.fileDict.keys()

		Debug.dprint("*** KEYES ***", 4)
		for i in keys:
			Debug.dprint(str(keys[i]), 4)

		for i in keys:
			Debug.dprint("i: " + str(i), 3)
			rt += self.fileDict[i]

		self.dictSem.release()

		return rt




"""Thread Function"""
#acuire the chunk_count from the shared variables
	#capture the current chunk_count to a thread variable
	#increment the shared chunk_count
#release the chunk_count

#URL for the download is non-changin so there is no need to lock it
#download the from [chunk_count * rangeSize] to [chunk_count * rangesize + rangeSize] into a string


#acquire the dictionary shared variable
	#store that string into a python dictionary at key:chunk_count
#release the dictionary shared variable
class Chunk(threading.Thread):
	def __init__(self,shared, myChunk):
		Debug.dprint("*** initializing Chunk ***", 5)
		threading.Thread.__init__(self)
		self.shared = shared
		self.data = ""
		self.myChunk = myChunk;

	def run(self):
		#self.myChunk = self.shared.getChunk()
		headerRange = "bytes=" + str((self.myChunk * self.shared.chunkSize)) + "-" + str((((self.myChunk + 1) * self.shared.chunkSize) - 1))

		Debug.dprint("Range " + headerRange, 3)

		header = {'Range': headerRange, 'Accept-Encoding':'identity'}
		url = self.shared.getURL()

		chunkTime = time.time();
		Debug.dprint("Grabbing chunk " + str(self.myChunk), 11)
		
		chunk = requests.get(url, headers=header)
		#print chunk.content[0:10]
		self.data = chunk.content

		chunkElapse = time.time() - chunkTime
		Debug.dprint("\t" + str(self.myChunk) + " - " + str(chunkElapse), 11)

		#self.shared.addChunk(self.myChunk, chunk.content)





"""Primary Function"""
class Main(object):
	def __init__(self):
		Debug.dprint("*** initializing Main ***", 5)
		
	def parse_options(self):
		Debug.dprint("*** RUNNING parse_options ***", 5)
		parser = argparse.ArgumentParser(prog='downloadAccelerator', description='A threaded http downloader', add_help=True)
		parser.add_argument('-n', '--number', type=int, action='store', help='number of threads to create', default=10)
		parser.add_argument('url', action='store', help='url of file to download')
		
		return parser.parse_args()

	def run(self):
		startTime = time.time()

		s = Shared()
		args = self.parse_options()

		Debug.dprint("*** results of command parse ***", 4)
		Debug.dprint(args.number, 3)
		Debug.dprint(args.url, 3)

		s.url = args.url
		#check if the url ends in an /
		if s.url[len(s.url) - 1] == '/':
			s.filename = "index.html"
		else:
			#if not, split and grab the last element as a filename
			urlSplit = s.url.split('/')
			s.filename = urlSplit[len(urlSplit) - 1]

		#print s.filename

		Debug.dprint("*** RUNNING Main.run ***", 5)

		headHeader = {'Accept-Encoding':'identity'}

		head = requests.head(args.url, headers=headHeader)
		Debug.dprint("Status Code: " + str(head.status_code), 11)
		Debug.dprint("Encoding: " + str(head.encoding), 11)
		Debug.dprint("Header Content:", 11)
		Debug.dprint(head.headers, 2)

		

		#!!!!!!! Potential breach of shared variables !!!!!!!!!!!

		print '\n'

		#if the headers have the proper responces, determine the number of needed chunks from content-length
		if head.status_code == 200:
			#then create n number of threads and run
			#print "--- Correct Status Code 200 ---"
			Debug.dprint('Content-Length: ' + str(head.headers['Content-Length']), 11)

			s.totalByte = head.headers['Content-Length']

			#this tells each thread to only grab one chunk
			s.chunkSize = (float(s.totalByte) / args.number) + 1


			s.totalChunk = float(head.headers['Content-Length']) / s.chunkSize
			Debug.dprint('Total Chunks Needed: ' + str(s.totalChunk),11)

			threads = {}

			for i in range(args.number):
				#create a new thread with the thread function
				threadChunk = Chunk(s, i)
				threads[i] = threadChunk
			
			for thread in threads.keys():
				threads[thread].start()

			for thread in threads.keys():
				threads[thread].join()


			outFile = open(s.filename, 'w')
			#join all the threads together
			for thread in threads.keys():
				outFile.write(threads[thread].data)
				
			outFile.close()


		else:
			#if the status code is wrong then we should break
			print "--- Something went wrong, Status Code != 200 ---"
		

		elapsedTime = time.time() - startTime

		print s.url + " " + str(args.number) + " " + str(s.totalByte) + " " + str(elapsedTime) + '\n'
		



m = Main()
m.run()