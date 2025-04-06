import numpy as np

def linear_regression(X, y):
    """
    Implement linear regression using least squares method.
    
    Parameters:
    X (list): Input features
    y (list): Target values
    
    Returns:
    list: [weights, bias]
    """
    # Convert inputs to numpy arrays for easier computation
    X = np.array(X)
    y = np.array(y)
    
    # Calculate the mean of X and y
    X_mean = np.mean(X)
    y_mean = np.mean(y)
    
    # Calculate the slope (weights) using the formula: m = Σ((x - x̄)(y - ȳ)) / Σ((x - x̄)²)
    numerator = np.sum((X - X_mean) * (y - y_mean))
    denominator = np.sum((X - X_mean) ** 2)
    weights = float(numerator / denominator)  # Convert to Python float
    
    # Calculate the intercept (bias) using the formula: b = ȳ - m * x̄
    bias = float(y_mean - weights * X_mean)  # Convert to Python float
    
    return [weights, bias]  # Return as list instead of tuple

def predict(X, weights, bias):
    """
    Make predictions using the trained linear regression model.
    
    Parameters:
    X (list): Input features
    weights (float): Slope of the line
    bias (float): Intercept of the line
    
    Returns:
    list: Predicted values
    """
    # Convert input to numpy array for vectorized operations
    X = np.array(X)
    
    # Calculate predictions using the formula: y = mx + b
    predictions = weights * X + bias
    
    return predictions.tolist()

# Test the implementation
if __name__ == "__main__":
    # Test case 1
    X1 = [1, 2, 3]
    y1 = [2, 4, 6]
    result1 = linear_regression(X1, y1)
    print(f"Test case 1:")
    print(f"Expected: [2.0, 0.0]")
    print(f"Got: {result1}")
    
    # Test case 2
    X2 = [0, 1, 2]
    y2 = [1, 3, 5]
    result2 = linear_regression(X2, y2)
    print(f"\nTest case 2:")
    print(f"Expected: [2.0, 1.0]")
    print(f"Got: {result2}") 