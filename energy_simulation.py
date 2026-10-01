
import tkinter as tk
import math, random

# ============================================================
# COMMUNITY ENERGY MANAGEMENT SYSTEM
# Single-file Tkinter demo - no external packages required.
# ============================================================

W, H = 1600, 1024
BG="#f4f7fb"; WHITE="#ffffff"; BORDER="#b9c7d8"; TEXT="#10243e"
MUTED="#64748b"; GREEN="#16a34a"; BLUE="#1677e8"; RED="#ef233c"
ORANGE="#f59e0b"; PURPLE="#7c3aed"; GRID="#dbe4ee"
NB_COLORS=["#ffd7d7","#d8e9ff","#dcfce7","#fff0c2","#eadcff"]

class App:
    def __init__(self, root):
        self.root=root
        root.title("Community Energy Management System")
        root.geometry(f"{W}x{H}")
        root.minsize(1200,760)
        root.configure(bg=BG)

        self.auto=True
        self.running=False
        self.sim_time=14.0
        self.speed=1.0

        self.cces_cap=80.0
        self.cces=60.0
        self.bat_cap=4.0
        self.bat=[random.uniform(.70,.95)*self.bat_cap for _ in range(5)]

        self.irr=tk.DoubleVar(value=800)
        self.cloud=tk.DoubleVar(value=20)
        self.temp=tk.DoubleVar(value=30)
        self.wind=tk.DoubleVar(value=10)

        self.last = {
            "solar":[0]*5, "ground":0, "demand":[0]*5,
            "status":["idle"]*5, "transfer":[0]*5,
            "cces_charge":0, "cces_discharge":0
        }

        self.c=tk.Canvas(root,bg=BG,highlightthickness=0,width=W,height=H)
        self.c.pack(fill="both",expand=True)

        self.make_widgets()
        self.reset()
        self.loop()

    # ---------- drawing primitives ----------
    def box(self,x1,y1,x2,y2,fill=WHITE,outline=BORDER,r=12):
        c=self.c
        c.create_rectangle(x1+r,y1,x2-r,y2,fill=fill,outline="")
        c.create_rectangle(x1,y1+r,x2,y2-r,fill=fill,outline="")
        c.create_arc(x1,y1,x1+2*r,y1+2*r,start=90,extent=90,fill=fill,outline="")
        c.create_arc(x2-2*r,y1,x2,y1+2*r,start=0,extent=90,fill=fill,outline="")
        c.create_arc(x1,y2-2*r,x1+2*r,y2,start=180,extent=90,fill=fill,outline="")
        c.create_arc(x2-2*r,y2-2*r,x2,y2,start=270,extent=90,fill=fill,outline="")
        c.create_rectangle(x1+r,y1,x2-r,y2,outline=outline,width=1)
        c.create_rectangle(x1,y1+r,x2,y2-r,outline=outline,width=1)

    def txt(self,x,y,s,size=11,bold=False,fill=TEXT,anchor="nw"):
        self.c.create_text(x,y,text=s,fill=fill,anchor=anchor,
                           font=("Arial",size,"bold" if bold else "normal"))

    def prog(self,x,y,w,h,f,color=GREEN):
        f=max(0,min(1,f))
        self.box(x,y,x+w,y+h,"#e6edf5","#e6edf5",h//2)
        if f>0:self.box(x,y,x+w*f,y+h,color,color,h//2)

    def arrow(self,x1,y1,x2,y2,color,width=4,label=None):
        self.c.create_line(x1,y1,x2,y2,fill=color,width=width,
                           arrow=tk.LAST,arrowshape=(12,14,5))
        if label:
            self.txt((x1+x2)/2,(y1+y2)/2-9,label,9,True,color,"center")

    def house(self,x,y,s=.75):
        c=self.c
        c.create_rectangle(x,y+14*s,x+38*s,y+39*s,fill="white",outline="#334155")
        c.create_polygon(x-3*s,y+14*s,x+19*s,y,x+41*s,y+14*s,
                         fill="#334155",outline="#334155")
        c.create_rectangle(x+15*s,y+25*s,x+23*s,y+39*s,fill="#64748b",outline="")
        c.create_polygon(x+7*s,y+11*s,x+22*s,y+3*s,x+30*s,y+9*s,
                         x+15*s,y+16*s,fill="#2d7dd2",outline="#1e4f7a")

    def pv(self,x,y,s=.8):
        c=self.c
        p=[x,y,x+55*s,y,x+68*s,y+35*s,x+13*s,y+35*s]
        c.create_polygon(p,fill="#2d7dd2",outline="#153c68",width=2)

    def tank(self,x,y,w=80,h=105):
        c=self.c
        c.create_rectangle(x,y+14,x+w,y+h,fill="#edf2f7",outline="#64748b",width=2)
        c.create_oval(x,y,x+w,y+28,fill="#dce5ef",outline="#64748b",width=2)
        c.create_oval(x,y+h-16,x+w,y+h+10,fill="#edf2f7",outline="#64748b",width=2)
        self.txt(x+w/2,y+43,"CCES",14,True,anchor="center")
        self.txt(x+w/2,y+66,"80 MWh",10,True,MUTED,"center")

    # ---------- widgets ----------
    def make_widgets(self):
        self.sliders=[]
        specs=[
            ("Solar Irradiance",self.irr,0,1000),
            ("Cloud Cover",self.cloud,0,100),
            ("Ambient Temperature",self.temp,0,50),
            ("Wind Speed",self.wind,0,50)]
        for _,var,lo,hi in specs:
            s=tk.Scale(self.root,variable=var,from_=lo,to=hi,
                       orient="horizontal",showvalue=False,resolution=1,
                       length=230,width=12,sliderlength=18,
                       bg=WHITE,troughcolor="#cbd5e1",
                       activebackground=BLUE,highlightthickness=0,bd=0,
                       command=lambda _:self.redraw())
            self.sliders.append(s)

        self.manual=tk.Button(self.root,text="Manual Control",
            font=("Arial",11,"bold"),bd=0,command=lambda:self.mode(False))
        self.auto_btn=tk.Button(self.root,text="Automatic Simulation",
            font=("Arial",11,"bold"),bd=0,command=lambda:self.mode(True))
        self.speed=tk.Scale(self.root,from_=.5,to=5,resolution=.5,
            orient="horizontal",showvalue=False,length=260,width=12,
            sliderlength=18,bg=WHITE,troughcolor="#cbd5e1",
            activebackground=BLUE,highlightthickness=0,bd=0,
            command=lambda v:setattr(self,"speed",float(v)))
        self.start=tk.Button(self.root,text="▶  Start",font=("Arial",11,"bold"),
            bg="#22c55e",fg="white",bd=0,command=self.start_sim)
        self.pause=tk.Button(self.root,text="Ⅱ  Pause",font=("Arial",11,"bold"),
            bg="#243b53",fg="white",bd=0,command=self.pause_sim)
        self.resetbtn=tk.Button(self.root,text="↻  Reset",font=("Arial",11,"bold"),
            bg="#e2e8f0",fg=TEXT,bd=0,command=self.reset)

    def place(self):
        for i,s in enumerate(self.sliders): s.place(x=250,y=57+i*38,width=235,height=28)
        self.manual.place(x=1195,y=45,width=155,height=36)
        self.auto_btn.place(x=1355,y=45,width=170,height=36)
        self.speed.place(x=1220,y=102,width=300,height=30)
        self.start.place(x=1195,y=140,width=100,height=38)
        self.pause.place(x=1302,y=140,width=100,height=38)
        self.resetbtn.place(x=1409,y=140,width=100,height=38)

    # ---------- model ----------
    def daylight(self):
        t=self.sim_time
        if 5.5<=t<=18.5:
            return max(0,math.sin(math.pi*(t-5.5)/13))
        return 0

    def sfactor(self):
        daylight=self.daylight()
        cloud=max(0,1-.65*self.cloud.get()/100)
        temp=max(.82,1-max(0,self.temp.get()-25)*.004)
        return daylight*(self.irr.get()/1000)*cloud*temp

    def values(self):
        f=self.sfactor()
        total=28*f
        solar=[total*x for x in [.185,.171,.218,.179,.197]]
        ground=12*f
        base=[4.6,4.0,4.4,4.3,4.1]
        t=self.sim_time
        if t<6: k=.72
        elif t<10:k=.82
        elif t<16:k=.68
        elif t<19:k=.90
        else:k=1.10
        mult=[1,.94,1.06,.98,1.03]
        demand=[base[i]*k*mult[i] for i in range(5)]
        return solar,ground,demand

    def battery_status(self,i,solar,demand):
        if solar>demand+.05 and self.bat[i]<self.bat_cap-.03:return "charging"
        if demand>solar+.05 and self.bat[i]>.40:return "discharging"
        return "idle"

    def step(self):
        if self.auto:
            self.sim_time=(self.sim_time+.15*self.speed)%24

        solar,ground,demand=self.values()
        dt=.0833*self.speed
        status=["idle"]*5
        transfer=[0]*5
        ccharge=0
        cdis=0

        # Solar serves local demand first. Surplus charges local Li-ion.
        surplus=[max(0,solar[i]-demand[i]) for i in range(5)]
        deficit=[max(0,demand[i]-solar[i]) for i in range(5)]

        for i in range(5):
            if surplus[i]>0:
                room=self.bat_cap-self.bat[i]
                p=min(surplus[i],1.2)
                e=min(room,p*dt*.94)
                actual=e/max(dt*.94,1e-9)
                if room>.01:
                    self.bat[i]+=e
                    status[i]="charging"
                    surplus[i]-=actual
                if surplus[i]>0:ccharge+=surplus[i]

        # Local Li-ion responds to local shortage.
        for i in range(5):
            if deficit[i]>0:
                available=max(0,self.bat[i]-.10*self.bat_cap)
                p=min(deficit[i],1.5,available/max(dt,1e-9)*.95)
                if p>0:
                    self.bat[i]-=p*dt/.95
                    deficit[i]-=p
                    status[i]="discharging"

        # If one neighbourhood is still short, transfer from another NB Li-ion.
        donors=[i for i in range(5) if self.bat[i]>.70*self.bat_cap]
        for r in range(5):
            if deficit[r]<=.05: continue
            for d in donors:
                if d==r:continue
                available=max(0,self.bat[d]-.50*self.bat_cap)
                p=min(deficit[r],1.0,available/max(dt,1e-9)*.92)
                if p>.01:
                    self.bat[d]-=p*dt/.92
                    self.bat[r]+=p*dt*.92
                    transfer[r]+=p
                    transfer[d]-=p
                    deficit[r]-=p

        # Remaining shortage comes from CCES.
        remain=sum(deficit)
        if remain>.01:
            p=min(remain,8)
            e=p*dt/.85
            e=min(e,max(0,self.cces-5))
            cdis=e/max(dt,1e-9)*.85
            self.cces-=e

        # Remaining solar surplus and CCES-ground solar charge CCES.
        ccharge+=ground
        if ccharge>0:
            room=self.cces_cap-self.cces
            e=min(room,ccharge*dt*.85)
            self.cces+=e
            ccharge=e/max(dt,1e-9)/.85

        self.cces=max(0,min(self.cces_cap,self.cces))
        self.bat=[max(0,min(self.bat_cap,x)) for x in self.bat]

        self.last={"solar":solar,"ground":ground,"demand":demand,
                   "status":status,"transfer":transfer,
                   "cces_charge":ccharge,"cces_discharge":cdis}

    # ---------- controls ----------
    def mode(self,a):
        self.auto=a
        self.auto_btn.config(bg=BLUE if a else "#dce5ef",fg="white" if a else TEXT)
        self.manual.config(bg="#dce5ef" if a else BLUE,fg=TEXT if a else "white")
        self.redraw()

    def start_sim(self): self.running=True
    def pause_sim(self): self.running=False

    def reset(self):
        self.running=False
        self.sim_time=14
        self.cces=60
        self.bat=[random.uniform(.70,.95)*self.bat_cap for _ in range(5)]
        self.last={"solar":[0]*5,"ground":0,"demand":[0]*5,
                   "status":["idle"]*5,"transfer":[0]*5,
                   "cces_charge":0,"cces_discharge":0}
        self.redraw()

    # ---------- dashboard ----------
    def redraw(self):
        c=self.c;c.delete("all")
        self.environment()
        self.time_panel()
        self.controls_panel()
        self.solar_panel()
        self.flow_panel()
        self.summary_panel()
        self.nb_cards()
        self.charts()
        self.place()

    def environment(self):
        self.box(10,10,650,205)
        self.txt(28,25,"Environmental Conditions",20,True)
        self.txt(310,27,"(Affecting Solar Generation)",15,True)
        rows=[("☀","Solar Irradiance",f"{self.irr.get():.0f} W/m²","#f59e0b"),
              ("☁","Cloud Cover",f"{self.cloud.get():.0f} %","#1687e8"),
              ("♨","Ambient Temperature",f"{self.temp.get():.0f} °C",RED),
              ("≋","Wind Speed",f"{self.wind.get():.0f} km/h",PURPLE)]
        for i,(ic,l,v,col) in enumerate(rows):
            y=61+i*38
            self.txt(30,y,ic,18,True,col);self.txt(65,y+2,l,12,True)
            self.txt(490,y+2,v,11,True,TEXT,"e")
            self.txt(530,y+2,"(0–1000)" if i==0 else "(0–100)",9,False,MUTED)

    def time_panel(self):
        self.box(665,10,1150,205)
        self.txt(685,25,"Time of Day",20,True)
        x1,x2,y=690,1125,78
        self.box(x1,y,x2,y+34,"#eef3fa","#eef3fa",17)
        self.box(x1,y,820,y+34,"#273477","#273477",17)
        self.box(820,y,1000,y+34,"#f6c24b","#f6c24b",17)
        self.box(1000,y,x2,y+34,"#273477","#273477",17)
        self.txt(705,83,"☾",20,True,"white")
        self.txt(1105,83,"☾",20,True,"white")
        self.txt(905,70,"☀",22,True,ORANGE)
        px=x1+(self.sim_time/24)*(x2-x1)
        self.c.create_line(px,y-8,px,y+42,fill=TEXT,width=2)
        self.txt(x1,125,"12 AM",11,True)
        self.txt((x1+x2)/2,125,"12 PM",11,True,TEXT,"center")
        self.txt(x2,125,"12 AM",11,True,TEXT,"e")
        self.txt(908,150,self.time_string(),24,True,TEXT,"center")
        state="DAYTIME – SOLAR GENERATION ACTIVE" if self.sfactor()>0 else "NIGHT – STORAGE SUPPLY MODE"
        self.box(800,175,1010,199,"#edf3f8","#edf3f8",10)
        self.txt(905,187,state,9,True,MUTED,"center")

    def controls_panel(self):
        self.box(1165,10,1590,205)
        self.txt(1185,25,"Simulation Control",20,True)
        self.txt(1185,82,"Mode:",11,True)
        self.txt(1230,82,"AUTOMATIC" if self.auto else "MANUAL",11,True,
                  BLUE if self.auto else ORANGE)
        self.txt(1185,110,"Simulation Speed",10,True,MUTED)
        self.txt(1515,110,f"{self.speed:.1f}×",10,True,TEXT,"e")
        self.txt(1190,188,"● RUNNING" if self.running else "● PAUSED",
                  10,True,GREEN if self.running else MUTED)

    def solar_panel(self):
        self.box(10,220,285,535)
        self.txt(28,235,"Rooftop Solar (All Houses)",16,True)
        f=self.sfactor();rt=28*f
        self.txt(28,273,"Total Rooftop Capacity",10,True,MUTED)
        self.txt(267,273,"28 MW",11,True,TEXT,"e")
        self.txt(28,301,"Current Generation",10,True,MUTED)
        self.txt(267,301,f"{rt:.1f} MW",11,True,TEXT,"e")
        self.prog(28,323,235,12,f,ORANGE)
        self.txt(267,345,f"{f*100:.0f}%",9,True,MUTED,"e")
        self.pv(70,385,1.2)
        self.txt(28,440,"Distributed rooftop PV",12,True)
        self.txt(28,462,"Local solar → local demand",10,True,GREEN)
        self.txt(28,484,"Excess → Li-ion → CCES",10,True,BLUE)
        self.box(10,548,285,815)
        self.txt(28,563,"Solar Farm (CCES Ground)",16,True)
        g=12*f
        self.txt(28,600,"Total Capacity",10,True,MUTED);self.txt(267,600,"12 MW",11,True,TEXT,"e")
        self.txt(28,628,"Current Generation",10,True,MUTED);self.txt(267,628,f"{g:.1f} MW",11,True,TEXT,"e")
        self.prog(28,650,235,12,f,GREEN)
        self.pv(70,700,.9)

    def flow_panel(self):
        self.box(305,220,1160,535)
        self.txt(325,235,"Power Flow Diagram (Real-time)",18,True)
        self.txt(840,245,"GREEN = SOLAR",9,True,GREEN)
        self.txt(960,245,"BLUE = CCES",9,True,BLUE)
        self.txt(1060,245,"ORANGE = Li-ion",9,True,ORANGE)

        self.box(325,285,535,350)
        self.pv(345,305,.75);self.txt(420,307,"Rooftop Solar",14,True)
        self.txt(420,330,"28 MW capacity",10,False,MUTED)

        self.box(325,370,535,435)
        self.pv(345,390,.75);self.txt(420,392,"Solar Farm",14,True)
        self.txt(420,414,"12 MW capacity",10,False,MUTED)

        self.box(600,285,870,535)
        self.txt(735,300,"Central Energy Station",17,True,TEXT,"center")
        self.txt(735,323,"(CCES)",12,True,MUTED,"center")
        self.tank(690,350,90,105)
        self.txt(735,470,f"{self.cces:.1f} / 80 MWh",14,True,TEXT,"center")
        self.prog(650,492,170,14,self.cces/80,GREEN)
        self.txt(735,516,f"{self.cces/80*100:.0f}% SOC",9,True,MUTED,"center")

        solar,ground,demand=self.values()
        if sum(solar)>0:self.arrow(535,318,650,380,GREEN,5,f"{sum(solar):.1f} MW")
        if ground>0:self.arrow(535,403,650,420,GREEN,5,f"{ground:.1f} MW")

        # Shared distribution bus.
        self.c.create_line(420,555,1120,555,fill="#334155",width=4)

        for i in range(5):
            x=335+i*162
            self.box(x,470,x+150,525,NB_COLORS[i],BORDER,10)
            self.house(x+15,485,.55)
            self.txt(x+57,484,f"Neighbourhood {i+1}",10,True)
            self.txt(x+57,502,"4,000 consumers",8,False,MUTED)
            status=self.last["status"][i]
            # Direction is explicit.
            if status=="discharging":
                self.arrow(735,455,x+75,470,BLUE,3,"CCES")
            elif status=="charging":
                self.arrow(x+75,470,735,455,ORANGE,3,"CHG")
            else:
                self.c.create_line(x+75,470,x+75,455,fill=GRID,width=2)

    def summary_panel(self):
        self.box(1175,220,1590,535)
        self.txt(1195,235,"System Summary (Current)",17,True)
        solar,ground,demand=self.values()
        total=sum(solar)+ground
        rows=[("Total Solar Generation",f"{total:.1f} MW"),
              ("Total Demand",f"{sum(demand):.1f} MW"),
              ("CCES Charging","ACTIVE" if self.last["cces_charge"]>0.01 else "0 MW"),
              ("CCES Discharging","ACTIVE" if self.last["cces_discharge"]>0.01 else "0 MW"),
              ("CCES State of Charge",f"{self.cces:.1f} / 80 MWh"),
              ("Total Li-ion Charge",f"{sum(self.bat):.1f} MWh")]
        y=270
        for lab,val in rows:
            col=GREEN if "Charging" in lab and val=="ACTIVE" else BLUE if "Discharging" in lab and val=="ACTIVE" else TEXT
            self.txt(1195,y,lab,10,True,MUTED);self.txt(1568,y,val,11,True,col,"e");y+=38
        self.txt(1195,475,"CCES SOC",9,True,MUTED)
        self.prog(1195,490,360,13,self.cces/80,GREEN)
        self.txt(1195,523,"Total Li-ion SOC",9,True,MUTED)
        self.prog(1195,538,360,13,sum(self.bat)/(5*self.bat_cap),BLUE)

    def nb_cards(self):
        solar,ground,demand=self.values()
        y=548;cw=306;gap=6
        for i in range(5):
            x=5+i*(cw+gap)
            self.box(x,y,x+cw,815,WHITE,BORDER,12)
            self.box(x,y,x+cw,y+54,NB_COLORS[i],NB_COLORS[i],12)
            self.house(x+17,y+10,.75)
            self.txt(x+70,y+10,f"Neighbourhood {i+1}",13,True)
            self.txt(x+70,y+31,"4,000 consumers",9,False,MUTED)

            yy=y+70
            self.txt(x+17,yy,"☀",15,True,ORANGE)
            self.txt(x+42,yy+1,"Rooftop Solar Generation",9,True)
            self.txt(x+292,yy+1,f"{solar[i]:.1f} MW",9,True,TEXT,"e")

            yy+=29
            self.txt(x+17,yy,"▥",14,True,BLUE)
            self.txt(x+42,yy+1,"Current Demand",9,True)
            self.txt(x+292,yy+1,f"{demand[i]:.1f} MW",9,True,TEXT,"e")

            yy+=31
            self.txt(x+17,yy,"▣",15,True,GREEN)
            self.txt(x+42,yy+1,"Li-ion Battery",9,True)
            frac=self.bat[i]/self.bat_cap
            self.txt(x+292,yy+1,f"{self.bat[i]:.1f}/4 MWh",9,True,TEXT,"e")
            self.prog(x+42,yy+19,225,10,frac,GREEN if frac>.25 else RED)
            self.txt(x+292,yy+36,f"{frac*100:.0f}%",8,True,MUTED,"e")

            st=self.last["status"][i]
            if st=="charging":
                self.box(x+17,yy+47,x+132,yy+70,"#dcfce7","#dcfce7",8)
                self.txt(x+74,yy+58,"⚡ CHARGING",9,True,GREEN,"center")
            elif st=="discharging":
                self.box(x+17,yy+47,x+145,yy+70,"#dbeafe","#dbeafe",8)
                self.txt(x+81,yy+58,"⚡ DISCHARGING",9,True,BLUE,"center")
            else:
                self.box(x+17,yy+47,x+82,yy+70,"#eef2f7","#eef2f7",8)
                self.txt(x+49,yy+58,"IDLE",9,True,MUTED,"center")

            yy+=82
            self.txt(x+17,yy,"Power Flow (Current)",9,True,MUTED)

            # Three unambiguous arrows.
            self.arrow(x+45,yy+45,x+45,yy+20,GREEN,4)
            self.txt(x+45,yy+56,f"{solar[i]:.1f} MW",8,True,TEXT,"center")
            self.txt(x+45,yy+70,"Solar → load",7,False,MUTED,"center")

            if demand[i]>solar[i]:
                self.arrow(x+150,yy+20,x+150,yy+45,BLUE,4)
                self.txt(x+150,yy+56,"CCES → load",8,True,BLUE,"center")
            else:
                self.arrow(x+150,yy+45,x+150,yy+20,ORANGE,4)
                self.txt(x+150,yy+56,"excess →",8,True,ORANGE,"center")

            if st=="charging":
                self.arrow(x+255,yy+20,x+255,yy+45,GREEN,4)
                self.txt(x+255,yy+56,"Solar → Li-ion",8,True,GREEN,"center")
            elif st=="discharging":
                self.arrow(x+255,yy+45,x+255,yy+20,BLUE,4)
                self.txt(x+255,yy+56,"Li-ion → load",8,True,BLUE,"center")
            else:
                self.txt(x+255,yy+35,"—",14,True,MUTED,"center")

            # Visible inter-neighbourhood support.
            if self.last["transfer"][i]>0.01:
                self.box(x+17,yy+80,x+289,yy+101,"#fff7ed","#fff7ed",7)
                self.txt(x+153,yy+90,"← OTHER NB Li-ion SUPPORT",7,True,ORANGE,"center")
            elif self.last["transfer"][i]<-0.01:
                self.box(x+17,yy+80,x+289,yy+101,"#fff7ed","#fff7ed",7)
                self.txt(x+153,yy+90,"OTHER NB Li-ion →",7,True,ORANGE,"center")

    def chart(self,x,y,w,h,title,data,color,maximum=None):
        self.box(x,y,x+w,y+h,WHITE,BORDER,10)
        self.txt(x+12,y+10,title,10,True)
        if not data:return
        mx=maximum or max(data+[1])
        px=x+28;py=y+32;pw=w-42;ph=h-48
        self.c.create_line(px,py+ph,px+pw,py+ph,fill=GRID)
        self.c.create_line(px,py,px,py+ph,fill=GRID)
        pts=[]
        n=len(data)
        for i,v in enumerate(data):
            xx=px+(i/max(1,n-1))*pw
            yy=py+ph-(v/mx)*ph
            pts.extend([xx,yy])
        if len(pts)>=4:self.c.create_line(*pts,fill=color,width=2,smooth=True)

    def charts(self):
        # Compact live charts matching the reference dashboard.
        y=823;h=196
        self.chart(5,y,390,h,"Total Solar Generation (MW)",
                   [sum(self.last["solar"])+self.last["ground"]]*2,ORANGE,40)
        self.chart(402,y,390,h,"Total Demand (MW)",
                   [sum(self.last["demand"])]*2,RED,30)
        self.chart(799,y,390,h,"CCES State of Charge (MWh)",
                   [self.cces],GREEN,80)
        self.chart(1196,y,394,h,"Total Li-ion State of Charge (MWh)",
                   [sum(self.bat)],BLUE,20)

    def time_string(self):
        h=int(self.sim_time);m=int((self.sim_time-h)*60)
        ap="AM" if h<12 else "PM";dh=h%12 or 12
        return f"{dh}:{m:02d} {ap}"

    def loop(self):
        if self.running:self.step();self.redraw()
        self.root.after(250,self.loop)


if __name__=="__main__":
    root=tk.Tk()
    App(root)
    root.mainloop()
