# app.py
import numpy as np
import pandas as pd
import pickle

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from sklearn.preprocessing import StandardScaler


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/healthInsurance'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable tracking modifications to avoid warning
app.secret_key = '12345'  # a secret key for session management
db = SQLAlchemy(app)

#login_manager = LoginManager(app)
heartmodel =  pickle.load(open('heart.pkl', 'rb'))
diabetesmodel = pickle.load(open('diabetes_RF_Model.pkl', 'rb'))
livermodel = pickle.load(open('liver.pkl', 'rb'))
liverscaler = pickle.load(open('scaler_liver.pkl', 'rb'))
heartscaler = pickle.load(open('scaler_heart.pkl', 'rb'))
prob = [0,0,0]


"""------------------------- database ---------------------------"""
class Customer(db.Model):
    accountid = db.Column(db.Integer, primary_key=True, unique=True)  # Add unique=True here
    password = db.Column(db.String(255))
    custname = db.Column(db.String(255))
    email = db.Column(db.String(255))
    address = db.Column(db.Text)

class Heart(db.Model):
    accountid = db.Column(db.Integer, db.ForeignKey('customer.accountid'), primary_key=True)
    age = db.Column(db.Integer)
    sex = db.Column(db.String(10))
    cp = db.Column(db.Integer)
    trestbps = db.Column(db.Integer)
    chol = db.Column(db.Integer)
    fbs = db.Column(db.Integer)
    restecg = db.Column(db.Integer)
    thalach = db.Column(db.Integer)
    exang = db.Column(db.Integer)
    oldpeak = db.Column(db.Float)
    slope = db.Column(db.Integer)
    ca = db.Column(db.Integer)
    thal = db.Column(db.Integer)
    heartrisk = db.Column(db.Float)

class Diabetes(db.Model):
    accountid = db.Column(db.Integer, db.ForeignKey('customer.accountid'), primary_key=True)
    pregnancies = db.Column(db.Float)
    glucose = db.Column(db.Integer)
    bloodpressure = db.Column(db.Integer)
    skinthickness = db.Column(db.Integer)
    insulin = db.Column(db.Integer)
    bmi = db.Column(db.Float)
    diabetespedigreefunction = db.Column(db.Float)
    age = db.Column(db.Integer)
    diabetesrisk = db.Column(db.Float)

