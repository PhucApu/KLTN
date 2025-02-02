import math
import random

        

# Hàm kích hoạt sigmoid
def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def sigmoid_derivative(x):
    sig = sigmoid(x)
    return sig * (1 - sig)

# Hàm chuẩn hóa và khôi phục giá trị
def normalize(data, min_val, max_val):
    return [(d - min_val) / (max_val - min_val) for d in data]

def denormalize(data, min_val, max_val):
    return [d * (max_val - min_val) + min_val for d in data]

# Dữ liệu huấn luyện
X = [[1, 1], [2, 2], [2, 3], [3, 3]]  # Đầu vào
y_true = [2, 4, 5, 6]  # Đầu ra mục tiêu

# Chuẩn hóa dữ liệu
x_min = min(min(row) for row in X)
x_max = max(max(row) for row in X)
X_normalized = [[(xi - x_min) / (x_max - x_min) for xi in row] for row in X]

y_min, y_max = min(y_true), max(y_true)
y_true_normalized = normalize(y_true, y_min, y_max)

# Khởi tạo trọng số và bias
random.seed(42)
weights_input_hidden = [[random.uniform(-0.5, 0.5) for _ in range(2)] for _ in range(4)]
bias_hidden = [random.uniform(-0.5, 0.5) for _ in range(4)]
weights_hidden_output = [random.uniform(-0.5, 0.5) for _ in range(4)]
bias_output = random.uniform(-0.5, 0.5)

# Tốc độ học
learning_rate = 0.04
epochs = 60000

# Huấn luyện
for epoch in range(epochs):
    total_loss = 0

    for x, y in zip(X_normalized, y_true_normalized):
        # Lan truyền xuôi
        hidden_inputs = [sum(w * xi for w, xi in zip(weights, x)) + b for weights, b in zip(weights_input_hidden, bias_hidden)]
        hidden_outputs = [sigmoid(h) for h in hidden_inputs]
        output_input = sum(w * h for w, h in zip(weights_hidden_output, hidden_outputs)) + bias_output
        output = sigmoid(output_input)

        # Tính lỗi
        loss = (y - output) ** 2
        total_loss += loss

        # Lan truyền ngược
        output_error = 2 * (output - y) * sigmoid_derivative(output_input)
        grad_weights_hidden_output = [output_error * h for h in hidden_outputs]
        grad_bias_output = output_error

        hidden_errors = [output_error * w * sigmoid_derivative(h) for w, h in zip(weights_hidden_output, hidden_inputs)]
        grad_weights_input_hidden = [[he * xi for xi in x] for he in hidden_errors]
        grad_bias_hidden = hidden_errors

        # Cập nhật trọng số và bias
        weights_hidden_output = [w - learning_rate * gw for w, gw in zip(weights_hidden_output, grad_weights_hidden_output)]
        bias_output -= learning_rate * grad_bias_output
        for i in range(4):
            weights_input_hidden[i] = [w - learning_rate * gw for w, gw in zip(weights_input_hidden[i], grad_weights_input_hidden[i])]
            bias_hidden[i] -= learning_rate * grad_bias_hidden[i]

    # In lỗi sau mỗi 1000 epoch
    if (epoch + 1) % 1000 == 0:
        predictions = []
        for x in X_normalized:
            hidden_inputs = [sum(w * xi for w, xi in zip(weights, x)) + b for weights, b in zip(weights_input_hidden, bias_hidden)]
            hidden_outputs = [sigmoid(h) for h in hidden_inputs]
            output_input = sum(w * h for w, h in zip(weights_hidden_output, hidden_outputs)) + bias_output
            output = sigmoid(output_input)
            prediction = denormalize([output], y_min, y_max)[0]
            predictions.append(prediction)
        print(f"Epoch {epoch + 1}, Loss: {total_loss / len(X):.4f}, Predictions: {predictions}")

# Kiểm tra kết quả sau khi học
print("\nFinal Predictions:")
for x in X_normalized:
    hidden_inputs = [sum(w * xi for w, xi in zip(weights, x)) + b for weights, b in zip(weights_input_hidden, bias_hidden)]
    hidden_outputs = [sigmoid(h) for h in hidden_inputs]
    output_input = sum(w * h for w, h in zip(weights_hidden_output, hidden_outputs)) + bias_output
    output = sigmoid(output_input)
    prediction = denormalize([output], y_min, y_max)[0]
    print(f"Input: {x}, Predicted Output: {prediction:.2f}")


# Hàm cho người dùng nhập vào sau khi mô hình học
def thinks(values):
    pass

def learn(valuesX,valueY):
    pass

if __name__ == "__main__":
    pass