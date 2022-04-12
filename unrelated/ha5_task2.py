import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

from sklearn.svm import SVC

from sklearn.ensemble import RandomForestClassifier

from sklearn.neighbors import KNeighborsClassifier

from sklearn.naive_bayes import GaussianNB

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from sklearn.metrics import accuracy_score

random_state = 42

class Module:
    def __init__(self, classifiers) -> None:
        """
        Initialize a class item with a list of classificators
        """
        self.classifiers = classifiers
        self.count = len(self.classifiers)

    def fit(self, X, y):
        """
        Fit classifiers from the initialization stage
        """
        for classifier in self.classifiers:
            classifier.fit(X, y)

    def predict(self, X):
        """
        Get predicts from all the classifiers and return
        the most popular answers
        """
        y_preds = []

        for classifier in self.classifiers:
            y_preds.append(classifier.predict(X))

        y_preds = np.stack(y_preds)
        
        # Most popular guess for each item. +0.5 because numpy can't round properly
        return np.floor(y_preds.sum(axis=0) / self.count + 0.5).astype(int) 
        

if __name__ == "__main__":
    """
    1. Load iris dataset
    2. Shuffle data and divide into train / test.
    3. Prepare classifiers to initialize <StructuralPatternName> class.
    4. Train the ensemble
    """
    train_size = 0.7

    X, y = load_iris(return_X_y=True)
    X, y = shuffle(X, y, random_state=random_state)

    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=train_size, random_state=random_state)

    classifiers = [make_pipeline(StandardScaler(), SVC(gamma='auto', random_state=random_state)),
                   make_pipeline(StandardScaler(), RandomForestClassifier(max_depth=5, random_state=random_state)),
                   make_pipeline(StandardScaler(), KNeighborsClassifier(7)),
                   make_pipeline(StandardScaler(), GaussianNB()),]

    ensemble = Module(classifiers)

    ensemble.fit(X_train, y_train)

    y_pred = ensemble.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)

    print(f"Accuracy score achieved with ensemble = {accuracy}")

    # Outputs:
    # Accuracy score achieved with ensemble = 0.9777777777777777