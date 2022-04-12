import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

from sklearn.svm import SVC

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from sklearn.metrics import accuracy_score

random_state = 42

class Builder:
    def __init__(self, X_train: np.ndarray, y_train: np.ndarray):
        self.X_train = X_train
        self.y_train = y_train

    def get_subsample(self, df_share: int):
        """
        1. Copy train dataset
        2. Shuffle data (don't miss the connection between X_train and y_train)
        3. Return df_share %-subsample of X_train and y_train
        """
        X = self.X_train.copy()
        y = self.y_train.copy()

        X, y = shuffle(X, y, random_state=random_state)

        num_to_take = int(len(y) * df_share / 100.0)

        return X[:num_to_take, :], y[:num_to_take]

if __name__ == "__main__":
    
    """
    1. Load iris dataset
    2. Shuffle data and divide into train / test.
    """
    train_size = 0.7

    X, y = load_iris(return_X_y=True)
    X, y = shuffle(X, y, random_state=random_state)

    num_train = int(len(y) * train_size)

    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=train_size, random_state=random_state)

    # print(f"Train size = {len(y_train)}, Test size = {len(y_test)}")

    clf = make_pipeline(StandardScaler(), SVC(gamma='auto'))

    pattern_item = Builder(X_train, y_train)
    for df_share in range(10, 101, 10):
        curr_X_train, curr_y_train = pattern_item.get_subsample(df_share)

        clf.fit(curr_X_train, curr_y_train)

        y_test_pred = clf.predict(X_test)

        accuracy = accuracy_score(y_test, y_test_pred)

        print(f"df_share = {df_share}%, accuracy on test = {accuracy}")
        
    """
    1. Preprocess curr_X_train, curr_y_train in the way you want
    2. Train Linear Regression on the subsample
    3. Save or print the score to check how df_share affects the quality
    """

# Outputs:
# df_share = 10%, accuracy on test = 0.8444444444444444
# df_share = 20%, accuracy on test = 0.9333333333333333
# df_share = 30%, accuracy on test = 0.9555555555555556
# df_share = 40%, accuracy on test = 0.9555555555555556
# df_share = 50%, accuracy on test = 0.9777777777777777
# df_share = 60%, accuracy on test = 0.9777777777777777
# df_share = 70%, accuracy on test = 0.9777777777777777
# df_share = 80%, accuracy on test = 0.9777777777777777
# df_share = 90%, accuracy on test = 0.9777777777777777
# df_share = 100%, accuracy on test = 0.9777777777777777