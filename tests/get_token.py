from src.auth.security import create_access_token
from src.schemas.jwt_schem import TokenData

token_data = TokenData(user_id=0)

test_token = create_access_token(data=token_data)

print(f"\nТвой тестовый JWT-токен для Swagger (user_id = {token_data.user_id}):")
print(f"Bearer {test_token}")
print("\nПросто скопируй строку БЕЗ слова 'Bearer' и вставь в поле Value в Swagger!\n")