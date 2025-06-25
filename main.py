import requests
import time
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timezone
import pytz  
from concurrent.futures import ThreadPoolExecutor

# 🚀 Firebase 
cred = credentials.Certificate("fb_rtdb.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://simcompanies-tracker-default-rtdb.firebaseio.com/"
})

# 🌍 Timezone Setup
IST = pytz.timezone("Asia/Kolkata")
API_TICKER_URL = "https://www.simcompanies.com/api/v3/market-ticker/0/"
API_PRODUCT_URL = "https://www.simcompanies.com/api/v3/market/0/{}"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1352185970237112331/c-pqVOMIP4MWg9o0R5-bxhhTCoG_xY10i6L4J5eLGcekGeFAiGRDInPuIzlAsmdABXKo"


# 🟢 Color Coding for Risk Levels
def get_risk_color(risk_level):
    if "ULTRA LOW" in risk_level:
        return 65280  # Bright Green
    elif "LOW RISK" in risk_level:
        return 3066993  # Green
    elif "MID RISK" in risk_level:
        return 16776960  # Yellow
    else:
        return 15158332  # Red

# 🚀 Send Discord Notification
def send_discord_notification(product_id, cost_price, avg_price, receiving_amount, quantity, profit, profit_percentage, risk_level, seller_name, quality):
    # 🛒 Product Name Dictionary
    PRODUCT_NAMES = {
    100: 'Aerospace research', 18: 'Aluminium', 125: 'Apple cider', 123: 'Apple pie', 
    3: 'Apples', 82: 'Attitude control', 58: 'Automotive research', 50: 'Basic interior', 
    22: 'Batteries', 15: 'Bauxite', 121: 'Bread', 33: 'Breeding research', 102: 'Bricks', 
    112: 'Bulldozer', 134: 'Butter', 51: 'Car body', 76: 'Carbon composite', 75: 'Carbon fibers', 
    103: 'Cement', 122: 'Cheese', 17: 'Chemicals', 34: 'Chemistry research', 140: 'Chocolate', 
    104: 'Clay', 81: 'Cockpit', 132: 'Cocktails', 136: 'Cocoa', 118: 'Coffee beans', 
    119: 'Coffee powder', 52: 'Combustion engine', 111: 'Construction units', 40: 'Cotton', 
    115: 'Cows', 10: 'Crude oil', 12: 'Diesel', 23: 'Displays', 137: 'Dough', 62: 'Dress', 
    55: 'Economy car', 53: 'Economy e-car', 9: 'Eggs', 48: 'Electric motor', 21: 'Electronic components', 
    32: 'Electronics research', 30: 'Energy research', 73: 'Ethanol', 41: 'Fabric', 
    59: 'Fashion research', 80: 'Flight computer', 133: 'Flour', 139: 'Fodder', 127: 'Frozen pizza', 
    77: 'Fuselage', 126: 'Ginger beer', 45: 'Glass', 61: 'Gloves', 68: 'Gold ore', 69: 'Golden bars', 
    6: 'Grain', 5: 'Grapes', 129: 'Hamburger', 64: 'Handbags', 87: 'Heat shield', 
    79: 'High grade e-comps', 88: 'Ion drive', 42: 'Iron ore', 147: "Jack o'lantern", 89: 'Jet engine', 
    26: 'Laptops', 130: 'Lasagna', 46: 'Leather', 105: 'Limestone', 56: 'Luxury car', 
    49: 'Luxury car interior', 54: 'Luxury e-car', 70: 'Luxury watch', 113: 'Materials research', 
    131: 'Meat balls', 74: 'Methane', 117: 'Milk', 14: 'Minerals', 31: 'Mining research', 
    27: 'Monitors', 71: 'Necklace', 47: 'On-board computer', 124: 'Orange juice', 4: 'Oranges', 
    128: 'Pasta', 11: 'Petrol', 116: 'Pigs', 108: 'Planks', 29: 'Plant research', 19: 'Plastic', 
    1: 'Power', 20: 'Processors', 84: 'Propellant tank', 146: 'Pumpkin', 149: 'Pumpkin soup', 
    98: 'Quadcopter', 145: 'Recipes', 101: 'Reinforced concrete', 114: 'Robots', 86: 'Rocket engine', 
    83: 'Rocket fuel', 142: 'Salad', 143: 'Samosa', 44: 'Sand', 138: 'Sauce', 8: 'Sausages', 
    66: 'Seeds', 16: 'Silicon', 24: 'Smart phones', 65: 'Sneakers', 35: 'Software', 
    85: 'Solid fuel booster', 7: 'Steak', 43: 'Steel', 107: 'Steel beams', 63: 'Stiletto Heel', 
    135: 'Sugar', 72: 'Sugarcane', 25: 'Tablets', 28: 'Televisions', 110: 'Tools', 
    13: 'Transport', 150: 'Tree', 57: 'Truck', 60: 'Underwear', 141: 'Vegetable oil', 
    120: 'Vegetables', 2: 'Water', 109: 'Windows', 78: 'Wing', 148: 'Witch costume', 
    106: 'Wood', 67: 'Xmas crackers', 144: 'Xmas ornaments'
}
    product_name = PRODUCT_NAMES.get(int(product_id), "Unknown Product")  # Get product name from dictionary
    product_link = f"https://www.simcompanies.com/market/resource/{product_id}/"  # Clickable link

    # import requests

    embed = {
        "title": f"🛒 Price Update: [{product_name}](<{product_link}>)",
        "description": f"""
        🔗 **[Click here to view the product (FOR MOBILES)]({product_link})**

        **⚠️ Risk Level:** `{risk_level}`
        **💰 Buying Price:** `${cost_price}`
        **📈 Selling Price:** `${avg_price}`

        **⚖️ Quantity:** `{quantity:,}x Units`
        **📦 Quality:** `{quality}`
        **💰 Total Buying Cost:** `${quantity * cost_price:,.2f}`

        **💸 Profit:** `${int(profit):,}`
        **📊 Profit %:** `{round(profit_percentage, 2)}%`

        **👤 Seller:** `{seller_name}`
        """,
        "color": get_risk_color(risk_level),
        "footer": {
            "text": "Simco Market Bulls",
        }
    }


    # Add a clickable button
    components = [
        {
            "type": 1,  # Action row
            "components": [
                {
                    "type": 2,  # Button
                    "label": "View Product",
                    "style": 5,  # Link button style
                    "url": product_link  # URL of the product
                }
            ]
        }
    ]

    # Send the webhook request
    data = {"embeds": [embed], "components": components}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)

    print(response.status_code, response.text)  # Debugging output


    if response.status_code == 204:
        print(f"✅ Notification Sent for {product_name}!")
    else:
        print(f"❌ Failed to send Discord notification: {response.status_code}")

