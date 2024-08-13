from kafka import KafkaProducer, KafkaConsumer
from flask import Flask, request, jsonify
from neo4j import GraphDatabase
import json
import pymongo
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
# import threading
# logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
application = app

server = pymongo.MongoClient("mongodb://admin:666@10.89.1.30:27017/")
mydb = server['songs']
mycol = mydb['user']
URI = "neo4j://10.0.47.59"
AUTH = ("neo4j", "h3rcul3s!")
driver = GraphDatabase.driver(URI, auth=AUTH)
driver.verify_connectivity()
producer = KafkaProducer(bootstrap_servers=['broker:9092'])

actor_insert = False
song_insert = False

# flag_lock = threading.Lock()

@app.route('/produce_actor/<actor>')
def actor_producer(actor: str):
    global actor_insert
    try:
        with driver.session() as session:
            actor_info = session.run(
                "MATCH (actor:Person {name: $name}) RETURN actor",
                name=actor
            )
            actor_data = None

            for record in actor_info:
                node = record['actor']
                actor_data = {
                    'element_id': node.element_id,
                    'name': node['name'],
                    'born': node['born']
                }

            if not actor_data:
                return jsonify({"error": "Actor not found"})

            records = session.run(
                "MATCH (actor:Person {name: $name})-[:ACTED_IN]->(movies) RETURN movies",
                name=actor
            )

            movies = []
            for record in records:
                movie = record['movies']
                movie_data = {
                    'element_id': movie.element_id,
                    'title': movie['title'],
                    'released': movie.get('released'),
                    'tagline': movie.get('tagline')
                }
                movies.append(movie_data)

            response_data = {
                'actor': actor_data,
                'movies': movies
            }

            if not response_data:
                return jsonify(f"There are no movies for {actor_data['name']}")

            response_bytes = json.dumps(response_data).encode('utf-8')
            producer.send('actor-topic', response_bytes)
            producer.flush()  # Ensure the message is sent before returning

            # with flag_lock:
            actor_insert = True
            if actor_insert and song_insert:
                # threading.Thread(target=consume_fuse).start()
                consume_fuse()

            return jsonify(response_data)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)})

@app.route('/produce_song/<year>')
def song_producer(year: str):
    global song_insert
    try:
        query = {"date_of_release": year}
        result = mycol.find(query)

        records = list(result)
        for record in records:
            record['_id'] = str(record['_id'])

        if not records:
            return jsonify(f'error": "No songs found for year {year}')

        response_bytes = json.dumps(records).encode('utf-8')
        producer.send('song-topic', response_bytes)
        producer.flush()

        # with flag_lock:
        song_insert = True
        if actor_insert and song_insert:
            # threading.Thread(target=consume_fuse).start()
            consume_fuse()

        return jsonify(records)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)})

def get_database_connection():
    conn = psycopg2.connect(dbname='mytestdb', user='admin', password='666', host='10.89.1.50', port='5432')
    return conn

def consume_fuse():
    actor_consume = KafkaConsumer(
        'actor-topic',
        bootstrap_servers=['10.89.1.40:9092'],
        auto_offset_reset='latest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        enable_auto_commit=True,
        # max_poll_records=20,
        group_id='my-group'
    )

    song_consume = KafkaConsumer(
        'song-topic',
        bootstrap_servers=['10.89.1.40:9092'],
        auto_offset_reset='latest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        enable_auto_commit=True,
        # max_poll_records=20,
        group_id='my-group'
    )
    # actor_consume.subscribe(topics=['actor-topic'])
    actor_data = {}
    song_data = {}
    global actor_insert, song_insert
    try:
        for actor in actor_consume:
            print("=============================Consume actor===============================================")
            actor_data = actor.value
            break
        actor_consume.close()

        for song in song_consume:
            print("=============================Consume song================================================")
            song_data = song.value
            break
        song_consume.close()

        sql_actor = actor_data['actor']
        sql_actor_val = "'" + sql_actor["element_id"] + "'" + ", " + "'" + sql_actor['name'] + "'" + ", " + "'" + str(sql_actor['born']) + "'"

        sql_movies = []
        for movie in actor_data['movies']:
            insert_value = []
            insert_value.append("'" + movie['element_id'] + "'")
            insert_value.append("'" + movie['title'] + "'")
            insert_value.append("'" + movie['tagline'] + "'")
            insert_value.append("'" + str(movie['released']) + "'")
            insert_value.append("'" + sql_actor["element_id"] + "'")
            sql_movies.append(insert_value)

        sql_songs = []
        for song in song_data:
            insert_value = []
            insert_value.append("'" + song['_id'] + "'")
            insert_value.append("'" + song['name'] + "'")
            insert_value.append("'" + sql_actor["element_id"] + "'")
            sql_songs.append(insert_value)

        sql_string_movies_list = []
        sql_string_song_list = []
        for row in sql_movies:
            sql_string_movies_list.append(", ".join(row))
        for row in sql_songs:
            sql_string_song_list.append(", ".join(row))

        conn = get_database_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(f"insert into actor values ({sql_actor_val})")
            conn.commit()
            for movie in sql_string_movies_list:
                print(f"insert into movies values ({movie})")
                cursor.execute(f"insert into movies values ({movie})")
                conn.commit()
                #cursor.commit()
            for song in sql_string_song_list:
                cursor.execute(f"insert into songs values ({song})")
                conn.commit()
            cursor.close()
            conn.close()
        except(Exception, psycopg2.DatabaseError) as e:
            print(e)
            conn.rollback()
        finally:
            cursor.close()
            cursor.close()
    except Exception as e:
        print(e)
    finally:
        # with flag_lock:
        actor_insert = False
        song_insert = False


if __name__ == '__main__':
    app.run(debug=True)
