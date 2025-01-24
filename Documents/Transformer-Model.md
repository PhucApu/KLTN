# Mô hình Transformer

## Mục lục


## 1. Sơ lược về Machine Learning và Deep Learning

### 1.1. Machine Learning

  - **Khái niệm**

    - Machine Learning là một nhánh của AI, trong đó các máy tính được lập trình để học từ dữ liệu mà không cần lập trình cụ thể cho từng tác vụ.

    - Thường được dùng trong các lĩnh vực dự đoán, phân tích đối với các **dữ liệu có cấu trúc** (dữ liệu được tổ chức dưới dạng bảng).  

- **Cách hoạt động**

    - Dựa trên các thuật toán thống kê và mô hình toán học.

    - Các tính năng (features) quan trọng trong dữ liệu phải được trích xuất thủ công bởi con người.

    - Mô hình học từ các đặc trưng này để dự đoán hoặc phân loại.

- **Phân loại**

    - **Học có giám sát (Supervised Learning)**: Dự đoán giá nhà, phân loại email (spam/non-spam).

      - Thuật toán: Hồi quy tuyến tính (Linear Regression), SVM, KNN.

    - **Học không giám sát (Unsupervised Learning)**: Phân cụm khách hàng.

      - Thuật toán: K-Means, DBSCAN.

    - **Học tăng cường (Reinforcement Learning)**: Trò chơi cờ vua, robot học cách di chuyển.

### 1.2. Deep Learning

  - **Khái niệm**

    - Deep Learning là **một nhánh con của Machine Learning**, sử dụng mạng nơ-ron nhân tạo (**Artificial Neural Networks**) với nhiều lớp (deep layers), để học trực tiếp từ dữ liệu mà không cần sự can thiệp thủ công của con người.

    - Thường được sử dụng trong các yêu cầu dịch thuật, nhận diện ảnh (video), sinh văn bản, tạo ảnh.

    - Và dữ liệu thường là **dữ liệu không có cấu trúc** (không thể biểu diễn dưới dạng bản; ví dụ sách báo, âm thanh, hình ảnh,.....).

- **Cách hoạt động**

  - Mô hình tự động trích xuất các đặc trưng quan trọng từ dữ liệu.
  
  - Xây dựng từ các lớp mạng nơ-ron (neural network), trong đó mỗi lớp học các đặc trưng khác nhau của dữ liệu.

- **Phân loại**

  - Nhận diện ảnh, xử lý video: Mạng nơ-ron tích chập (CNN).

  - Xử lý chuỗi, dịch máy: Mạng nơ-ron hồi tiếp (RNN). 

  - xử lý ngôn ngữ tự nhiên (NLP): **Transformer**, RNN.

  - Tạo ảnh giả: GAN (Generative Adversarial Networks).                                    

**Như vậy**, ta có thể thấy *Mô hình Transformer* thuộc lĩnh vực Deep Learning nơi xử dụng các mạng nơ-ron để xử lý dữ liệu. 

## 2. Tìm hiểu về cách hoạt động của "Mạng nơ-ron nhân tạo" (Artificial Neural Networks - ANN)

Mạng nơ-ron nhân tạo là một mô hình lấy cảm hứng từ **cấu trúc của bộ não con người**, bao gồm các "nơ-ron" nhân tạo kết nối với nhau để xử lý thông tin.

### 2.1. Cấu trúc của một mạng nơ-ron 

Mạng nơ-ron cơ bản thường gồm **ba thành phần chính**:

- **Tầng đầu vào (Input Layer)**: Nhận dữ liệu đầu vào từ bên ngoài (ví dụ: hình ảnh, văn bản, số liệu).

- **Tầng ẩn (Hidden Layers)**: Xử lý và học các đặc trưng phức tạp từ dữ liệu.

- **Tầng đầu ra (Output Layer)**: Tạo ra kết quả cuối cùng (ví dụ: phân loại, dự đoán).

Mỗi tầng bao gồm một tập hợp các "nơ-ron" (neurons) được kết nối với nơ-ron ở tầng trước và sau.

### 2.2. Cơ chế mạng nơ-ron hoạt động:

