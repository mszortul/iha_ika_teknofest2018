import math
import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d # version 1.1.0
from scipy.signal import argrelextrema, find_peaks
import glob
import copy

def view():
    print('get_inv()')
    print('grid_pos()')
    print('get_peaks()')
    print('get_cell_w()')


class Cell:
    
    def __init__(self, t, b, l, r, c):
        self.top = t
        self.bot = b
        self.left = l
        self.right = r
        self.coors = c
        self.visited = False
        self.visited_id = -1
    
    def show_info(self):
        ways = []
        if not self.top:
            ways.append('Top')
        if not self.bot:
            ways.append('Bot')
        if not self.left:
            ways.append('Left')
        if not self.right:
            ways.append('Right')
        
        print('Coors:', self.coors)
        print(ways)

        
    def visited_by(self, ghost_id):
        self.visited = True
        self.visited_id = ghost_id
        
def get_inv(fname):
    '''
    get_inv()
    
    Görüntüdeki siyah ve beyaz pikselleri tersine çevirir.
    
    Input:
        fname --> Dosya yolu (string)
        
    Output:
        inv --> Dönüştürülmüş görüntü (np.array - 2d)
        
    '''
    
    im =cv2.imread(fname)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    inv = np.invert(gray)
    return inv


def grid_pos(im, sigma=3):
    '''
    grid_pos()
    
    Görüntüdeki pikselleri kullanarak yatay ve dikey düzlemlerde yoğunluk oylaması yapar ve gauss filtresinden geçirerek yumuşatır.
    
    Input:
        im --> get_inv() ile dönüştürülmüş görüntü (np.array - 2d)
        sigma --> Gauss filtresi için sigma değeri (int - 2'den büyük değer almalı)
        
    Output:
        ysm --> Dikey düzlemde yumuşatılmış oylama sonuçları (np.array - 1d)
        xsm --> Yatay düzlemde yumuşatılmış oylama sonuçları (np.array - 1d)
    
    '''
    
    (h, w) = im.shape
    nons = np.transpose(np.nonzero(im))
    yh = np.zeros(h).astype(np.float64)
    xh = np.zeros(w).astype(np.float64)
    for px in nons:
        yh[px[0]] += 1
        xh[px[1]] += 1
    ysm = gaussian_filter1d(yh, sigma)
    xsm = gaussian_filter1d(xh, sigma)
    
    return ysm, xsm


def get_peaks(ysm, xsm, plot=False):
    '''
    get_peaks()
    
    Oylama sonuçlarının tepe noktalarını tespit eder.
    
    Input:
        ysm --> grid_pos() çıktısı (np.array - 1d)
        xsm --> grid_pos() çıktısı (np.array - 1d)
        plot --> True yapıldığı takdirde oylama sonuçlarının grafiğini çizer (bool)
        
    Output:
        ypeaks --> Dikey düzlem tepe noktaları (np.array - 1d)
        xpeaks --> Yatay düzlem tepe noktaları (np.array - 1d)
    
    '''
    
    ypeaks = find_peaks(ysm)[0]
    xpeaks = find_peaks(xsm)[0]
    yp = np.arange(ysm.shape[0])
    xp = np.arange(xsm.shape[0])
    
    if plot:
        plt.figure(figsize=(20,5))
        plt.subplot(121)
        plt.plot(yp, ysm, 'r-')
        plt.title('Dikey (Y)')
        plt.subplot(122)
        plt.plot(xp, xsm, 'b-')
        plt.title('Yatay (X)')
        plt.show()
    return ypeaks, xpeaks



def boundry_cond(ypeaks, xpeaks, hor_line_imgs, ver_line_imgs, cell_w, no_of_cells):
    '''
    
    boundry_cond()
    
    Labirent üzerindeki duvarların varlığını veya yokluğunu kontrol eder.
    
    Input:
        ypeaks --> get_peaks() çıktısı (np.array - 1d)
        xpeaks --> get_peaks() çıktısı (np.array - 1d)
        hor_line_imgs --> get_line_imgs() çıktısı, yatay çizgi şeklindeki görüntü listesi (python list)
        ver_line_imgs --> get_line_imgs() çıktısı, dikey çizgi şeklindeki görüntü listesi (python list)
        cell_w --> get_cell_prop() çıktısı, hücre genişliği (int)
        no_of_cells --> get_cell_prop() çıktısı, dikey veya yatayda hücre sayısı (int)
        
    Output:
        hor_walls --> Sırasıyla dikey görüntülerde tespit edilmiş yatay duvarların konumları (np.array - 2d - bool)
        ver_walls --> Sırasıyla yatay görüntülerde tespit edilmiş dikey duvarların konumları (np.array - 2d - bool)
    
    '''
    
    true_bounds_x = [xpeaks[0]]
    true_bounds_y = [ypeaks[0]]
    for i in range(no_of_cells):
        true_bounds_x.append(xpeaks[0]+cell_w*(i+1))
        true_bounds_y.append(ypeaks[0]+cell_w*(i+1))


    ver_walls = []
    for hor_l in hor_line_imgs:
        ysm_l, xsm_l = grid_pos(hor_l)
        _, xpeaks_l = get_peaks(ysm_l, xsm_l)

        line_wall = []
        for b in true_bounds_x:
            temp_wall = False
            pad = int(cell_w/4)
            for j in range(-pad,pad):
                val = b+j
                if val in xpeaks_l:
                    temp_wall = True
                    break
            line_wall.append(temp_wall)

        ver_walls.append(line_wall)

    hor_walls = []
    for ver_l in ver_line_imgs:
        ysm_l, xsm_l = grid_pos(ver_l)
        ypeaks_l, _ = get_peaks(ysm_l, xsm_l)

        line_wall = []
        for b in true_bounds_y:
            temp_wall = False
            pad = int(cell_w/4)
            for j in range(-pad,pad):
                val = b+j
                if val in ypeaks_l:
                    temp_wall = True
                    break
            line_wall.append(temp_wall)

        hor_walls.append(line_wall)
        
    hor_walls = np.array(hor_walls)
    ver_walls = np.array(ver_walls)
    
    return hor_walls, ver_walls







