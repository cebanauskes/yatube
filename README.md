# Yatube
Социальная  сеть для блогеров (выполнен во время обучения в Яндекс.Практикум)
# Описание
Социальня сеть для личных публикаций (допускаются текст и картинки). Здесь можно создать свой аккаунт. Зайдя на страницу пользователя можно подписаться на него и увидеть
все его публикации, количество подписчиков. Авторизованные пользователи могут оставлять комментарии к постам авторов. При создании поста автор может выбрать группу, к которой пост будет принадлежать. Зайдя на страницу группы можно увидеть все посты от разных авторов, принадлежащие к этой группе. Администратор может модерировать записи и банить пользователей за флуд или спам.
# Инструкция по развертыванию проекта
1. Скачать проект или клонировать с помощью git (`git clone https://github.com/cebanauskes/yatube_.git`)
2. Перейти в каталог с проектом и создать виртуальное окружение (`python3 -m venv venv`)
3. Запустить виртуальное окружение (`source venv/bin/activate`) на Mac/Linux или (`source venv/Scripts/activate`) на Windows
4. Установить все необходимые пакеты, указанные в файле requirements.txt (`pip install -r requirements.txt`)
5. Запустить миграции (`python manage.py migrate`)
6. Для проверки работы проекта запустить тестовый сервер (`python manage.py runserver`)
7. Перейти по адресу http://127.0.0.1:8000