- **Ý tưởng hàm số**

  - Cấu trúc của mạng nơ-ron được biểu diễn dưới dạng một **hàm số** $\textbf{y = f(x)}$ - nơi một tham số đầu vào $x$ (tầng đầu vào) đi vào một hàm số $f$ (tầng ẩn) nào đó để cho đầu ra là một giá trị $y$ (tầng đầu ra).

  - Hàm số $y = f(x)$ đơn giản nhất là hàm số tuyến tính bậc 1 (**Linear Function**). Khi hàm số ở dạng bậc 1 thì mối quan hệ giữa x và y là mối quan hệ tuyến tính:

    ![](../images/Linear-Function-Graph-removebg-preview.png)

  - Khi hiểu diễn hàm số $y = ax + b$ ở **dạng đồ thị graph** thay vì không gian tọa độ 2 chiều:

    ![](../images/Linear-Function-Graph(1).png)

  - Về ý nghĩa của **đồ thị hàm bậc 1** bên trên: 
  
    - Input đầu vào sẽ là tham số $x$ nhân với một hệ số $a$ sau đó cộng với một hạng tử tự do là $b$ để cho Output đầu ra là $y$.

  - Mở rộng vấn đề khi có **nhiều hơn một input đầu vào** và có một output đầu ra:

    ![](../images/Linear-Function-Graph(2).png)

  - Như hình trên ta thấy có 3 input đầu vào là $x_1,x_2,x_3$ và chỉ có một output đầu ra là $y$. Thì ra sẽ có công thức biểu diễn là: $$y = w_1x_1 + w_2x_2 + w_3x_3 + w_0$$

  - Với $w_1,w_2,w_3$ ($w$ - weight) là các trọng số và $w_0$ là hạng số tự do. $x$ và $y$ có ý nghĩa như hàm bậc 1.

  - $w_0$ được biểu diễn bên trên nhân với 1 do hạng số nào nhân với 1 cũng bằng chính nó.

  - Từ đó ta có tổng thức tổng quát của **hàm có $n$ input đầu vào** là:

    ![](../images/Linear-Function-Graph(3).png)

  - Công thức $$y = \sum_{i=1}^{n} w_ix_i + w_0$$

  - Với $w_i$ như đã nói ở trên là các trọng số, thể hiện mối liên kết giữa input đầu vào và output đầu ra, có bao nhiêu input đầu vào $x_i$ thì sẽ có bấy nhiêu trọng số $w_i$.

  - $w_0$ là một trọng số đặt biệt do không liên kết với bất kỳ input đầu vào nào hết. Và thường được biểu diễn nhân với 1 vì trọng số nào nhân với 1 cũng bằng chính nó. Ngoài ra, $w_0$ còn có tên gọi khác là hệ số **bias**.

  - **$w_i$ và $w_0$ có mối quan hệ trực tiếp đến giá trị input đầu vào. Một giá trị input đầu vào có quan trọng hay không đều phụ thuộc vào trọng số $w$ và hệ số tự do $w_0$.**

  - Trong một số tài liệu, người ta có thể rút gọn công thức tổng quát bên trên bằng cách **thêm một input đầu vào $x_0$ nữa và $x_0$ này sẽ luôn có giá trị bằng 1**. Lúc này công thức tổng quát sẽ được biểu diễn lại là: $$y = \sum_{i=0}^{n} w_ix_i \hspace{0.8cm} với \ x_0 = 1$$

  - **Như vậy**, hàm số tuyến tính bậc 1 là hàm số đơn giản nhất được dùng để biểu diễn mối quan hệ giữa input đầu vào $x$ và output đầu ra $y$. Còn đối với các hàm phi tuyến tính (Non-Linear Function) là các hàm mà mối quan hệ giữa input $x$ và output $y$ không phải là bậc $1$ nữa mà bậc $n+1$ (bậc 2, 3,...).

  - Hoặc là một phân thức mà nó có thể kết hợp với một hàm mũ như ví dụ bên dưới:

    ![](../images/Sigmoid-Function.png)

  - Hàm $$\theta(x) = \frac{1}{1+e^{-x}}$$ được gọi là hàm **Sigmoid**

  - Trong lĩnh vực AI, các hàm phi tuyến như hàm Sigmoid được gọi là hàm kích hoạt (**Activation function**). Thật ra không phải hàm phi tuyến nào cũng là hàm kích hoạt, nhưng **đã là hàm kích hoạt thì chắc chắn nó là một hàm phi tuyến**.

  - Hàm phí tuyến được dùng để biểu diễn mối quan hệ phức tạp giữa input $x$ và output $y$.

  - Và hàm **Sigmoid** là một trong những hàm kích hoạt đời đầu.

