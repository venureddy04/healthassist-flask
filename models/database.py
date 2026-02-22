from supabase import create_client, Client
from config import Config
from datetime import datetime
import hashlib
import json

supabase: Client = None

def init_supabase():
    global supabase
    try:
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        print("✅ Supabase connected successfully")
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ========== USER MANAGEMENT ==========
def create_user(mobile, name, password):
    try:
        existing = get_user(mobile)
        if existing:
            return False, "Mobile number already registered"

        hashed_password = hash_password(password)
        supabase.table("users").insert({
            "mobile": mobile,
            "name": name,
            "password": hashed_password,
            "created_at": datetime.now().isoformat()
        }).execute()
        return True, "Account created successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"

def verify_login(mobile, password):
    try:
        user = get_user(mobile)
        if not user:
            return False, "Mobile number not registered"

        hashed_password = hash_password(password)
        if user["password"] == hashed_password:
            return True, "Login successful"
        else:
            return False, "Incorrect password"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_user(mobile):
    try:
        result = supabase.table("users").select("*").eq("mobile", mobile).execute()
        return result.data[0] if result.data else None
    except:
        return None

def update_password(mobile, new_password):
    try:
        hashed_password = hash_password(new_password)
        supabase.table("users").update({
            "password": hashed_password,
            "updated_at": datetime.now().isoformat()
        }).eq("mobile", mobile).execute()
        return True, "Password updated successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"

def set_security_question(mobile, question, answer):
    try:
        hashed_answer = hash_password(answer.lower().strip())
        supabase.table("users").update({
            "security_question": question,
            "security_answer": hashed_answer
        }).eq("mobile", mobile).execute()
        return True, "Security question set"
    except Exception as e:
        return False, f"Error: {str(e)}"

def verify_security_answer(mobile, answer):
    try:
        user = get_user(mobile)
        if not user:
            return False, "Mobile number not found"
        if not user.get("security_answer"):
            return False, "Security question not set"

        hashed_answer = hash_password(answer.lower().strip())
        if user["security_answer"] == hashed_answer:
            return True, "Answer verified"
        else:
            return False, "Incorrect answer"
    except Exception as e:
        return False, f"Error: {str(e)}"

# ========== HISTORY MANAGEMENT ==========
def save_history(mobile, category, data):
    try:
        result = supabase.table("history").insert({
            "mobile": mobile,
            "category": category,
            "data": json.dumps(data) if isinstance(data, dict) else data,
            "timestamp": datetime.now().isoformat()
        }).execute()
        return result.data[0]["id"] if result.data else None
    except Exception as e:
        print(f"Error saving history: {e}")
        return None

def get_user_history(mobile, category=None):
    try:
        query = supabase.table("history").select("*").eq("mobile", mobile)
        if category:
            query = query.eq("category", category)
        result = query.order("timestamp", desc=True).execute()

        for item in result.data:
            if isinstance(item.get("data"), str):
                try:
                    item["data"] = json.loads(item["data"])
                except:
                    pass
        return result.data
    except:
        return []

def get_history_item(history_id):
    try:
        result = supabase.table("history").select("*").eq("id", history_id).execute()
        if result.data:
            item = result.data[0]
            if isinstance(item.get("data"), str):
                try:
                    item["data"] = json.loads(item["data"])
                except:
                    pass
            return item
        return None
    except:
        return None

def delete_history_item(history_id):
    try:
        supabase.table("history").delete().eq("id", history_id).execute()
        return True
    except:
        return False

def clear_user_history(mobile, category=None):
    try:
        query = supabase.table("history").delete().eq("mobile", mobile)
        if category:
            query = query.eq("category", category)
        query.execute()
        return True
    except:
        return False