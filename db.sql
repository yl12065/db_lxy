CREATE TABLE customer (
    accountid SERIAL PRIMARY KEY,
    password VARCHAR(255),
    custname VARCHAR(255),
    email VARCHAR(255),
    address TEXT
);

CREATE TABLE heart (
    accountid INTEGER REFERENCES customer(accountid),
    age INTEGER,
    sex VARCHAR(10),
    cp INTEGER,
    trestbps INTEGER,
    chol INTEGER,
    fbs INTEGER,
    restecg INTEGER,
    thalach INTEGER,
    exang INTEGER,
    oldpeak FLOAT,
    slope INTEGER,
    ca INTEGER,
    thal INTEGER,
    heartrisk FLOAT,
    PRIMARY KEY (accountid)
);

CREATE TABLE diabetes (
    accountid INTEGER REFERENCES customer(accountid),
    pregnancies FLOAT,
    glucose INTEGER,
    bloodpressure INTEGER,
    skinthickness INTEGER,
    insulin INTEGER,
    bmi FLOAT,
    diabetespedigreefunction FLOAT,
    age INTEGER,
    diabetesrisk FLOAT,
    PRIMARY KEY (accountid)
);

CREATE TABLE liver (
    accountid INTEGER REFERENCES customer(accountid),
    age INTEGER,
    gender VARCHAR(10),
    totalbilirubin FLOAT,
    directbilirubin FLOAT,
    alkalinephosphotase INTEGER,
    alamineamint INTEGER,
    aspartateamint INTEGER,
    totalproteins FLOAT,
    albumin FLOAT,
    aandgratio FLOAT,
    liverrisk FLOAT,
    PRIMARY KEY (accountid)
);
