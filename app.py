from flask import Flask, request, jsonify, render_template, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

#app = Flask(__name__)
app = Flask(__name__, static_folder='static')

# MongoDB connection
username = os.environ.get('MONGO_USER')
password = os.environ.get('MONGO_PASS')
cluster = os.environ.get('MONGO_CLUSTER')
dbname = os.environ.get('MONGO_DBNAME')

# Connect to MongoDB
mongo_uri = f"mongodb+srv://{username}:{password}@{cluster}/{dbname}?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client.sample_mflix  # bezkoder_db2 # bezkoder_db2 
collection = db.FiveWs #FamilyAndAllautoGen_notes27jan  

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 7
    documents = collection.find().skip((page - 1) * per_page).limit(per_page)
    total_documents = collection.count_documents({})
    total_pages = (total_documents // per_page) + (1 if total_documents % per_page > 0 else 0)
    #print(f" TYPE(documents)******** = {type(documents)}")   
    return render_template('index.html', documents=documents, page=page, total_pages=total_pages, message="DB.COLLECTION: ROOT240830.FiveWs",searchResult_1=f" All {total_documents} documents")

def recursive_search(document, search_qry):
    if isinstance(document, dict):
        for key, value in document.items():
            if key == "image": # skip comparing substrings from base64 code
                continue
            if recursive_search(value, search_qry):
                return True
    elif isinstance(document, list):
        for item in document:
            if recursive_search(item, search_qry):
                return True
    elif isinstance(document, str):
        if search_qry.lower() in document.lower():
            return True
    return False

@app.route('/search', methods=['GET', 'POST']) #search_query1
def index2():
    #search_query1 = request.form.get('searchstring1') 
    #search_query2 = request.form.get('searchstring2') 
    results = []
    if request.method == 'POST':
        print(f" @#$%^ P O S T req detected @#$%^")
        search_query1 = request.form.get('searchstring1') # if request.method == 'POST' else ""
        search_query2 = request.form.get('searchstring2')
        print(f" TTTOP1 search_query1 = {search_query1} type is {type(search_query1)}*** search_query2 = {search_query2} type is {type(search_query2)}" )
        if type(search_query1)== None: search_query1="" 
        if  search_query2 == None: search_query2=""         
        print(f" TTTOP2 search_query1 = {search_query1} type is {type(search_query1)}*** search_query2 = {search_query2} type is {type(search_query2)}" )
        #
        all_documents = collection.find()
        matching_ids = [doc['_id'] for doc in all_documents if (recursive_search(doc, search_query1) and ( (recursive_search(doc, search_query2)) if (search_query2!="all") else True ))]
        print(f" @#$%^@#$%^ matching_ids: {matching_ids} @#$%^@#$%^")
        if matching_ids:
            page = request.args.get('page', 1, type=int)
            per_page = 7
            documents = collection.find({'_id': {'$in': matching_ids}}).skip((page - 1) * per_page).limit(per_page)
            total_documents = collection.count_documents({'_id': {'$in': matching_ids}})
            total_pages = (total_documents // per_page) + (1 if total_documents % per_page > 0 else 0)
            #
            '''
            return render_template('search.html', documents=documents, page=page, total_pages=total_pages, search_query1=search_query1, search_query2=search_query2, message=f"ROOT240830.FiveWs search_query2 {search_query2}",searchResult_0="", searchResult_1=f"  {total_documents} doc(s) has \"{search_query1}\" under \"{search_query2}\"", total_docs = total_documents, per_page=per_page ) 
            '''
            #
        else:
            return render_template('index.html', page=1, total_pages=0, searchResult_0=f" . . .      \"{search_query1}\" was not found.", searchResult_1="")
    else:     
        print(f" @#$%^ G E T req detected @#$%^")
        search_query1 = request.args.get('searchstring1')
        search_query2 = request.args.get('searchstring2')
        print(f" *** search_query1 *** is {search_query1}*** search_query2 = {search_query2}" )
        page = request.args.get('page', 1, type=int)
        all_documents = collection.find()
        matching_ids = [doc['_id'] for doc in all_documents if (recursive_search(doc, search_query1) and ( (recursive_search(doc, search_query2)) if (search_query2!="all") else True ))]
        per_page = 7
        documents = collection.find({'_id': {'$in': matching_ids}}).skip((page - 1) * per_page).limit(per_page)
        total_documents = collection.count_documents({'_id': {'$in': matching_ids}})
        total_pages = (total_documents // per_page) + (1 if total_documents % per_page > 0 else 0)
    print(f" BOT1 search_query1 = {search_query1} *** search_query2 = {search_query2}" )
    #search_scope = ""
    return render_template('search.html', documents=documents, page=page, total_pages=total_pages, search_query1=search_query1, search_query2=search_query2, message=f"ROOT240830.FiveWs search_query2 {search_query2}",searchResult_0="", searchResult_1=f"  {total_documents} doc(s) has \"{search_query1}\" under \"{search_query2}\"", total_docs = total_documents, per_page=per_page ) 


@app.route('/f1') #FI is find one
def index():
    data = collection.find_one()
    return render_template('index3.html', message="trying find one command" ) #,mongoDBdata=data


# Create a new document
@app.route('/about', methods=['GET'])
def collection_info():
    info = {
        "database_name": db.name,
        "collection_name": collection.name,
        "document_count": collection.count_documents({}),
        "indexes": collection.index_information()
    }
    return jsonify(info), 200

@app.route('/update2', methods=['POST'])
def update2():
    updates = {}
    for field in request.form:
        new_value = request.form[field]
        print(f"**** the detected new value is: {new_value}")
        if new_value:
            updates[field] = new_value
    print(f"attempting to update mongoDB {updates} ")
    theID =updates['_id']
    del updates['_id']        
    print(f" THIS IS IT:  {json.dumps(updates, indent=4)} ***theID {theID} ") # {jsonify(updates)}

    # Update document in MongoDB
    if updates:
        #print(f"attempting to update mongoDB {updates} ")
        result=collection.update_one({'_id': ObjectId(theID) }, {'$set': updates}) #ObjectId(   str(updates['_id'])
        # Print the result of the update operation 
        print(f"Matched count: {result.matched_count}") 
        print(f"Modified count: {result.modified_count}")

    return redirect(url_for('home'))
 
 
# Create a new document
@app.route('/create', methods=['POST'])
def create():
    data = request.json
    result = collection.insert_one(data)
    return jsonify({"_id": str(result.inserted_id)}), 201

# Read all documents
@app.route('/read', methods=['GET'])
def read_all():
    documents = []
    for doc in collection.find():
        doc['_id'] = str(doc['_id'])
        documents.append(doc)
    return jsonify(documents), 200

# Read a single document by ID
@app.route('/read/<id>', methods=['GET'])
def read_one(id):
    document = collection.find_one({"_id": ObjectId(id)})
    if document:
        document['_id'] = str(document['_id'])
        return jsonify(document), 200
    return jsonify({"error": "Document not found"}), 404

# Update a document by ID
@app.route('/update/<id>', methods=['PUT'])
def update(id):
    data = request.json
    result = collection.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.matched_count:
        return jsonify({"message": "Document updated"}), 200
    return jsonify({"error": "Document not found"}), 404

# Delete a document by ID
@app.route('/delete/<id>', methods=['DELETE'])
def delete(id):
    result = collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"message": "Document deleted"}), 200
    return jsonify({"error": "Document not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)

