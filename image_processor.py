from PIL import Image
import numpy as np
import sys


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

	print("The original image width is %i pixels." %im.size[0])
	print("The original image height is %i pixels." %im.size[1])
	print("The image mode is %s." %im.mode)

	# remove transparency for simplicity
	if im.mode == "RGBA":
		trans_image_array = np.array(im.getdata(), np.uint8).reshape(im.size[1], im.size[0], 4)
		trans_image_array = trans_image_array[:,:,:3]
	elif im.mode == "RGB":
		trans_image_array = np.array(im.getdata(), np.uint8).reshape(im.size[1], im.size[0], 3)
	else:
		print("%s is not a supported mode." %im.mode)
		sys.exit()

	image_array = transpose_xy(trans_image_array)
	im.close

	return image_array


# make a png image from numpy array
def create_image_from_array(image_array, filename):

	im = Image.fromarray(transpose_xy(image_array), "RGB")

	print("The final image width is %i pixels." %im.size[0])
	print("The final image height is %i pixels." %im.size[1])

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


# reduce number of pixels by 4X
def compress_image(image_array):

	print("Compressing image...")

	og_width = image_array.shape[0]
	og_height = image_array.shape[1]
	new_image_array = np.zeros( (int(og_width/2), int(og_height/2), 3) , np.uint8)

	for j in range(new_image_array.shape[1]):
		for i in range(new_image_array.shape[0]):
			new_image_array[i,j] = average_of([image_array[2*i,2*j], image_array[2*i+1,2*j], image_array[2*i,2*j+1], image_array[2*i+1,2*j+1]])

	return new_image_array


# gain resolution by averaging neighboring pixels
def enlarge_image(image_array):

	print("Enlarging image...")

	og_width = image_array.shape[0]
	og_height = image_array.shape[1]
	new_image_array = np.zeros( (og_width*2, og_height*2, 3) , np.uint8)

	# first loop spreads original pixels into 4 times the area
	for j in range(new_image_array.shape[1]):
		for i in range(new_image_array.shape[0]):
			if i%2 == 1 and j%2 == 1:
				new_image_array[i,j] = image_array[int((i-1)/2),int((j-1)/2)]

	# second loop fills empty pixels in every other row with the average of their neighbors
	for j in range(new_image_array.shape[1]):
		for i in range(new_image_array.shape[0]):
			if i != 0 and i != new_image_array.shape[0]:
				if i%2 == 0 and j%2 == 1:
					new_image_array[i,j] = average_of([new_image_array[i-1,j], new_image_array[i+1,j]])

	# third loop fills the rest of the image with the average of their vertical neighbors
	for j in range(new_image_array.shape[1]):
		for i in range(new_image_array.shape[0]):
			if i != 0 and i != new_image_array.shape[0] and j != 0 and j != new_image_array.shape[1]:
				if j%2 == 0:
					new_image_array[i,j] = average_of([new_image_array[i,j+1], new_image_array[i,j-1]])

	return new_image_array


# return the average of a list of color tuples
def average_of(colors):

	red_sum = 0
	green_sum = 0
	blue_sum = 0

	for color in colors:
		red_sum += color[0]
		green_sum += color[1]
		blue_sum += color[2]

	red_avg = red_sum/len(colors)
	green_avg = green_sum/len(colors)
	blue_avg = blue_sum/len(colors)

	return ( red_avg, green_avg, blue_avg )


# main function
if __name__ == "__main__":

	if len(sys.argv) != 2:
		print("Usage: python3 image_processor.py <filename>")
		print("Exiting...")
		sys.exit()

	filename = sys.argv[1]

	image_array = get_image_array(filename)

	for i in range(50):
		image_array = compress_image(image_array)
		image_array = enlarge_image(image_array)

	create_image_from_array(image_array, filename)

	print("File saved as new_%s" %filename)
