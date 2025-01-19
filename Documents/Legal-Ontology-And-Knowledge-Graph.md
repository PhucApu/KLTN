# Mô hình Legal-Ontology và Đồ thị tri thức

## Mục lục

1. [Legal-Ontology](#1-mô-hình-legal-ontology)

    1.1. [Khái niệm](#11-khái-niệm)

    1.2. [Ontology](#12-ontology)

    1.3. [Legal-Onto](#13-legal-onto)

    1.4. [Thành phần chính của Legal-Onto](#14-thành-phần-chính-của-legal-onto)

2. [Đồ thị tri thức](#2-đồ-thị-tri-thức-knowledge-graphics)
    
3. [Công thức TF-IDF](#3-công-thức-tf-idf)

    3.1. [Công thức tuần suất từ TF (Term Frequency)](#31-công-thức-tần-suất-từ-tf---term-frequency)

    3.2. [Công thức tần suất nghịch đảo tài liệu IDF (Inverse Document Frequency)](#32-tần-suất-nghịch-đảo-tài-liệu-idf---inverse-document-frequency)

    3.3. [Công thức TF - IDF](#33-công-thức-tf-idf)

    3.4 [Ví dụ](#34-ví-dụ)


## 1. Mô hình Legal-Ontology

### 1.1. Khái niệm

- **Ontology Legal-Onto** là một mô hình ontology được thiết kế đặc biệt để biểu diễn và quản lý tri thức pháp luật.

- Mục tiêu của Legal-Onto là tổ chức các khái niệm, quan hệ, và tri thức từ các tài liệu pháp luật thành một cấu trúc có hệ thống, dễ dàng sử dụng cho các ứng dụng như tìm kiếm, truy vấn ngữ nghĩa, và phân tích pháp lý.

### 1.2. Ontology

- Ontology là một phương pháp biểu diễn tri thức trong các lĩnh vực cụ thể thông qua việc định nghĩa:

  - Các khái niệm (**concepts**): Đại diện cho các thực thể hoặc ý tưởng.

  - Quan hệ giữa các khái niệm (**relations**): Liên kết các khái niệm lại với nhau.

  - Các quy tắc (**rules**): Dùng để suy luận ra tri thức mới từ các mối quan hệ.

### 1.3. Legal-Onto

- Legal-Onto là **một ontology chuyên biệt cho các tài liệu pháp luật**, được thiết kế dựa trên:

  - **Rela-model**: Một mô hình quan hệ để tổ chức các khái niệm và mối quan hệ trong miền pháp luật.

  - **Knowledge Graph (Đồ thị tri thức)**: Tạo liên kết giữa các khái niệm pháp lý và cụm từ khóa.

  <br>

### 1.4. Thành phần chính của Legal-Onto

- **Công thức tổng quát:**

$$
    K = (C,R,Rules) + (Cons,Rel)
$$

  <br>

- **$C -$ Concepts** (Khái niệm)

  - Là **tập hợp các khái niệm trong pháp luật**.

  - Mỗi khái niệm có tên (**Name**), ý nghĩa (**Meaning**), các thuộc tính (**Attrs**), và các cụm từ khóa liên quan (**Keyphrases**).

  - Ví dụ về một **concepts** được biểu diễn trong mô hình Legel-Onto:

    - **Concepts "xe máy"** sẽ được biểu diễn:

    | Element        | Type   | Value                                                |
    | :------------- | :----- | :--------------------------------------------------- |
    | **Name**       | String | Xe máy                                               |
    | **Meaning**    | String | Phương tiện giao thông có hai bánh chạy bằng động cơ |
    | **Attrs**      | Dict   | {"Loại phương tiện": "Giao thông đường bộ"}          |
    | **Keyphrases** | Set    | ["Xe máy", "Mô tô"]                                  |

  <br>

- **$R -$ Relation (Quan hệ)**

  - Là tập hợp các mối quan hệ giữa các khái niệm với nhau.

    - Ví dụ: "Sử dụng", "Thuộc về", "Quy định".

  - Cấu trúc của một quan hệ được biểu diễn như sau:

$$
      r=(Name,Meaning,ConckeyS,ConckeyO,Prop,Keywords)
$$

- Với:

  - **Name**: Là tên của mối quan hệ.

  - **Meaning**: Là khái niệm, ý nghĩa của tên mối quan hệ.

  - **ConckeyS**: Là chủ ngữ trong mối quan hệ.

  - **ConckeyO**: Là tân ngữ trong mối quan hệ.

  - **Prop**: Thuộc tính của quan hệ (ví dụ: bắc cầu, đối xứng).

  - **Keywords**: Các từ khóa liên quan.

- Ví dụ về **Relation "sử dụng"** được biểu diễn trong mô hình Legel-Onto:

  | Element      | Type       | Value                                                                                                                                                    |
  | :----------- | :--------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | **Name**     | String     | sử dụng                                                                                                                                                  |
  | **Meaning**  | String     | Người **sử dụng một trong các đối tượng trong danh sách ConcKeyO** làm phương tiện phục vụ nhu cầu hoặc mục đích nhất định khi tham gia trong giao thông |
  | **ConckeyS** | Key phrase | Người                                                                                                                                                    |
  | **ConckeyO** | List       | Xe máy, Nón bảo hiểm, Ô tô                                                                                                                               |
  | **Prop**     | Set        | ["Không bắt cầu","Không đối xứng"]                                                                                                                       |
  | **Keywords** | Set        | ["sử dụng","điều khiển"]                                                                                                                                 |

- Giải thích về "**bắt cầu**" và "**đối xứng**"

  - **Bắt cầu**: Một mối quan hệ được gọi là bắc cầu nếu khi $A \rightarrow B$ và $B \rightarrow C$ thì có thể suy ra $A \rightarrow C$ (với $A, B, C$ là các khái niệm concepts).

    - Trong ví dụ trên, Relation "**sử dụng**" không bắt cầu khi:

      - $A = ``Người \ lái \ xe \ máy"$

      - $B = ``Xe \ máy"$

      - $C = ``Đường \ bộ"$

      - Nếu "Người lái xe" sử dụng "Xe máy" và "Xe máy" di chuyển trên "Đường bộ", không thể suy ra "Người lái xe" sử dụng "Đường bộ".

  - **Đối xứng**: Một mối quan hệ được gọi là đối xứng nếu mối quan hệ đó **tồn tại theo cả hai chiều**. Tức là $A \rightarrow B$ thì $B \rightarrow A$ (với $A, B$ là các khái niệm concept)

    - Ví dụ Relation "sử dụng" giữa "Người lái xe máy" và "xe máy":

      - $A = ``Người \ lái \ xe \ máy"$

      - $A = ``Xe \ máy"$

      - Nếu "Người lái xe" sử dụng "Xe máy", điều này không có nghĩa là "Xe máy" sử dụng "Người lái xe".

  <br>

- **$ Rules -$ Luật suy diễn**

  - Các quy tắc để suy luận tri thức mới từ các quan hệ hiện có.

  - Ví dụ: "Nếu một người điều khiển xe máy, họ cần có bằng lái hợp lệ".

 <br>

- **$Conc \ và \ Rel$**

  - Là 2 thành phần chính trong việc xây dựng đồ thị tri thức.

  - Đồ thị tri thức sẽ bao gồm các node là các $Conc$ (có thể lấy giá trị **Name** của **Concept** hoặc lấy trong danh sách **Keyphrases**) được nối với nhau bởi các cạnh $Rel$ (có thể lấy giá trị **Name** của **Relation** hoặc lấy trong danh sách **Keywords** sao cho ý nghĩa phù hợp giữa 2 khái niệm).

  - Ngoài ra còn có thể có thêm các thuộc tính (**attributes**): Cung cấp thông tin bổ sung về các nút và cạnh, ví dụ: loại khái niệm, ý nghĩa mối quan hệ, hoặc trọng số.

<br>
<br>

## 2. Đồ thị tri thức (Knowledge Graphics)

- **Đồ thị tri thức (Knowledge Graph)** là một cách tổ chức và biểu diễn tri thức dưới dạng các nút (nodes) và cạnh (edges), trong đó:

  - Các **node là các khái niệm** $Conc$ (có thể lấy giá trị **Name** của **Concept** hoặc lấy trong danh sách **Keyphrases**).

  - Các **cạnh là các quan hệ** giữa các khái niệm $Rel$ (có thể lấy giá trị **Name** của **Relation** hoặc lấy trong danh sách **Keywords** sao cho ý nghĩa phù hợp giữa 2 khái niệm).

  - Các thuộc tính (**attributes**): Cung cấp thông tin bổ sung về các nút và cạnh, ví dụ: loại khái niệm, ý nghĩa mối quan hệ, hoặc trọng số.

- Ví dụ về sơ đồ tri thức:

  ![Knowledge Graphics Example](/images/Knowledge-Graphics-Example.jpg)

<br>

## 3. Công thức TF-IDF

- **Công dụng:**

  - **TF-IDF (Term Frequency - Inverse Document Frequency)** là một công thức dùng để đánh giá tầm quan trọng của một từ (term) trong một tài liệu (document) thuộc một tập hợp tài liệu (corpus).

  - TF-IDF được sử dụng rộng rãi trong xử lý ngôn ngữ tự nhiên (NLP), khai thác dữ liệu văn bản (text mining), và các ứng dụng tìm kiếm thông tin (information retrieval).

- **Ý nghĩa:**

  - **TF (Term Frequency)**: Đo lường mức độ xuất hiện của từ trong một tài liệu cụ thể.

  - **IDF (Inverse Document Frequency)**: Đo lường mức độ đặc biệt của từ trong toàn bộ tập tài liệu.

  - **TF-IDF**: Kết hợp cả hai yếu tố trên, nhằm đánh giá: Từ quan trọng trong tài liệu nhưng ít phổ biến trong tập dữ liệu lớn sẽ có giá trị TF-IDF cao.

### 3.1. Công thức tần suất từ (TF - Term Frequency):

$$
    TF(t,d) = \frac{f(t,d)}{\left| d \right|}
$$

- Trong đó:

  - $f(t,d)$: là số lần từ $t$ xuất hiện trong tài liệu $d$.

  - $\left| d \right|$: Tổng số từ trong tài liệu $d$.

- **Ý nghĩa:**

  - Đo lường **tần suất xuất hiện của từ $\textbf{t}$ trong tài liệu cụ thể**.

  - **Từ xuất hiện nhiều lần trong một tài liệu sẽ có giá trị $\textbf{TF}$ cao**.

### 3.2. Tần suất nghịch đảo tài liệu (IDF - Inverse Document Frequency):

$$
    IDF(t,D) = \log(\frac{\left| D \right|}{ 1 + \left| d \in D : t \in D \right|})
$$

- Trong đó:

  - $\left| D \right|$: Tổng số tài liệu trong tập dữ liệu $D$.

  - $\left| d \in D : t \in D \right|$: Số tài liệu chứa từ $t$.

- **Ý nghĩa:**

  - IDF **giảm giá trị của những từ phổ biến** trong toàn bộ tập tài liệu (như "và", "là", "của").

  - **Từ xuất hiện ở ít tài liệu (độc đáo) sẽ có giá trị IDF cao hơn**.

### 3.3. Công thức TF-IDF

$$
    TF-IDF(t,d,D) = TF(t,d) \times IDF(t,D)
$$

- **Ý nghĩa:**

  - Kết hợp TF và IDF để đo lường mức độ quan trọng của từ $t$ trong tài liệu $d$ so với toàn bộ tập dữ liệu $D$.

  - Một từ có **tần suất xuất hiện ít trong một tài liệu (TF thấp) và độ phổ biến thấp trong toàn bộ tập tài liệu (IDF cao) thường được coi là một từ quan trọng**. Đây là từ đặc trưng của tài liệu đó và có khả năng giúp phân biệt tài liệu này với các tài liệu khác trong tập dữ liệu.

  - Một từ có **giá trị TF - IDF cao** được xem là một từ quan trọng.

  - Bạn có thể dùng công thức **TF-IDF** để xem các khái niệm (concepts) nào là quan trọng, từ đó tối giản đồ thị tri thức sao cho đồ thị tối ưu nhất (**các node đồ thị là các từ quan trọng**)

### 3.4. Ví dụ

- Giả sử chúng ta có tập tài liệu gồm 3 tài liệu:

  - **Tài liệu 1 (d1)**: "Xe máy là phương tiện giao thông phổ biến."

  - **Tài liệu 2 (d2)**: "Người lái xe cần bằng lái để điều khiển xe máy."

  - **Tài liệu 3 (d3)**: "Luật quy định người điều khiển xe máy phải đủ tuổi."

- Cần tính từ "**xe máy**" xem nó có phải là một từ quan trọng hay không:

  <br>

  **Bước 1**: Tính TF (Term Frequency)

  - Từ "xe máy" xuất hiện:

    - Trong $d1$: 1 lần, tổng số từ là 6.

      $$TF(``xe máy",d1) = \frac{1}{6} = 0.167$$

    - Trong $d2$: 1 lần, tổng số từ là 8.

      $$TF(``xe máy",d2) = \frac{1}{8} = 0.125$$

    - Trong $d3$: 1 lần, tổng số từ là 99.

      $$TF(``xe máy",d3) = \frac{1}{9} = 0.111$$

  **Bước 2**: Tính IDF (Inverse Document Frequency)

  - Tổng số tài liệu $\left| D \right| = 3$

  - Số tài liệu chứa từ "xe máy": $\left| d \in D : t \in d \right| = 3$

  - Công thức IDF:

    $$IDF(``xe \ máy",D) = \log(\frac{3}{3+1}) = \log(0.75) \approx -0.125$$

  **Bước 3: Tính TF-IDF**

  - Trong $d1$:
    
    $TF-IDF(``xe \ máy",d1,D) = TF(``xe \ máy",d1) \times IDF(``xe \ máy",D) = 0.167 \times - 0.125 \approx -0.021$

  - Trong $d2$:
    
    $$TF-IDF(``xe \ máy",d2,D) = TF(``xe \ máy",d2) \times IDF(``xe \ máy",D) = 0.125 \times - 0.125 \approx -0.016$$

  - Trong $d3$:
    
    $$TF-IDF(``xe \ máy",d3,D) = TF(``xe \ máy",d3) \times IDF(``xe \ máy",D) = 0.111 \times - 0.125 \approx -0.014$$

  **Bước 4: Kết luận**

  - Từ "xe máy" **có giá trị TF-IDF thấp** trong cả 3 tài liệu, cho thấy đây là một từ phổ biến và không đặc biệt quan trọng khi phân tích nội dung.
