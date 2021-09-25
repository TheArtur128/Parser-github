from github_parser import *

Users = []

while True:
    action = input("\n1. Parse github page\n2. Save all users to json\n3. Save a specific user\n4. Exit\n\> ").strip()
    if action == "1":
        while True:
            try:
                url = input("\nEnter the URL of the github page or stop to stop \> ")
                if url == "stop":
                    break
                else:
                    Users.append(Github_User(url))
            except:
                print(f"\nFailed to parse github data from url \"{url}\"")

    elif action == "2":
        print("")
        for user in Users:
            user.save_instances()
            Users.remove(user)

    elif action == "3":
        if len(Users) > 0:
            try:
                index = int(input(f"\n{Users}\nEnter the index of the desired item \> "))
                Users[index].save_instances()
                Users.remove(Users[index])
            except Exception as error:
                print(f"\nFailed to save information. More details: {error}")
        else:
            print("\nYou have no parsing data")

    elif action == "4":
        break

    else:
        print("\nThere is no such command")
