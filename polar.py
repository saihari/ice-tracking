# !/usr/local/bin/python3
#
# Authors: Sai Hari

from PIL import Image
from numpy import *
from scipy.ndimage import filters
from scipy.stats import norm
import sys
import imageio
from utils import *

# calculate "Edge strength map" of an image                                                                                                                                      
def edge_strength(input_image):
    grayscale = array(input_image.convert('L'))
    filtered_y = zeros(grayscale.shape)
    filters.sobel(grayscale,0,filtered_y)
    return sqrt(filtered_y**2)

# draw a "line" on an image (actually just plot the given y-coordinates
#  for each x-coordinate)
# - image is the image to draw on
# - y_coordinates is a list, containing the y-coordinates and length equal to the x dimension size
#   of the image
# - color is a (red, green, blue) color triple (e.g. (255, 0, 0) would be pure red
# - thickness is thickness of line in pixels
def draw_boundary(image, y_coordinates, color, thickness):
    for (x, y) in enumerate(y_coordinates):
        for t in range( int(max(y-int(thickness/2), 0)), int(min(y+int(thickness/2), image.size[1]-1 )) ):
            image.putpixel((x, t), color)
    return image

def draw_asterisk(image, pt, color, thickness):
    for (x, y) in [ (pt[0]+dx, pt[1]+dy) for dx in range(-3, 4) for dy in range(-2, 3) if dx == 0 or dy == 0 or abs(dx) == abs(dy) ]:
        if 0 <= x < image.size[0] and 0 <= y < image.size[1]:
            image.putpixel((x, y), color)
    return image


# Save an image that superimposes three lines (simple, hmm, feedback) in three different colors 
# (yellow, blue, red) to the filename
def write_output_image(filename, image, simple, hmm, feedback, feedback_pt):
    new_image = draw_boundary(image, simple, (255, 255, 0), 2)
    new_image = draw_boundary(new_image, hmm, (0, 0, 255), 2)
    new_image = draw_boundary(new_image, feedback, (255, 0, 0), 2)
    new_image = draw_asterisk(new_image, feedback_pt, (255, 0, 0), 2)
    imageio.imwrite(filename, new_image)

def calc_prob_dist(x, mean = 0, sd = 1):
    return norm.pdf(x,mean,sd)

def calc_emission_prob(edge_strength):
    #Implementation taken from https://stackoverflow.com/questions/43644320/how-to-make-numpy-array-column-sum-up-to-1
    return edge_strength / edge_strength.sum(axis=0)

def simple(edge_strength):
    # This Task Does not contain Transition probabilities and only contains emission probabilities. 
    # For air-ice given a column the maximum probability that a pixel denotes the boundary is  the pixel with the maximum normalized edge strength.

    edge_strength_normalised = edge_strength / (amax(edge_strength))
    air_ice = edge_strength_normalised.argmax(axis=0)
    

    ice_rock = []
    for col in range(edge_strength_normalised.shape[1]):
        ice_rock.append(argmax(edge_strength_normalised[air_ice[col]+10:,col]) + air_ice[col]+10)


    return air_ice,ice_rock

def p_transition(distribution,s_prev,s):
    diff = s - s_prev
    size_factor = int(len(distribution)/2)
    
    if  (diff + size_factor < len(distribution)) and (diff + size_factor >= 0):
        return distribution[s - s_prev + 2] 
    else:
        return 0

# main program
if __name__ == "__main__":

    if len(sys.argv) != 6:
        raise Exception("Program needs 5 parameters: input_file airice_row_coord airice_col_coord icerock_row_coord icerock_col_coord")

    input_filename = sys.argv[1]
    gt_airice = [ int(i) for i in sys.argv[2:4] ]
    gt_icerock = [ int(i) for i in sys.argv[4:6] ]

    # load in image 
    input_image = Image.open(input_filename).convert('RGB')
    image_array = array(input_image.convert('L'))

    # compute edge strength mask -- in case it's helpful. Feel free to use this.
    edge_strength = edge_strength(input_image)
    imageio.imwrite('edges.png', uint8(255 * edge_strength / (amax(edge_strength))))

    airice_simple, icerock_simple =  simple(edge_strength)
    airice_hmm = initiateViterbi(edge_strength, "air_ice", None, None)
    icerock_hmm = initiateViterbi(edge_strength, "ice_rock", airice_hmm, None)
    airice_feedback = initiateViterbi(edge_strength, "air_ice", None, gt_airice)
    icerock_feedback = initiateViterbi(edge_strength, "ice_rock", airice_feedback, gt_icerock)
    
    # Now write out the results as images and a text file
    write_output_image("air_ice_output.png", input_image.copy(), airice_simple, airice_hmm, airice_feedback, gt_airice)
    write_output_image("ice_rock_output.png", input_image.copy(), icerock_simple, icerock_hmm, icerock_feedback, gt_icerock)
    with open("layers_output.txt", "w") as fp:
        for i in (airice_simple, airice_hmm, airice_feedback, icerock_simple, icerock_hmm, icerock_feedback):
            fp.write(str(i) + "\n")
