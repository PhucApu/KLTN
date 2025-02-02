import math
import random

class DataTrain:
    def __init__(self):
        self.inputX = [[1, 1], [2, 2], [2, 3], [3, 3], [1, 3], [1, 5], [3, 2], [6, 1], [2, 4]]
        self.outputY_true = [2, 4, 5, 6, 4, 6, 5, 7, 6]

        self.update_min_max()

    # Cập nhật min/max của dữ liệu
    def update_min_max(self):
        self.x_min = min(min(row) for row in self.inputX)
        self.x_max = max(max(row) for row in self.inputX)
        self.y_min = min(self.outputY_true)
        self.y_max = max(self.outputY_true)

    # Chuẩn hóa dữ liệu thành [0,1]
    def normalize(self, data, min_val, max_val):
        if isinstance(data[0], list):  # Nếu là danh sách 2D
            return [[(d - min_val) / (max_val - min_val) for d in row] for row in data]
        return [(d - min_val) / (max_val - min_val) for d in data]

    # Khôi phục dữ liệu từ chuẩn hóa
    def denormalize(self, data, min_val, max_val):
        return [d * (max_val - min_val) + min_val for d in data]

    # Kiểm tra định dạng dữ liệu
    def isDataFormat(self, dataString):
        x_values = dataString.split()
        if len(x_values) != 2:
            return False
        try:
            [int(i) for i in x_values]  # Kiểm tra nếu chuyển đổi thành số được
            return True
        except ValueError:
            return False

    # Thêm dữ liệu mới vào tập huấn luyện
    def addDataTrain(self, Xtrain, Ytrain):
       #      X_new = [int(i) for i in Xtrain.split()]
            Y_new = int(Ytrain)
            self.inputX.append(Xtrain)
            self.outputY_true.append(Y_new)
            self.update_min_max()  # Cập nhật min/max

    # Getter
    def getInputX(self):
        return self.inputX

    def getOutputY_true(self):
        return self.outputY_true

    def getX_ValueMax(self):
        return self.x_max

    def getX_ValueMin(self):
        return self.x_min

    def getY_ValueMax(self):
        return self.y_max

    def getY_ValueMin(self):
        return self.y_min


class NN:
    def __init__(self, learning_rate, epochs):
        random.seed(42)
        self.weights_input_hidden = [[random.uniform(-0.5, 0.5) for _ in range(2)] for _ in range(4)]
        self.bias_hidden = [random.uniform(-0.5, 0.5) for _ in range(4)]
        self.weights_hidden_output = [random.uniform(-0.5, 0.5) for _ in range(4)]
        self.bias_output = random.uniform(-0.5, 0.5)

        self.learning_rate = learning_rate
        self.epochs = epochs

    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x))

    def sigmoid_derivative(self, x):
        sig = self.sigmoid(x)
        return sig * (1 - sig)

    def train(self, dataTrain):
        dataX = dataTrain.getInputX()
        dataY = dataTrain.getOutputY_true()

        X_normalized = dataTrain.normalize(dataX, dataTrain.getX_ValueMin(), dataTrain.getX_ValueMax())
        y_normalized = dataTrain.normalize(dataY, dataTrain.getY_ValueMin(), dataTrain.getY_ValueMax())

        for epoch in range(self.epochs):
            total_loss = 0
            for x, y in zip(X_normalized, y_normalized):
                # Lan truyền xuôi
                hidden_inputs = [sum(w * xi for w, xi in zip(weights, x)) + b for weights, b in zip(self.weights_input_hidden, self.bias_hidden)]
                hidden_outputs = [self.sigmoid(h) for h in hidden_inputs]
                output_input = sum(w * h for w, h in zip(self.weights_hidden_output, hidden_outputs)) + self.bias_output
                output = self.sigmoid(output_input)

                # Tính lỗi
                loss = (y - output) ** 2
                total_loss += loss

                # Lan truyền ngược
                output_error = 2 * (output - y) * self.sigmoid_derivative(output_input)
                grad_weights_hidden_output = [output_error * h for h in hidden_outputs]
                grad_bias_output = output_error

                hidden_errors = [output_error * w * self.sigmoid_derivative(h) for w, h in zip(self.weights_hidden_output, hidden_inputs)]
                grad_weights_input_hidden = [[he * xi for xi in x] for he in hidden_errors]
                grad_bias_hidden = hidden_errors

                # Cập nhật trọng số và bias
                self.weights_hidden_output = [w - self.learning_rate * gw for w, gw in zip(self.weights_hidden_output, grad_weights_hidden_output)]
                self.bias_output -= self.learning_rate * grad_bias_output
                for i in range(4):
                    self.weights_input_hidden[i] = [w - self.learning_rate * gw for w, gw in zip(self.weights_input_hidden[i], grad_weights_input_hidden[i])]
                    self.bias_hidden[i] -= self.learning_rate * grad_bias_hidden[i]

            if (epoch + 1) % 10000 == 0:
              #   pass
                print(f"Epoch {epoch + 1}, Loss: {total_loss / len(dataX):.4f}")

    def predict(self, dataTrain, x_question):
        if not dataTrain.isDataFormat(x_question):
            print("Dữ liệu không hợp lệ!")
            return

        x_question = [int(i) for i in x_question.split()]
        x_norm = dataTrain.normalize([x_question], dataTrain.getX_ValueMin(), dataTrain.getX_ValueMax())[0]

        hidden_inputs = [sum(w * xi for w, xi in zip(weights, x_norm)) + b for weights, b in zip(self.weights_input_hidden, self.bias_hidden)]
        hidden_outputs = [self.sigmoid(h) for h in hidden_inputs]
        output_input = sum(w * h for w, h in zip(self.weights_hidden_output, hidden_outputs)) + self.bias_output
        output = self.sigmoid(output_input)
        prediction = dataTrain.denormalize([output], dataTrain.getY_ValueMin(), dataTrain.getY_ValueMax())[0]

        print(f"Dự đoán: {prediction:.2f}")
        confirm = input("Kết quả có đúng không? (y/n): ")
        if confirm.lower() == 'y':
            dataTrain.addDataTrain(x_question, prediction)
            print("Dữ liệu đã được cập nhật!")
            
            self.train(dataTrain=dataTrain)
        else:
            y_input_true = input(f"Vậy hãy nhập dữ liệu đúng của phép tính {x_question[0]} + {x_question[1]}: ")
            dataTrain.addDataTrain(x_question, y_input_true)
            print("Dữ liệu đã được cập nhật!")
            
            self.train(dataTrain=dataTrain)

if __name__ == "__main__":
    data = DataTrain()
    nn = NN(0.04, 60000)
    nn.train(data)
    while True:
        x_input = input("Nhập dữ liệu x: ")
        nn.predict(data, x_input)
        
