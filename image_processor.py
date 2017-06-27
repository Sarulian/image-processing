from PIL import Image
import numpy as np
import sys, argparse


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
	im.close()

	return image_array


# make a png image from numpy array
def create_image_from_array(image_array, filename):

	im = Image.fromarray(transpose_xy(image_array), "RGB")

	print("The final image width is %i pixels." %im.size[0])
	print("The final image height is %i pixels." %im.size[1])

	im.save(filename)
	im.close()


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


# tints picture towards the chosen colors
def tint_image(image_array, colors):

	print("Tinting image...")

	for j in range(image_array.shape[1]):
		for i in range(image_array.shape[0]):	
			image_array[i,j] = tint_pixel(image_array[i,j], colors)

	return image_array

# tints pixel towards the chosen colors
def tint_pixel(pixel, colors):

	tint_scale = 0.8
	color = get_closest_color(pixel, colors)
	pixel_array = [pixel[0], pixel[1], pixel[2]]

	for i in range(len(pixel)):
		pixel_array[i] += int(tint_scale * (color[i] - pixel_array[i]))

	return (pixel_array[0], pixel_array[1], pixel_array[2])


# treat colors as vectors, return color closest to the pixel's color
def get_closest_color(pixel, colors):

	closest_index = 0
	closest_color = colors[0]
	closest_diff = pow(255,2)*3

	for color in colors:
		diff = 0
		for i in range(len(pixel)):
			diff += pow((pixel[i]-color[i]),2)
		if diff < closest_diff:
			closest_color = color
			closest_diff = diff

	return closest_color


def get_team_colors(team_name):

	team_colors = {

		"Warriors": [(0,0,0),(255,255,255),(0,107,182),(255,225,76)],
		"Ducks": [(0,0,0),(255,255,255),(0,121,53),(254,225,35)],
		"49ers": [(0,0,0),(255,255,255),(175,30,44),(230,190,138)],
		"Kings": [(0,0,0),(255,255,255),(178,183,187)],
		"Leafs": [(0,0,0),(255,255,255),(1,62,127)],
		"Packers": [(0,0,0),(255,255,255),(23,94,34),(255,184,28)],
		"Vikings": [(0,0,0),(255,255,255),(84,41,109),(255,184,28)]
	}

	return team_colors[team_name]


# main function
if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Manipulate images.')
	parser.add_argument("file", help="the file to manipulate")
	parser.add_argument("action", help="what to do with the file")
	parser.add_argument("-t", "--team", help="the name of the team whose colors to use for tint")

	args = parser.parse_args()
	filename = args.file
	image_array = get_image_array(filename)

	if args.action == "enlarge":

		image_array = enlarge_image(image_array)
		create_image_from_array(image_array, "large_" + filename)
		print("File saved as large_%s" %filename)

	elif args.action == "compress":

		image_array = compress_image(image_array)
		create_image_from_array(image_array, "small_" + filename)
		print("File saved as small_%s" %filename)

	elif args.action == "tint":

		image_array = tint_image(image_array, get_team_colors(args.team))
		create_image_from_array(image_array, args.team + "_" + filename)
		print("File saved as %s" %(args.team + "_" + filename))
