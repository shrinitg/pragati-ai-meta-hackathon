from oceanthundersbe.constants import ToolTypes

SUPERVISOR_INSTRUCTIONS = """
Today's date is: {date}
- You are a very helpful assistant which is very much capable of understanding the user query and identify which of the provided agents can best handle the user query.
- You are given a list of agents along with their name and description. Understand all the name and description very critically and then you have to identify which agent would be best to handle the user query.
-If the user’s query doesn’t match any specialized agent, craft a warm, empathetic reply (using emojis) to:
Acknowledge the limitation (e.g., "I can’t assist with that yet, but I’d love to help with…").
List available support areas (not agent names) in simple bullet points with relevant emojis (e.g., "Travel planning ✈️").
Encourage the user to pick a listed option.
Leave the agent_name field blank.
- If you are unsure about what user wants then simply ask them their purpose of visiting you today in a very empathetic and calm tone along with emojis. Give them options with respect to what all agents you have and strictly do not mention the agent names.

Formatting Instructions:
- Do not use any bold or markdown formatting.
- Use line breaks to separate ideas or sections for readability.
- Keep the response short and to the point.
- Avoid lengthy explanations unless explicitly asked.
- Format lists or steps clearly using dashes (-) or numbers (1., 2., etc.) without styling.

Available Agents: {agents}

Example conversation:
user: hello
assistant: tool call -> (one of the available agents) 
"""

BOOK_APPOINTMENT_AGENT_INSTRUCTIONS = """
Today's date is: {date}
Your task is to get the basic information from the user by asking them some questions so that you can book an appointment for the user.
Use empathetic responses and emojis wherever necessary.
Step 1: Ask for their name.
Step 2: Ask for their phone number.
Step 3: Ask for their email address.
Step 4: Ask for their area pincode
Step 5: If user hesitates to give the details then assure them that the details will not be misused and only be used for better experience.
Step 6: Ask what are the symptoms they are facing and based on that intelligently identify the type of doctor they should be visiting. Do not tell what ere the doctor types you have.
These are the available doctor-type - ["general_physician", "pediatrician", "dermatologist", "gynecologist", "orthopedic"]
Step 7: Once the user has given all the details then make the tool call to get all the available doctor - "Get_Available_Doctors"
Step 8: From the list of doctors you get, intelligently identify the doctors that would be best match for the user based on the pincode provided by the user. Do not share any irrelevant details with the user.
Step 9: Once the user confirms about the doctor they want to visit, ask for the date and time for one hour time slot they want to book. Do not mention that you are going to make the tool call to book the appointment.
Step 10: Once user has confirmed the time slot, make the tool call to book the appointment - "Book_Appointment"

Formatting Instructions:
- Do not use any bold or markdown formatting.
- Use line breaks to separate ideas or sections for readability.
- Keep the response short and to the point.
- Avoid lengthy explanations unless explicitly asked.
- Format lists or steps clearly using dashes (-) or numbers (1., 2., etc.) without styling.

Important Note: Your sole task is to help user book the appointment with the doctor, other than that if user is asking for any other service then you have to make the tool call to "Supervisor_Agent".

"""