- **Như vậy**, hàm tuyến tính (**Linear Function**) là những hàm được dùng để biểu diễn **mối quan hệ đơn giản** giữa input đầu vào và output đầu ra. Trong khi đó hàm phi tuyến tính (**Non-Linear Function**) là những hàm được dùng để **biểu diễn mối quan hệ phức tạp** giữa input đầu vào và output đầu ra.

- Và khi kết hợp giữa hàm tuyến tính và phi tuyến tính vào với nhau, ta sẽ có một nơ-ron.

  ![](../images/no-ron-function.png)

  - Một nơ-ron là sự kết hợp giữa một hàm phi tuyến tính và một hàm tuyến tính. $$y_{pred} = \theta (\sum_{i=0}^{n}w_ix_i)$$

  - Nó có thể vừa xử lý, học hỏi các mối quan hệ đơn giản vừa xử lý học hỏi cả các mối quan hệ phức tạp. 

- Vậy giờ bây giờ ta có nhiều hàm số như vậy, các hàm số này nhận cùng các giá trị input đầu vào và cho ra các giá trị output đầu ra khác nhau. Lúc đó ta sẽ có một **Layer**.

  ![](../images/layer.png)

  - **Layer** về bản chất là tập hợp của nhiều nơ-ron. Các nơ-ron này đều nhận giá trị input đầu vào giống nhau nhưng lại có trọng số ($w_i$) khác nhau dẫn đến output đầu ra của các nơ-ron này cũng sẽ khác nhau.

  - **Lưu ý**: các nơ-ron trong cùng một Layer sẽ không có sự gắn kết (kết nối với nhau) trực tiếp với nhau.

  ![](../images/layer(2).png)

- Giờ ta sẽ sắp thêm các Layer khác nằm song song và kết nối với nhau. Lúc này ta sẽ có một mạng nơ-ron nhân tạo (**Artificial Neural Network**).

  ![](../images/Artificial_Neural_Network.png) 

  - **Lưu ý**: **Artificial Neural Network** (mạng nơ-ron nhân tạo) là tên gọi được dùng để phân biệt với mạng nơ-ron thật sự nằm trong trí óc của con người. Sau này để đơn giản hơn người ta thường lượt bỏ từ "Artificial" đi và chỉ gọi đơn giản là Neural Network.

  - Một Neural Network có bao nhiêu Layer Neural cũng được.

  - Các giá trị output của nơ-ron thuộc layer trước sẽ làm các giá trị input cho các nơ-ron thuộc layer phía sau.

  - Các Layer Neural được xem là tầng ẩn (Hidden Layers).

  - Ví dụ về một mạng nơ-ron được dùng trong bài toán nhận diện ảnh:

    ![](../images/Artificial_Neural_Network_.Example.png)

  - Trong ví dụ trên, ảnh sẽ được lưu dưới dạng dữ liệu mảng với mỗi giá trị trong mảng tượng trưng cho giá trị màu của các pixel. Nếu là ảnh đen trắng thì mỗi pixel sẽ được lưu dưới dạng mảng 2 chiều, còn nếu là ảnh màu thì mỗi pixel sẽ được lưu dưới dạng mảng ba chiều (R,G,B).

  - Và các giá trị đó sẽ là dữ liệu đầu vào cho tầng **Input Layer**.

  - Các hidden layer ban đầu sẽ thực hiện các tính toán đơn giản trước (lấy ra các đặc điểm đặc trưng cơ bản của ảnh). Các Hidden Layer gần cuối Ouput đầu ra sẽ thực hiện các tính toán phức tạp hơn (lấy ra các đặc điểm đặc trưng nhất) để cho ra kết quả đúng.  

### 2.3. Tóm lại:

- Mỗi nơ-ron sẽ gồm có **2 phần**: 
  
  - Hàm nhận dữ liệu đầu vào (hàm tuyến tính)
  
  - Hàm kích hoạt để xem giá trị đó có được truyền sang các nơ-ron kế tiếp hay không (hàm phi tuyến)

