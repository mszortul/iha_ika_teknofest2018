from maze_util import *

class Ghost:
    
    newborn_id = 0
    
    def __init__(self, parent_list, p_route):
        self.id = self.newborn_id
        Ghost.newborn_id +=1
        self.parents = parent_list
        self.route = p_route


class Maze:
    
    '''
    
    Kullanım:
        Görüntünün dosya yolunu parametre olarak girerek obje oluştur.
            ornek = Maze('ornek.jpg')
        Giriş ve çıkış koordinatlarını tanımla.
            ornek.set_start_exit_coors((0,0), (19,19))
        Çözüm fonksiyonunu yürüt.
            cozum = ornek.solve()
            print(cozum)
    
    '''
    
    def __init__(self, fname, debug=False):
        self.ghosts = []
        self.solved = False
        self.img = cv2.imread(fname)
        self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.inv = get_inv(fname)
        
        ysm, xsm = grid_pos(self.inv)
        ypeaks, xpeaks = get_peaks(ysm, xsm, plot=False)
        if debug:
            print('ypeaks:', ypeaks)
            print('xpeaks:', xpeaks)
        self.cell_w, self.no_of_cells = get_cell_prop(self.inv)
        if debug:    
            print('cell_w:', self.cell_w)
            print('no_of_cells:', self.no_of_cells)
        hor_line_imgs, ver_line_imgs = get_line_imgs(self.inv, ypeaks, xpeaks, self.cell_w, self.no_of_cells)
        
        hor_walls, ver_walls = boundry_cond(ypeaks, xpeaks, hor_line_imgs, ver_line_imgs, self.cell_w, self.no_of_cells)
        
        self.cells = create_cells(hor_walls, ver_walls, self.no_of_cells)
        
    def set_start_exit_coors(self, st_coor, ex_coor): #(9,0), (10,19)
        self.start = st_coor
        self.exit = ex_coor
    
    def create_ghost_f(self, coor):
        self.ghosts.append(Ghost([], []))
        self.move_ghost(0, coor)
    
    def move_ghost(self, index, coor):
        (self.ghosts[index]).route.append(coor)
        (self.cells[coor[0]][coor[1]]).visited_by(self.ghosts[index].id)
    
    def create_child(self, p_list, p_route):
        self.ghosts.append(Ghost(p_list, p_route))
    
    def show_ghost_info(self, ind):
        print('\nGhost id:', self.ghosts[ind].id)
        print('Parents:', self.ghosts[ind].parents)
        print('Route:', self.ghosts[ind].route)
    
    def test(self):
        for i in range(5):
            self.create_child([], [])
        
        self.move_ghost(2, (5,5))
        
        for i in range(5):
            self.show_ghost_info(i)

    def check_ghosts(self):
        new_childs = []
        to_move = []
        to_kill = []

        for i in range(len(self.ghosts)):
            curr_coor = self.ghosts[i].route[-1]
            curr_ways = self.check_ways(curr_coor)

            if len(curr_ways) == 0:
                to_kill.append(i)
            if len(curr_ways) == 1:
                coor = copy.deepcopy(curr_ways[0])
                to_move.append((i, coor))
            if len(curr_ways) > 1:
                for j in curr_ways:
                    c = copy.deepcopy(j)
                    p = copy.deepcopy(self.ghosts[i].parents)
                    r = copy.deepcopy(self.ghosts[i].route)
                    add = [c,p,r]
                    new_childs.append(add)
                to_kill.append(i)

        for k in range(len(to_move)):
            ind = to_move[k][0]
            cr = to_move[k][1]
            self.move_ghost(ind, cr)

        for l in range(len(new_childs)):
            nc = new_childs[l][0]
            np = new_childs[l][1]
            nr = new_childs[l][2]
            self.create_child(np, nr)
            self.move_ghost(-1, nc)

        to_kill.sort(reverse=True)
        for ind in to_kill:
            self.ghosts.pop(ind)
            
    def check_ways(self, coor):
        (x, y) = coor
        ways = []
        if not self.cells[x][y].top:
            if not self.cells[x][y-1].visited:
                ways.append((x, y-1))
        if not self.cells[x][y].bot:
            if not self.cells[x][y+1].visited:
                ways.append((x, y+1))
        if not self.cells[x][y].left:
            if not self.cells[x-1][y].visited:
                ways.append((x-1, y))
        if not self.cells[x][y].right:
            if not self.cells[x+1][y].visited:
                ways.append((x+1, y))
        
        return ways
    
    def is_solved(self):
        for i in range(len(self.ghosts)):
            if self.exit == self.ghosts[i].route[-1]:
                return (True, i)
        return (False, -1)
    
    def solve(self, debug=False):
        self.create_ghost_f(self.start)
        (st_x, st_y) = self.start
        
        #print(self.cells[9][0].right)
        
        if st_x-1<0:
            self.cells[st_x][st_y].left = True
        elif st_x+1==self.no_of_cells:
            self.cells[st_x][st_y].right = True
        elif st_y-1<0:
            self.cells[st_x][st_y].top = True
        elif st_y+1==self.no_of_cells:
            self.cells[st_x][st_y].bot = True
        
        end = False
        iterr = 0
        while 1:
            if debug:
                print('\n\nITERATION: ', iterr)
                
                print('\nlen(self.ghosts):', len(self.ghosts))
                for i in range(len(self.ghosts)):
                    print(str(i) + '.' + ' id', self.ghosts[i].id, 'route: ', self.ghosts[i].route)
                lenc = self.no_of_cells
                
                visited_coors = []
                for i in range(lenc):
                    for j in range(lenc):
                        if self.cells[i][j].visited:
                            visited_coors.append((i,j))
                print('visited_coors: ', visited_coors)
            (end, ind) = self.is_solved()
            if end:
                return self.ghosts[ind].route
            else:
                self.check_ghosts()
                iterr += 1
            