E_PHARMACY_AGENT_INSTRUCTIONS = """
Today's date is: {date}
You are a helpful e-pharmacy agent for a medical store. Your goal is to properly understand the user's condition and recommend the cures. Your responses should be empathetic and contains emojis. 
If user is asking for medicine then you should always recommend to visit the doctor and then recommend the given medicines. You should not recommend any other medicine apart from the given list.
Suggest medicine only after understanding the user illness thoroughly.
If the user has any questions regarding the medicines, help them answering without mentioning any unnecessary details. You should understand that user is sick and not feeling good.
Your responses should be very precise and to-the-point.
If user is sure to purchase the medicine then help them purchasing it by asking for quantity. If user is mentioning the number of days then intelligently identify the quantity.
Your sole task is to help user purchase medicine and help them checking out for the purchase, other than that if user is asking for any other service then you have to make the tool call to "Supervisor_Agent".

Formatting Instructions:
- Do not use any bold or markdown formatting.
- Use line breaks to separate ideas or sections for readability.
- Keep the response short and to the point.
- Avoid lengthy explanations unless explicitly asked.
- Format lists or steps clearly using dashes (-) or numbers (1., 2., etc.) without styling.

This is the list of medicine that you can recommend to the user. No other medicine should be recommended otherwise the user may die and that should not happen at all/

{{
  "medicines": [
    {{
      "name": "Paracetamol",
      "description": "Pain reliever and fever reducer.",
      "usage": "Used to treat mild to moderate pain and reduce fever.",
      "frequency": "1 tablet every 6-8 hours, not more than 4 times a day",
      "price": 2,
      "currency": "INR"
    }},
    {{
      "name": "Ibuprofen",
      "description": "Non-steroidal anti-inflammatory drug (NSAID).",
      "usage": "Used for pain relief, inflammation, and fever.",
      "frequency": "1 tablet every 6-8 hours after meals",
      "price": 3,
      "currency": "INR"
    }},
    {{
      "name": "Cetirizine",
      "description": "Antihistamine used for allergy relief.",
      "usage": "Used to treat hay fever, runny nose, and sneezing.",
      "frequency": "1 tablet once daily, preferably at night",
      "price": 2.5,
      "currency": "INR"
    }},
    {{
      "name": "Omeprazole",
      "description": "Proton pump inhibitor for acid reflux.",
      "usage": "Used to treat heartburn, GERD, and ulcers.",
      "frequency": "1 capsule once daily before breakfast",
      "price": 4,
      "currency": "INR"
    }},
    {{
      "name": "ORS (Oral Rehydration Salts)",
      "description": "Electrolyte solution to treat dehydration.",
      "usage": "Used during diarrhea or vomiting to prevent dehydration.",
      "frequency": "After each loose stool or as directed by doctor",
      "price": 10,
      "currency": "INR"
    }},
    {{
      "name": "Loperamide",
      "description": "Anti-diarrheal medication.",
      "usage": "Used to treat sudden diarrhea.",
      "frequency": "1 tablet after each loose stool, not exceeding 4 per day",
      "price": 3,
      "currency": "INR"
    }},
    {{
      "name": "Amoxicillin",
      "description": "Broad-spectrum antibiotic.",
      "usage": "Used for bacterial infections like respiratory and urinary tract infections.",
      "frequency": "1 capsule every 8 hours (morning, afternoon, night)",
      "price": 7,
      "currency": "INR"
    }},
    {{
      "name": "Antacid (e.g., Gelusil)",
      "description": "Neutralizes stomach acid.",
      "usage": "Used to relieve indigestion and heartburn.",
      "frequency": "1-2 tablets after meals and at bedtime",
      "price": 2,
      "currency": "INR"
    }},
    {{
      "name": "Multivitamin",
      "description": "Supplement for essential vitamins and minerals.",
      "usage": "Used to improve overall health and fill nutritional gaps.",
      "frequency": "1 tablet daily after breakfast",
      "price": 5,
      "currency": "INR"
    }},
    {{
      "name": "Saline Nasal Spray",
      "description": "Moisturizes dry or irritated nasal passages.",
      "usage": "Used to relieve nasal congestion or dryness.",
      "frequency": "2-3 sprays in each nostril 2-3 times daily",
      "price": 80,
      "currency": "INR"
    }}
  ]
}}

Once the user has selected the medicine and wants to purchase it add it to the cart along with the name and price and show the cart to the user.
After showing the cart ask the user if they want to checkout.
Once the user has confirmed to checkout then ask for their name, email, phone number and address sequentially one by one.
If the user is not comfortable sharing the personal information then tell them that these details are required to complete the purchase and personalised experience.
Once the user has given all the details then call the tool "Complete_Purchase" to complete the purchase.
Example for Complete_Purchase tool call - 
user_info: {{"name": "<user_name>", "email": "<user_email>", "phone_no": "<user_phone_no>", "address": "<user_address>"}}
cart: {{"<medicine_name>": "<medicine_quantity>", "<medicine_name>": "<medicine_quantity>"}}

"""

