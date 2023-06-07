"""
    Run: python main.py
"""

import numpy as np
import random
import sys
import mysql.connector  # pip install mysql-connector-python

from dataclasses import dataclass

# Данные для подключения к базе данных
DB_HOST = "localhost"
Db_PORT = 3306
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "library"


@dataclass
class UserAction:
    user_id: int
    book_id: int
    reward: float


class QLearningRecommendationSystem:
    def __init__(
        self, max_users, max_books, learning_rate, discount_factor, exploration_rate
    ):
        self.max_users = max_users
        self.max_books = max_users
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate

        self.Q = np.zeros((max_users, max_books))

    def get_action(self, user_id, available_books):
        if random.random() < self.exploration_rate:
            return random.choice(available_books)
        else:
            q_values = self.Q[user_id][available_books]
            max_q_value = max(q_values)
            max_indices = np.where(q_values == max_q_value)[0]
            return available_books[random.choice(max_indices)]

    def update_Q(self, user_id, book_id, reward, next_user_id):
        current_q_value = self.Q[user_id][book_id]
        next_q_value = max(self.Q[next_user_id])
        td_error = reward + self.discount_factor * next_q_value - current_q_value
        self.Q[user_id][book_id] += self.learning_rate * td_error

    def recommend_books(self, user_id, available_books):
        q_values = self.Q[user_id][available_books]
        max_q_value = max(q_values)
        max_indices = np.where(q_values == max_q_value)[0]
        return [available_books[i] for i in max_indices]


def get_available_books():
    # Подключение к базе данных MySQL
    cnx = mysql.connector.connect(
        user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME
    )
    cursor = cnx.cursor()

    # Запрос к базе данных
    query = "SELECT id FROM books;"
    cursor.execute(query)

    book_ids = [row[0] for row in cursor.fetchall()]

    # Закрытие соединения с базой данных
    cursor.close()
    cnx.close()

    return book_ids


def get_users_count():
    # Подключение к базе данных MySQL
    cnx = mysql.connector.connect(
        user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME
    )
    cursor = cnx.cursor()

    # Запрос к базе данных
    query = "SELECT COUNT(*) FROM users;"
    cursor.execute(query)

    user_count = cursor.fetchone()[0]

    # Закрытие соединения с базой данных
    cursor.close()
    cnx.close()

    return user_count


def get_user_actions():
    # Подключение к базе данных MySQL
    cnx = mysql.connector.connect(
        user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME
    )
    cursor = cnx.cursor()

    # Запрос к базе данных
    query = "SELECT reservationMadeFor_user_id, book_id FROM reservations;"
    cursor.execute(query)

    user_actions = []
    for row in cursor.fetchall():
        user_id = row[0]
        book_id = row[1]
        user_actions.append(UserAction(user_id, book_id, 1.0))

    # Закрытие соединения с базой данных
    cursor.close()
    cnx.close()

    return user_actions


from flask import Flask, request, jsonify

app = Flask(__name__)

def get_recommendations(user_id):
    # Получаем действия пользователей
    user_actions = get_user_actions()

    # Рекомендуем книги пользователю
    available_books = get_available_books()

    num_users = get_users_count()
    num_books = len(available_books)
    learning_rate = 0.1
    discount_factor = 0.9
    exploration_rate = 0.5
    recommendation_system = QLearningRecommendationSystem(
        200, 200, learning_rate, discount_factor, exploration_rate
    )

    # Обучаем рекомендательную систему на основе последовательности действий
    for _ in range(100):
        for user_action in user_actions:
            next_user_id = (
                user_action.user_id + 1 if user_action.user_id < num_users - 1 else 0
            )
            recommendation_system.update_Q(
                user_action.user_id,
                user_action.book_id,
                user_action.reward,
                next_user_id,
            )

    recommended_books = recommendation_system.recommend_books(
        int(user_id), available_books
    )

    return recommended_books


@app.route("/books/recomends", methods=["GET"])
def get_book_recommendations():
    user_id = request.args.get("user_id")
    if user_id:
        try:
            recommendations = get_recommendations(user_id)
            return jsonify(dict(data=recommendations))

        except Exception as e:
             return jsonify(dict(data=list(set(random.choices(get_available_books(), k=20)))))

    else:
        return "Missing user_id parameter", 400


if __name__ == "__main__":
    app.run(port=8888)
