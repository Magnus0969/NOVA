from Frontend.GUI import(
    GraphicUserInterface, SetAssistantStatus,
    ShowTextToScreen, TempDirectoryPath,
    SetMicStatus, AnswerModifier,
    QueryModifier, GetAssistantStatus,
    GetMicStatus)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognizer
from Backend.Chatbot import Chatbot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
import os
from time import sleep
import subprocess
import json
import threading

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = "NOVA"  # Set assistant name directly

DefaultMessage= f'''{Username}: Hello {Assistantname}, How are you?
{Assistantname}: Hello {Username}! I am fine, thank you! How can I assist you today?'''

subprocess= []
Functions= ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultMessageIfNoChats():
    File = open(r'Data\ChatLog.json', 'r', encoding='utf-8')
    if len(File.read())<5:
        with open(TempDirectoryPath('Database.data'),'w',encoding='utf-8') as file:
            file.write('')
        
        with open(TempDirectoryPath('Responses.data'),'w',encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLog():
    with open(r"Data\ChatLog.json", 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLog()
    formatted_chatlog=''
    for entry in json_data:
        if entry['role'] == 'user':
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry['role'] == 'assistant':
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    
    formatted_chatlog= formatted_chatlog.replace("User",Username + " ")
    formatted_chatlog= formatted_chatlog.replace("Assistant",Assistantname + " ")

    with open(TempDirectoryPath("Database.data"), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    File= open(TempDirectoryPath("Database.data"), 'r', encoding='utf-8')
    Data= File.read()
    if len(str(Data))>0:
        lines= Data.split("\n")
        result= '\n'.join(lines)
        File.close()
        File= open(TempDirectoryPath("Responses.data"), 'w', encoding='utf-8')
        File.write(result)
        File.close()

def InitialExecution():
    SetMicStatus("False")
    ShowTextToScreen("")
    ShowDefaultMessageIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def MainExecution():
    TaskExecution= False
    ImageExecution= False
    ImageGenerationQuery= ""

    SetAssistantStatus("Listening...")
    Query= SpeechRecognizer()
    ShowTextToScreen(f"{Username}: {Query}")
    SetAssistantStatus("Processing...") #Thinking...
    Desicion= FirstLayerDMM(Query)

    print("")
    print(f"Decision: {Desicion}")
    print("")

    Gen_Q = any([i for i in Desicion if i.startswith("general")])
    Real_Q = any([i for i in Desicion if i.startswith("realtime")])

    Merged_Q = "and".join(
        [" ".join(i.split()[1:]) for i in Desicion if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Desicion:
        if "generate" in queries:
            ImageGenerationQuery= str(queries)
            ImageExecution= True
    
    for queries in Desicion:
        if TaskExecution== False:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Desicion)))
                TaskExecution= True
    
    if ImageExecution== True:
        
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery}, True")
        
        try:
            p1= subprocess.Popen(["python",r"Backend\ImageGeneration.py"],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE, shell=False)
            subprocess.append(p1)
        
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")
    
    if Gen_Q and Real_Q or Real_Q:
        SetAssistantStatus("Searching...")
        Answer= RealtimeSearchEngine(QueryModifier(Merged_Q))
        ShowTextToScreen(f"{Assistantname}: {Answer}")
        SetAssistantStatus("Speaking...") #Answering...
        TextToSpeech(Answer)
        return True
    
    else:
        for Queries in Desicion:
            if "general" in Queries:
                SetAssistantStatus("Processing...") #Thinking...
                QueryFinal= Query.replace("general", "")
                Answer= Chatbot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Speaking...") #Answering...
                TextToSpeech(Answer)
                return True
            
            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal= Query.replace("realtime", "")
                Answer= RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Speaking...")
                TextToSpeech(Answer)
                return True
            
            elif "exit" in Queries:
                QueryFinal= "Okay, Bye!"
                Answer= Chatbot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Speaking...") #Answering...
                TextToSpeech(Answer)
                SetAssistantStatus("Exiting...")
                os._exit(1)

def FirstThread():
    while True:
        Current_Mic_Status = GetMicStatus()
        if Current_Mic_Status == "True":
            MainExecution()
        else:
            AI_Status= GetAssistantStatus()
            
            if "Available... "  in AI_Status:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")

def SecondThread():

    GraphicUserInterface()

if __name__=="__main__":
    # Create threads
    thread2= threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()