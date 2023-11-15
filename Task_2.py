from flask import Flask, request, jsonify
import json
import re
from datetime import date, datetime
# my name is muazzam
app = Flask(__name__)
# what are you doing 
# Load data from the JSON file
def load_data():
    try:
        with open('G:\Ftutorial\Task_1_data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

items = load_data()
id_counter = max(item['ID'] for item in items) if items else 0

# Define the current start_date as a date object
start_date = date.today()

@app.route('/items', methods=['GET'])
def get_items():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
    status = request.args.get('status', type=str)
    priority = request.args.get('priority', type=str)
    get_by_delivery_date = request.args.get('delivery_date', type=str)
    get_by_date = request.args.get('start_date', type=str)

    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page  # Calculate total pages
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)

    # Convert get_by_delivery_date and get_by_date to date objects
    get_by_delivery_date = datetime.strptime(get_by_delivery_date, "%d-%m-%y").date() if get_by_delivery_date else None
    get_by_date = datetime.strptime(get_by_date, "%d-%m-%y").date() if get_by_date else None

    # Filter items based on the status and delivery_date parameters
    filtered_items = [item for item in items if
        (status is None or item['status'] == status) and
        (priority is None or item['priority'] == priority) and
        (get_by_delivery_date is None or datetime.strptime(item.get("delivery_date"), "%d-%m-%y").date() == get_by_delivery_date) and
        (get_by_date is None or datetime.strptime(item.get("start_date"), "%d-%m-%y").date() == get_by_date)
    ]
    if any(item for item in filtered_items) is True:
            # total_items = len(items)
        total_items = len(filtered_items)
        total_pages = (total_items + per_page - 1) // per_page  # Calculate total pages
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages

        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_items)
        # if any(item for item in filtered_items) is not True:
        #     return jsonify({"Message":"Invalid input"}),400
        
        paginated_items = filtered_items[start_idx:end_idx]

        prev_page = page - 1 if page > 1 else None
        next_page = page + 1 if page < total_pages else None
        nav_bar = {
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page,
            'prev_page': prev_page,
            'next_page': next_page
        }

        response_data = [
            {
                'Items': paginated_items,
                "Details": nav_bar
            }
        ]

        return jsonify(response_data), 200    
    else:
        nav_bar = {
            'total_items': 0,
            'total_pages': 0,
            'current_page': page,
            'per_page': per_page,
            'prev_page': None,
            'next_page': None
        }
        response_data=[
            {
                "Items":[],
                "Details":nav_bar
            }
        ]
        return response_data
    


@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item_to_get = next((item for item in items if item['ID'] == item_id), None)
    if item_to_get is None:
        return jsonify({"message": "Item not found"}), 404
    return jsonify(item_to_get), 200

@app.route('/items', methods=['POST'])
def add_item():
    data = request.get_json()

    if not all(key in data for key in ["description", "status", "delivery_date"]):
        return jsonify({"message": "Required fields:  description, status, delivery_date"}), 400

    status_condition = r"^(completed|inprogress|pending)$"
    if not re.search(status_condition, data["status"]):
        return jsonify({"Message": "Enter status only completed, inprogress and pending"}), 400

    # Use a regular expression to validate the delivery_date format
    date_format_condition = r"^(0[1-9]|[12][0-9]|3[01])\-(0[1-9]|1[0-2])\-\d{2}$"
    if not re.search(date_format_condition, data["delivery_date"]):
        return jsonify({"Message": "Enter delivery_date in this format (dd-mm-yy)"})
    
    # Convert delivery_date to a date object
    delivery_date = datetime.strptime(data["delivery_date"], "%d-%m-%y").date()

    if delivery_date < start_date:
        return jsonify({"Message": "Delivery date should be equal to or after the current date"}), 400

    priority_condition = r"^(normal|low|high)$"
    if "priority" not in data:
        data['priority'] = "normal"
    elif not re.search(priority_condition, data["priority"]):
        return jsonify({"Message": "The priority can only be high, low, or normal"}), 400

    global id_counter
    id_counter += 1
    new_item = data
    new_item['start_date'] = start_date.strftime("%d-%m-%y")
    new_item['ID'] = id_counter
    items.append(new_item)

    with open('G:\Ftutorial\Task_1_data.json', 'w') as file:
        json.dump(items, file, indent=4)

    return jsonify(new_item), 201


    # ...

@app.route('/items/<int:item_id>', methods=['PUT'])
def put_item(item_id):
    name_condition = r"^(?![0-9._])(?!.*[0-9._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z_ ]+$"
    
    updated_item = request.get_json()
    item_to_update = next((item for item in items if item["ID"] == item_id), None)
    if item_to_update is None:
        return jsonify({"Message": "item not found."}), 404

    if not all(key in updated_item for key in ["description", "status", "delivery_date"]):
        # return jsonify({"message": "Required fields: description, status, delivery_date"}), 400
        pass
    else:
        status_condition = r"^(completed|inprogress|pending)$"
        if not re.search(status_condition, updated_item["status"]):
            return jsonify({"Message": "Enter status only completed, inprogress, and pending"}), 400

        # Use a regular expression to validate the delivery_date format
        date_format_condition = r"^(0[1-9]|[12][0-9]|3[01])\-(0[1-9]|1[0-2])\-\d{2}$"
        if not re.search(date_format_condition, updated_item["delivery_date"]):
            return jsonify({"Message": "Enter delivery_date in this format (dd-mm-yy)"}), 400

        # Convert delivery_date to a date object
        delivery_date = datetime.strptime(updated_item["delivery_date"], "%d-%m-%y").date()

        if delivery_date < start_date:
            return jsonify({"Message": "Delivery date should be equal to or after the current date"}), 400

    if "name" in updated_item:
        if not isinstance(updated_item["name"], str) or not re.search(name_condition, updated_item["name"]):
            return jsonify({"Message": "Name must be a valid string"}), 400

    item_to_update.update(updated_item)

    # Save the updated data to the JSON file
    with open('G:\Ftutorial\Task_1_data.json', 'w') as file:
        json.dump(items, file)

    return jsonify(item_to_update), 200

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if not item_exists(item_id):
        return jsonify({"message": "Item not found"}), 404

    items[:] = [item for item in items if item['ID'] != item_id]

    # Save the updated data to the JSON file
    with open('G:\Ftutorial\Task_1_data.json', 'w') as file:
        json.dump(items, file, indent=4)

    return jsonify({"message": "Item deleted successfully"}), 200

# Validation function for checking if a status is valid
def is_valid_status(status):
    return status in ['completed', 'inprogress', 'pending']

# Validation function for checking if an item exists
def item_exists(item_id):
    for item in items:
        if item['ID'] == item_id:
            return True
    return False

if __name__ == '__main__':
    app.run(debug=True)

