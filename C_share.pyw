from Network2 import Server, Client
import Network
import threading
import customtkinter
from PIL import ImageTk, Image
from tkinter import * #type: ignore
from tkinter import filedialog
import os
import sys
from pathlib import Path


BASE_DIR= Path(__file__).resolve().parent
os.chdir(BASE_DIR)


customtkinter.set_default_color_theme("dark-blue")
customtkinter.set_appearance_mode("dark")  

def Resize_image(image, size=(32, 32)):
    image=ImageTk.PhotoImage(file=image, size=size)
    return image


file_types=[
    ['.png', '.jpeg', '.jpg'], 
    ['.mp4'], 
    ['.mp3'], 
    ['.exe', '.txt', '.dll', '.log'], ]

type_dict={
    0 : f"{BASE_DIR}\icons\\image.png",
    1 : f"{BASE_DIR}\icons\\video.png",
    2 : f"{BASE_DIR}\icons\\audio.png",
    3 : f"{BASE_DIR}\icons\\file.png",
    4 : f"{BASE_DIR}\icons\\file2.png"
    }

class Message:
    def __init__(self, user, master, message, index, message_list:list, admin=False):
        self.message = message
        self.user = user
        self.admin = admin
        
        self.message_list=message_list
        self.message_list.append([self.user, self.message])

        self.index=index

        separator=customtkinter.CTkFrame(master, width=500, height=5)
        separator.grid(row=self.index, column=1)
        self.mainframe = customtkinter.CTkFrame(master, width=400, border_width=2)
        self.User_label=customtkinter.CTkLabel(self.mainframe, text=self.user, width=150, anchor=W)
        self.Message_label=customtkinter.CTkLabel(self.mainframe, text=self.message, width=400, wraplength=390, anchor=W)

        if self.admin:
            self.mainframe.configure(fg_color='#059e05')
            self.User_label.configure(fg_color='#035803')
            self.Message_label.configure(fg_color='#035803')
            self.mainframe.grid(row=self.index+1, column=1, sticky=E)
        
        else:
            self.mainframe.configure(fg_color='#404140')
            self.User_label.configure(fg_color='#292b29')
            self.Message_label.configure(fg_color='#292b29')
            self.mainframe.grid(row=self.index+1, column=1, sticky=W)

        self.User_label.grid(row=1, column=1, sticky=W)
        self.Message_label.grid(row=2, column=1, sticky=W)
      
class User:
    def __init__(self, master, index, name:str, Type:str, User_dict:dict, admin=False) -> None:
        self.master = master
        self.name = name
        self.index = index
        self.Type = Type
        self.User_dict = User_dict

        self.mainframe = customtkinter.CTkFrame(self.master, width=500)
        self.Id=customtkinter.CTkLabel(self.mainframe, text=self.index, width=20)
        self.Image=customtkinter.CTkLabel(self.mainframe, text='', bg_color='#141414', width=32, height=32)
        self.name_label = customtkinter.CTkLabel(self.mainframe, text=f"  {self.name}", width=398, height=35, anchor=W)
        self.host_frame=customtkinter.CTkFrame(self.mainframe, width=70)
        self.dot=customtkinter.CTkFrame(self.host_frame, width=10, height=10, border_width=2, fg_color='#00f529')
        self.host_label= customtkinter.CTkLabel(self.host_frame, text='  Host  ', text_color='#e6ff06')

    def __repr__(self) -> str:
        return self.name

    def Create(self):
        self.mainframe.grid(row=self.index, column=1, sticky=W)  
        self.Id.grid(row=1, column=0)
        self.Image.grid(row=1, column=1)
        self.name_label.grid(row=1, column=2)

        if self.Type == 'host':
            self.Host()
        else:
            self.Client()

        self.User_dict[self.name] = self
        
    def Host(self):
        self.Type = 'host'
        self.host_frame.grid(row=1, column=3, sticky=E)
        self.dot.grid(row=1, column=1, sticky=W)
        self.host_label.grid(row=1, column=2)
        self.Image.configure(image = Resize_image(f"{BASE_DIR}\icons\\user.png", (24, 24)))

    def Client(self):
        self.Type = 'client'
        self.host_label.grid_forget()
        self.dot.grid_forget()
        self.host_frame.grid_forget()
        self.Image.configure(image = Resize_image(f"{BASE_DIR}\icons\\user4.png", (24,24)))

    def Update(self, text):
        del self.User_dict[self.name]

        self.name=text
        self.name_label.configure(text=self.name)
        self.User_dict[self.name] = self

    def Delete(self):
        self.mainframe.destroy()
        del self.User_dict[self.name]

