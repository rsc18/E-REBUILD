# Import SQLAlchemy database defined in erebuild/__init__.py
from erebuild import E_DB
from datetime import datetime

# Database tables
class UserGameLogs(E_DB.Model):
    """
    table to hold observables per user per game level.
    """
    __tablename__ = "gameobservables"

    # User/level info
    id = E_DB.Column(E_DB.Integer, primary_key=True)
    user_email = E_DB.Column(E_DB.String, nullable=False)
    level_id = E_DB.Column(E_DB.String, nullable=False)
    play_time = E_DB.Column(E_DB.DateTime, default=datetime.utcnow)

    # Observables
    Angle = E_DB.Column(E_DB.Float)
    AssignmentComplete = E_DB.Column(E_DB.Boolean)
    BuildingComplete = E_DB.Column(E_DB.Boolean)
    Collect = E_DB.Column(E_DB.Float)
    Distance = E_DB.Column(E_DB.Float)
    EmptyInventory = E_DB.Column(E_DB.Integer)
    FillArea2D = E_DB.Column(E_DB.Float)
    FillVolume = E_DB.Column(E_DB.Float)
    Fold3D = E_DB.Column(E_DB.Float)
    LevelComplete = E_DB.Column(E_DB.Boolean)
    LivingArea = E_DB.Column(E_DB.Float)
    MaterialCredits = E_DB.Column(E_DB.Float)
    NumAssignments = E_DB.Column(E_DB.Integer)
    NumBlocks = E_DB.Column(E_DB.Integer)
    NumFailedAssignments = E_DB.Column(E_DB.Integer)
    NumFamilyCollected = E_DB.Column(E_DB.Integer)
    NumTrades = E_DB.Column(E_DB.Integer)
    NumWrong = E_DB.Column(E_DB.Integer)
    Paint = E_DB.Column(E_DB.Float)
    PercentLost = E_DB.Column(E_DB.Float)
    PlaceItems = E_DB.Column(E_DB.Float)
    ProtectFloor = E_DB.Column(E_DB.Float)
    Size = E_DB.Column(E_DB.Float)
    Time = E_DB.Column(E_DB.Float)
    TotalLost = E_DB.Column(E_DB.Float)


class UserCompetency(E_DB.Model):
    __tablename__ = "usercompetency"

    # User/level info
    id = E_DB.Column(E_DB.Integer, primary_key=True)
    user_email = E_DB.Column(E_DB.String, nullable=False)
    level_id = E_DB.Column(E_DB.String, nullable=False)
    play_time = E_DB.Column(E_DB.DateTime, nullable=False)

    # Competencies
    competency = E_DB.Column(E_DB.Text, nullable=False)


class UserInfo(E_DB.Model):
    """ Table to store login information of all types of users
    """
    # the table name in the database
    __tablename__ = "user_info"

    #user_id = E_DB.Column(E_DB.Integer, primary_key=True)
    #user_email = E_DB.Column(E_DB.String, nullable=False)
    #user_password = E_DB.Column(E_DB.String, nullable=False)
    #user_class = E_DB.Column(E_DB.String, nullable=False)
    #user_school = E_DB.Column(E_DB.String)
    #user_firstname = E_DB.Column(E_DB.String)
    #user_lastname = E_DB.Column(E_DB.String)

    id = E_DB.Column(E_DB.Integer, nullable=False, primary_key=True)
    user_email = E_DB.Column(E_DB.VARCHAR, nullable=False)
    user_password = E_DB.Column(E_DB.VARCHAR, nullable=False)
    user_firstname = E_DB.Column(E_DB.Text)
    user_lastname = E_DB.Column(E_DB.Text)
    user_class = E_DB.Column(E_DB.Text)
    user_school = E_DB.Column(E_DB.Text)

    # 0 = Admin --> create teacher registration links
    # 1 = Teacher --> view stats of a class
    # 2 = User --> regular user who can view stats of ones game play only
    user_type = E_DB.Column(E_DB.Integer, nullable=False)


class TeacherRegistrationCodes(E_DB.Model):
    """ Table to store active registration codes of teachers
    """
    __tablename__ = "teacherregistrationcodes"

    id = E_DB.Column(E_DB.Integer, primary_key=True)
    code = E_DB.Column(E_DB.String, nullable=False)


class LatestBayesNet(E_DB.Model):
    """
    Table to store the latest Bayesian Network for each user.
    """
    __tablename__ = "latestbayesnet"

    user_email = E_DB.Column(E_DB.String, nullable=False, primary_key=True)
    bayesnet = E_DB.Column(E_DB.Text, nullable=False)

