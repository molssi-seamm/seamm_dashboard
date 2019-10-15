from pymongo import MongoClient
client = MongoClient('localhost', 27017) # defaults
# same as
client = MongoClient('mongodb://localhost:27017')

# By specifying this database name and saving data to it,
# you create the database automatically.
db = client.pymongo_test
# or the dictionary-like access
#db = client['pymongo_test']


# Collections and documents are akin to SQL tables and rows
posts = db.posts

def inser_one():
    post_data = {
        'title': 'Python and MongoDB',
        'content': 'PyMongo is fun',
        'author': 'Scott'
    }
    result = posts.insert_one(post_data)
    print('One post: {0}'.format(result.inserted_id))

def insert_multiple():
    # Insert multiple
    post_1 = {
        'title': 'Python and MongoDB',
        'content': 'PyMongo is fun, you guys',
        'author': 'Scott'
    }
    post_2 = {
        'title': 'Virtual Environments',
        'content': 'Use virtual environments, you guys',
        'author': 'Scott'
    }
    post_3 = {
        'title': 'zzzzzzzzLearning Python',
        'content': 'Learn Python, it is easy',
        'author': 'Bill'
    }
    new_result = posts.insert_many([post_1, post_2, post_3])
    print('Multiple posts: {0}'.format(new_result.inserted_ids))


# Queries:
# --------

def find_one():
    bills_post = posts.find_one({'author': 'Bill'})
    print('===== One Bill: ', bills_post)

def find_many():
    scotts_posts = posts.find({'author': 'Scott'})
    print(scotts_posts)

    for post in scotts_posts:
        print(post)

def print_all():
    # All posts:
    all_posts = posts.find()
    print('-------- All Posts -----------: ', all_posts.count())
    for post in all_posts:
        print(post)


insert_multiple()
find_one()
find_many()
print_all()
