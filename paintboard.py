from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap,QPainter,  QPaintEvent, QMouseEvent, QPen,QColor
from PyQt5.QtCore import QPoint,QSize
from PyQt5.QtCore import Qt


class PaintBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.size_x = 500
        self.size_y = 500
        self.size = QSize(self.size_x, self.size_y)
        self.board = QPixmap(self.size)
        self.board.fill(Qt.white)
        self.clipping_points=[]
        self.clipped_points=[]
        self.current_mouse_position =QPoint(0, 0)
        self.painter = QPainter()
        self.mode=None
        self.clipping_flag = False
        self.clipped_flag = False

    def mouse(self):
        self.mode = None

    def clear(self):
        self.clipping_flag = False
        self.clipped_flag = False
        self.clipping_points.clear()
        self.clipped_points.clear()
        self.board.fill(Qt.white)
        self.update()

    def polygon(self):
        self.mode = 'polygon'

    def convexPolygon(self):
        self.mode ='convex polygon'


    def paintEvent(self, paintEvent):
        self.painter.begin(self)
        self.painter.drawPixmap(0, 0, self.board)
        self.painter.end()

    def mousePressEvent(self, mouseEvent):
        if self.mode == None:
            return
        self.current_mouse_position = (mouseEvent.pos().x(),mouseEvent.pos().y())
        #print(self.current_mouse_position)
        self.painter.begin(self.board)
        self.painter.setPen(QPen(Qt.black, 3))
        self.painter.drawPoint(self.current_mouse_position[0],self.current_mouse_position[1])
        self.painter.end()
        self.update()


    def mouseMoveEvent(self, mouseEvent):
        pass
        # self.current_mouse_position = mouseEvent.pos()
        # print(self.current_mouse_position)

    def drawLine(self,x1,y1,x2,y2,pen):
        self.painter.begin(self.board)
        self.painter.setPen(pen)
        self.painter.drawLine(x1,y1,x2,y2)
        self.painter.end()
        self.update()

    def isConvex(self,points):
        def sgn(x):
            if x > 0:
                return 1
            else:
                return -1
        vx1, vy1 = points[-1][0] - points[-2][0], points[-1][1] - points[-2][1]
        vx2, vy2 = points[0][0] - points[-1][0], \
                   points[0][1] - points[-1][1]
        sign = sgn(vx1 * vy2 - vx2 * vy1)
        for i in range(len(points)-1):
            vx1, vy1 = points[i][0] - points[i-1][0], points[i][1] - points[i-1][1]
            vx2, vy2 = points[i+1][0] - points[i][0], \
                       points[i+1][1] - points[i][1]
            if sign != sgn(vx1 * vy2 - vx2 * vy1):
                return False
        return True



    def mouseReleaseEvent(self, mouseEvent):
        #clipping convex
        if self.mode == 'convex polygon':
            if len(self.clipping_points) ==0:
                self.clipping_points.append(self.current_mouse_position)
                return
            if self.clipping_points[0][0] - 5 <= self.current_mouse_position[0] <= self.clipping_points[0][0] +5 and \
               self.clipping_points[0][1] - 5 <= self.current_mouse_position[1] <= self.clipping_points[0][1] + 5:
                self.drawLine(self.clipping_points[-1][0], self.clipping_points[-1][1],
                              self.clipping_points[0][0],self.clipping_points[0][1],
                              QPen(Qt.black, 1, Qt.DashDotDotLine))
                self.mode = None
                if self.isConvex(self.clipping_points):
                    print("convex polygon")
                    self.clipping_flag = True
                else:
                    print("non-convex polygon")
                return

            self.clipping_points.append(self.current_mouse_position)
            self.drawLine(self.clipping_points[-2][0], self.clipping_points[-2][1],
                          self.clipping_points[-1][0],self.clipping_points[-1][1],
                          QPen(Qt.black, 1, Qt.DashDotDotLine))
        #clipped polygon
        elif self.mode == 'polygon':
            if len(self.clipped_points) ==0:
                self.clipped_points.append(self.current_mouse_position)
                return
            if self.clipped_points[0][0] - 5 <= self.current_mouse_position[0] <= self.clipped_points[0][0] +5 and \
               self.clipped_points[0][1] - 5 <= self.current_mouse_position[1] <= self.clipped_points[0][1] + 5:
                self.drawLine(self.clipped_points[-1][0], self.clipped_points[-1][1],
                              self.clipped_points[0][0], self.clipped_points[0][1],
                              QPen(Qt.yellow, 1, Qt.SolidLine))
                self.mode = None
                self.clipped_flag = True
                return

            self.clipped_points.append(self.current_mouse_position)
            self.drawLine(self.clipped_points[-2][0],self.clipped_points[-2][1],
                          self.clipped_points[-1][0],self.clipped_points[-1][1],
                          QPen(Qt.yellow, 1, Qt.SolidLine))


    def sutherlandHodgman(self):

        def draw(outPoly,outPoly_state):
            self.painter.begin(self.board)
            #self.painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
            (x1, y1) = outPoly[-1]
            previous_state = outPoly_state[-1]
            for (x2, y2), current_state in zip(outPoly, outPoly_state):
                if previous_state == 0 or current_state == 0:  # if the two neighbor vertices are all on the edge of clipping points, do not draw line between them
                    self.painter.drawLine(x1, y1, x2, y2)
                (x1, y1) = (x2, y2)
                previous_state = current_state
            self.painter.end()

        def sgn(x):
            if x>0:
                return 1
            else:
                return -1

        def isInside(point,clipping_points):
            x = point[0]
            y = point[1]
            vx1, vy1 = x - clipping_points[-1][0], y - clipping_points[-1][1]
            vx2, vy2 = clipping_points[0][0] - clipping_points[-1][0], \
                       clipping_points[0][1] - clipping_points[-1][1]
            sign =sgn(vx1*vy2-vx2*vy1)
            (x1,y1) = clipping_points[0]
            for (x2,y2) in clipping_points[1:]:
                vx1, vy1 = x - x1, y - y1
                vx2, vy2 = x2 - x1, y2 - y1
                if sign != sgn(vx1*vy2-vx2*vy1):
                    return False
                (x1,y1) = (x2,y2)
            return True

        def intersect(start_point,end_point,clipping_points):
            x1 = start_point[0]
            y1 =start_point[1]
            x2 = end_point[0]
            y2 = end_point[1]

            if x2-x1==0:
               k1=None
               b1=0
            else:
                k1 = (y2-y1)/(x2-x1)
                b1 = y1 - x1*k1

            min_x,max_x=(x1,x2) if x1<x2 else (x2,x1)
            (x3,y3) = clipping_points[-1]
            for (x4,y4) in clipping_points:
                if x4 - x3 == 0:
                    k2 = None
                    b2=0
                else:
                    k2 = (y4 - y3) / (x4 - x3)
                    b2 = y3 - x3 * k2

                if k1==None and k2==None:
                    (x3, y3) = (x4, y4)
                    continue

                if k2==None:
                    x = x3
                elif k1==None:
                    x = x1
                else:
                    if k1-k2==0:
                        (x3, y3) = (x4, y4)
                        continue
                    x = (b2-b1)/(k1-k2)

                if min_x<=x<=max_x and min(x3,x4)<=x<=max(x3,x4):
                    if k1 ==None:
                        y = k2 * x + b2
                    else:
                        y = k1 * x + b1

                    x, y = int(x), int(y)
                    return (x,y)

                (x3,y3)=(x4,y4)




        if not self.clipping_flag or not self.clipped_flag:
            return
        print(self.clipping_points)
        print(self.clipped_points)
        #rectangle
        # self.clipping_points= [[100, 100], [100, 200], [200, 200], [200, 100]]
        # self.clipped_points =[[150,150],[150,250],[175,250],[175,150]]
        # self.clipping_points= [[100, 100], [100, 200], [200, 200], [200, 100]]
        # self.clipped_points =[[100, 100], [100, 200], [200, 200], [200, 100]]
        outPoly=[]
        outPoly_state=[]
        start_point = self.clipped_points[-1]
        for end_point in self.clipped_points:
            if isInside(end_point,self.clipping_points):
                if isInside(start_point,self.clipping_points):
                    outPoly.append(end_point),outPoly_state.append(0)
                else:
                    intersect_point = intersect(start_point,end_point,self.clipping_points)
                    outPoly.append(intersect_point),outPoly_state.append(1)
                    outPoly.append(end_point),outPoly_state.append(0)
            elif isInside(start_point,self.clipping_points):
                intersect_point = intersect(start_point, end_point,self.clipping_points)
                outPoly.append(intersect_point),outPoly_state.append(1)

            start_point = end_point

        #drawing
        if len(outPoly):
            draw(outPoly, outPoly_state)

        self.update()

    def vertexSorting(self):

        def draw(AET,y):
            self.painter.begin(self.board)
            i=0
            while i<len(AET):
                self.painter.drawLine(int(AET[i][1]),y,int(AET[i+1][1]),y)
                i+=2
            self.painter.end()

        def ET(A,B):
            x1,y1=A[0],A[1]
            x2,y2=B[0],B[1]
            ymax = max(y1,y2)
            if x2-x1==0:
                m = None
            else:
                m = (y2-y1)/(x2-x1)
                if  m !=0:
                    m=1/m
            if m==None or m>=0:
                x = min(x1,x2)
            else:
                x = max(x1,x2)
            return [ymax,x,m]


        if not self.clipped_flag:
            return
        #rectangle
        #self.clipped_points=[[100,100],[100,200],[200,200],[200,100]]
        P = [list(x) for x in self.clipped_points]
        N = len(P)
        #sorted by y coordinate and then x
        indices=[i for _,i in sorted(zip(P,range(N)),key=lambda x: (x[0][1],x[0][0]))]
        AET = []

        k = 0
        i = indices[k]
        y = P[indices[0]][1]
        ymax = P[indices[N-1]][1]

        while y<ymax:
            while P[i][1] == y:
                if P[i-1][1] > P[i][1]:
                    AET.append(ET(P[i],P[i-1]))
                if P[(i+1)%N][1] > P[i][1]:
                    AET.append(ET(P[i],P[(i+1)%N]))
                k+=1
                i=indices[k]

            #sort AET by x value
            AET.sort(key=lambda x: x[1])

            #fill pixels between pairs of intersections
            draw(AET,y)

            #++y
            y+=1

            #remove from AET edges for which ymax = y
            AET =[x for x in AET if x[0]!=y]

            #for each edge in AET
            #        x += 1/m
            for x in AET:
                if x[2]!=None:
                    x[1]+=x[2]
        self.update()

