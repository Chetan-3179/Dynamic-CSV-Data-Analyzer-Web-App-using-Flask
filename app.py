import os
import uuid
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, send_file, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
CHART_FOLDER = 'static/charts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHART_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html', theme=session.get('theme', 'light'))

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    theme = request.form.get('theme', 'light')
    session['theme'] = theme  # Make sure session is storing the theme correctly

    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        df = pd.read_csv(filepath)
        session['preview_file'] = filepath

        chart_files = generate_charts(df)
        return render_template('result.html', tables=[df.head(10).to_html(classes='table table-bordered table-striped table-hover', header=True, index=False, escape=False).replace('\n', '')],
                               chart_files=chart_files, theme=theme)
    return redirect('/')

@app.route('/download_data')
def download_data():
    filepath = session.get('preview_file')
    return send_file(filepath, as_attachment=True)

@app.route('/download_chart/<filename>')
def download_chart(filename):
    return send_file(os.path.join(CHART_FOLDER, filename), as_attachment=True)

@app.route('/switch_theme', methods=['POST'])
def switch_theme():
    current_theme = session.get('theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    session['theme'] = new_theme
    return redirect('/')

def generate_charts(df):
    chart_files = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            plt.figure()
            df[col].hist(color='skyblue', edgecolor='black')
            plt.title(f'Histogram of {col}')
            filename = f"{uuid.uuid4()}.png"
            path = os.path.join(CHART_FOLDER, filename)
            plt.savefig(path)
            plt.close()
            chart_files.append(filename)
        elif pd.api.types.is_categorical_dtype(df[col]) or df[col].nunique() < 10:
            plt.figure()
            df[col].value_counts().plot(kind='bar', color='lightcoral', edgecolor='black')
            plt.title(f'Bar Chart of {col}')
            filename = f"{uuid.uuid4()}.png"
            path = os.path.join(CHART_FOLDER, filename)
            plt.savefig(path)
            plt.close()
            chart_files.append(filename)
    return chart_files


if __name__ == '__main__':
    app.run(debug=True)