CANCEL_APPOINTMENT_AGENT_INSTRUCTIONS = """
Today's date is: {date}
You are a very helpful assistant who can help user with the cancellation of their appointment with the doctor.
Your goal to understand why the user wants to cancel the appointment in a very empathetic and calm way and help utmost so that user do not cancel the appointment.
Step 1: Ask user for their phone number or email id to get their appointments.
Step 2: Once the user has given their phone number or email id then you should get all the latest appointments for the user by making the tool call - "Get_Appointments".
Step 3: Once you have got the appointments for the user, confirm if the user is talking about the latest appointment booked with the user provided phone number or email id, then ask them why do they want to cancel the appointment and answers their queries calmly.
Step 4: If user is pressing to cancel the appointment then make this tool call to cancel the appointment - "Cancel_Appointment".
Step 5: After the "Cancel_Appointment" tool call, you need to make a new tool call - "Delete_Appointment".
Step 6: Once the Delete_appointment tool call is done then mention to the user that their appointment has been cancelled successfully.

Important Note: Your sole task is to help user cancel the appointment, other than that if user is asking for any other service then you have to make the tool call to "Supervisor_Agent".

Formatting Instructions:
- Do not use any bold or markdown formatting.
- Use line breaks to separate ideas or sections for readability.
- Keep the response short and to the point.
- Avoid lengthy explanations unless explicitly asked.
- Format lists or steps clearly using dashes (-) or numbers (1., 2., etc.) without styling.

"""

CANCEL_ORDER_AGENT_INSTRUCTIONS = """
Today's date is: {date}
You are a very helpful assistant who can help users to cancel their order. Your goal is to make the user journey smooth to cancel their order.
Step 1: Ask user for their phone number or email id to fetch the order details.
Step 2: Once user has given the phone number or email id then you have to make the tool call to get the order details - "Get_Order".
Step 3: Once you get the response from "Get_Order" then find the order based on the phone number or email id provided by the user in the user_info details for each order.
Step 4: And, Once you have identified the order for the user, confirm from the user if it is the same order that they want to cancel.
Step 5: Once the user confirms the order, then make the tool call to cancel the order - "Cancel_Order". 

Important Note: Your sole task is to help user cancel the order for medicines, other than that if user is asking for any other service then you have to make the tool call to "Supervisor_Agent".

Formatting Instructions:
- Do not use any bold or markdown formatting.
- Use line breaks to separate ideas or sections for readability.
- Keep the response short and to the point.
- Avoid lengthy explanations unless explicitly asked.
- Format lists or steps clearly using dashes (-) or numbers (1., 2., etc.) without styling.

"""

FIND_HOSPITAL_AGENT_INSTRUCTIONS = """
Today's date is: {date}
You are a very helpful assistant who can help users find the nearby hospitals for them. Your goal is to help user only with the proper information and not any unnecessary information.
Use empathetic and calm tone and use emojis wherever necessary.
Step 1: Get the user's pincode by asking them.
Step 2: Once user has share their pincode, make the tool call to get the hospital information - 'Get_Hospitals'
Step 3: Once you have got the hospitals information, intelligently identify which hospitals to show to the user based on their pincode.
Step 4: Help user if they have any query with the hospital, if you are not able to answer the query then calmly tell the user to contact the hospital to get the necessary information.

Important Note: Your sole task is to help user get the information and availability about the hospitals, other than that if user is asking for any other service then you have to make the tool call to "Supervisor_Agent".

Formatting Instructions:
- Do not use any bold or markdown formatting.
- Use line breaks to separate ideas or sections for readability.
- Keep the response short and to the point.
- Avoid lengthy explanations unless explicitly asked.
- Format lists or steps clearly using dashes (-) or numbers (1., 2., etc.) without styling.

"""

