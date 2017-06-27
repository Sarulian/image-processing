import argparse
import image_processor as im


# main function
if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Manipulate images.')
	parser.add_argument("file", help="the file to manipulate")
	parser.add_argument("action", help="compress, enlarge, or tint (requires -t and -p)")
	parser.add_argument("-t", "--team", help="the name of the team whose colors to use for tint",
						default="Warriors", type=str)
	parser.add_argument("-p", "--percent", help="how strong to tint (0-1)",
						default="1", type=float)

	args = parser.parse_args()
	filename = args.file
	image_array = im.get_image_array(filename)

	if args.action == "enlarge":

		image_array = im.enlarge_image(image_array)
		im.create_image_from_array(image_array, "large_" + filename)
		print("File saved as large_%s" %filename)

	elif args.action == "compress":

		image_array = im.compress_image(image_array)
		im.create_image_from_array(image_array, "small_" + filename)
		print("File saved as small_%s" %filename)

	elif args.action == "tint":

		image_array = im.tint_image(image_array, im.get_team_colors(args.team), args.percent)
		im.create_image_from_array(image_array, args.team + "_" + filename)
		print("File saved as %s" %(args.team + "_" + filename))