class Files:
    def __init__(self, master, index, name:str, main_dict:dict) -> None:
        self.location = name
        
        name.replace("/", "\\") 
        x=name.rfind("/")
        self.name= name[x+1:]
        self.image = None
        self.main_dict = main_dict

        self.Create_image()

        self.mainframe = customtkinter.CTkFrame(master)
        self.mainframe.grid(row = index, column=0, sticky=W)

        self.image_label = customtkinter.CTkLabel(self.mainframe, text='', image=Resize_image(self.image, (24, 24)),width=32, height=32)
        self.image_label.grid(row=1, column=1)

        self.name_frame = customtkinter.CTkFrame(self.mainframe, width=440, height=32)
        self.name_frame.grid(row=1, column=2)
        self.name_label = customtkinter.CTkLabel(self.name_frame, text=self.name, width=440, height=32, anchor=W)
        self.name_label.grid(row = 1, column=1)

        self.close_btn=customtkinter.CTkButton(self.mainframe, text='X', command=self.Delete, width=30, height=30)
        self.close_btn.grid(row=1, column=3)

        self.main_dict[self.name] = self


    def __repr__(self) -> str:
        return self.name

    def Create_image(self):
        for index, types in enumerate(file_types):
            for file in types:
                if file in self.name:
                    self.image = type_dict[index]
                    return
                
        if self.image == None:
            self.image = type_dict[4]

    def Delete(self):
        self.mainframe.destroy()
        self.main_dict.pop(self.name)

