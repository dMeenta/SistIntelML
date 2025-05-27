import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle
import os

X = np.random.randint(1, 6, size=(1000, 60))
y = np.random.choice(['R', 'I', 'A', 'S', 'E', 'C'], size=(1000,))

X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y)
model = RandomForestClassifier()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

os.makedirs("app/models", exist_ok=True)
with open("app/models/riasec_model.pkl", "wb") as f:
    pickle.dump(model, f)