- Hàm nhận giá trị đầu vào sẽ được biểu diễn như sau: $$y = \sum_{i=1}^{n} w_ix_i + w_0$$ hoặc $$y = \sum_{i=1}^{n} w_ix_i + b \  (bias)$$

  - Với:

    - $y$: là giá trị hàm số được tính toán dựa trên giá trị $x$ đầu vào.

    - $x_i$: là các giá trị input đầu vào.

    - $w_i$: là trọng số (weight), gắn với mỗi giá trị đầu vào. Có bao nhiêu giá trị $x_i$ đầu vào thì sẽ có bấy nhiêu $w_i$. Và $w_i$ thể hiện mức độ quan trọng đối với giá trị $x_i$ đầu vào ($w_i$ càng lớn thì dữ liệu đó càng quan trọng).

    - $w_0$ (hoặc $b$): là hệ số tự do (trong một số tài liệu gọi là hệ số bias). Được dùng để điều chỉnh đường quyết định để mô hình có thể học được nhiều dữ liệu hơn trước khi qua hàm quyết định.

      ![](../images/decision_road.png)

- Sau khi hàm nhận giá trị đầu vào $y$ tính toán xong sẽ được truyền vào hàm quyết định (**Activation function**) để xem giá trị đó có được tiếp tục truyền cho các nơ-ron kế tiếp hay không:

  - Hàm kích hoạt **Sigmoid**: $$\theta(y) = \frac{1}{1+e^{-y}}$$

    hay: $$y_{pred} = \frac{1}{1+e^{-y}}$$

  - Với:

    - $y_{pred}$ hay $\theta(y)$: là giá trị output đầu ra của một nơ-ron.

    - $y$: là giá trị của hàm nhận giá trị đầu vào được tính toán theo dữ liệu $x$ đã nhắc đến bên trên.

- Sau khi trải qua hàm nhận giá trị đầu vào và hàm kích hoạt để cho ra $y_{pred}$. Các output $y_{pred}$ của nơ-ron trong cùng layer này sẽ truyền tiếp cho các nơ-ron thuộc layer kế tiếp để tiếp tục thực hiện lại các bước tính toán. Lúc này, các giá trị output $y_{pred}$ của layer nơ-ron trước sẽ là giá trị input cho các layer nơ-ron kế.

- Và các tính toán bên trong nơ-ron kế tiếp cũng được thực hiện y như vậy (trải qua hàm nhận giá trị đầu vào $y$ sau đó đến hàm kích hoạt $y_{pred}$).

- Cho đến khi dữ liệu đến tầng đầu ra (Output Layers).


## 3. Hàm mất mát (Loss Function)

### 3.1. Khái niệm

  - **Hàm mất mát (Loss Function)** là một công cụ đo lường mức độ chênh lệch giữa đầu ra dự đoán của mô hình và giá trị thực tế (ground truth). 
  
  - Nói cách khác, **hàm mất mát giúp xác định mô hình của bạn hoạt động tốt hay không**, bằng cách tính toán một con số thể hiện mức lỗi.

  - **Giá trị thể hiện mức lỗi có lớn hay không thường phụ thuộc vào các trọng số ($w$) và hệ số tự do ($w_0$) ở input đầu vào**. Do như đã nói bên trên, $w$ và $w_0$ có quan hệ trực tiếp đến giá trị input đầu vào. 
  
  - Sau khi có được giá trị thể hiện mức lỗi, ta sẽ thực hiện "**Lan truyền ngược (Backpropagation)**"  để điều chỉnh các trọng số và hệ số tự do sau cho mức lỗi thấp nhất có thể.

### 3.2. Cơ sở hình thành hàm mất mát

