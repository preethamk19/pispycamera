#!/usr/bin/python

# Copyright 2014 Clayton Lambert
# https://github.com/claytonn
# http://claytonn.com

# **Note: This per pixel method is really really inefficient. Seriously. 

import io
import time
import os
import picamera
import dropbox
from time import sleep
from PIL import Image
from random import randint
scan = True
images = []



color_offset = 25 # Adjusts for slight varitaions in color

while(scan):
	timestr = time.strftime("%Y%m%d-%H%M%S")
	mp4 = ".mp4"	
	product = timestr + mp4
	
	stream = io.BytesIO()
	with picamera.PiCamera() as camera:
		camera.resolution = (128,64) #Low Res For Faster Comparison
		camera.capture(stream, format='jpeg')
	stream.seek(0)	
	
	if(len(images)!=2):
		images.append(Image.open(stream))
	else:
		images[0] = Image.open(stream)

	x = 0
	y = 0
	diff = 0

	if len(images) != 1:
		#Start On X and Move Down Y 
		while(x < images[0].size[0]):
			while(y < images[0].size[1]):

				#Add Up All RGB Values For Current Pixel
				img1 = images[1].getpixel((x,y))
				val = img1[0] + img1[1] + img1[2]
				img2 = images[0].getpixel((x,y))
				val2 = img2[0] + img2[1] + img2[2]
				
				pd = abs(val2-val)
				
				if(pd > color_offset):
					diff += 1
				y += 1
				
			#Move Right 1 & Reset Y For Next Loop
			x+=1
			y=0
		
		changed  = (diff * 100) / (images[0].size[0] * images[0].size[1])

		
		cinder = '/test_dropbox/'
		endpoint= cinder+product		

			
		if changed >= 25:
			with picamera.PiCamera() as camera:
				camera.start_recording('video.h264')
				camera.start_preview()
				sleep(5)
				camera.stop_preview()
				camera.stop_recording()
				
				os.system("MP4Box -add video.h264 product.mp4")
				os.rename('product.mp4',product)				

				import dropbox

				class TransferData:
				    def __init__(self, access_token):
				        self.access_token = access_token
				
				    def upload_file(self, file_from, file_to):
				        """upload a file to Dropbox using API v2
				        """
				        dbx = dropbox.Dropbox(self.access_token)
				
				        with open(file_from, 'rb') as f:
				            dbx.files_upload(f, file_to)
				
				def main():
				    access_token = 'sG_pWholnQoAAAAAAAAApSuLSYTlBkNGyaM31dOBmOVCRiKEuil6dswgMDorawAU'
				    transferData = TransferData(access_token)
				
				    file_from = product
				    file_to = endpoint  # The full path to upload the file to, including the file name
				
				    # API v2
				    transferData.upload_file(file_from, file_to)
				sleep(5)				

				if __name__ == '__main__':
				    main()
				os.remove('video.h264')
				os.remove(product)				
			
		print str(changed) + "% changed."

                images[1] = images[0]
	

		