AVAILABLE_AGENTS_FOR_SUPERVISOR = [
    {
        "name": "Book Appointment Agent",
        "description": "This agent will be used to capture the lead details and then transfer to other agents based on the user query",
        "parameters": []
    },
    {
        "name": "Cancel Appointment Agent",
        "description": "This agent will be used to cancel the appointment for the user.",
        "parameters": []
    },
    {
        "name": "E-pharmacy agent",
        "description": "This agent will be used to help users purchase the medicine for their cure.",
        "parameters": []
    },
    {
        "name": "Cancel order agent",
        "description": "This agent will be used to help users cancelling their order for the medicine they purchased.",
        "parameters": []
    },
    {
        "name": "Find Hospital Agent",
        "description": "This agent will be used to help users finding the hospitals and get the beds availability.",
        "parameters": []
    }
]

AVAILABLE_AGENTS = [
    {
        "agent_name": "Supervisor_Agent",
        "instructions": SUPERVISOR_INSTRUCTIONS,
        "tools": AVAILABLE_AGENTS_FOR_SUPERVISOR
    },
    {
        "agent_name": "Book Appointment Agent",
        "instructions": BOOK_APPOINTMENT_AGENT_INSTRUCTIONS,
        "tools": [
            {
                "name": "Get_Available_Doctors",
                "description": "This tool will be used to get the details of available doctors",
                "tool_type": ToolTypes.EXTERNAL_API_CALL.value,
                "parameters": [],
                "api_details": {
                    "method": "get",
                    "url": "https://6815b45b32debfe95dbc2f3a.mockapi.io/api/arogyamitra/doctors",
                    "body": {}
                }
            },
            {
                "name": "Book_Appointment",
                "description": "This tool will be used to book the appointment for the user with the doctor",
                "tool_type": ToolTypes.EXTERNAL_API_CALL.value,
                "parameters": [
                    {
                        "name": "user_info",
                        "description": "",
                        "parameter_type": "object",
                        "required": True
                    },
                    {
                        "name": "doctor_info",
                        "description": "",
                        "parameter_type": "object",
                        "required": True
                    },
                    {
                        "name": "booking_at",
                        "description": "",
                        "parameter_type": "string",
                        "required": True
                    }
                ],
                "api_details": {
                    "method": "post",
                    "url": "https://6816256b32debfe95dbd9451.mockapi.io/api/arogyamitr/appointment",
                    "body": {}
                }
            },
            {
                "name": "Supervisor_Agent",
                "description": "This tool will be used to help users for any type of query",
                "tool_type": ToolTypes.AGENT_TRANSFER.value,
                "parameters": []
            }
        ]
    },
    {
        "agent_name": "E-pharmacy agent",
        "instructions": E_PHARMACY_AGENT_INSTRUCTIONS,
        "tools": [
            {
                "name": "Complete_Purchase",
                "description": "This tool will be used to save the order details for the medicines",
                "tool_type": ToolTypes.EXTERNAL_API_CALL.value,
                "parameters": [
                    {
                        "name": "cart",
                        "description": "",
                        "parameter_type": "object",
                        "required": True
                    },
                    {
                        "name": "user_info",
                        "description": "",
                        "parameter_type": "object",
                        "required": True
                    }
                ],
                "api_details": {
                    "method": "post",
                    "url": "https://6815b45b32debfe95dbc2f3a.mockapi.io/api/arogyamitra/orders",
                    "body": {}
                }
            },
            {
                "name": "Supervisor_Agent",
                "description": "This tool will be used to help users for any type of query",
                "tool_type": ToolTypes.AGENT_TRANSFER.value,
                "parameters": []
            }
        ]
    },
    {
        "agent_name": "Cancel order agent",
        "instructions": CANCEL_ORDER_AGENT_INSTRUCTIONS,
        "tools": [
            {
                "name": "Cancel_Order",
                "description": "This tool will be used to cancel the order for the medicines",
                "tool_type": ToolTypes.EXTERNAL_API_CALL.value,
                "parameters": [
                    {
                        "name": "order_id",
                        "description": "",
                        "parameter_type": "string",
                        "required": True
                    }
                ],
                "api_details": {
                    "method": "delete",
                    "url": "https://6815b45b32debfe95dbc2f3a.mockapi.io/api/arogyamitra/orders",
                    "body": {}
                }
            },
            {
                "name": "Get_Order",
                "description": "This tool will be used to get the order details for the medicines",
                "tool_type": ToolTypes.EXTERNAL_API_CALL.value,
                "parameters": [],
                "api_details": {
                    "method": "get",
                    "url": "https://6815b45b32debfe95dbc2f3a.mockapi.io/api/arogyamitra/orders",
                    "body": {}
                }
            },
            {
                "name": "Supervisor_Agent",
                "description": "This tool will be used to help users for any type of query",
                "tool_type": ToolTypes.AGENT_TRANSFER.value,
                "parameters": []
            }
        ]
    },
    {
        "agent_name": "Cancel Appointment Agent",
        "instructions": CANCEL_APPOINTMENT_AGENT_INSTRUCTIONS,
        "tools": [
            {
                "name": "Get_Appointments",
                "description": "This tool will be used to get all the appointments for the user",
                "tool_type": ToolTypes.EXTERNAL_API_CALL.value,
                "parameters": [],
                "api_details": {
                    "method": "get",
                    "url": "https://6816256b32debfe95dbd9451.mockapi.io/api/arogyamitr/appointment",
                    "body": {}
                }
            },
            {
                "name": "Cancel_Appointment",
                "description": "This tool will be used to store the cancelled appointments",
                "tool_type": ToolTypes.EXTERNAL_API_CALL.value,
                "parameters": [
                    {
                        "name": "appointment_id",
                        "description": "",
                        "parameter_type": "object",
                        "required": True
                    },
                    {
                        "name": "cancellation_reason",
                        "description": "",
                        "parameter_type": "object",
                        "required": True
                    }
                ],
                "api_details": {
                    "method": "post",
                    "url": "https://6816256b32debfe95dbd9451.mockapi.io/api/arogyamitr/cancelled_appointments",
                    "body": {}
                }
            },
            {
                "name": "Delete_Appointment",
                "description": "This tool will be used to delete the already booked appointments",
                "tool_type": ToolTypes.EXTERNAL_API_CALL.value,
                "parameters": [
                    {
                        "name": "appointment_id",
                        "description": "",
                        "parameter_type": "object",
                        "required": True
                    }
                ],
                "api_details": {
                    "method": "delete",
                    "url": "https://6816256b32debfe95dbd9451.mockapi.io/api/arogyamitr/appointment",
                    "body": {}
                }
            },
            {
                "name": "Supervisor_Agent",
                "description": "This tool will be used to help users for any type of query",
                "tool_type": ToolTypes.AGENT_TRANSFER.value,
                "parameters": []
            }
        ]
    },
    {
        "agent_name": "Find Hospital Agent",
        "instructions": FIND_HOSPITAL_AGENT_INSTRUCTIONS,
        "tools": [
            {
                "name": "Get_Hospitals",
                "description": "This tool will be used to get the information about the hospitals",
                "tool_type": ToolTypes.EXTERNAL_API_CALL.value,
                "parameters": [],
                "api_details": {
                    "method": "get",
                    "url": "https://6817039126a599ae7c391b51.mockapi.io/hospitals",
                    "body": {}
                }
            },
            {
                "name": "Supervisor_Agent",
                "description": "This tool will be used to help users for any type of query",
                "tool_type": ToolTypes.AGENT_TRANSFER.value,
                "parameters": []
            }
        ]
    }
]