class Liver(db.Model):
    accountid = db.Column(db.Integer, db.ForeignKey('customer.accountid'), primary_key=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    totalbilirubin = db.Column(db.Float)
    directbilirubin = db.Column(db.Float)
    alkalinephosphotase = db.Column(db.Integer)
    alamineamint = db.Column(db.Integer)
    aspartateamint = db.Column(db.Integer)
    totalproteins = db.Column(db.Float)
    albumin = db.Column(db.Float)
    aandgratio = db.Column(db.Float)
    liverrisk = db.Column(db.Float)

def get_logged_in_customer():
    if 'customer_id' in session:
        customer_id = session['customer_id']
        customer = Customer.query.get(customer_id)
        return customer
    return None

@app.route('/')
def index():
    customer = get_logged_in_customer()
    return render_template('index.html', customer=customer)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        accountid = request.form['accountid']
        password = request.form['password']
        custname = request.form['custname']
        email = request.form['email']
        address = request.form['address']

        new_customer = Customer(
            accountid=accountid,
            password=password,
            custname=custname,
            email=email,
            address=address
        )
        heart_data = Heart(
            accountid=new_customer.accountid,
            age=0,
            sex=0,
            cp=0,
            trestbps=0,
            chol=0,
            fbs=0,
            restecg=0,
            thalach=0,
            exang=0,
            oldpeak=0,
            slope=0,
            ca=0,
            thal=0,
            heartrisk=0
        )

        diabetes_data = Diabetes(
            accountid=new_customer.accountid,
            pregnancies=0,
            glucose=0,
            bloodpressure=0,
            skinthickness=0,
            insulin=0,
            bmi=0,
            diabetespedigreefunction=0,
            age=0,
            diabetesrisk=0
        )

        liver_data = Liver(
            accountid=new_customer.accountid,
            age=0,
            gender=0,
            totalbilirubin=0,
            directbilirubin=0,
            alkalinephosphotase=0,
            alamineamint=0,
            aspartateamint=0,
            totalproteins=0,
            albumin=0,
            aandgratio=0,
            liverrisk=0
        )


        db.session.add(new_customer)
        db.session.add(heart_data)
        db.session.add(diabetes_data)
        db.session.add(liver_data)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        accountid = request.form['accountid']
        password = request.form['password']

        customer = Customer.query.filter_by(accountid=accountid, password=password).first()

        if customer:
            session['customer_id'] = customer.accountid
            return redirect(url_for('profile'))
        else:
            flash('Login failed. Please check your credentials and try again.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('customer_id', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    customer = get_logged_in_customer()

    if not customer:
        flash('Please log in to view your profile.', 'error')
        return redirect(url_for('login'))

    # Retrieve the corresponding Heart record from the database
    customer_heart = Heart.query.filter_by(accountid=customer.accountid).first()
    customer_diabetes = Diabetes.query.filter_by(accountid=customer.accountid).first()
    customer_liver = Liver.query.filter_by(accountid=customer.accountid).first()

    if request.method == 'POST':
        updated_name = request.form.get('updated_name')
        updated_email = request.form.get('updated_email')
        updated_address = request.form.get('updated_address')

        customer.custname = updated_name
        customer.email = updated_email
        customer.address = updated_address

        db.session.commit()

        flash('Profile updated successfully', 'success')

    return render_template('profile.html', customer=customer, customer_heart=customer_heart,
                           customer_diabetes=customer_diabetes, customer_liver=customer_liver)

@app.route('/edit_customer', methods=['GET', 'POST'])
def edit_customer():
    customer = get_logged_in_customer()

    if not customer:
        flash('Please log in to edit your information.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Extract edited information from the form
        updated_name = request.form.get('updated_name')
        updated_email = request.form.get('updated_email')
        updated_address = request.form.get('updated_address')

        # Update the customer record in the database
        customer.custname = updated_name
        customer.email = updated_email
        customer.address = updated_address

        # Commit the changes to the database
        db.session.commit()

        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', customer=customer)

# Add this route to your app.py file
@app.route('/heart_profile', methods=['GET', 'POST'])
def heart_profile():
    customer = get_logged_in_customer()

    if not customer:
        flash('Please log in to view your heart profile.', 'error')
        return redirect(url_for('login'))

    customer_heart = Heart.query.filter_by(accountid=customer.accountid).first()

    if request.method == 'POST':
        # Retrieve the updated values from the form
        updated_age = request.form.get('updated_age')
        updated_sex = request.form.get('updated_sex')
        updated_cp = request.form.get('updated_cp')
        updated_trestbps = request.form.get('updated_trestbps')
        updated_chol = request.form.get('updated_chol')
        updated_fbs = request.form.get('updated_fbs')
        updated_restecg = request.form.get('updated_restecg')
        updated_thalach = request.form.get('updated_thalach')
        updated_exang = request.form.get('updated_exang')
        updated_oldpeak = request.form.get('updated_oldpeak')
        updated_slope = request.form.get('updated_slope')
        updated_ca = request.form.get('updated_ca')
        updated_thal = request.form.get('updated_thal')
        

        # Update the Heart record
        customer_heart.age = updated_age
        customer_heart.sex = updated_sex
        customer_heart.cp = updated_cp
        customer_heart.trestbps = updated_trestbps
        customer_heart.chol = updated_chol
        customer_heart.fbs = updated_fbs
        customer_heart.restecg = updated_restecg
        customer_heart.thalach = updated_thalach
        customer_heart.exang = updated_exang
        customer_heart.oldpeak = updated_oldpeak
        customer_heart.slope = updated_slope
        customer_heart.ca = updated_ca
        customer_heart.thal = updated_thal

        # Commit the changes to the database
        db.session.commit()

        flash('Heart profile updated successfully', 'success')

    return render_template('heart_profile.html', customer=customer, customer_heart=customer_heart)



@app.route('/liver_profile', methods=['GET', 'POST'])
def liver_profile():
    customer = get_logged_in_customer()

    if not customer:
        flash('Please log in to view your liver profile.', 'error')
        return redirect(url_for('login'))

    customer_liver = Liver.query.filter_by(accountid=customer.accountid).first()

    if request.method == 'POST':
        # Retrieve the updated values from the form
        updated_age = request.form.get('updated_age')
        updated_gender = request.form.get('updated_gender')
        updated_totalbilirubin = request.form.get('updated_totalbilirubin')
        updated_directbilirubin = request.form.get('updated_directbilirubin')
        updated_alkalinephosphotase = request.form.get('updated_alkalinephosphotase')
        updated_alamineamint = request.form.get('updated_alamineamint')
        updated_aspartateamint = request.form.get('updated_aspartateamint')
        updated_totalproteins = request.form.get('updated_totalproteins')
        updated_albumin = request.form.get('updated_albumin')
        updated_aandgratio = request.form.get('updated_aandgratio')

        # Update the Liver record
        customer_liver.age = updated_age
        customer_liver.gender = updated_gender
        customer_liver.totalbilirubin = updated_totalbilirubin
        customer_liver.directbilirubin = updated_directbilirubin
        customer_liver.alkalinephosphotase = updated_alkalinephosphotase
        customer_liver.alamineamint = updated_alamineamint
        customer_liver.aspartateamint = updated_aspartateamint
        customer_liver.totalproteins = updated_totalproteins
        customer_liver.albumin = updated_albumin
        customer_liver.aandgratio = updated_aandgratio

        # Commit the changes to the database
        db.session.commit()

        flash('Liver profile updated successfully', 'success')

    return render_template('liver_profile.html', customer=customer, customer_liver=customer_liver)


# Diabetes Profile
@app.route('/diabetes_profile', methods=['GET', 'POST'])
def diabetes_profile():
    customer = get_logged_in_customer()

    if not customer:
        flash('Please log in to view your diabetes profile.', 'error')
        return redirect(url_for('login'))

    customer_diabetes = Diabetes.query.filter_by(accountid=customer.accountid).first()

    if request.method == 'POST':
        # Retrieve the updated values from the form
        updated_pregnancies = request.form.get('updated_pregnancies')
        updated_glucose = request.form.get('updated_glucose')
        updated_bloodpressure = request.form.get('updated_bloodpressure')
        updated_skinthickness = request.form.get('updated_skinthickness')
        updated_insulin = request.form.get('updated_insulin')
        updated_bmi = request.form.get('updated_bmi')
        updated_diabetespedigreefunction = request.form.get('updated_diabetespedigreefunction')
        updated_age = request.form.get('updated_age')


        # Update the Diabetes record
        customer_diabetes.pregnancies = updated_pregnancies
        customer_diabetes.glucose = updated_glucose
        customer_diabetes.bloodpressure = updated_bloodpressure
        customer_diabetes.skinthickness = updated_skinthickness
        customer_diabetes.insulin = updated_insulin
        customer_diabetes.bmi = updated_bmi
        customer_diabetes.diabetespedigreefunction = updated_diabetespedigreefunction
        customer_diabetes.age = updated_age


        # Commit the changes to the database
        db.session.commit()

        flash('Diabetes profile updated successfully', 'success')

    return render_template('diabetes_profile.html', customer=customer, customer_diabetes=customer_diabetes)

'''---------------------------------------- end ------------------------------------'''



# Assuming 'heartmodel' is a trained model loaded before this point

@app.route('/predictheart', methods=['GET', 'POST'])
def predictheart():
    if request.method == 'POST':
        input_features = [[float(x) for x in request.form.values()]]
        scaler = StandardScaler()
        scaler.fit(input_features)

        input_features= heartscaler.transform(input_features)

        features_name = ["age", "sex", "cp", "trestbps", "chol", "fbs",
                         "restecg", "thalach", "exang", "oldpeak", "slope", "ca",
                         "thal"]

        df = pd.DataFrame(input_features, columns=features_name)

        # Assuming 'heartmodel' is a trained model loaded before this point
        output = heartmodel.predict_proba(df)
        
        # Assuming 'heartmodel' returns a tuple with the prediction at index 1
        prob[0] = output[0][0]

        """--------------------- database -----------------------"""
        # Store the input features and prediction result in the Heart table
        customer = get_logged_in_customer()
        customer_heart = Heart.query.filter_by(accountid=customer.accountid).first()

         # Convert form values to appropriate data types
        customer_heart.age = int(request.form.get('age'))
        customer_heart.sex = request.form.get('sex')
        customer_heart.cp = int(request.form.get('cp'))
        customer_heart.trestbps = int(request.form.get('trestbps'))
        customer_heart.chol = int(request.form.get('chol'))
        customer_heart.fbs = int(request.form.get('fbs'))
        customer_heart.restecg = int(request.form.get('restecg'))
        customer_heart.thalach = int(request.form.get('thalach'))
        customer_heart.exang = int(request.form.get('exang'))
        customer_heart.oldpeak = float(request.form.get('oldpeak'))
        customer_heart.slope = int(request.form.get('slope'))
        customer_heart.ca = int(request.form.get('ca'))
        customer_heart.thal = int(request.form.get('thal'))
        customer_heart.heartrisk = prob[0]

        db.session.commit()
        """------------------------- end --------------------------"""

        res_val = f"{prob[0] * 100:.2f}%"

        return render_template('heart_result.html', prediction_text=res_val)

    # Handle GET request (display the form)
    return render_template('heart_form.html')


@app.route('/predictDiabetes', methods=['GET', 'POST'])
def predict_diabetes():
    if request.method == 'POST':
        input_features = [float(x) for x in request.form.values()]

        features_name = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI",
                         "DiabetesPedigreeFunction", "Age"]

        df = pd.DataFrame([input_features], columns=features_name)

        # Assuming 'diabetesmodel' is a trained model loaded before this point
        
        output = diabetesmodel.predict_proba(df)
        
        # Assuming 'diabetesmodel' returns a tuple with the prediction at index 1
        prob[1] = output[0][1]



        """--------------------- database -----------------------"""
        # Store the input features and prediction result in the Diabetes table
        customer = get_logged_in_customer()
        customer_diabetes = Diabetes.query.filter_by(accountid=customer.accountid).first()


        # Update the fields
        customer_diabetes.pregnancies = int(request.form.get('pregnancies'))
        customer_diabetes.glucose = int(request.form.get('glucose'))
        customer_diabetes.bloodpressure = int(request.form.get('bloodpressure'))
        customer_diabetes.skinthickness = int(request.form.get('skinthickness'))
        customer_diabetes.insulin = int(request.form.get('insulin'))
        customer_diabetes.bmi = float(request.form.get('bmi'))
        customer_diabetes.diabetespedigreefunction = float(request.form.get('diabetespedigreefunction'))
        customer_diabetes.age = int(request.form.get('age'))
        customer_diabetes.diabetesrisk=prob[1]

        db.session.commit()
        """------------------------- end --------------------------"""

        res_val = f"{int(prob[1]* 100)}"
        nonres = f"{int((1 - prob[1])* 100)}"

        return render_template('diabetes_result.html', prediction_text=res_val, nonpred = nonres)

    # Handle GET request (display the form)
    return render_template('diabetes_form.html')

@app.route('/predictLiverDisease', methods=['GET', 'POST'])
def predict_liver_disease():
    if request.method == 'POST':
        # Extracting input features from the form
        input_features = [[float(x) for x in request.form.values()]]

        features_name = ["Age", "Gender", "Total_Bilirubin", "Direct_Bilirubin", "Alkaline_Phosphotase",
                         "Alamine_Aminotransferase", "Aspartate_Aminotransferase", "Total_Protiens",
                         "Albumin", "Albumin_and_Globulin_Ratio"]
        
        input_features= liverscaler.transform(input_features)

        df = pd.DataFrame(input_features, columns=features_name)

        # Assuming 'livermodel' returns a binary prediction (0 or 1)
        output = livermodel.predict_proba(df)
        
        # Assuming 'diabetesmodel' returns a tuple with the prediction at index 1
        prob[2] = output[0][1]

        """--------------------- database -----------------------"""
        # Store the input features and prediction result in the Liver table
        customer = get_logged_in_customer()
        customer_liver = Liver.query.filter_by(accountid=customer.accountid).first()
        customer_liver.age = int(request.form.get('age'))
        customer_liver.gender = request.form.get('gender')
        customer_liver.totalbilirubin = float(request.form.get('totalbilirubin'))
        customer_liver.directbilirubin = float(request.form.get('directbilirubin'))
        customer_liver.alkalinephosphotase = int(request.form.get('alkalinephosphotase'))
        customer_liver.alamineamint = int(request.form.get('alamineamint'))
        customer_liver.aspartateamint = int(request.form.get('aspartateamint'))
        customer_liver.totalproteins = float(request.form.get('totalproteins'))
        customer_liver.albumin = float(request.form.get('albumin'))
        customer_liver.aandgratio = float(request.form.get('aandgratio'))

        db.session.commit()
        """------------------------- end --------------------------"""

        res_val = f"{prob[2] * 100:.2f}% "

        return render_template('liverdisease_result.html', prediction_text=res_val)

    # Handle GET request (display the form)
    return render_template('liverdisease_form.html')

@app.route('/final_report', methods=['GET'])
def final_report():
    # Assuming 'heart_prob', 'diabetes_prob', and 'liver_prob' are the probabilities from the models

    # Calculate the total insurance amount
    total_insurance_amount = sum(prob)* 100

    customer = get_logged_in_customer()

    if not customer:
        flash('Please log in to view the final report.', 'error')
        return redirect(url_for('login'))

    # Retrieve the corresponding records from Heart, Diabetes, Liver tables
    customer_heart = Heart.query.filter_by(accountid=customer.accountid).first()
    customer_diabetes = Diabetes.query.filter_by(accountid=customer.accountid).first()
    customer_liver = Liver.query.filter_by(accountid=customer.accountid).first()

    # Calculate the total insurance amount
    total_insurance_amount = 2 * customer_heart.age + sum(prob) * 200

    if total_insurance_amount <= 500:
        return  render_template('website2-1.html', customer=customer, 
                           customer_heart=customer_heart, 
                           customer_diabetes=customer_diabetes, 
                           customer_liver=customer_liver,
                           total_insurance_amount=total_insurance_amount)
    elif total_insurance_amount <= 1000:
        return  render_template('website2-2.html', customer=customer, 
                    customer_heart=customer_heart, 
                    customer_diabetes=customer_diabetes, 
                    customer_liver=customer_liver,
                    total_insurance_amount=total_insurance_amount)
    else:
        return  render_template('website2-3.html', customer=customer, 
                    customer_heart=customer_heart, 
                    customer_diabetes=customer_diabetes, 
                    customer_liver=customer_liver,
                    total_insurance_amount=total_insurance_amount)

    #return render_template('final_report.html', total_insurance_amount=total_insurance_amount)


"""------------------------------  profile 

@app.route('/heart_form', methods=['GET', 'POST'])
def heart_form():
    customer = get_logged_in_customer()

    if not customer:
        flash('Please log in to fill the form.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
         # Extracting input features from the form
        input_features = [float(x) for x in request.form.values()]

        features_name = ["age", "sex", "cp", "trestbps", "chol", "fbs",
                         "restecg", "thalach", "exang", "oldpeak", "slope", "ca",
                         "thal"]

        df = pd.DataFrame([input_features], columns=features_name)

        # Assuming 'heartmodel' is a trained model loaded before this point
        output = heartmodel.predict_proba(df)
        
        # Assuming 'heartmodel' returns a tuple with the prediction at index 1
        heart_risk = output[0][1]

        # Create a new Heart record and store it in the Heart table
        heart_data = Heart(
            accountid=customer.accountid,
            age=request.form.get('age'),
            sex=request.form.get('sex'),
            cp=request.form.get('cp'),
            trestbps=request.form.get('trestbps'),
            chol=request.form.get('chol'),
            fbs=request.form.get('fbs'),
            restecg=request.form.get('restecg'),
            thalach=request.form.get('thalach'),
            exang=request.form.get('exang'),
            oldpeak=request.form.get('oldpeak'),
            slope=request.form.get('slope'),
            ca=request.form.get('ca'),
            thal=request.form.get('thal'),
            heartrisk=heart_risk
        )

        db.session.add(heart_data)
        db.session.commit()

        flash('Heart form submitted successfully', 'success')
        return redirect(url_for('heart_result'))

    return render_template('heart_form.html', customer=customer)

@app.route('/diabetes_form', methods=['GET', 'POST'])
def diabetes_form():
    customer = get_logged_in_customer()

    if not customer:
        flash('Please log in to fill the form.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Extracting input features from the form
        input_features = [float(x) for x in request.form.values()]

        features_name = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI",
                         "DiabetesPedigreeFunction", "Age"]

        df = pd.DataFrame([input_features], columns=features_name)

        # Assuming 'diabetesmodel' is a trained model loaded before this point
        output = diabetesmodel.predict_proba(df)
        
        # Assuming 'diabetesmodel' returns a tuple with the prediction at index 1
        diabetes_risk = output[0][1]

        # Create a new Diabetes record and store it in the Diabetes table
        diabetes_data = Diabetes(
            accountid=customer.accountid,
            pregnancies=request.form.get('pregnancies'),
            glucose=request.form.get('glucose'),
            bloodpressure=request.form.get('bloodpressure'),
            skinthickness=request.form.get('skinthickness'),
            insulin=request.form.get('insulin'),
            bmi=request.form.get('bmi'),
            diabetespedigreefunction=request.form.get('diabetespedigreefunction'),
            age=request.form.get('age'),
            diabetesrisk=diabetes_risk
        )

        db.session.add(diabetes_data)
        db.session.commit()

        flash('Diabetes form submitted successfully', 'success')
        return redirect(url_for('diabetes_result'))

    return render_template('diabetes_form.html', customer=customer)

@app.route('/liverdisease_form', methods=['GET', 'POST'])
def liverdisease_form():
    customer = get_logged_in_customer()

    if not customer:
        flash('Please log in to fill the form.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Extracting input features from the form
        input_features = [float(x) for x in request.form.values()]

        features_name = ["Age", "Gender", "Total_Bilirubin", "Direct_Bilirubin", "Alkaline_Phosphotase",
                         "Alamine_Aminotransferase", "Aspartate_Aminotransferase", "Total_Protiens",
                         "Albumin", "Albumin_and_Globulin_Ratio"]
        
        df = pd.DataFrame([input_features], columns=features_name)

        # Assuming 'livermodel' is a trained model loaded before this point
        output = livermodel.predict_proba(df)
        
        # Assuming 'livermodel' returns a tuple with the prediction at index 1
        liver_risk = output[0][1]

        # Create a new Liver record and store it in the Liver table
        liver_data = Liver(
            accountid=customer.accountid,
            age=request.form.get('age'),
            gender=request.form.get('gender'),
            totalbilirubin=request.form.get('totalbilirubin'),
            directbilirubin=request.form.get('directbilirubin'),
            alkalinephosphotase=request.form.get('alkalinephosphotase'),
            alamineamint=request.form.get('alamineamint'),
            aspartateamint=request.form.get('aspartateamint'),
            totalproteins=request.form.get('totalproteins'),
            albumin=request.form.get('albumin'),
            aandgratio=request.form.get('aandgratio'),
            liverrisk=liver_risk
        )

        db.session.add(liver_data)
        db.session.commit()

        flash('Liver disease form submitted successfully', 'success')
        return redirect(url_for('liverdisease_result'))

    return render_template('liverdisease_form.html', customer=customer)
-----------------------------"""

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
