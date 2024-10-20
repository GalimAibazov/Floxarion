
from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Это используется для безопасности сессий и флеш-сообщений.

# Функция генерации последовательного ID в шестнадцатеричной системе
def generate_id():
    try:
        with open('video_counter.txt', 'r') as f:
            current_id = int(f.read())
    except FileNotFoundError:
        current_id = 0
    video_id = hex(current_id)[2:].upper()  # Генерация ID
    with open('video_counter.txt', 'w') as f:
        f.write(str(current_id + 1))  # Увеличиваем счетчик
    return video_id

# Регистрация пользователя
def register_user(username, password):
    with open('users.txt', 'a') as f:
        f.write(f'{username}:{password}\n')

# Проверка пользователя
def check_user(username, password):
    with open('users.txt', 'r') as f:
        for line in f:
            if line.strip() == f'{username}:{password}':
                return True
    return False

# Загрузка видео
def upload_video(video_id, title, video_file):
    video_path = f'uploads/{video_id}.mp4'  # Путь и расширение для видео
    video_file.save(video_path)  # Сохранение файла в указанное место
    with open('videos.txt', 'a') as f:
        f.write(f'{video_id}:{title}:0:0\n')  # Лайки и дизлайки равны 0

# Получение отсортированных видео
def get_videos():
    videos = []
    with open('videos.txt', 'r') as f:
        for line in f:
            video_id, title, likes, dislikes = line.strip().split(':')
            videos.append({
                'id': video_id,
                'title': title,
                'likes': int(likes),
                'dislikes': int(dislikes),
                'fun_factor': int(likes) - int(dislikes)
            })
    return sorted(videos, key=lambda x: x['fun_factor'], reverse=True)

@app.route('/')
def index():
    videos = get_videos()
    return render_template('index.html', videos=videos)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        register_user(username, password)
        flash("Registration successful!")
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username, password):
            flash("Login successful!")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials!")
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        video_file = request.files['video_file']  # Получаем загруженный файл
        video_id = generate_id()
        upload_video(video_id, title, video_file)  # Передаем файл в функцию загрузки
        flash("Video uploaded successfully!")
        return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/video/<video_id>')
def video(video_id):
    videos = get_videos()
    for video in videos:
        if video['id'] == video_id:
            return render_template('video.html', video=video)
    return 'Video not found', 404

@app.route('/uploads/<path:filename>')
def upload_video_file(filename):
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    # Создание папки для загрузки видео, если нет
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host='0.0.0.0', port=5000, debug=True)
