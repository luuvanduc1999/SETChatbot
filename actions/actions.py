
from typing import Any, Text, Dict, List

from pathlib import Path
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted   
from rasa_sdk.events import SlotSet
import sqlite3
import random
import json
from pymongo import MongoClient
from bson.json_util import dumps, loads
import regex

client = MongoClient("mongodb+srv://luuvanduc:poiu1234@chathear.zkuk0.mongodb.net/chatbot?retryWrites=true&w=majority")
db = client.test
db = client['chat_bot']
collection_register = db['register']
collection_lecturer = db['lecturer']


def findLecturer(name):
    myCursor = collection_lecturer.find( { "name": {
        "$regex": name,
        "$options" :'i' # case-insensitive
    } } )
    list_cur = list(myCursor)
    json_data = dumps(list_cur, indent = 2) 
    data=json.loads(json_data)
    return data

class ActionChecklecturer(Action):

    def name(self) -> Text:
        return 'action_find_lecturer'

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,   domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("co goi nha")
        for blob in tracker.latest_message['entities']:
            if blob['entity'] == 'lecturer_name':
                name = blob['value']
                print("name")
                result = findLecturer(name)
                if (len(result)):
                    dispatcher.utter_message(text=f"Giảng viên {result[0]['name']} hiện là {result[0]['position']}\nlàm việc ở văn phòng tại {result[0]['work_place']}  \nemail liên hệ: {result[0]['email']}" )
                else:
                    dispatcher.utter_message(text=f"Không tìm thấy giảng viên {name} trong hệ thống." )

        return []

class ActionSaveForm(Action):

    def name(self) -> Text:
        return 'action_save_form'

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Any]:

        try:
            coll_name = ''
            document_data = {}

            for turn, event in enumerate(reversed(tracker.events)):
                name = event.get('name')
                # Check only for the latest form
                coll_name = 'bookings'
                document_data.update(tracker.slots)
                del document_data["lecturer_name"]
                del document_data["requested_slot"]
                del document_data["session_started_metadata"]
            # Insert into DB only if recent and valid form was found
            if coll_name:
                print(document_data)
                collection_register.insert_one(document_data)
        
        except Exception:
            pass
        
        finally:
            return []

class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message("Xin lỗi, tôi chưa hiểu ý bạn. Bạn có thể nói lại được không ?")

        # Revert user message which led to fallback.
        return [UserUtteranceReverted()]