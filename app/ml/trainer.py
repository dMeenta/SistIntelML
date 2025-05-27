import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

X = np.random.randint(1, 6, size=(1000, 60))
y = np.random.choice(['R', 'I', 'A', 'S', 'E', 'C'], size=(1000,))

model = RandomForestClassifier()
model.fit(X, y)

os.makedirs("app/ml", exist_ok=True)
with open("app/ml/riasec_model.pkl", "wb") as f:
    pickle.dump(model, f)