def get_cell_prop(inv):
    '''

        get_cell_prop()

        Hücre boyutlarının kaç piksel uzunluğunda olduğunu tespit eder.
        *Hücrelerin kare olduğu varsayılmıştır.

        Input:
            inv --> get_inv() çıktısı (np.array - 2d)

        Output:
            cell_w --> Hücre genişliği/yüksekliği (int)
            no_of_cells --> Dikey veya yatayda hücre sayısı (int)

    '''

    ysm, xsm = grid_pos(inv)
    ypeaks, xpeaks = get_peaks(ysm, xsm)
    diffs = []
    for i in range(ypeaks.shape[0]-1):
        temp = ypeaks[i+1] - ypeaks[i]
        diffs.append(temp)
    for j in range(xpeaks.shape[0]-1):
        temp = xpeaks[i+1] - xpeaks[i]
        diffs.append(temp)
    
    diffs_arr = np.zeros(100)
    for el in diffs:
        diffs_arr[el] += 1
    diffs_arr_sm = gaussian_filter1d(diffs_arr, 3)
    diffs_peaks = find_peaks(diffs_arr_sm)[0]
    
    max_diff = -1
    for el in diffs_peaks:
        if diffs_arr_sm[el] > max_diff:
            max_diff = el

    cell_w = int(max_diff)
    
    ypeaks = np.float64(ypeaks)
    maze_w = ypeaks[-1] - ypeaks[0]
    no_of_cells = int(round(maze_w/cell_w))
    
    return cell_w, no_of_cells


def get_line_imgs(inv, ypeaks, xpeaks, cell_w, no_of_cells):
    '''
    
    Satır ve sütun görüntülerini çıkartır.
    
    Input:
        inv --> get_inv() çıktısı (np.array - 2d)
        ypeaks --> get_peaks() çıktısı (np.array - 1d)
        xpeaks --> get_peaks() çıktısı (np.array - 1d)
        cell_w --> get_cell_prop() çıktısı, hücre piksel genişliği (int)
        no_of_cells --> get_cell_prop() çıktısı, hücre sayısı (int)
    
    Output:
        hor_line_imgs --> Yatay görüntü listesi (python list)
        ver_line_imgs --> Dikey görüntü listesi (python list)
    
    '''
    
    hor_line_imgs = []
    ver_line_imgs = []

    ypeaks = np.int64(ypeaks)
    
    crop = int(cell_w/3)
    
    for i in range(no_of_cells):
        start = ypeaks[0] + i*cell_w
        temp_img = inv[start+crop:start+cell_w-crop,:]
        hor_line_imgs.append(temp_img)

    for j in range(no_of_cells):
        start = xpeaks[0] + j*cell_w
        temp_img = inv[:,start+crop:start+cell_w-crop]
        ver_line_imgs.append(temp_img)
    
    return hor_line_imgs, ver_line_imgs

def create_cells(hor_walls, ver_walls, no_of_cells):
    '''
    
    Labirentten topladığı duvar bilgileri ile hücre objelerini oluşturur.
    
    Input:
        hor_walls --> boundry_cond() çıktısı (python list)
        ver_walls --> boundry_cond() çıktısı (python list)
        no_of_cells --> get_cell_prop() çıktısı (int)
        
    Output:
        cells --> Hücre objeleri listesi, koordinatlar (x,y) şeklindedir. +y aşağıyı, +x sağı göstermektedir. (python list)
    
    '''
    
    cells = []
    for i in range(no_of_cells):
        add = []
        for j in range(no_of_cells):
            temp_cell = Cell(t=hor_walls[i][j], 
                             b=hor_walls[i][j+1], 
                             l=ver_walls[j][i], 
                             r=ver_walls[j][i+1], 
                             c=(i,j))
            add.append(temp_cell)
        cells.append(add)
    
    return cells

