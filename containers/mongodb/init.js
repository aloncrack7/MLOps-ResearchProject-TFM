db = db.getSiblingDB('mlflow');
db.init.insertOne({created: true, timestamp: new Date()});