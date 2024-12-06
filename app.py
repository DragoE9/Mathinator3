import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
import utilities as ut
import threading
import sys
import os.path
import pandas
import math

class Logger(object):
    def __init__(self,textbox:ScrolledText):
        self.textbox = textbox
        self.textbox.configure(state="disabled")
             
    def write(self,text:str):
        """Write text to the textbox and scroll it"""
        self.textbox.configure(state="normal")
        self.textbox.insert("end",text)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")
        
    def flush(self):
        """required"""
        pass

class Mathinator:
    def __init__(self,p_window:tk.Tk):
        self.is_running = False
        self.banlist_mode = tk.StringVar()
        self.clear_mode = tk.StringVar()
        
        #Widget Building Here
        self.window = p_window
        self.window.title("Mathinator3")
        label1 = tk.Label(self.window,text="UserAgent: ")
        self.user = tk.Entry(self.window)
        label2 = tk.Label(self.window,text="Target Region: ")
        self.target = tk.Entry(self.window)
        dump_button = tk.Button(self.window,text="Download Nations Data",command=self.dump_init)
        officer_button = tk.Button(self.window,text="Check ROs",command=self.officer_check)
        table_button = tk.Button(self.window,text="Prepare Regiontable",command=self.regiontable_init)
        label3 = tk.Label(self.window,text="----  Banlist Creators: ----")
        self.log = ScrolledText(self.window,height=5,width=120)
        banmode1 = tk.Radiobutton(self.window,text="By Influence",value="inf",variable=self.banlist_mode)
        banmode2 = tk.Radiobutton(self.window,text="WA Focus",value="wa",variable=self.banlist_mode)
        banmode3 = tk.Radiobutton(self.window,text="Efficiency Weighted",value="ef",variable=self.banlist_mode)
        banlist_button = tk.Button(self.window,text="Make Banlist",command=self.banlistinator)
        label4 = tk.Label(self.window,text="----  Region Clearing: ----")
        clearmode1 = tk.Radiobutton(self.window,text="Dirty",value="dirty",variable=self.clear_mode)
        clearmode2 = tk.Radiobutton(self.window,text="With Password",value="pass",variable=self.clear_mode)
        clearmode3 = tk.Radiobutton(self.window,text="With Transition",value="trans",variable=self.clear_mode)
        clear_button = tk.Button(self.window,text="Clear The Region",command=self.empty)

        
        #Now Grid Them
        label1.grid(row=0,column=0,padx=(100,10),pady=(10,10))
        self.user.grid(row=0,column=1,padx=(10,10),pady=(10,10))
        label2.grid(row=1,column=0,padx=(100,10),pady=(10,10))
        self.target.grid(row=1,column=1,padx=(10,10),pady=(10,10))
        dump_button.grid(row=2,column=0,padx=(100,10),pady=(10,10))
        table_button.grid(row=2,column=1,padx=(10,10),pady=(10,10))
        officer_button.grid(row=2,column=2,padx=(10,100),pady=(10,10))
        label3.grid(row=3,column=0,columnspan=3,padx=(100,100),pady=(10,10))
        banmode1.grid(row=4,column=0,padx=(100,10),pady=(10,10))
        banmode2.grid(row=4,column=1,padx=(10,10),pady=(10,10))
        banmode3.grid(row=4,column=2,padx=(10,100),pady=(10,10))
        banlist_button.grid(row=5,column=1,padx=(10,10),pady=(10,10))
        label4.grid(row=6,column=0,columnspan=3,padx=(100,100),pady=(10,10))
        clearmode1.grid(row=7,column=0,padx=(100,10),pady=(10,10))
        clearmode2.grid(row=7,column=1,padx=(10,10),pady=(10,10))
        clearmode3.grid(row=7,column=2,padx=(10,100),pady=(10,10))
        clear_button.grid(row=8,column=1,padx=(10,10),pady=(10,10))
        self.log.grid(row=9,column=0,columnspan=3,padx=(100,100),pady=(10,10))
        
        #Redirect the Console Logs to the window
        console = Logger(self.log)
        sys.stdout = console
        sys.stderr = console
        
    def data_dump(self):
        ut.get_data_dump(self.user.get())
        self.is_running = False
        
    def dump_init(self):
        if self.is_running == True:
            print("Please Wait")
            return
        if os.path.isfile("nations.csv"):
            user_response = messagebox.askquestion('File Exists','A nations.csv file already exists in the directory. Are you trying to re-download the latest dump?')
            if user_response == 'no':
                return
        if self.user.get() == "":
            print("Please specify a user agent")
            return
        self.is_running = True
        threading.Thread(target=self.data_dump,daemon=True).start()
        
    def regiontable(self,nations:pandas.DataFrame):
        ut.make_regiontable(nations,self.target.get().lower().replace(" ","_"),self.user.get())
        self.is_running = False
        
    def regiontable_init(self):
        if self.is_running == True:
            print("Please Wait")
            return
        try:
            nations = pandas.read_csv("nations.csv")
        except:
            print("File not found. You have to download the nationdata first.")
        if os.path.isfile("regiontable.csv"):
            user_response = messagebox.askquestion('Overwrite','A file called retiontable.csv already exists in this directory. This will overwrite that file. Proceed?')
            if user_response == 'no':
                return     
        if self.user.get() == "":
            print("Please specify a user agent")
            return
        self.is_running = True
        threading.Thread(target=self.regiontable,daemon=True,args=(nations,)).start()
        
    def officer_check(self):
        if self.is_running == True:
            print("Please Wait")
            return
        try:
            nations = pandas.read_csv("regiontable.csv")
        except:
            print("File not found. You have to create a regiontable first.")
            return None
        
        self.is_running = True
        officer_info = ut.officer_check(self.user.get(),self.target.get().lower().replace(" ","_"),nations)
        
        print("ROs have {} inf (average {:.2f} each) and an average of {:.2f} endorsements per RO.".format(officer_info["INFLUENCENUM"].sum(),officer_info["INFLUENCENUM"].mean(),officer_info["ENDORSEMENTS"].mean()))
        user_response = messagebox.askquestion("Save","Done. Save RO report as a file?")
        if user_response == "yes":
            (officer_info.drop(columns=["UNSTATUS"])).to_csv("RO_report.csv",index=False,header=True)
        self.is_running = False
    
    def banlistinator(self):
        if self.is_running == True:
            print("Please Wait")
            return
        try:
            nations = pandas.read_csv("regiontable.csv")
        except:
            print("File not found. You have to create a regiontable first.")
            return None
        
        self.is_running == True
            
        #Remove any WAs endorsing the delegate from the table
        goodnations = ut.delendos(self.user.get(),self.target.get().lower().replace(" ","_"))
        try:
            nations = nations[(~nations["NAME"].isin(goodnations))]
        except:
            self.is_running == False
            return None
        
        if self.banlist_mode.get() == "inf":
            nations = nations.sort_values(by=["INFLUENCENUM"], ascending=True)
            
        elif self.banlist_mode.get() == "wa":
            nations = nations.sort_values(by=["UNSTATUS","INFLUENCENUM"], ascending=[False,True])
            
        elif self.banlist_mode.get() == "ef":
            nations["EF"] = nations.apply(lambda x: ut.efficiency(x["ENDORSEMENTS"],x["INFLUENCENUM"],x["LASTLOGIN"]), axis=1)
            nations = nations.sort_values(by=["EF"], ascending=False)
            
        else:
            print("Mode not set properly. Defaulting to sort by influence.")
            nations = nations.sort_values(by=["INFLUENCENUM"], ascending=True)
            
        with open("banlist.txt","w") as file:
            for index, row in nations.iterrows():
               file.write("{} - {:n}".format(row["URL"],row["INFLUENCENUM"]))
               file.write("\n")
        print("Done")
        self.is_running == False
    
    def empty(self):
        if self.is_running == True:
            print("Please Wait")
            return
        try:
            nations = pandas.read_csv("regiontable.csv")
        except:
            print("File not found. You have to create a regiontable first.")
            return None
        
        self.is_running = True
        #First. Remove all the ROs for free
        officers = ut.officer_check(self.user.get(),self.target.get().lower().replace(" ","_"),nations)["NAME"]
        nations = nations[(~nations["NAME"].isin(officers))]
        #Next. Assume all pilers ejected. Calculate cost and remove them from the table.
        goodnations = ut.delendos(self.user.get(),self.target.get().lower().replace(" ","_"))
        total_inf = 0
        for piler in goodnations:
            nationinfo = nations.loc[nations["NAME"] == piler]
            if nationinfo.empty:
                continue
            total_inf += math.ceil(nationinfo.iloc[0]["INFLUENCENUM"] * (2/3))
        nations = nations[(~nations["NAME"].isin(goodnations))]
        
        #Only nations to be banned should be left at this point. Asses their total cost
        total_inf += nations["INFLUENCENUM"].sum()
        pass_cost = 40*len(officers)
        
        #Finally, optimize as required
        nations.sort_values(by="INFLUENCENUM", ascending=False)
        
        self.is_running = False
        if self.clear_mode.get() == "trans":
            #Base cost for the transition. 2 WAs in the region (del and 1 RO endorser)
            trans_cost = 160
            i = 0
            for index, row in nations.iterrows():
                if trans_cost >= total_inf/(len(officers) - 1):
                    #Assumes an officer will also save for a password
                    print("Empty the region until {} nations remain. Ban Cost: {}, Password Cost: {}, Transition Cost: {}".format(i+2,total_inf/(len(officers) - 1),(i+2)*40,trans_cost))
                    return
                i += 1
                total_inf -= row["INFLUENCENUM"]
                if row["UNSTATUS"] == "WA Member":
                    trans_cost += 160 #Adding cost for the member, plus the cost of keeping an extra RO in to maintian endos
                    i += 1
                else:
                    trans_cost += 20
        elif self.clear_mode.get() == "pass":
            i = 0          
            for index, row in nations.iterrows():
                #Start moving the password point down the list. Reduce the ban cost accordingly and increase the password cost
                if pass_cost >= total_inf/len(officers):
                    #When the two values cross over is the point of maximum efficiency.
                    print("Empty the region until {} nations remain. Ban Cost: {}. Password Cost: {}".format(i+len(officers),math.ceil(total_inf/len(officers)),pass_cost))
                    return
                i += 1
                total_inf -= (1/3)*row["INFLUENCENUM"]
                pass_cost += 40                 
        else:
            if self.clear_mode.get() != "dirty":
                print("Mode not set properly. Defaulting to Dirty")
            #Just dumb ban everyone - del counts as 2 ROs because of their double efficiency
            print("{} influence to clear the region, {} per RO".format(total_inf,total_inf/(len(officers)+1)))      

root = tk.Tk()
app = Mathinator(root)
root.mainloop()