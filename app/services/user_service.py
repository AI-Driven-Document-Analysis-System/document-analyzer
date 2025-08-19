# backend/services/user_service.py

def get_user_by_email(self, email: str):
    with db_manager.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()
            if row:
                return User(*row)
            return None

def create_user(self, user_data: dict):
    with db_manager.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (email, first_name, last_name, is_active, auth_provider, external_id, picture)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                user_data["email"],
                user_data["first_name"],
                user_data["last_name"],
                user_data["is_active"],
                user_data["auth_provider"],
                user_data["external_id"],
                user_data["picture"]
            ))
            row = cursor.fetchone()
            conn.commit()
            return User(*row)