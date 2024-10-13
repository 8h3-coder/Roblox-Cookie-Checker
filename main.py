import requests
import json
import os
from colorama import Fore, init

init(autoreset=True)

class CookieChecker:
    def __init__(self):
        self.cookies = []
        self.load_cookies()
        self.results = {"hits": 0, "bads": 0, "errors": 0}

    def load_cookies(self):
        """Load cookies from a file and remove duplicates."""
        if os.path.exists("cookies.txt"):
            with open("cookies.txt", "r") as file:
                cookies = [line.strip() for line in file.readlines() if line.strip()]
                self.cookies = list(set(cookies))

            self.display_startup_info(len(cookies), len(self.cookies))

    def display_startup_info(self, total_cookies, unique_cookies):
        """Display startup information."""
        print(f"{Fore.CYAN}Starting Cookie Checker...")
        print(f"{Fore.YELLOW}Total Cookies in file: {total_cookies}")
        print(f"{Fore.GREEN}Unique Cookies after removing duplicates: {unique_cookies}")
        print(f"{Fore.CYAN}{'='*40}\n")

    def check_cookie(self, cookie):
        """Check the validity of a single cookie and gather additional info."""
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        cookies = {
            '.ROBLOSECURITY': cookie
        }

        try:
            user_info_resp = requests.get("https://users.roblox.com/v1/users/authenticated", cookies=cookies, headers=headers)
            
            if user_info_resp.status_code == 200:
                user_info = user_info_resp.json()
                extra_info = self.get_additional_info(cookies)
                
                user_id = user_info.get('id', 'N/A')
                username = user_info.get('name', 'N/A')
                friends_count = extra_info.get('friendsCount', 'N/A')
                description = extra_info.get('description', 'N/A')
                account_created = extra_info.get('created', 'N/A')

                valid_cookie_info = (
                    f"{Fore.GREEN}Valid Cookie!\n"
                    f"User ID: {user_id}\n"
                    f"Username: {username}\n"
                    f"Number of Friends: {friends_count}\n"
                    f"Description: {description}\n"
                    f"Account Created: {account_created}"
                )

                self.save_valid_cookie(cookie)
                return valid_cookie_info

            elif user_info_resp.status_code == 401:
                return f"{Fore.RED}Invalid Cookie! Status Code: {user_info_resp.status_code}"

            else:
                return f"{Fore.YELLOW}Error! Status Code: {user_info_resp.status_code}"

        except requests.RequestException as e:
            return f"{Fore.YELLOW}Error checking cookie: {str(e)}"

    def get_additional_info(self, cookies):
        """Get additional user information such as friends count, description, etc."""
        additional_info = {}

        try:
            friends_resp = requests.get("https://friends.roblox.com/v1/my/friends/count", cookies=cookies)
            if friends_resp.status_code == 200:
                additional_info['friendsCount'] = friends_resp.json().get('count', 0)

            user_resp = requests.get("https://users.roblox.com/v1/users/authenticated", cookies=cookies)
            if user_resp.status_code == 200:
                user_data = user_resp.json()
                additional_info['description'] = user_data.get('description', 'No description available')
                additional_info['created'] = user_data.get('created', 'Unknown')

        except requests.RequestException as e:
            print(f"{Fore.YELLOW}Error getting additional info: {str(e)}")

        return additional_info

    def run(self):
        """Run the cookie checker."""
        for index, cookie in enumerate(self.cookies, start=1):
            print(f"{Fore.CYAN}Checking cookie {index}/{len(self.cookies)}...")
            result = self.check_cookie(cookie)
            print(result)
            self.categorize_result(result)

        self.display_summary()

    def categorize_result(self, result):
        """Categorize results into hits, bads, and errors."""
        if "Valid Cookie" in result:
            self.results["hits"] += 1
        elif "Invalid Cookie" in result:
            self.results["bads"] += 1
        else:
            self.results["errors"] += 1

    def save_valid_cookie(self, cookie):
        """Save valid cookies to a file."""
        with open("valid_cookies.txt", "a") as file:
            file.write(cookie + "\n")

    def display_summary(self):
        """Display a summary of the results."""
        print(f"\n{Fore.CYAN}{'='*40}")
        print(f"{Fore.GREEN}Hits (Valid Cookies): {self.results['hits']}")
        print(f"{Fore.RED}Bads (Invalid Cookies): {self.results['bads']}")
        print(f"{Fore.YELLOW}Errors: {self.results['errors']}")
        print(f"{Fore.CYAN}{'='*40}\n")

if __name__ == "__main__":
    checker = CookieChecker()
    checker.run()
