# This file contains a variety of image processing functions to be called
# by another file to run.

from PIL import Image
import numpy as np
import os, sys, argparse
import math
import matplotlib


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


# make a png image from numpy array and save to ./OutputImages
def create_image_from_array(image_array, filename):

	im = Image.fromarray(transpose_xy(image_array), "RGB")

	print("The final image width is %i pixels." %im.size[0])
	print("The final image height is %i pixels." %im.size[1])

	if not os.path.exists("./OutputImages"):
		os.makedirs("./OutputImages")

	im.save("./OutputImages/" + filename)
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
def tint_image(image_array, colors, percent):

	print("Tinting image...")

	# add black and white to color scheme
	colors.append((0,0,0))
	colors.append((255,255,255))

	for j in range(image_array.shape[1]):
		for i in range(image_array.shape[0]):	
			image_array[i,j] = tint_pixel(image_array[i,j], colors, percent)

		# some feedback on progress
		if (j+1)%100 == 0:
			print("Finished row %i" %(j+1))

	return image_array


# tints pixel towards the chosen colors
def tint_pixel(pixel, colors, percent):

	tint_scale = percent
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

		"Warriors": [(0,107,182),(255,225,76)],
		"Ducks": [(0,121,53),(254,225,35)],
		"49ers": [(175,30,44),(230,190,138)],
		"Kings": [(255,255,255),(178,183,187)],
		"Leafs": [(255,255,255),(1,62,127)],
		"Packers": [(23,94,34),(255,184,28)],
		"Vikings": [(84,41,109),(255,184,28)],
		"Giants": [(251,91,31),(255,253,208)],
		"RG": [(255,0,0),(0,255,0)],
		"GB": [(0,255,0),(0,0,255)],
		"BR": [(0,0,255),(255,0,0)],
		"RY": [(255,0,0),(255,255,0)]
	}

	return team_colors[team_name]


def check_orthogonal(team):

	colors = get_team_colors(team)
	vec_0 = np.array(colors[0])
	vec_1 = np.array(colors[1])

	dot_product = vec_0.dot(vec_1)
	print(str(dot_product) + "\n")


# tints picture towards the chosen colors with linear algebra
def hsv_tint_image(image_array, colors):

	print("Tinting image...")

	# add black and white to color scheme
	colors.append((0,0,0))
	colors.append((255,255,255))

	hsv_colors = []

	# change team colors from RGB to HSV
	for color in colors:
		rgb_color = np.array([color[0]/255, color[1]/255, color[2]/255])
		hsv_color = matplotlib.colors.rgb_to_hsv(rgb_color)
		hsv_colors.append(hsv_color)

	# applying transformation to each pixel in image
	for j in range(image_array.shape[1]):
		for i in range(image_array.shape[0]):	
			image_array[i,j] = hsv_tint_pixel(image_array[i,j], hsv_colors)

		# some feedback on progress
		if (j+1)%100 == 0:
			print("Finished row %i" %(j+1))

	return image_array


# tints pixel using scaling
def hsv_tint_pixel(pixel, hsv_colors):

	# turn tuple into np array (vector)
	rgb_pixel = np.array([pixel[0]/255, pixel[1]/255, pixel[2]/255])
	hsv_pixel = matplotlib.colors.rgb_to_hsv(rgb_pixel)

	# replace hue of pixel with closest team color
	closest_diff = 1
	closest_color = np.array([1,1,1])

	for hsv_color in hsv_colors:
		diff = abs(hsv_color[0] - hsv_pixel[0])
		if diff < closest_diff:
			closest_color = hsv_color
			closest_diff = diff

	hsv_pixel[0] = closest_color[0]
	rgb_pixel = matplotlib.colors.hsv_to_rgb(hsv_pixel)
	
	# round back artifacts from outside of RGB values (0, 255)
	for i in range(len(rgb_pixel)):
		if rgb_pixel[i] > 1:
			rgb_pixel[i] = 1
		if rgb_pixel[i] < 0:
			rgb_pixel[i] = 0

	# change back into a tuple
	final_pixel_vector = (int(255*rgb_pixel[0]), int(255*rgb_pixel[1]), int(255*rgb_pixel[2]))

	return final_pixel_vector


# tints picture towards the chosen colors with linear algebra
def vector_tint_image(image_array, colors, percent):

	print("Tinting image...")

	# creating 1st unit vector from colors[0]
	color_vector_0 = np.array([colors[0][0], colors[0][1], colors[0][2]])
	mag_color_vector_0 = np.sqrt(color_vector_0.dot(color_vector_0))
	unit_vector_0 = [component/mag_color_vector_0 for component in color_vector_0]

	# creating 2nd unit vector from colors[1]
	color_vector_1 = np.array([colors[1][0], colors[1][1], colors[1][2]])
	mag_color_vector_1 = np.sqrt(color_vector_1.dot(color_vector_1))
	unit_vector_1 = [component/mag_color_vector_1 for component in color_vector_1]

	# generating 3rd orthogonal unit vector with cross product
	unit_vector_2 = np.cross(unit_vector_0, unit_vector_1)

	# matrix that will transform the pixel into the team color vector space
	transformation_matrix = np.column_stack( (unit_vector_0, unit_vector_1, unit_vector_2) )
	inv_transformation_matrix = np.linalg.inv(transformation_matrix)

	# applying transformation to each pixel in image
	for j in range(image_array.shape[1]):
		for i in range(image_array.shape[0]):	
			image_array[i,j] = vector_tint_pixel(image_array[i,j], colors, transformation_matrix, inv_transformation_matrix, percent)

		# some feedback on progress
		if (j+1)%100 == 0:
			print("Finished row %i" %(j+1))

	return image_array


# tints pixel using linear algebra
def vector_tint_pixel(pixel, colors, transformation_matrix, inv_transformation_matrix, percent):

	# turn tuple into np array (vector)
	pixel_vector = np.array([pixel[0], pixel[1], pixel[2]])

	# transform the pixel into the team color vector space
	transformed_pixel_vector = inv_transformation_matrix.dot(pixel_vector)

	# transform pixel back into RGB space
	cut_pixel_vector = transformation_matrix.dot([transformed_pixel_vector[0], transformed_pixel_vector[1], 0])

	# round back artifacts from outside of RGB values (0, 255)
	for i in range(len(cut_pixel_vector)):
		if cut_pixel_vector[i] > 255:
			cut_pixel_vector[i] = 255
		if cut_pixel_vector[i] < 0:
			cut_pixel_vector[i] = 0

	# change back into a tuple
	final_pixel_vector = (int(cut_pixel_vector[0]), int(cut_pixel_vector[1]), int(cut_pixel_vector[2]))

	return final_pixel_vector


# main function for local testing (use process_image.py for argument parsing)
if __name__ == "__main__":

	teams = ["Warriors","Ducks","49ers","Kings","Leafs","Packers","Vikings","Giants","RG","GB","BR"]
	for team in teams:
		print(team)
		check_orthogonal(team)
