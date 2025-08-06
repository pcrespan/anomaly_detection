from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

admin = KafkaAdminClient(
    bootstrap_servers="kafka:9092",
    client_id="metrics-topic-creator"
)

try:
    topic_name = "metrics"
    topic = NewTopic(
        name=topic_name,
        num_partitions=5,
        replication_factor=1
    )
    admin.create_topics([topic])
    print(f"Topic {topic_name} created successfully.")
except TopicAlreadyExistsError:
    print(f"Topic {topic_name} already exists.")
finally:
    admin.close()
