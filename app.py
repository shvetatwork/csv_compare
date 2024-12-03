from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from sqlalchemy import distinct
from models import SessionLocal, Finding
from parser import parse_html_report, extract_date_from_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'html'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    db = SessionLocal()
    
    # Get all unique finding names and dates
    finding_names = db.query(distinct(Finding.finding_name)).order_by(Finding.finding_name).all()
    finding_names = [name[0] for name in finding_names]
    
    dates = db.query(distinct(Finding.report_date)).order_by(Finding.report_date).all()
    dates = [date[0] for date in dates]
    
    # Create a matrix of findings
    findings_matrix = []
    for name in finding_names:
        row = {'finding_name': name}
        for date in dates:
            finding = db.query(Finding).filter_by(
                finding_name=name,
                report_date=date
            ).first()
            row[date.strftime('%Y-%m-%d')] = finding.occurrences if finding else 0
        findings_matrix.append(row)
    
    db.close()
    return render_template('index.html', findings_matrix=findings_matrix, dates=dates)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            report_date = extract_date_from_filename(filename)
            findings = parse_html_report(file.read().decode('utf-8'))
            
            db = SessionLocal()
            
            # Delete existing findings for this date
            db.query(Finding).filter_by(report_date=report_date).delete()
            
            # Add new findings
            for finding_name, occurrences in findings:
                new_finding = Finding(
                    finding_name=finding_name,
                    report_date=report_date,
                    occurrences=occurrences
                )
                db.add(new_finding)
            
            db.commit()
            db.close()
            
            flash('File successfully uploaded and processed')
        except Exception as e:
            flash(f'Error processing file: {str(e)}')
        finally:
            os.remove(file_path)
            
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 