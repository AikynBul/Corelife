import os
import hashlib
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class AuthService:
    def __init__(self):
        self.client = None
        self.db = None
        self.users = None
        self._connect()

    def _connect(self):
        mongo_uri = os.getenv("MONGO_URI")
        if mongo_uri:
            try:
                self.client = MongoClient(mongo_uri)
                self.db = self.client.get_database("ai_calendar_db")
                self.users = self.db.get_collection("users")
            except Exception as e:
                print(f"Error connecting to MongoDB (Auth): {e}")
        else:
            print("MONGO_URI not found in .env")

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password, email=""):
        if self.users is None:
            return False, "Database not connected"
        
        try:
            if self.users.find_one({"username": username}):
                return False, "Username already exists"
            
            user = {
                "username": username,
                "password": self._hash_password(password),
                "email": email,
                "created_at": datetime.datetime.now()
            }
            self.users.insert_one(user)
            return True, "Registration successful"
        except Exception as e:
            print(f"Registration Error: {e}")
            return False, f"Database Error: {str(e)}"

    def login(self, username, password):
        if self.users is None:
            return None, "Database not connected"
        
        try:
            user = self.users.find_one({
                "username": username,
                "password": self._hash_password(password)
            })
            
            if user:
                return {
                    "id": str(user["_id"]),
                    "username": user["username"],
                    "name": user.get("name", user["username"].capitalize()),
                    "email": user.get("email", "")
                }, "Login successful"
            
            return None, "Invalid username or password"
        except Exception as e:
            print(f"Login Error: {e}")
            return None, f"Database Error: {str(e)}"

    def update_user_profile(self, user_id, name, email):
        if self.users is None:
            return False, "Database not connected"
        
        from bson.objectid import ObjectId
        try:
            result = self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"name": name, "email": email}}
            )
            return True, "Profile updated successfully"
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False, f"Error updating profile: {e}"

    def change_password(self, user_id, current_password, new_password):
        if self.users is None:
            return False, "Database not connected"
            
        from bson.objectid import ObjectId
        try:
            user = self.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return False, "User not found"
                
            if user["password"] != self._hash_password(current_password):
                return False, "Incorrect current password"
                
            self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"password": self._hash_password(new_password)}}
            )
            return True, "Password changed successfully"
        except Exception as e:
            print(f"Error changing password: {e}")
            return False, f"Error changing password: {e}"

auth_service = AuthService()
