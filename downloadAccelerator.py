#!/usr/bin/env python
import requests
from requests import Request
import threading
import argparse

"""Shared Objects"""
class Shared:
	def __init__(self):
		self.chunkSem = threading.Semaphore()
		self.dictSem = threading.Semaphore()
		self.stateSem = threading.Semaphore()
		self.urlSem = threading.Semaphore()
		self.compileSem = threading.Semaphore(0)

		self.chunk = 0
		self.chunkSize = 1024
		self.totalChunk = 0
		self.chunksRemain = True
		self.url = ""
		self.fileDict = {}

	def getChunk(self):
		self.chunkSem.acquire()
		rt = self.chunk
		self.chunk = self.chunk + 1
		if(self.chunk > self.totalChunk):
			self.chunksRemain = False
		self.chunkSem.release()
		return rt

	def setState(self, newState):
		self.stateSem.acquire()
		print "*** SETTING chunksRemain STATE *** - " + str(newState)
		self.chunksRemain = newState
		self.stateSem.release()

	def checkState(self):
		self.stateSem.acquire()
		print "*** CHECKING chunksRemain STATE *** - " + str(self.chunksRemain)
		rt = self.chunksRemain
		self.stateSem.release()
		return rt

	def getURL(self):
		self.urlSem.acquire()
		rt = self.url
		self.urlSem.release()
		return rt

	def addChunk(self, chunk, chunkText):
		print "*** adding chunk *** chunk:" + str(chunk)
		self.dictSem.acquire()
		self.fileDict[chunk] = chunkText
		if(len(self.fileDict) > self.totalChunk):
			self.compileSem.release()
		self.dictSem.release()

	def compile(self):
		print "*** RUNNING compile ***"
		rt = ""

		self.dictSem.acquire()

		keys = self.fileDict.keys()

		print "*** KEYES ***", keys

		for i in keys:
			print "i: " + str(i)
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
	def __init__(self,shared):
		print "*** initializing Chunk ***"
		threading.Thread.__init__(self)
		self.shared = shared

	def run(self):
		print "*** running Chunk.run ***"
		while self.shared.checkState():
			print "currentState: " + str(self.shared.chunksRemain)
			self.myChunk = self.shared.getChunk()
			headerRange = str((self.myChunk * self.shared.chunkSize)) + "-" + str((((self.myChunk + 1) * self.shared.chunkSize) - 1))

			print "Range " + headerRange

			header = {'Range': headerRange, 'Accept-Encoding':'identity'}
			url = 'http://' + self.shared.getURL()
			chunk = requests.get(url, headers=header)
			#print chunk.text
			self.shared.addChunk(self.myChunk, chunk.text)
			
			#header = {'Range':'bytes=0-100', 'Accept-Encoding':'identity'}
			#url = "http://cs360.byu.edu/fall-2015/"
			#chunk = requests.get(url, headers=header)
			#print chunk.text
			


"""Primary Function"""
class Main(object):
	def __init__(self):
		print "*** initializing Main ***"
		
	def parse_options(self):
		print "*** RUNNING parse_options ***"
		parser = argparse.ArgumentParser(prog='downloadAccelerator', description='A threaded http downloader', add_help=True)
		parser.add_argument('-n', '--number', type=int, action='store', help='number of threads to create', default=10)
		parser.add_argument('url', action='store', help='url of file to download')
		


		return parser.parse_args()

	def run(self):
		s = Shared()
		args = self.parse_options()
		print "*** results of command parse ***"
		print args.number
		print args.url
		s.url = args.url

		print "*** Running Main Function ***"
		head = requests.head('http://' + args.url)
		print "Status Code: " + str(head.status_code)
		print "Encoding: " + str(head.encoding)
		print "Header Content:"
		print head.headers

		

		#!!!!!!! Potential breach of shared variables !!!!!!!!!!!

		print '\n'

		#if the headers have the proper responces, determine the number of needed chunks from content-length
		if head.status_code == 200:
			#then create n number of threads and run
			print "--- Correct Status Code 200 ---"
			print 'Content-Length: ' + str(head.headers['Content-Length'])

			s.totalChunk = float(head.headers['Content-Length']) / s.chunkSize
			print 'Total Chunks Needed: ' + str(s.totalChunk)

			for i in range(args.number):
				#create a new thread with the thread function
				thread = Chunk(s)
				thread.start()
			
			#print '\n' + "Range 101-200: "
			#header = {'Range':'bytes=101-200', 'Accept-Encoding':'identity'}
			#url = "http://cs360.byu.edu/fall-2015/"
			#chunk = requests.get(url, headers=header)
			#print chunk.text

		else:
			#if the status code is wrong then we should break
			print "--- Something went wrong, Status Code != 200 ---"

		s.compileSem.acquire()

		print "*** ABOUT to Compile ***"
		s.compile()
		

#Check the URL to verify that a 200 response was acquired

#Capture the size of the body of the page

#Calculate the number of chunks of a specified size that will need to be applied

#Create the specifed number of threads and start them



m = Main()
m.run()