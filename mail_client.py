import requests
import json
import time
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from datetime import datetime

class MailGwClient:
    def __init__(self):
        self.base_url = "https://api.mail.gw"
        self.token = None
        self.email = None
        self.password = None
        self.console = Console()

    def get_domains(self):
        """Get available email domains"""
        response = requests.get(f"{self.base_url}/domains")
        if response.status_code == 200:
            domains = response.json()
            return domains.get("hydra:member", [])[0].get("domain")
        return None

    def create_account(self):
        """Create a new email account"""
        domain = self.get_domains()
        if not domain:
            self.console.print("[red]No domains available[/red]")
            return False

        import random
        import string
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        self.email = f"{username}@{domain}"
        self.password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        data = {
            "address": self.email,
            "password": self.password
        }

        response = requests.post(
            f"{self.base_url}/accounts",
            json=data
        )

        if response.status_code == 201:
            self.console.print(f"[green]Account created successfully![/green]")
            self.console.print(f"Email: {self.email}")
            self.console.print(f"Password: {self.password}")
            return True
        else:
            self.console.print("[red]Failed to create account[/red]")
            return False

    def login(self):
        """Login to the email account"""
        if not self.email or not self.password:
            self.console.print("[red]No account credentials available[/red]")
            return False

        data = {
            "address": self.email,
            "password": self.password
        }

        response = requests.post(
            f"{self.base_url}/token",
            json=data
        )

        if response.status_code == 200:
            self.token = response.json().get("token")
            return True
        return False

    def get_messages(self):
        """Get all messages from inbox"""
        if not self.token:
            self.console.print("[red]Not logged in[/red]")
            return []

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        response = requests.get(
            f"{self.base_url}/messages",
            headers=headers
        )

        if response.status_code == 200:
            return response.json().get("hydra:member", [])
        return []

    def display_messages(self):
        """Display messages in a nice table format"""
        messages = self.get_messages()
        
        if not messages:
            self.console.print("[yellow]No messages found[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim")
        table.add_column("From")
        table.add_column("Subject")
        table.add_column("Date")

        for msg in messages:
            date = datetime.fromisoformat(msg.get("createdAt").replace('Z', '+00:00'))
            formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")
            table.add_row(
                str(msg.get("id")),
                msg.get("from").get("address"),
                msg.get("subject") or "(No subject)",
                formatted_date
            )

        self.console.print(table)

    def get_message_content(self, message_id):
        """Get content of a specific message"""
        if not self.token:
            self.console.print("[red]Not logged in[/red]")
            return None

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        response = requests.get(
            f"{self.base_url}/messages/{message_id}",
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        return None

def main():
    client = MailGwClient()
    console = Console()

    console.print("[bold blue]Temporary Email Client[/bold blue]")
    console.print("Creating new email account...")
    
    if client.create_account():
        console.print("\n[bold green]Logging in...[/bold green]")
        if client.login():
            console.print("[green]Successfully logged in![/green]")
            
            while True:
                console.print("\n[bold cyan]Menu:[/bold cyan]")
                console.print("1. Check messages")
                console.print("2. View message content")
                console.print("3. Exit")
                
                choice = input("\nEnter your choice (1-3): ")
                
                if choice == "1":
                    console.print("\n[bold]Checking messages...[/bold]")
                    client.display_messages()
                
                elif choice == "2":
                    msg_id = input("Enter message ID: ")
                    message = client.get_message_content(msg_id)
                    if message:
                        console.print("\n[bold]Message Content:[/bold]")
                        console.print(f"From: {message.get('from', {}).get('address')}")
                        console.print(f"Subject: {message.get('subject', '(No subject)')}")
                        console.print(f"Content:\n{message.get('text', '(No content)')}")
                    else:
                        console.print("[red]Message not found[/red]")
                
                elif choice == "3":
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                
                else:
                    console.print("[red]Invalid choice[/red]")

if __name__ == "__main__":
    main() 