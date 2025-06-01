import json
import os
# RabbitMQ imports (assuming they are correct and use their own naming conventions)
from messageService import MessageService 
from rabbitmq.fanoutProducer import sendAnuncio 
from rabbitmq.topicProducer import sendProyecto 

# Azure Service Bus imports
from azureMicrosoft.directProducer import sendTaskOrResponse # Corrected import

from dotenv import load_dotenv
from multiprocessing import Process, Event
from datetime import datetime

load_dotenv()

USERS_FILE = "users.json" # Constants often an exception to camelCase, but can be user_file if strict

# Context for the Azure consumer of the current user
currentAzureConsumerContext = {
    "process": None,
    "stopEvent": None
}

# --- User Management Functions ---
def loadUsers():
    """Loads registered users from the JSON file."""
    if not os.path.exists(USERS_FILE):
        print(f"Warning: {USERS_FILE} not found. No users can be loaded.")
        return [] # Return empty list if file doesn't exist
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {USERS_FILE}.")
        return []
    except Exception as e:
        print(f"Error loading users: {e}")
        return []


def saveUsers(usersList):
    """Saves users to the JSON file."""
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(usersList, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving users: {e}")

def loginUser(): # Renamed from login
    """Handles user login."""
    usersList = loadUsers()
    if not usersList:
        print("No user data available for login.")
        return None
        
    print("=== Login ===")
    userNameInput = input("User: ").strip()
    passwordInput = input("Password: ").strip()

    for userData in usersList:
        if userData.get("username") == userNameInput and userData.get("password") == passwordInput: # Added .get for safety
            print(f"\nWelcome {userData['username']}! Role: {userData['role']}, Group: {userData['group']}\n")
            return userData
    print("Invalid credentials.\n")
    return None

def createUser():
    """Creates a new user (admin only)."""
    print("=== Create New User ===")
    newUserName = input("New username: ").strip()
    newUserPassword = input("Password: ").strip()
    newUserRole = input("Role (admin/profesor/estudiante): ").strip().lower()
    newUserGroup = input("Group (e.g., group1, math_teachers, etc.): ").strip().lower()

    usersList = loadUsers()
    if any(u.get("username") == newUserName for u in usersList):
        print("Username already exists.\n")
        return

    usersList.append({
        "username": newUserName,
        "password": newUserPassword,
        "role": newUserRole,
        "group": newUserGroup
    })
    saveUsers(usersList)
    print("User created successfully.\n")

def viewUsers():
    """Displays all registered users."""
    usersList = loadUsers()
    print("=== User List ===")
    if not usersList:
        print("No users to display.")
        return
    for userData in usersList:
        print(f" {userData.get('username')} | Role: {userData.get('role')} | Group: {userData.get('group')}")
    print()

# --- Azure Consumer Management ---
def startCurrentUserAzureConsumer(userName):
    """Starts the Azure consumer for the current user in a separate process."""
    if currentAzureConsumerContext["process"] is None:
        # Local import for multiprocessing compatibility
        from azureMicrosoft.directConsumer import startAzureTaskConsumer 
        
        currentAzureConsumerContext["stopEvent"] = Event()
        currentAzureConsumerContext["process"] = Process(
            target=startAzureTaskConsumer,
            args=(userName, currentAzureConsumerContext["stopEvent"])
        )
        currentAzureConsumerContext["process"].start()
        print(f"Azure task/response receiver started for {userName}.")
    else:
        print(f"Azure task/response receiver is already active for {userName}.")

def stopCurrentUserAzureConsumer():
    """Stops the Azure consumer for the current user."""
    if currentAzureConsumerContext["stopEvent"]:
        print("Sending stop signal to Azure receiver...")
        currentAzureConsumerContext["stopEvent"].set()
    
    if currentAzureConsumerContext["process"]:
        currentAzureConsumerContext["process"].join(timeout=7) 
        if currentAzureConsumerContext["process"].is_alive():
            print("Azure receiver did not terminate in time, forcing termination...")
            currentAzureConsumerContext["process"].terminate()
            currentAzureConsumerContext["process"].join() 
        print("Azure task/response receiver stopped.")
        currentAzureConsumerContext["process"] = None
        currentAzureConsumerContext["stopEvent"] = None

# --- Azure Message Handling (Display) ---
def listUserAzureMessages(userName, messageTypeFilter=None, showContent=False):
    """Lists saved messages for the user from JSON files."""
    messageDir = f"user_messages/{userName}"
    if not os.path.exists(messageDir):
        print("You have no saved messages/tasks.")
        return []

    messagesList = []
    print(f"\n=== Messages/Tasks for {userName} (Azure SB) ===")
    
    try:
        fileNames = sorted(
            [f for f in os.listdir(messageDir) if f.endswith(".json")],
            key=lambda x: x.split('_')[1] + x.split('_')[2].split('.')[0] if '_' in x and x.count('_') >= 2 else x,
            reverse=True 
        )
    except Exception: 
        fileNames = [f for f in os.listdir(messageDir) if f.endswith(".json")]

    foundMessages = False
    for fileName in fileNames:
        if messageTypeFilter and not fileName.startswith(messageTypeFilter):
            continue
        try:
            with open(os.path.join(messageDir, fileName), "r", encoding="utf-8") as f:
                messageData = json.load(f)
                messagesList.append(messageData)
                
                print(f"  ----------------------------------")
                print(f"  From: {messageData.get('fromUser', 'N/A')}")
                print(f"  Subject: {messageData.get('title', 'N/A')}")
                print(f"  Type: {messageData.get('type', 'N/A')}")
                timestampString = messageData.get('timestamp', '')
                if timestampString:
                    try:
                        print(f"  Date: {datetime.fromisoformat(timestampString).strftime('%d-%m-%Y %H:%M:%S')}")
                    except ValueError:
                        print(f"  Date: {timestampString} (unrecognized format)")
                else:
                    print(f"  Date: N/A")

                if showContent:
                    print(f"  Content: {messageData.get('content', 'N/A')}")
                else:
                     print(f"  Content: {messageData.get('content', 'N/A')[:60]}...")
                foundMessages = True
        except Exception as e:
            print(f"Error reading message {fileName}: {e}")

    if not foundMessages:
        print("No messages found" + (f" of type '{messageTypeFilter}'." if messageTypeFilter else "."))
    print("  ----------------------------------\n")
    return messagesList

# --- Main Menu Logic ---
def userMenu(currentUser): # Renamed from menu
    """Displays the menu based on the user's role."""
    # Start RabbitMQ services (existing logic)
    rabbitMqService = MessageService() # Changed variable name
    rabbitMqService.startForUser(currentUser["username"], currentUser["role"], currentUser["group"])

    # Start Azure consumer for this user
    startCurrentUserAzureConsumer(currentUser["username"])

    while True:
        print(f"\n--- Menu {currentUser['role']}: {currentUser['username']} ---")
        # Admin Menu
        if currentUser["role"] == "admin":
            print("1. Create User")
            print("2. View All Users")
            print("3. Send General Announcement (RabbitMQ Fanout)")
            print("4. Assign Task to User (Azure SB)")
            print("5. Publish Project by Group/Role (RabbitMQ Topic)")
            print("6. View My Received Messages/Tasks (Azure SB)")
            print("0. Logout")
            option = input("Select option: ").strip()

            if option == "1": createUser()
            elif option == "2": viewUsers()
            elif option == "3": # RabbitMQ
                announcementMessage = input("General announcement message: ")
                sendAnuncio(announcementMessage) # Assumes sendAnuncio is correct
                print("Announcement sent.\n")
            elif option == "4": # Azure SB - Assign Task
                recipientUser = input("Recipient username: ").strip()
                taskTitle = input("Task title: ")
                taskContent = input("Task message: ")
                sendTaskOrResponse(
                    fromUser=currentUser["username"],
                    toUser=recipientUser,
                    title=taskTitle,
                    content=taskContent,
                    messageType="task_assignment"
                )
            elif option == "5": # RabbitMQ
                topicRoutingKey = input("Routing key (e.g., role.group or #.group1): ")
                projectMessageContent = input("Project message: ")
                sendProyecto(topicRoutingKey, projectMessageContent) # Assumes sendProyecto is correct
                print("Project sent.\n")
            elif option == "6": # Azure SB - View messages
                listUserAzureMessages(currentUser["username"], showContent=True)
            elif option == "0": break
            else: print("Invalid option.\n")

        # Professor Menu
        elif currentUser["role"] == "profesor":
            print("1. Assign Task to Student (Azure SB)")
            print("2. View My Received Messages/Tasks (Azure SB)")
            print("3. Respond to a Message (Azure SB)")
            print("0. Logout")
            option = input("Select an option: ").strip()

            if option == "1": # Azure SB - Assign Task
                recipientStudent = input("Recipient student username: ").strip()
                taskTitle = input("Task title: ")
                taskDescription = input("Task description: ")
                sendTaskOrResponse(
                    fromUser=currentUser["username"],
                    toUser=recipientStudent,
                    title=taskTitle,
                    content=taskDescription,
                    messageType="task_assignment"
                )
            elif option == "2": # Azure SB - View messages
                listUserAzureMessages(currentUser["username"], showContent=True)
            elif option == "3": # Azure SB - Respond
                print("To respond, you need to know who sent you the original message.")
                responseRecipient = input("User to respond to (original sender): ").strip()
                originalMessageSubject = input("Subject of the original message (for reference): ").strip()
                responseContent = input("Your response content: ")
                sendTaskOrResponse(
                    fromUser=currentUser["username"],
                    toUser=responseRecipient,
                    title=f"Re: {originalMessageSubject}",
                    content=responseContent,
                    messageType="task_response"
                    # originalTaskId could be added here if known/retrieved
                )
            elif option == "0": break
            else: print("Invalid option.\n")

        # Student Menu
        elif currentUser["role"] == "estudiante":
            print("1. View My Tasks/Messages (Azure SB)")
            print("2. Respond to a Task/Message (Azure SB)")
            print("0. Logout")
            option = input("Select option: ").strip()

            if option == "1": # Azure SB - View messages
                viewOnlyTasks = input("View only assigned tasks? (y/N): ").lower() == 'y'
                filterType = "task_assignment" if viewOnlyTasks else None
                listUserAzureMessages(currentUser["username"], messageTypeFilter=filterType, showContent=True)
            
            elif option == "2": # Azure SB - Respond
                print("Listing your assigned tasks to help you respond...")
                assignedTasks = listUserAzureMessages(currentUser["username"], messageTypeFilter="task_assignment", showContent=False)
                
                if not assignedTasks:
                    print("You have no assigned tasks to respond to currently.")
                else:
                    responseRecipient = input("Who are you sending this response to (professor/admin who assigned the task)?: ").strip()
                    originalTaskSubject = input("Subject/Title of the task you are responding to: ").strip()
                    responseContent = input("Your response/submission: ").strip()
                    
                    # Find originalTaskId if possible (enhancement)
                    # For now, not sending originalTaskId unless manually input or selected
                    # originalTaskIdToLink = None 
                    # for task in assignedTasks:
                    #    if task.get('title') == originalTaskSubject and task.get('fromUser') == responseRecipient:
                    #        originalTaskIdToLink = task.get('timestamp') # Or a real ID if Azure provides one
                    #        break
                            
                    sendTaskOrResponse(
                        fromUser=currentUser["username"],
                        toUser=responseRecipient,
                        title=f"Response to: {originalTaskSubject}",
                        content=responseContent,
                        messageType="task_response"
                        # originalTaskId=originalTaskIdToLink # Add this if you implement ID linking
                    )
            elif option == "0": break
            else: print("Invalid option.\n")
        
        else: # Unknown role
            print("Unrecognized role. Logging out.")
            break
            
    print("Logging out...")
    # Stop RabbitMQ services
    rabbitMqService.stopAll()
    # Stop Azure consumer
    stopCurrentUserAzureConsumer()
    print("All messaging services stopped. Session closed.\n")

# --- Application Entry Point ---
def main():
    """Main function to run the application."""
    # Ensure user messages directory exists
    os.makedirs("user_messages", exist_ok=True)

    # Attempt to load users to check if USERS_FILE is valid at startup
    if not os.path.exists(USERS_FILE):
         print(f"Critical: {USERS_FILE} does not exist. Please create it with user data or the application cannot login users.")
         # Optionally, create a very basic one or guide the user. For now, it will just fail login.
         # example_users = [{"username": "admin", "password": "admin", "role": "admin", "group": "admin_group"}]
         # saveUsers(example_users)
         # print(f"Created a sample {USERS_FILE} with an admin user.")

    try:
        while True:
            activeUser = None
            while not activeUser: 
                activeUser = loginUser()
                if activeUser is None: 
                    retryLogin = input("Login failed. Retry? (Y/n): ").strip().lower()
                    if retryLogin == 'n':
                        print("Exiting application.")
                        return 
            
            if activeUser:
                userMenu(activeUser) 
            
            continueApp = input("Login as another user or exit application? (L for login / E for exit): ").strip().lower()
            if continueApp == 'e':
                print("Exiting Task Manager application.")
                break 
    finally:
        if currentAzureConsumerContext["process"] and currentAzureConsumerContext["process"].is_alive():
            print("Unexpected application closure detected, attempting to stop Azure receiver...")
            stopCurrentUserAzureConsumer()

if __name__ == "__main__":
    main()