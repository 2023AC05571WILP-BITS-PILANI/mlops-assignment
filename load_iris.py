from sklearn.datasets import load_iris
import pandas as pd

# Load the Iris dataset
data = load_iris()

# Create a DataFrame with feature data
df = pd.DataFrame(data.data, columns=data.feature_names)

# Add the target column to the DataFrame
df['target'] = data.target

# Display the first few rows of the DataFrame
print(df.head())
