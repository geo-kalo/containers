from kafka import KafkaProducer
from flask import Flask, request, jsonify
from neo4j import GraphDatabase
import json
import pymongo
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
application = app

URI = "neo4j://10.0.47.59"
AUTH = ("neo4j", "h3rcul3s!")
driver = GraphDatabase.driver(URI, auth=AUTH)
driver.verify_connectivity()


producer = KafkaProducer(bootstrap_servers=['broker:9092'])




@app.route('/produce_actor/<actor>', methods=['POST'])
def actor_producer(actor: str):
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
            return jsonify(response_data)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    app.run(debug=True)


