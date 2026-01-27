import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class EventStore:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.user_id = None # Set when user logs in
        self._connect()

    def _connect(self):
        mongo_uri = os.getenv("MONGO_URI")
        if mongo_uri:
            try:
                self.client = MongoClient(mongo_uri)
                self.db = self.client.get_database("ai_calendar_db")
                self.collection = self.db.get_collection("events")
                print("Connected to MongoDB")
            except Exception as e:
                print(f"Error connecting to MongoDB: {e}")
        else:
            print("MONGO_URI not found in .env")

    def set_user(self, user_id):
        self.user_id = user_id

    def add_event(self, title, start_date, end_date, description, event_type="event", recurrence=None, priority="Medium", completed=False):
        if self.collection is None or not self.user_id:
            print("Database not connected or user not set")
            return None

        new_event = {
            "user_id": self.user_id,
            "title": title,
            "start": start_date,
            "end": end_date,
            "description": description,
            "type": event_type,
            "recurrence": recurrence,
            "priority": priority,
            "completed": completed,
            "created_at": datetime.now()
        }
        try:
            result = self.collection.insert_one(new_event)
            new_event["id"] = str(result.inserted_id)
            return new_event
        except Exception as e:
            print(f"Error adding event: {e}")
            return None

    def update_event(self, event_id, updates):
        if self.collection is None or not self.user_id:
            return None
        
        from bson.objectid import ObjectId
        try:
            # Ensure we only update fields that are allowed and belong to the user
            result = self.collection.update_one(
                {"_id": ObjectId(event_id), "user_id": self.user_id},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating event: {e}")
            return False

    def delete_event(self, event_id):
        if self.collection is None or not self.user_id:
            return
        
        from bson.objectid import ObjectId
        try:
            self.collection.delete_one({"_id": ObjectId(event_id), "user_id": self.user_id})
        except Exception as e:
            print(f"Error deleting event: {e}")

    def get_events_for_month(self, year, month):
        if self.collection is None or not self.user_id:
            return []

        # Get all events for the user (filtering by date is complex with recurrence, so we fetch all and filter in python for now)
        # Optimization: In a real app, we would query for non-recurring events in range OR recurring events
        try:
            cursor = self.collection.find({"user_id": self.user_id})
            events = []
            for doc in cursor:
                doc["id"] = str(doc["_id"])
                events.append(doc)
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
        
        results = []
        
        # Helper to get number of days in month
        import calendar
        _, num_days = calendar.monthrange(year, month)
        
        for event in events:
            # Handle both "YYYY-MM-DD" and "YYYY-MM-DD HH:MM"
            try:
                start_str = event["start"].split(" ")[0]
                start_dt = datetime.strptime(start_str, "%Y-%m-%d").date()
            except (ValueError, IndexError):
                continue

            recurrence = event.get("recurrence")
            
            # If non-recurring, check if it falls in this month
            if not recurrence or recurrence == "none":
                if start_dt.year == year and start_dt.month == month:
                    results.append(event)
                continue
                
            # Handle recurrence
            # We only care if the event started on or before this month (or if it repeats yearly in this month)
            
            # Optimization: If event starts after this month, skip
            if start_dt.year > year or (start_dt.year == year and start_dt.month > month):
                continue
                
            # Generate occurrences for this month
            for day in range(1, num_days + 1):
                current_date = datetime(year, month, day).date()
                
                # Skip if before start date
                if current_date < start_dt:
                    continue
                    
                should_add = False
                
                if recurrence == "daily":
                    should_add = True
                elif recurrence == "workdays":
                    # Mon=0, Sun=6
                    if current_date.weekday() < 5:
                        should_add = True
                elif recurrence == "weekends":
                    if current_date.weekday() >= 5:
                        should_add = True
                elif recurrence == "monthly":
                    if current_date.day == start_dt.day:
                        should_add = True
                elif recurrence == "yearly":
                    if current_date.month == start_dt.month and current_date.day == start_dt.day:
                        should_add = True
                        
                if should_add:
                    # Create a virtual event instance
                    instance = event.copy()
                    instance["start"] = current_date.isoformat()
                    instance["end"] = current_date.isoformat()
                    # Append original ID to track it
                    results.append(instance)
                    
        return results

# Global instance
store = EventStore()