class App:
    def __init__(self) -> None:
        self.username= Network.socket.gethostname()
        self.enabled_color='#4043ce'
        self.disabled_color='#1d1e63'
        self.status = ""
        self.path = str(BASE_DIR) + "\\"
        self.message_index = 1
        self.file_index = 0
        self.files={}
        self.Users={}
        self.Message_list=[]

        self.server_client = Client(self.username, self.Message_func, self.File_func, self.Users_func)

    def Update(self):
        self.Files_label.configure(text=f"Files: {len(self.files)}")
        self.Client_label.configure(text=f"Users: {len(self.Users)}")
        self.Status.configure(text = self.status)

        if self.server_client.connected:
            self.status = self.server_client.status
        
        if len(self.files) == 0:
            self.file_send_btn.grid_forget()
        else:
            self.file_send_btn.grid(row=3, column=1, sticky=SE)

        self.window.after(1000, self.Update)
 
    def User_message_func(self):
        text=self.chat_entry.get()
        
        Message(self.user.name, self.chat_data, text, self.message_index, self.Message_list, True)
        self.message_index += 2

        if self.server_client.active == 'server':
            for user in self.server_client.Users:
                self.server_client.Send(user, 'chat', text)

        else:
            self.server_client.Send(self.username, 'chat', text)

    def Message_func(self, user, message):
        Message(user, self.chat_data, message, self.message_index, self.Message_list)
        self.message_index += 2

    def Send_file(self):
        thread = threading.Thread(target=self.Send)
        thread.start()

    def Send(self):
        
        data=list(self.files.values())
        
        file_t=data[self.file_index]

        with open(file_t.location, 'rb') as file:
            data= file.read()
            
            if self.server_client.active == 'server':
                for user in self.server_client.Users:
                    self.server_client.Send(user, 'file', data, file_t.name)

            else:
                self.server_client.Send(self.username, 'file', data, file_t.name)
            file.close()

        if self.file_index + 1 >= len(self.files):
            self.file_index = 0
            return

        else:
            self.file_index += 1
            self.window.after(1000, self.Send_file)                

    def File_func(self, user, filenm:str, data, Recv=True):
        filename = self.path  + filenm

        if Recv:
            datafile=Files(self.Files_Sframe, (len(self.files) + 1), filenm, self.files)
            self.files[filenm] = datafile

        if not Recv:

            with open(filename, 'wb') as file:
                file.write(data)
                file.close()

            self.status = "Successfully recieved the file"
        
    def Browse(self):
        if len(self.files) != 0:

            while len(self.files) != 0:
                data = list(self.files.values())
                files:Files = data[0]
                files.Delete()
 
            self.files.clear()

        find=filedialog.askopenfiles(title="Files to Send") 

        if len(find) == 0:
            return
        
        for file in find:
            file=Files(self.Files_Sframe, (len(self.files) + 1), file.name, self.files)
            self.files[file.name] = file

    def Users_func(self, user, Type = 'Client', Delete = False):
        if Delete:
            data:User = self.Users[user]
            data.Delete()
            return
        
        if not Delete:
            data = User(self.client_frame, len(self.Users) + 1, user, Type, self.Users)
            data.Create()
            if Type == 'Server':
                data.Host()            

    def Bluetooth(self, Type:str):
        if Type == 'host':
            self.bluetooth.configure(state='disabled', fg_color=self.disabled_color)
            self.bluetooth_connect.configure(state='normal', fg_color=self.enabled_color)
            self.hotspot.configure(state='normal', fg_color=self.enabled_color)
            self.hotspot_connect.configure(state='normal', fg_color=self.enabled_color)
        
        else:
            self.bluetooth_connect.configure(state='disabled', fg_color=self.disabled_color)
            self.bluetooth.configure(state='normal', fg_color=self.enabled_color)      
            self.hotspot.configure(state='normal', fg_color=self.enabled_color)
            self.hotspot_connect.configure(state='normal', fg_color=self.enabled_color)
        
        pass

    def Wireless(self, Type:str):
        if Type == 'host':
            self.hotspot.configure(state='disabled', fg_color=self.disabled_color)
            self.hotspot_connect.configure(state='normal', fg_color=self.enabled_color)
            self.bluetooth.configure(state='normal', fg_color=self.enabled_color)
            self.bluetooth_connect.configure(state='normal', fg_color=self.enabled_color)

            if self.server_client.client:
                self.server_client.Close_client()

            self.server_client =Server(self.username, self.Message_func, self.File_func, self.Users_func)

            self.server_client.Server_start()
            self.status= self.server_client.status
            self.user.Host()
        
        else:
            self.hotspot_connect.configure(state='disabled', fg_color=self.disabled_color)

            self.hotspot.configure(state='normal', fg_color=self.enabled_color)
            self.bluetooth_connect.configure(state='normal', fg_color=self.enabled_color)
            self.bluetooth.configure(state='normal', fg_color=self.enabled_color) 

            if self.server_client.server:
                self.server_client.Close_server()
            self.server_client =Client(self.username, self.Message_func, self.File_func, self.Users_func)

            self.server_client.Client_connect()
            self.status= self.server_client.status
            self.user.Client()  

    def Detail_update(self, text, path):
        self.small_window.destroy()
        self.username = text
        self.user_detail.configure(text=self.username)
        self.user.Update(text)
        self.server_client.name = text
        if path != "":
            self.path=path + "\\"

    def Detail_update_window(self):
        self.small_window = customtkinter.CTkToplevel()
        self.small_window.attributes("-topmost", True)
        self.small_window.bell()

        name_label = customtkinter.CTkLabel(self.small_window, text="Username")
        name_label.grid(row = 1, column = 1)
        name_entry=customtkinter.CTkEntry(self.small_window, placeholder_text= "Enter your username", width=200)
        name_entry.grid(row=1, column=2)
        
        path_label = customtkinter.CTkLabel(self.small_window, text="Save Path")
        path_label.grid(row = 2, column = 1)
        path_entry =customtkinter.CTkEntry(self.small_window, placeholder_text="Enter recieved-files folder path", width=200)
        path_entry.grid(row=2, column=2)

        save_btn = customtkinter.CTkButton(self.small_window, text="Save", command=lambda:self.Detail_update(name_entry.get(), path_entry.get()))
        save_btn.grid(row=3, column=1, columnspan = 2, sticky = S)

    def Create(self):
        self.window = customtkinter.CTk()
        self.window.resizable(False, False)

        self.user_frame =customtkinter.CTkFrame(self.window, width=1050, height=100)
        self.user_frame.grid(row=1, column=1, columnspan=2)

        self.user_detail = customtkinter.CTkLabel(self.user_frame, text=self.username, width=950, height=100, anchor=W, font=('Cabri', 30))
        self.user_detail.grid(row=1,rowspan=2 , column=1)

        self.Update_details_btn = customtkinter.CTkButton(self.user_detail, text="Update", command=self.Detail_update_window)
        self.Update_details_btn.grid(row=1, column=1, sticky=NE)

        self.hotspot=customtkinter.CTkButton(self.user_frame, text="", image=Resize_image(f"{BASE_DIR}\icons\hotspot2.png"), fg_color=self.enabled_color, command=lambda:self.Wireless('host'), width=50, height=50)
        self.hotspot.grid(row=1, column=2, sticky=E)

        self.hotspot_connect=customtkinter.CTkButton(self.user_frame,  text="", image=Resize_image(f"{BASE_DIR}\icons\wifi2.png"), fg_color=self.enabled_color, command=lambda:self.Wireless('recv'), width=50, height=50)
        self.hotspot_connect.grid(row=1, column=3, sticky=E)

        self.bluetooth=customtkinter.CTkButton(self.user_frame,  text="",  fg_color=self.enabled_color, command=lambda:self.Bluetooth('host'), width=50, height=50, state='disabled')
        self.bluetooth.grid(row=2, column=2, sticky=E)
        
        self.bluetooth_connect=customtkinter.CTkButton(self.user_frame,  text="", fg_color=self.enabled_color, command=lambda:self.Bluetooth('recv'), width=50, height=50, state='disabled')
        self.bluetooth_connect.grid(row=2, column=3, sticky=E)

        self.client_frame=customtkinter.CTkScrollableFrame(self.window, fg_color='#141414', width=500, height=200)
        self.client_frame.grid(row=2, column=1)

        self.Client_label=customtkinter.CTkLabel(self.client_frame, text='Users', width=500, fg_color='#313131')
        self.Client_label.grid(row=0,column=1)

        self.chat_frame=customtkinter.CTkFrame(self.window, width=500, height=200)
        self.chat_frame.grid(row=3, column=1)

        self.chat_entry=customtkinter.CTkEntry(self.chat_frame, width=470, height=32, placeholder_text="Chat here...")
        self.chat_entry.grid(row=0, column=1)

        self.Chat_send_btn=customtkinter.CTkButton(self.chat_frame, image=Resize_image(f"{BASE_DIR}\icons\chat.png"), width=32, height=32, text='', fg_color=self.enabled_color, command=self.User_message_func)
        self.Chat_send_btn.grid(row=0, column=2, columnspan=2)

        self.chat_data=customtkinter.CTkScrollableFrame(self.chat_frame, width=500, height=168)
        self.chat_data.grid(row=1, column=1, columnspan=2)

        self.Files_frame=customtkinter.CTkFrame(self.window, fg_color='#141414', width=500, height=400)
        self.Files_frame.grid(row=2, rowspan=2, column=2)

        self.Files_label=customtkinter.CTkLabel(self.Files_frame, text='Files', width=500)
        self.Files_label.grid(row=1,column=1)

        self.Browse_btn=customtkinter.CTkButton(self.Files_frame, text="Browse", fg_color=self.enabled_color, command=self.Browse)
        self.Browse_btn.grid(row=2, column=1)

        self.Files_Sframe=customtkinter.CTkScrollableFrame(self.Files_frame, fg_color='#141414', width=500, height=350)
        self.Files_Sframe.grid(row=3, column=1)

        self.file_send_btn=customtkinter.CTkButton(self.Files_frame, text='', image=Resize_image(f"{BASE_DIR}\icons\send.png"), width=40, height=40, command=self.Send_file)
        self.file_send_btn.grid(row=3, column=1, sticky=SE)

        self.Status=customtkinter.CTkLabel(self.window, text='', width=1050, height=20, anchor=W)
        self.Status.grid(row=4, column=1, columnspan=2)

        

        #_______Functions__________#
        self.user=User(self.client_frame, 1, self.username, 'client', self.Users, True)
        self.user.Create()

        self.window.protocol("WM_DELETE_WINDOW", self.App_exit)

        self.Update()

        self.window.mainloop()
    
    def App_exit(self):
        self.window.destroy()
        os._exit(0)

App().Create()