# 🚚 Transport Cost Data
transport_reqd = { 
    100: 0, 18: 1, 125: 1, 123: 2, 3: 1, 82: 1, 58: 0, 50: 2, 22: 1, 15: 1, 121: 1, 33: 0, 102: 1, 
    112: 5, 134: 1, 51: 2, 76: 1, 75: 0.1, 103: 1, 122: 1, 17: 1, 34: 0, 140: 1, 104: 1, 81: 1, 
    132: 2, 136: 0.1, 118: 0.1, 119: 1, 52: 2, 111: 0, 40: 0.5, 115: 1, 10: 1, 12: 1, 23: 1, 137: 1, 
    62: 1, 55: 5, 53: 5, 9: 0.1, 48: 2, 21: 1, 32: 0, 30: 0, 73: 1, 41: 0.5, 59: 0, 80: 1, 133: 0.1, 
    139: 1, 127: 1, 77: 2, 126: 1, 45: 1, 61: 1, 68: 10, 69: 1000, 6: 0.1, 5: 1, 129: 2, 64: 1, 87: 1, 
    79: 1, 88: 1, 42: 1, 147: 1, 89: 1, 26: 2, 130: 2, 46: 1, 105: 1, 56: 5, 49: 2, 54: 5, 70: 1, 
    113: 0, 131: 2, 74: 1, 117: 1, 14: 1, 31: 0, 27: 2, 71: 1, 47: 1, 124: 1, 4: 1, 128: 1, 11: 1, 
    116: 1, 108: 1, 29: 0, 19: 1, 1: 0, 20: 1, 84: 1, 146: 1, 149: 2, 98: 2, 145: 0, 101: 10, 114: 2, 
    86: 1, 83: 1, 142: 2, 143: 2, 44: 1, 138: 2, 8: 0.1, 66: 0.1, 16: 1, 24: 2, 65: 1, 35: 0, 85: 1, 
    7: 1, 43: 1, 107: 5, 63: 1, 135: 1, 72: 0.1, 25: 2, 28: 2, 110: 1, 13: 0, 150: 1, 57: 5, 60: 1, 
    141: 1, 120: 0.2, 2: 0, 109: 1, 78: 2, 148: 1, 106: 1, 67: 0.5, 144: 0.5
}