- **Kiến thức khoảng cách Euclidean**

  - Khoảng cách Euclidean là một cách đo khoảng cách ngắn nhất giữa hai điểm trong không gian Euclidean (không gian thông thường mà chúng ta sống, như 2D hoặc 3D). Nó **được tính dựa trên định lý Pythagoras**.

  - Giả sử chúng ta có 2 điểm $A$ và $B$ trong không gian 2 chiều (tọa độ $x,y$) như sau:

    - $A(3,4)$

    - $B(0,0)$

    - Thì khoảng cách Euclidean được tính bằng công thức: $$d(A,B) = \sqrt{(3-0)^2 + (4-0)^2} = 5$$

  - Đối với trong không gian 3 chiều ($x,y,z$)

    - $A(1,2,3)$

    - $B(4,6,8)$

    - Thì khoảng cách Euclidean được tính bằng công thức: $$d(A,B) = \sqrt{(1-4)^2 + (2-6)^2 + (3-8)^2} \approx 7.07$$

  - Từ đó ta có **công thức tổng quát khoảng cách Euclidean trong $n$ chiều**: $$d(A,B) = \sqrt{ \sum_{i=1}^{n} (x_i-y_i)^2}$$

- **Hàm mất mát MSE - Mean Squared Error**

  - Đây là một trong những hàm mất mát đầu tiên được sử dụng, phổ biến trong các bài toán hồi quy.
  
  - Hàm MSE dựa trên khoảng cách Euclidean bình phương nhưng **bỏ qua bước lấy căn bậc hai**. Thay vào đó, nó lấy trung bình bình phương độ lệch giữa giá trị thực và giá trị dự đoán.

  - Từng bước xây dựng:

    - Giả sử ta có 2 giá trị output đầu ra $y_{pred}$ và $y_{true}$. Với: 
      
      - $y_{pred}$ - là giá trị output mà mô hình (nơ-ron) ta tính toán được.
      
      - $y_{true}$ - là giá trị output đúng mà ta mong đợi cho kết quả chạy của mô hình (nơ-ron).

    - Để tính được sai số giữa $y_{pred}$ và $y_{true}$ thì ta thực hiện phép tính trừ:$$Sai \ số = y_{true} - y_{pred}$$

    - Để đảm bảo kết quả sai số là số dương, ta tiến hành bình phương 2 vế: $$(Sai \ số)^2 = (y_{true} - y_{pred})^2$$

    - Mở rộng công thức ra với $n$ giá trị output đầu ra, ta có công thức tổng quát:$$(Sai \ số)^2 = \sum_{i=1}^{n} (y_{true,i} - y_{pred,i})^2$$

    - **Lấy trung bình sai số bình phương**: Để chuẩn hóa mất mát cho toàn bộ tập dữ liệu, lấy trung bình tổng sai số bình phương: $$(Sai \ số)^2 = \frac{1}{n} \sum_{i=1}^{n} (y_{true,i} - y_{pred,i})^2$$

  - Từ đó ta có **công thức hàm mất mát MSE - Mean Squared Error**: $$L (Loss) = \frac{1}{n} \sum_{i=1}^{n} (y_{true,i} - y_{pred,i})^2$$

    - $L$: giá trị của hàm mất mát (Loss).

    - $n$: số lượng dữ liệu trong tập huấn luyện.

    - $y_{pred,i}$: giá trị thực tế của điểm dữ liệu thứ $i$.

    - $y_{true,i}$: giá trị mong muốn của mô hình tại điểm thứ $i$.

  
## 4. Lan truyền ngược (Backpropagation)

### 4.1. Khái niệm

- **Lan truyền ngược (Backpropagation)** là một thuật toán dùng để tối ưu hóa các mạng nơ-ron nhân tạo bằng cách tính toán và lan truyền ngược độ lỗi (error) từ đầu ra về phía các trọng số đầu vào. Đây là một phần cốt lõi trong quá trình huấn luyện của mạng nơ-ron.

- Nó là việc từ giá trị output $y_{pred}$ ta sẽ thực hiện việc tính ngược lại (đi ngược lại) để tính toán **điều chỉnh các trọng số $w_i$ và hệ số tự do $w_0$ sao cho giá trị của hàm mất mát là thấp nhất** qua các lớp nơ-ron. Sau cho giá trị $y_{pred}$ gần với giá trị mà ta mong muốn $y_{true}$.

### 4.2. Quá trình lan truyền ngược

