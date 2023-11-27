import tkinter as tk
from PIL import Image, ImageTk, ImageGrab
tk.Canvas.create_circle = lambda self, x, y, r, **kwargs:self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

img_name = "file.png"
xD = 0.90
zF = 0.46
xB = 0.24
q = 0.5
R = None
R_relation = 1.3
# R = R_relation * R_min

BORDER_COLOR = "black"
POINTER_COLOR = "blue"
POINTER_SIZE = 4
POINTER_BORDER_COLOR = "white"
POINTER_BORDER_SIZE = 1
GUIDE_LINE_COLOR = "magenta"
GUIDE_LINE_SIZE = 4
Q_LINE_SIZE = 4
Q_LINE_COLOR = "blue"
R_LINE_SIZE = 4
R_LINE_COLOR = "green"
S_LINE_SIZE = 4
S_LINE_COLOR = "red"
TRAY_LINE_COLOR = "magenta"
TRAY_LINE_SIZE = 4

class main:
    def __init__(self,fname,xD=float|int|None,zF=float|int|None,xB=float|int|None,q=float|int|None,R=float|int|None):
        self.xD = xD
        self.zF = zF
        self.xB = xB
        self.q = q
        self.R = R

         # Setup gui, with image
        self.root = tk.Tk()
        self.img = ImageTk.PhotoImage(Image.open(fname))
        self.root.geometry(f"{self.img.width()}x{self.img.height()}")
        self.root.bind("<KeyPress>",self.keydown)
        self.canvas = tk.Canvas(self.root, height=self.img.height(), width=self.img.width(),bd=0, highlightthickness=0)
        self.canvas.bind("<Button-1>",self.left_click)
        self.canvas.bind("<Button-3>",self.right_click)
        self.canvas.create_image(self.img.width()/2,self.img.height()/2,image=self.img)
        self.canvas.place(x=0,y=0)

        # Lists used for bounding box selection
        self.bounding_box:list[tuple[int,int,int]] = []
        self.bounding_box_lines:list[int] = []

        # Keep track of state, this is the starting one
        self.state = "STATE_DRAWING_BOUNDING_BOX"

        # Setup the graph area, from axis
        self.graph_min_x = 0
        self.graph_max_x = 1
        self.graph_min_y = 0
        self.graph_max_y = 1
        
        # Intersect between the lines
        self.q_intersect = None
        self.r_intersect = None

        self.trays = []

        # Make it stop upon script stop
        check = lambda:self.root.after(500, check)
        self.root.after(500, check)
        self.root.mainloop()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self,val:str):
        self.root.title(val)
        self._state=val

    def screenshot(self,widget,fname):
        widget.update()
        x=self.root.winfo_rootx()+widget.winfo_x()
        y=self.root.winfo_rooty()+widget.winfo_y()
        x1=x+widget.winfo_width()
        y1=y+widget.winfo_height()
        ImageGrab.grab().crop((x,y,x1,y1)).save(fname)

    def left_click(self,event:tk.Event):
        print(event)
        if not isinstance(event.widget,tk.Canvas):return
        match self.state:
            case "STATE_DRAWING_BOUNDING_BOX":
                # If all made, switch to next state
                if len(self.bounding_box)==2:return

                # Draw circle
                canvas = event.widget
                circle = canvas.create_circle(event.x,event.y,POINTER_SIZE,fill=POINTER_COLOR, outline=POINTER_BORDER_COLOR, width=POINTER_BORDER_SIZE)
                self.bounding_box.append((event.x,event.y,circle))

                # If both circles are drawn, connect them with lines
                if len(self.bounding_box)!=2:return
                for x,y,circle in self.bounding_box:
                    canvas.delete(circle)

                x1,y1,_ = self.bounding_box[0]
                x2,y2,_ = self.bounding_box[1]
                self.bounding_box_lines = [
                    canvas.create_line(x1,y1,x1,y2,width=2,fill=BORDER_COLOR),
                    canvas.create_line(x2,y2,x1,y2,width=2,fill=BORDER_COLOR),
                    canvas.create_line(x1,y1,x2,y1,width=2,fill=BORDER_COLOR),
                    canvas.create_line(x2,y2,x2,y1,width=2,fill=BORDER_COLOR),
                ]

                self.box_min_x = min(self.bounding_box,key=lambda _:_[0])[0]
                self.box_max_x = max(self.bounding_box,key=lambda _:_[0])[0]
                self.box_min_y = min(self.bounding_box,key=lambda _:_[1])[1]
                self.box_max_y = max(self.bounding_box,key=lambda _:_[1])[1]
            case "STATE_DRAWING_Q":
                # If all made, switch to next state
                if self.q_intersect!=None:return

                # Draw circle
                canvas = event.widget
                circle = canvas.create_circle(event.x,event.y,POINTER_SIZE,fill=POINTER_COLOR, outline=POINTER_BORDER_COLOR, width=POINTER_BORDER_SIZE)
                self.q_intersect = (event.x,event.y,circle)

                x,y = self.graph_to_box(self.zF,self.zF)
                self.q_line = canvas.create_line(x,y,event.x,event.y,width=Q_LINE_SIZE,fill=Q_LINE_COLOR)
            case "STATE_DRAWING_R":
                if self.R == None:
                    # If all made, switch to next state
                    if self.r_intersect!=None:return

                    # Draw circle
                    canvas = event.widget
                    circle = canvas.create_circle(event.x,event.y,POINTER_SIZE,fill=POINTER_COLOR, outline=POINTER_BORDER_COLOR, width=POINTER_BORDER_SIZE)
                    self.r_intersect = (event.x,event.y,circle)

                    x,y = self.graph_to_box(self.xD,self.xD)
                    self.r_line = canvas.create_line(x,y,event.x,event.y,width=R_LINE_SIZE,fill=R_LINE_COLOR)
            case "STATE_DRAWING_TRAYS":
                canvas = event.widget

                val_x,val_y,_,_ = self.trays[-1]
                new_val_x,_ = self.box_to_graph(event.x,0) 

                r_x,r_y,_ = self.r_intersect
                if event.x>r_x:
                    # We are on the r line
                    new_val_y = new_val_x*self.R/(self.R+1) + self.xD/(self.R+1)
                elif new_val_x > self.xB:
                    # We are on the s line
                    new_val_y = new_val_x*(self.vB+1)/(self.vB) - self.xB/(self.vB)
                else:
                    # We are done!
                    new_val_y = new_val_x

                x1,y1 = self.graph_to_box(val_x,val_y)
                x2,y2 = self.graph_to_box(new_val_x,val_y)
                x3,y3 = self.graph_to_box(new_val_x,new_val_y)
                self.trays.append((
                    new_val_x,
                    new_val_y,
                    canvas.create_line(x1,y1,x2,y2,width=TRAY_LINE_SIZE,fill=TRAY_LINE_COLOR),
                    canvas.create_line(x2,y2,x3,y3,width=TRAY_LINE_SIZE,fill=TRAY_LINE_COLOR)
                ))

                canvas.delete(self.temp_line)
                x1,y1 = self.graph_to_box(self.graph_min_x,new_val_y)
                x2,y2 = self.graph_to_box(self.graph_max_x,new_val_y)
                self.temp_line = self.canvas.create_line(x1,y1,x2,y2,fill=GUIDE_LINE_COLOR,dash=True,width=GUIDE_LINE_SIZE)


    def right_click(self,event:tk.Event):
        print(event)
        if not isinstance(event.widget,tk.Canvas):return
        match self.state:
            case "STATE_DRAWING_BOUNDING_BOX":
                canvas = event.widget
                for x,y,circle in self.bounding_box:
                    canvas.delete(circle)
                self.bounding_box=[]

                for line in self.bounding_box_lines:
                    canvas.delete(line)
                self.bounding_box_lines=[]
            case "STATE_DRAWING_Q":
                if self.q_intersect == None:return
                x,y,circle = self.q_intersect
                canvas = event.widget
                canvas.delete(circle)
                canvas.delete(self.q_line)
                self.q_intersect = None
            case "STATE_DRAWING_R":
                if self.R == None:
                    if self.r_intersect == None:return
                    x,y,circle = self.r_intersect
                    canvas = event.widget
                    canvas.delete(circle)
                    canvas.delete(self.r_line)
                    self.r_intersect = None
            case "STATE_DRAWING_TRAYS":
                if len(self.trays)<2:return
                canvas = event.widget
                canvas.delete(self.temp_line)
                val_x,val_y,line1,line2 = self.trays.pop()
                old_val_x,old_val_y,_,_ = self.trays[-1]
                canvas.delete(line1)
                canvas.delete(line2)
                x1,y1 = self.graph_to_box(self.graph_min_x,old_val_y)
                x2,y2 = self.graph_to_box(self.graph_max_x,old_val_y)
                self.temp_line = self.canvas.create_line(x1,y1,x2,y2,fill=GUIDE_LINE_COLOR,dash=True,width=GUIDE_LINE_SIZE)


    def keydown(self,event:tk.Event):
        print(event)
        match event.keysym:
            case "Return":
                match self.state:
                    case "STATE_DRAWING_BOUNDING_BOX":
                        if len(self.bounding_box)!=2:return
                        self.state = "STATE_DRAWING_Q"
                        if isinstance(self.xD,(float,int)):
                            x,y = self.graph_to_box(self.xD,self.xD)
                            self.canvas.create_circle(x,y,POINTER_SIZE,fill=R_LINE_COLOR, outline=POINTER_BORDER_COLOR, width=POINTER_BORDER_SIZE)
                        if isinstance(self.zF,(float,int)):
                            x,y = self.graph_to_box(self.zF,self.zF)
                            self.canvas.create_circle(x,y,POINTER_SIZE,fill=Q_LINE_COLOR, outline=POINTER_BORDER_COLOR, width=POINTER_BORDER_SIZE)
                        if isinstance(self.xB,(float,int)):
                            x,y = self.graph_to_box(self.xB,self.xB)
                            self.canvas.create_circle(x,y,POINTER_SIZE,fill=S_LINE_COLOR, outline=POINTER_BORDER_COLOR, width=POINTER_BORDER_SIZE)
                        if isinstance(self.q,(float,int)):
                            if self.q == 0: # Horizontal
                                x1 = self.graph_min_x
                                y1 = self.zF
                                x2 = self.graph_max_x
                                y2 = self.zF
                            elif self.q == 1: # Vertical
                                x1 = self.zF
                                y1 = self.graph_min_y
                                x2 = self.zF
                                y2 = self.graph_max_y
                            else: # Other
                                x1 = self.graph_min_x
                                y1 = x1*q/(q-1) - (self.zF)/(self.q-1)
                                x2 = self.graph_max_x
                                y2 = x2*q/(q-1) - (self.zF)/(self.q-1)

                            x1,y1 = self.graph_to_box(x1,y1)
                            x2,y2 = self.graph_to_box(x2,y2)
                            self.temp_line = self.canvas.create_line(x1,y1,x2,y2,fill=GUIDE_LINE_COLOR,dash=True,width=GUIDE_LINE_SIZE)

                    case "STATE_DRAWING_Q":
                        if self.q_intersect == None:return
                        if not isinstance(self.xD,(float,int)):
                            print("xD required")
                            return
                        self.state = "STATE_DRAWING_R"
                        self.canvas.delete(self.temp_line)
                        x1,y1,circle = self.q_intersect
                        self.canvas.delete(circle)
                        x2,y2 = self.graph_to_box(self.xD,self.xD)
                        self.temp_line = self.canvas.create_line(x1,y1,x2,y2,fill=GUIDE_LINE_COLOR,dash=True,width=GUIDE_LINE_SIZE)

                    case "STATE_DRAWING_R":
                        if self.R == None:
                            if self.r_intersect == None:return
                            self.canvas.delete(self.temp_line)
                            x1,y1,circle = self.r_intersect
                            self.canvas.delete(circle)
                            x1,y1 = self.box_to_graph(x1,y1)
                            x2,y2 = self.xD,self.xD

                            self.screenshot(self.canvas,"r_min.png")
                            self.canvas.delete(self.r_line)

                            a = (y1-y2)/(x1-x2)
                            R_min = -a/(a-1)
                            self.R = R_relation * R_min
                            
                            print("x1 =",x1)
                            print("y1 =",y1)
                            print("x2 =",x2)
                            print("y2 =",y2)
                            print("a =",a)
                            print("R_min =",R_min)
                            print("R =",self.R)

                        self.state = "STATE_DRAWING_TRAYS"
                        x = (self.xD*(self.q-1) + self.zF*(self.R+1))/(self.q+self.R)
                        y = x*self.R/(self.R+1) + self.xD/(self.R+1)
                        x1,y1 = self.graph_to_box(x,y)
                        x2,y2 = self.graph_to_box(self.xD,self.xD)

                        a = (self.xB-y)/(self.xB-x)
                        self.vB = 1/(a-1)

                        # Draw circle
                        """
                        circle = self.canvas.create_circle(x1,y1,POINTER_SIZE,fill=POINTER_COLOR, outline=POINTER_BORDER_COLOR, width=POINTER_BORDER_SIZE)
                        self.r_intersect = (x1,y1,circle)
                        self.canvas.delete(circle)
                        """
                        self.r_line = self.canvas.create_line(x1,y1,x2,y2,width=R_LINE_SIZE,fill=R_LINE_COLOR)

                        x2,y2 = self.graph_to_box(self.xB,self.xB)
                        self.s_line = self.canvas.create_line(x1,y1,x2,y2,width=S_LINE_SIZE,fill=S_LINE_COLOR)
                        
                        self.trays = [(self.xD,self.xD,0.0,0.0)]
                        x1,y1 = self.graph_to_box(self.graph_min_x,self.xD)
                        x2,y2 = self.graph_to_box(self.graph_max_x,self.xD)
                        self.temp_line = self.canvas.create_line(x1,y1,x2,y2,fill=GUIDE_LINE_COLOR,dash=True,width=GUIDE_LINE_SIZE)

                    case "STATE_DRAWING_TRAYS":
                        self.state = "STATE_DONE"
                        self.canvas.delete(self.temp_line)
                        self.screenshot(self.canvas,"trays.png")

    def graph_to_box(self,x,y):
        x-=self.graph_min_x
        y-=self.graph_min_y
        x*=(self.box_max_x-self.box_min_x)/(self.graph_max_x-self.graph_min_x)
        y*=(self.box_min_y-self.box_max_y)/(self.graph_max_y-self.graph_min_y)
        x+=self.box_min_x
        y+=self.box_max_y
        return (x,y)

    def box_to_graph(self,x,y):
        x-=self.box_min_x
        y-=self.box_max_y
        x*=(self.graph_max_x-self.graph_min_x)/(self.box_max_x-self.box_min_x)
        y*=(self.graph_max_y-self.graph_min_y)/(self.box_min_y-self.box_max_y)
        x+=self.graph_min_x
        y+=self.graph_min_y

        return (x,y)
main(img_name,xD,zF,xB,q,R)