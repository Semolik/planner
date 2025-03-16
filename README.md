# Первоначальная настройка

### Регистрация и Институты

-   **Первый пользователь**: Первый зарегистрированный пользователь автоматически становится администратором.
-   **`institute_id`**: При регистрации указывается ID института, к которому принадлежит пользователь.

### Управление Институтами

Используйте скрипт [manage_institutes.py](/api/scripts/manage_institutes.py) для создания или просмотра институтов (нужно при создании первого пользователя, так как без прав администратора нельзя создать институт).

1. **Список институтов**:

    ```bash
    docker-compose exec <api_container_name> python scripts/manage_institutes.py list
    ```

2. **Создать институт**:

    ```bash
    docker-compose exec <api_container_name> python scripts/manage_institutes.py create "Название института 1" "Название института 2"
    ```

3. **Удалить институт**:
    ```bash
    docker-compose exec <api_container_name> python scripts/manage_institutes.py delete <institute_id>
    ```

Запуск без аргументов показывает справку.