- Quá trình lan truyền ngược diễn ra theo 2 giai đoạn chính:

  - **Giai đoạn 1**: Lan truyền xuôi (Forward Propagation)

    - Là quá trình mà các dữ liệu $x$ đi từ tầng dữ liệu đầu vào vào các nơ-ron để thực hiện các tính toán thông qua **hàm tính dữ liệu đầu vào và hàm kích hoạt** để cho ra giá trị output $y_{pred}$ như đã nói bên trên: $$y_{pred} = \theta \ \left(\sum_{i=1}^{n} w_ix_i + w_0 \right)$$

    - Sau khi có được giá trị $y_{pred}$, ta tiến hành **tính hàm mất mát $L$** giữa giá trị đầu ra thực tế của mô hình là $y_{pred}$ và giá trị đầu ra mong muốn là $y_{true}$. $$L (Loss) = \frac{1}{n} \sum_{i=1}^{n} (y_{true,i} - y_{pred,i})^2$$

  - **Giai đoạn 2**: Lan truyền ngược (Backpropagation)

    - **Nhắc lại kiến thức đạo hàm**

      - Hồi xưa, để biết được một hàm số $y$ có đồ thị đang đi lên hay đi xuống (đồ thị tăng hay giảm) ta thường dùng đạo hàm $f'(y)$ để xét.

      - Như ví dụ, xét đồ thị hàm số $y=x^2$:

        - Ta có đạo hàm của $f'(y) = 2x$

          - Tại $x=0$ thì $y=0$.

          - Tại $x=1$ thì $y=2$.

          $\rightarrow$ Hàm số $y=x^2$ là một đồ thị hàm số tăng.

    - Đối với hàm số nhiều biến $f(x,y,...)$ thì ta xét đồ thị tăng hay giảm bằng **Gradient**.

    - **Gradient** là tập các vector chứa tất cả các đạo hàm riêng của hàm đó đối với từng biến. Gradient chỉ hướng của độ dốc lớn nhất và độ lớn của nó cho biết tốc độ thay đổi nhanh nhất của hàm.

    - Công thức của **Gradient** theo hàm $f(x,y)$: $$\nabla f(x,y) = \left( \frac{\partial f}{\partial x}, \frac{\partial f}{\partial y} \right)$$

      - $\frac{\partial f}{\partial x}$ là đạo hàm $f$ theo biến $x$.

      - $\frac{\partial f}{\partial y}$ là đạo hàm $f$ theo biến $y$.

    - **Độ dốc** là chỉ điểm mà đồ thị gốc $f(x)$ bắt đầu dốc lên hay dốc xuống. Được xem xét thông qua đạo hàm như sau:

      - Nếu $f'(x) > 0$: Đồ thị $f(x)$ đang đi lên nếu di chuyển theo trục $x$.

      - Nếu $f'(x) < 0$: Đồ thị $f(x)$ đang đi xuống nếu di chuyển theo trục $x$.

      - Nếu $f'(x) = 0$: Đồ thị $f(x)$ có điểm dừng (có thể là điểm cực đại, cực tiểu, hoặc điểm uốn).
    
    - **Độ dốc trong đồ thị nhiều biến** sẽ phức tạp hơn. Với công thức **Gradient** theo hàm $f(x,y)$: $$\nabla f(x,y) = \left( \frac{\partial f}{\partial x}, \frac{\partial f}{\partial y} \right)$$

      Với giá trị $x,y$ tùy chọn:

      - Nếu $\frac{\partial f}{\partial x} > 0$ thì đồ thị $f(x,y)$ sẽ có chiều đi lên nếu di chuyển theo trục $x$.

      - Nếu $\frac{\partial f}{\partial x} < 0$ thì đồ thị $f(x,y)$ sẽ có chiều đi xuống nếu di chuyển theo trục $x$.

      - Tương tự đối với $\frac{\partial f}{\partial y}$ di chuyển theo trục $y$.

      - Nếu $\nabla f(x,y) = 0$ thì đồ thị $f(x,y)$ có thể đạt giá trị cực đại hoặc cực tiểu.

    - **Hướng của gradient** là hướng mà hàm $f(x,y)$ thay đổi nhanh nhất. 

    - **Độ lớn của gradient** là **tốc độ thay đổi của hàm** theo hướng đó. Có công thức tính: $$\left| \nabla f(x,y) \right| = \sqrt{\left(\frac{\partial f}{\partial x}\right)^2 + \left(\frac{\partial f}{\partial y}\right)^2}$$

      - Nếu $\left| \nabla f(x,y) \right|$ càng lớn thì độ dốc của $f(x,y)$ sẽ thay đổi nhanh tại đó. 

    - Ví dụ hàm số $f(x,y) = x^2y + y^3$. Tính Gradient: $$\nabla f(x,y) = \left( 2xy, \ x^2 + 3y \right)$$

      - Tại điểm $(1,1)$: $$\nabla f(1,1) = (2,4)$$

        - Ý nghĩa: Tại điểm $(1,1)$, đồ thị sẽ từ từ hướng lên (dốc lên) điểm $(2,4)$ nếu di chuyển theo cả 2 chiều trục $x$ và $y$ (hướng của Gradient là $(2,4)$).

          - $\frac{\partial f}{\partial x} = 2 > 0$: nếu di chuyển theo trục $x$ thì đồ thị $f(x,y)$ sẽ dốc lên.

          - $\frac{\partial f}{\partial y} = 4 > 0$: nếu di chuyển theo trục $y$ thì đồ thị $f(x,y)$ sẽ dốc lên.

        - Độ lớn của Gradient: $$\left| \nabla f(1,1) \right| = \sqrt{2^2 + 4^2} \approx 4.47$$

          - $4.47$ biểu thị rằng nếu ta di chuyển theo hướng gradient từ $(1,1)$ đến $(2,4)$ thì giá trị của hàm $f(x,y)$ sẽ tăng nhanh nhất (dốc lên nhanh nhất) với tốc độ $4.47$ đơn vị mỗi bước. 

      - Ví dụ hàm số $f(x) = x^2$. Tính Gradient: $$\nabla f(x) = \left(2x\right)$$ 

        - Tại điểm $x=0$: $$\nabla f(0) = (0)$$

          thì đồ thị $f(x)$ sẽ đạt giá trị cực tiểu hoặc cực đại.

        - Tại điểm $x=1$: $$\nabla f(1) = (2)$$

          thì đồ thị $f(x)$ sẽ dốc lên nếu di chuyển theo trục $x$.

        - Và độ lớn Gradient sẽ là $$\left| \nabla f(1) \right| = \sqrt{2^2} = 2$$ 

          - Với $\left| \nabla f(1) \right| = 2$ thì độ dốc của hàm $f(x)$ thay đổi là tương đối nhỏ (với tốc độ khoảng $2$ đơn vị mỗi bước).

  - **Tính Gradient của hàm mất mát L(Loss) để biết mức độ thay đổi thông qua từng tham số $w_i$ và $w_0$**

    - Khi huấn luyện mạng nơ-ron, mục tiêu của chúng ta là **tối ưu hóa các tham số (trọng số và bias) sao cho hàm mất mát $L$ trở nên nhỏ nhất (giảm độ dốc và tốc độ thay đổi độ dóc của hàm $L$)**. Để làm được điều này, chúng ta cần tính gradient của L đối với từng tham số và sử dụng gradient descent để điều chỉnh các tham số.

    - Ta xem các trọng số và bias là các biến $x,y$ cần xem xét tùy chỉnh sao cho độ dốc của hàm mất mát là nhỏ nhất: $$\nabla f(w_i,w_0) = \left( \frac{\partial L}{\partial w_i},\frac{\partial L}{\partial w_0} \right)$$

    - Do $L$ phụ thuộc vào $w_i$ thông qua nhiều lớp trung gian, ta sử dụng quy tắc chuỗi (chain Rule): $$\frac{\partial L}{\partial w_i} = \frac{\partial L}{\partial y_{pred}} \times \frac{\partial y_{pred}}{\partial y} \times \frac{\partial y}{\partial w_i}$$

    - Tương tự với $w_0$: $$\frac{\partial L}{\partial w_0} = \frac{\partial L}{\partial y_{pred}} \times \frac{\partial y_{pred}}{\partial y} \times \frac{\partial y}{\partial w_0}$$

    - Giả sử ta sử dụng công thức **hàm kích hoạt Sigmoid** và **hàm mất mát MSE**. Công thức $\frac{\partial L}{\partial w_i}$ sẽ là: $$\frac{\partial L}{\partial w_i} = \frac{2}{n} (y_{pred} - y_{true}) \times y_{pred}(1-y_{pred}) \times x_i$$ và $$\frac{\partial L}{\partial w_0} = \frac{2}{n} (y_{pred} - y_{true}) \times y_{pred}(1-y_{pred})$$

  - **Cập nhật trọng số và bias**

    - Sử dụng thuật toán **Gradient Descent** - một thuật toán tối ưu hóa các trọng số $w_i$ và bias $w_0$, các tham số được cập nhật bằng cách di chuyển theo hướng ngược lại của gradient để giảm giá trị hàm mất mát $L$:

    - Cập nhật trọng số $w_i$: $$w_i^{new} = w_i^{old} - \eta . \frac{\partial L}{\partial w_i}$$

    - Cập nhật trọng số $w_0$: $$w_0^{new} = w_0^{old} - \eta . \frac{\partial L}{\partial w_0}$$

    - Trong đó, **$\eta$ là tốc độ học (Learning Rate)**.

      - Tốc độ học $\eta$ là một hệ số quyết định mức độ thay đổi của trọng số $w_i$ trong mỗi bước cập nhật trong quá trình huấn luyện.

      - Nếu tốc độ học quá lớn, mô hình có thể vượt quá điểm tối ưu và không hội tụ (convergence). Nếu tốc độ học quá nhỏ, quá trình huấn luyện sẽ rất chậm và có thể dừng lại trước khi đạt được kết quả tối ưu.

      - Cách hoạt động của tốc độ học:

        - Nếu độ dốc $\frac{\partial L}{\partial w_i}$ lớn:

          - Khi gradient lớn, mô hình cần phải thay đổi mạnh mẽ để đạt được sự cải thiện nhanh chóng.

          - Tuy nhiên, nếu tốc độ học $\eta$ quá lớn, mô hình có thể "nhảy" qua các giá trị tối ưu và không hội tụ, hoặc đi đến một điểm không tối ưu.
      
        - Nếu độ dốc $\frac{\partial L}{\partial w_i}$ nhỏ:

          - Khi gradient nhỏ, sự thay đổi cần thiết là rất nhỏ, và nếu tốc độ học quá lớn, mô hình sẽ di chuyển quá nhanh, bỏ qua các điểm tối ưu tiềm năng.

          - Nếu tốc độ học quá nhỏ, mô hình sẽ hội tụ rất chậm.

      - Khi nào nên tăng hay giảm tốc độ học ($\eta$)?

        - Khi độ dốc $\frac{\partial L}{\partial w_i}$ lớn:

          - Nếu gradient lớn, mô hình có thể cập nhật trọng số nhanh chóng. Nếu tốc độ học $\eta$ vẫn ở mức hợp lý, việc cập nhật sẽ tiến nhanh về điểm tối ưu.

          - Tăng tốc độ học có thể hữu ích nếu mô hình đang chậm cập nhật và cần di chuyển nhanh hơn để hội tụ.

        - Khi độ dốc $\frac{\partial L}{\partial w_i}$ nhỏ:

          - Khi gradient nhỏ, mô hình chỉ cần thay đổi một chút để tối ưu hóa. Nếu $\eta$ quá lớn, mô hình có thể nhảy qua điểm tối ưu.

          - Giảm tốc độ học có thể là cần thiết khi mô hình đang quá nhạy với các cập nhật, và cần di chuyển chậm lại để tìm được điểm tối ưu tốt hơn.

      - **Điểm tối ưu (Optimal Point)** là giá trị của các tham số mô hình (trọng số $w_i$, bias $w_0$...) **sao cho hàm mất mát $L$ đạt giá trị thấp nhất (tối thiểu)**.

      - Khi hàm mất mát $L$ đạt giá trị thấp nhất và không thể thấp hơn được nữa qua các bước huấn luyện, ta gọi đó là **hội tụ**.   


        













## 1. Sơ lược về Transformer Model

- **Transformer là gì ?**

  - Mô hình Transformer là một kiến trúc mạng thần kinh sâu, được giới thiệu lần đầu tiên trong bài báo "**Attention is All You Need**" của nhóm tác giả Vaswani và cộng sự vào năm **2017**. 
  
  - Đây là một **bước đột phá trong xử lý ngôn ngữ tự nhiên (NLP) và học sâu**, đóng vai trò quan trọng trong sự phát triển của các mô hình ngôn ngữ hiện đại như GPT (bao gồm GPT-4), BERT, và T5.