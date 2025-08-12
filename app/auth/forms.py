from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from app.models import User

# Country codes for phone numbers
COUNTRY_CODES = [
    ('+233', 'Ghana (+233)'),
    ('+234', 'Nigeria (+234)'),
    ('+27', 'South Africa (+27)'),
    ('+254', 'Kenya (+254)'),
    ('+256', 'Uganda (+256)'),
    ('+255', 'Tanzania (+255)'),
    ('+251', 'Ethiopia (+251)'),
    ('+20', 'Egypt (+20)'),
    ('+212', 'Morocco (+212)'),
    ('+216', 'Tunisia (+216)'),
    ('+1', 'United States (+1)'),
    ('+44', 'United Kingdom (+44)'),
    ('+33', 'France (+33)'),
    ('+49', 'Germany (+49)'),
    ('+39', 'Italy (+39)'),
    ('+34', 'Spain (+34)'),
    ('+31', 'Netherlands (+31)'),
    ('+32', 'Belgium (+32)'),
    ('+41', 'Switzerland (+41)'),
    ('+46', 'Sweden (+46)'),
    ('+47', 'Norway (+47)'),
    ('+45', 'Denmark (+45)'),
    ('+358', 'Finland (+358)'),
    ('+48', 'Poland (+48)'),
    ('+420', 'Czech Republic (+420)'),
    ('+36', 'Hungary (+36)'),
    ('+43', 'Austria (+43)'),
    ('+30', 'Greece (+30)'),
    ('+351', 'Portugal (+351)'),
    ('+353', 'Ireland (+353)'),
    ('+61', 'Australia (+61)'),
    ('+64', 'New Zealand (+64)'),
    ('+81', 'Japan (+81)'),
    ('+82', 'South Korea (+82)'),
    ('+86', 'China (+86)'),
    ('+91', 'India (+91)'),
    ('+65', 'Singapore (+65)'),
    ('+60', 'Malaysia (+60)'),
    ('+66', 'Thailand (+66)'),
    ('+84', 'Vietnam (+84)'),
    ('+63', 'Philippines (+63)'),
    ('+62', 'Indonesia (+62)'),
    ('+880', 'Bangladesh (+880)'),
    ('+92', 'Pakistan (+92)'),
    ('+971', 'UAE (+971)'),
    ('+966', 'Saudi Arabia (+966)'),
    ('+972', 'Israel (+972)'),
    ('+90', 'Turkey (+90)'),
    ('+7', 'Russia (+7)'),
    ('+380', 'Ukraine (+380)'),
    ('+375', 'Belarus (+375)'),
    ('+371', 'Latvia (+371)'),
    ('+372', 'Estonia (+372)'),
    ('+370', 'Lithuania (+370)'),
    ('+421', 'Slovakia (+421)'),
    ('+386', 'Slovenia (+386)'),
    ('+385', 'Croatia (+385)'),
    ('+387', 'Bosnia and Herzegovina (+387)'),
    ('+389', 'North Macedonia (+389)'),
    ('+382', 'Montenegro (+382)'),
    ('+381', 'Serbia (+381)'),
    ('+359', 'Bulgaria (+359)'),
    ('+40', 'Romania (+40)'),
    ('+355', 'Albania (+355)'),
    ('+373', 'Moldova (+373)'),
    ('+995', 'Georgia (+995)'),
    ('+374', 'Armenia (+374)'),
    ('+994', 'Azerbaijan (+994)'),
    ('+93', 'Afghanistan (+93)'),
    ('+98', 'Iran (+98)'),
    ('+964', 'Iraq (+964)'),
    ('+962', 'Jordan (+962)'),
    ('+961', 'Lebanon (+961)'),
    ('+963', 'Syria (+963)'),
    ('+967', 'Yemen (+967)'),
    ('+968', 'Oman (+968)'),
    ('+974', 'Qatar (+974)'),
    ('+973', 'Bahrain (+973)'),
    ('+965', 'Kuwait (+965)'),
    ('+960', 'Maldives (+960)'),
    ('+977', 'Nepal (+977)'),
    ('+975', 'Bhutan (+975)'),
    ('+95', 'Myanmar (+95)'),
    ('+856', 'Laos (+856)'),
    ('+855', 'Cambodia (+855)'),
    ('+673', 'Brunei (+673)'),
    ('+670', 'East Timor (+670)'),
    ('+856', 'Laos (+856)'),
    ('+855', 'Cambodia (+855)'),
    ('+673', 'Brunei (+673)'),
    ('+670', 'East Timor (+670)'),
    ('+976', 'Mongolia (+976)'),
    ('+992', 'Tajikistan (+992)'),
    ('+996', 'Kyrgyzstan (+996)'),
    ('+998', 'Uzbekistan (+998)'),
    ('+993', 'Turkmenistan (+993)'),
    ('+994', 'Azerbaijan (+994)'),
    ('+374', 'Armenia (+374)'),
    ('+995', 'Georgia (+995)'),
    ('+373', 'Moldova (+373)'),
    ('+355', 'Albania (+355)'),
    ('+40', 'Romania (+40)'),
    ('+359', 'Bulgaria (+359)'),
    ('+381', 'Serbia (+381)'),
    ('+382', 'Montenegro (+382)'),
    ('+389', 'North Macedonia (+389)'),
    ('+387', 'Bosnia and Herzegovina (+387)'),
    ('+385', 'Croatia (+385)'),
    ('+386', 'Slovenia (+386)'),
    ('+421', 'Slovakia (+421)'),
    ('+370', 'Lithuania (+370)'),
    ('+372', 'Estonia (+372)'),
    ('+371', 'Latvia (+371)'),
    ('+375', 'Belarus (+375)'),
    ('+380', 'Ukraine (+380)'),
    ('+7', 'Russia (+7)'),
    ('+90', 'Turkey (+90)'),
    ('+972', 'Israel (+972)'),
    ('+966', 'Saudi Arabia (+966)'),
    ('+971', 'UAE (+971)'),
    ('+92', 'Pakistan (+92)'),
    ('+880', 'Bangladesh (+880)'),
    ('+62', 'Indonesia (+62)'),
    ('+63', 'Philippines (+63)'),
    ('+84', 'Vietnam (+84)'),
    ('+66', 'Thailand (+66)'),
    ('+60', 'Malaysia (+60)'),
    ('+65', 'Singapore (+65)'),
    ('+91', 'India (+91)'),
    ('+86', 'China (+86)'),
    ('+82', 'South Korea (+82)'),
    ('+81', 'Japan (+81)'),
    ('+64', 'New Zealand (+64)'),
    ('+61', 'Australia (+61)'),
    ('+353', 'Ireland (+353)'),
    ('+351', 'Portugal (+351)'),
    ('+30', 'Greece (+30)'),
    ('+43', 'Austria (+43)'),
    ('+36', 'Hungary (+36)'),
    ('+420', 'Czech Republic (+420)'),
    ('+48', 'Poland (+48)'),
    ('+358', 'Finland (+358)'),
    ('+45', 'Denmark (+45)'),
    ('+47', 'Norway (+47)'),
    ('+46', 'Sweden (+46)'),
    ('+41', 'Switzerland (+41)'),
    ('+32', 'Belgium (+32)'),
    ('+31', 'Netherlands (+31)'),
    ('+34', 'Spain (+34)'),
    ('+39', 'Italy (+39)'),
    ('+49', 'Germany (+49)'),
    ('+33', 'France (+33)'),
    ('+44', 'United Kingdom (+44)'),
    ('+1', 'United States (+1)'),
    ('+216', 'Tunisia (+216)'),
    ('+212', 'Morocco (+212)'),
    ('+20', 'Egypt (+20)'),
    ('+251', 'Ethiopia (+251)'),
    ('+255', 'Tanzania (+255)'),
    ('+256', 'Uganda (+256)'),
    ('+254', 'Kenya (+254)'),
    ('+27', 'South Africa (+27)'),
    ('+234', 'Nigeria (+234)'),
    ('+233', 'Ghana (+233)'),
]


class RegistrationForm(FlaskForm):
    """Form for user registration"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=50),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Username can only contain letters, numbers, and underscores')
    ])
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    country_code = SelectField('Country Code', choices=COUNTRY_CODES, default='+233')
    phone = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=9, max=15),
        Regexp(r'^[0-9]+$', message='Phone number can only contain numbers')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Validate that the username is not already taken"""
        user = User.query.filter_by(username=username.data.lower()).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different username.')
    
    def validate_email(self, email):
        """Validate that the email is not already registered"""
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')
    
    def validate_phone(self, phone):
        """Validate that the phone number is not already registered"""
        # Combine country code with phone number for validation
        country_code = self.country_code.data
        full_phone = f"{country_code}{phone.data}"
        user = User.query.filter_by(phone=full_phone).first()
        if user:
            raise ValidationError('Phone number already registered. Please use a different phone number.')


class LoginForm(FlaskForm):
    """Form for user login"""
    email = StringField('Email or Phone', validators=[
        DataRequired()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')