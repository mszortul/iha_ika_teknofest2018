from solve import *
from calib import *



# functions for finding the nearest corner of the maze


def conv_inv(img, th = 180):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inv = np.invert(gray)
    inv[inv<th] = 0
    return inv

def rotate_to(img, debug=False):
    inv = conv_inv(img)
    (h, w) = inv.shape
    my = int(h/2)
    mx = int(w/2)

    nons = np.transpose(np.nonzero(inv))
    if (len(nons)):
        rngs = []
        for px in nons:
            (y, x) = px
            rngs = math.sqrt((y-my)**2 + (x-mx)**2)
    else:
        return None
    max_ind = np.argmax(rngs)
    dot_coor = nons[max_ind]

    diff_y = dot_coor[0] - my
    diff_x = dot_coor[1] - mx
    rat = abs(diff_y / diff_x)
    deg = np.rad2deg(np.arctan(rat))

    if debug:
        plt.imshow(inv)
        plt.show()
        print('dot_coor:', dot_coor)
        print('diff_y:', diff_y)
        print('diff_x:', diff_x)
        print('rat:', rat)
        print('deg:', deg)

    if (diff_y < 0):
        if (diff_x >= 0):
            return deg
        else:
            return 180 - deg
    else:
        if (diff_x < 0):
            return 180 + deg
        else:
            return 360 - deg

def are_we_there_yet(img, debug=False):
    inv = conv_inv(img)
    (h, w) = inv.shape
    my = int(h/2)
    mx = int(w/2)
    if inv[my, mx]:
        return True
    else:
        return False


def make_parallel(img, debug=False):
    inv = conv_inv(img)
    correct = -99
    for angle in np.arange(0, 90, 1):
        rotated = imutils.rotate_bound(inv, angle)
        ysm, xsm = grid_pos(rotated)
        ypeaks, xpeaks = get_peaks(ysm, xsm)

        y_peak_vals = ysm[ypeaks]
        y_max_ind = np.argmax(y_peak_vals)
        if debug:
            print(ypeaks)
            print(y_peak_vals)
            print(y_max_ind)
            print(len(ypeaks))

        if ((y_max_ind == 0) or (y_max_ind == len(ypeaks)-1)):
            correct = angle
            break
    return correct
