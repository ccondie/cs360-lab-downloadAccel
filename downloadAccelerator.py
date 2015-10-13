#!/usr/bin/env python
import requests
from requests import Request

"""Shared Objects"""
class Shared:
	def __init__(self):
		self.chunkSem = threading.Semaphore()
		self.dictSem = threading.Semaphore()
		self.chunk = 0
		self.totalChunk = 0
		self.chunksRemain = true

	def getChunk(self):
		self.chunkSem.acquire()
		rt = self.chunk
		#may not be valid syntax
		self.chunk++
		self.chunkSem.release()
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
		while(self.shared.chunksRemain)
			self.myChunk = self.shared.getChunk()
			


"""Primary Function"""
class Main(object):
	def __init__(self):
		print "*** initializing Main ***"
		

	def run(self):
		print "*** Running Main Function ***"

		head = requests.head("http://cs360.byu.edu/fall-2015/")
		print "Status Code: " + str(head.status_code)
		print "Encoding: " + str(head.encoding) + '\n'
		print "Header Content"
		print head.headers
		print '\n'

		print "Range 0-100: "
		header = {'Range':'bytes=0-100', 'Accept-Encoding':'identity'}
		url = "http://cs360.byu.edu/fall-2015/"
		chunk = requests.get(url, headers=header)
		print chunk.text
		

		
		print '\n' + "Range 101-200: "
		header = {'Range':'bytes=101-200', 'Accept-Encoding':'identity'}
		url = "http://cs360.byu.edu/fall-2015/"
		chunk = requests.get(url, headers=header)
		print chunk.text
		

		

#Check the URL to verify that a 200 response was acquired

#Capture the size of the body of the page

#Calculate the number of chunks of a specified size that will need to be applied

#Create the specifed number of threads and start them


m = Main()
m.run()