timestamp = datetime.now(timezone.utc).isoformat()

def process_item(item):
    kind = str(item["kind"])
    price = item["price"]
    
    # 🕰 Get current IST time
    now_ist = datetime.now(IST)
    date_key = f"{now_ist.day}_{now_ist.month}_{now_ist.year}"
    time_key = f"{now_ist.hour}_{now_ist.minute}_{now_ist.second}"

    # 🔥 Store Data in Firebase
    db.reference(f"Data/{kind}/{date_key}").update({time_key: price})
    db.reference(f"LastPrices/{kind}").update({"price": price, "last_updated": now_ist.strftime("%Y-%m-%d %H:%M:%S IST")})
    print(f"✅ Data Stored: Kind {kind} | Price: {price} | time: {timestamp}")
    print("--------------------------------------------------")

    # 🚀 Fetch Transport Price
    transport_price = db.reference("LastPrices/13/price").get() or 0

    # 🚀 Fetch Avg Price
    avg_price = db.reference(f"AveragePrice/{kind}").get() or 0

    # 🏗 Calculate Transport Cost & Receiving Amount
    transport_cost = transport_reqd.get(int(kind), 0) * transport_price
    receiving_amount = (avg_price * 0.97) - transport_cost

    # 🎯 Fetch Product Market Data
    product_response = requests.get(API_PRODUCT_URL.format(kind), timeout=10)
    if product_response.status_code == 200:
        product_data = product_response.json()
        if product_data:
            item_data = product_data[0]
            quantity = item_data["quantity"]
            quality = item_data["quality"]
            cost_price = item_data["price"]
            seller_name = item_data["seller"]["company"]


            # 💰 Profit Calculation
            profit = (receiving_amount - cost_price) * quantity
            profit_percentage = ((receiving_amount - cost_price) / avg_price) * 100

            # 📊 Risk Level
            risk_level = (
                "🟢💎 ULTRA LOW RISK – Golden Opportunity! 🚀" if profit_percentage > 8 else
                "✅🟢 LOW RISK – Safe & Profitable! 🏆" if profit_percentage >= 5 else
                "⚠️🟡 MID RISK – Analyze before selling! 🤔" if profit_percentage >= 3 else
                "🚨🔴 HIGH RISK – Think Twice! ⚡" if profit_percentage >= 0 else
                "❌💔 LOSS – Avoid Selling! 😓"
            )


            # 📝 Print Results if Profit % > 2
            if profit_percentage > 0:
                # 🔥 Store Profit Analysis in Firebase
                db.reference(f"Analysis/{kind}/{date_key}").update({
                    time_key: {
                        "cost_price": cost_price,
                        "avg_price": avg_price,
                        "recvd_amount": receiving_amount,
                        "quantity": quantity,
                        "profit": profit,
                        "risk_level": risk_level,
                        "seller": seller_name,
                        "profit_percent": profit_percentage
                    }
                })
                if profit > 1000 and int(kind) != 151 and int(kind) != 152:
                    # 🔥 Send Instant Notification to Discord
                    send_discord_notification(kind, cost_price, avg_price, receiving_amount, quantity, profit, profit_percentage, risk_level, seller_name, quality)
    
                print(f"🔹 Product: {kind} | Quality: {quality} | Seller: {seller_name}")
                print(f"🔹 Cost Price: {cost_price} | Avg Price: {avg_price} | Amount Receved: {receiving_amount}")
                print(f"🔹 Quantity: {quantity} | Profit: {profit} | ")
                print(f"🔹 Profit%: {profit_percentage}% | Risk Level: {risk_level}")
                print("-------------------------------------------------")

while True:
    url = API_TICKER_URL
    print(url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                timestamp = datetime.now(timezone.utc).isoformat()
                with ThreadPoolExecutor(max_workers=10) as executor:
                    executor.map(process_item, data)

    except Exception as e:
        print(f"⚠️ Error: {e}, Retrying in 10 sec...")
        time.sleep(10)
