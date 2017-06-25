from PIL import Image
import numpy as np


# transpose x and y coordinates
def transpose_xy(array):

	trans_array = np.zeros( (array.shape[1], array.shape[0], 3) , np.uint8)

	for j in range(array.shape[1]):
		for i in range(array.shape[0]):
			trans_array[j,i] = array[i,j]

	return trans_array

# returns the given image as a numpy array [x[], y[], color[R,G,B]]
def get_image_array(filepath):

	im = Image.open(filepath)

	print(im.mode)

	print(im.size[0])
	print(im.size[1])

	trans_image_array = np.array(im.getdata(), np.uint8).reshape(im.size[1], im.size[0], 3)
	image_array = transpose_xy(trans_image_array)
	im.close

	return image_array


# make a png image from numpy array
def create_image_from_array(image_array, filename):

	im = Image.fromarray(transpose_xy(image_array), "RGB")

	im.save("new_" + filename)


# R->G G->B B->R
def swap_colors(image_array):

	new_image_array = image_array.copy()

	for j in range(image_array.shape[1]):
		for i in range(image_array.shape[0]):
			new_image_array[i,j,1] = image_array[i,j,0]
			new_image_array[i,j,2] = image_array[i,j,1]
			new_image_array[i,j,0] = image_array[i,j,2]

	return new_image_array


# 
def compress_image(image_array):

	new_image_array = image_array.copy()

	for j in range(image_array.shape[1]):
		for i in range(image_array.shape[0]):
			if i%2 == 0:
				new_image_array[i,j] = image_array[i,j]
			else:
				new_image_array[i,j] = image_array[i-1,j]

	return new_image_array


# gain resolution by averaging neighboring pixels
def enlarge_image(image_array):

	og_width = image_array.shape[0]
	og_height = image_array.shape[1]
	new_image_array = np.zeros( (og_width*2, og_height*2, 3) , np.uint8)

	for j in range(new_image_array.shape[1]):
		for i in range(new_image_array.shape[0]):
			if i%2 == 1 and j%2 == 1:
				new_image_array[i,j] = image_array[int((i-1)/2),int((j-1)/2)]

	for j in range(new_image_array.shape[1]):
		for i in range(new_image_array.shape[0]):
			if i != 0 and i != new_image_array.shape[0]:
				if i%2 == 0 and j%2 == 1:
					new_image_array[i,j] = average_of(new_image_array[i-1,j], new_image_array[i+1,j])

	for j in range(new_image_array.shape[1]):
		for i in range(new_image_array.shape[0]):
			if i != 0 and i != new_image_array.shape[0] and j != 0 and j != new_image_array.shape[1]:
				if j%2 == 0:
					new_image_array[i,j] = average_of(new_image_array[i,j+1], new_image_array[i,j-1])

	return new_image_array


# return the average of two color tuples
def average_of(color1, color2):

	new_color = ( int((int(color1[0])+int(color2[0]))/2), int((int(color1[1])+int(color2[1]))/2), int((int(color1[2])+int(color2[2]))/2) )
	#print(new_color)
	return new_color


# main function
if __name__ == "__main__":

	filename = "new_new_baboon.png"

	image_array = get_image_array(filename)

	#image_array = swap_colors(image_array)

	#image_array = compress_image(image_array)

	image_array = enlarge_image(image_array)

	#print(average_of( (255, 255, 1), (255, 255, 0) ))

	create_image_from_array(image_array, filename)

	print("Done!")
