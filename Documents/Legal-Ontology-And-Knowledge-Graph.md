# Mô hình Legal-Ontology và Đồ thị tri thức


## Mục lục
1. [Legal-Ontology](#1-mô-hình-legal-ontology)
  
    1.1. [Khái niệm](#11-khái-niệm)

    1.2. [Ontology](#12-ontology)

    1.3. [Legal-Onto](#13-legal-onto) 

    1.4. [Thành phần chính của Legal-Onto](#14-thành-phần-chính-của-legal-onto)

2. [Đồ thị tri thức](#2-đồ-thị-tri-thức-knowledge-graphics)    


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

  - **$C - $ Concepts** (Khái niệm)
    
    - Là **tập hợp các khái niệm trong pháp luật**.

    - Mỗi khái niệm có tên (**Name**), ý nghĩa (**Meaning**), các thuộc tính (**Attrs**), và các cụm từ khóa liên quan (**Keyphrases**).

    - Ví dụ về một **concepts** được biểu diễn trong mô hình Legel-Onto:

      - **Concepts "xe máy"** sẽ được biểu diễn:

      | Element | Type | Value |
      | :--- | :--- | :--- |
      | **Name** | String | Xe máy |
      | **Meaning** | String | Phương tiện giao thông có hai bánh chạy bằng động cơ |
      | **Attrs** | Dict | {"Loại phương tiện": "Giao thông đường bộ"} |
      | **Keyphrases** | Set | ["Xe máy", "Mô tô"]

  <br>

  - **$ R - $ Relation (Quan hệ)**

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

      | Element | Type | Value |
      | :--- | :--- | :--- |
      | **Name** | String | sử dụng |
      | **Meaning** | String | Người **sử dụng một trong các đối tượng trong danh sách ConcKeyO** làm phương tiện phục vụ nhu cầu hoặc mục đích nhất định khi tham gia trong giao thông |
      | **ConckeyS** | Key phrase | Người |
      | **ConckeyO** | List | Xe máy, Nón bảo hiểm, Ô tô |
      | **Prop** | Set | ["Không bắt cầu","Không đối xứng"] |
      | **Keywords** | Set | ["sử dụng","điều khiển"] |

    - Giải thích về "**bắt cầu**" và "**đối xứng**"

      - **Bắt cầu**: Một mối quan hệ được gọi là bắc cầu nếu khi $ A \rightarrow B $ và $ B \rightarrow C $ thì có thể suy ra $ A \rightarrow C $ (với $ A, B, C$ là các khái niệm concepts).
        
        - Trong ví dụ trên, Relation "**sử dụng**" không bắt cầu khi:

          - $ A = ``Người \ lái \ xe \ máy" $
          
          - $ B = ``Xe \ máy" $

          - $ C = ``Đường \ bộ" $

          - Nếu "Người lái xe" sử dụng "Xe máy" và "Xe máy" di chuyển trên "Đường bộ", không thể suy ra "Người lái xe" sử dụng "Đường bộ".

      - **Đối xứng**: Một mối quan hệ được gọi là đối xứng nếu mối quan hệ đó **tồn tại theo cả hai chiều**. Tức là $ A \rightarrow B $ thì $ B \rightarrow A $ (với $ A, B$ là các khái niệm concept)

        - Ví dụ Relation "sử dụng" giữa "Người lái xe máy" và "xe máy":
          
          - $ A = ``Người \ lái \ xe \ máy" $

          - $ A = ``Xe \ máy" $

          - Nếu "Người lái xe" sử dụng "Xe máy", điều này không có nghĩa là "Xe máy" sử dụng "Người lái xe".




  
  <br>

  - **$ Rules -$ Luật suy diễn**

    - Các quy tắc để suy luận tri thức mới từ các quan hệ hiện có.

    - Ví dụ: "Nếu một người điều khiển xe máy, họ cần có bằng lái hợp lệ".

 <br>

  - **$Conc \ và \ Rel$**  

    - Là 2 thành phần chính trong việc xây dựng đồ thị tri thức.

    - Đồ thị tri thức sẽ bao gồm các node là các $ Conc $ (có thể lấy giá trị **Name** của **Concept** hoặc lấy trong danh sách **Keyphrases**) được nối với nhau bởi các cạnh $ Rel $ (có thể lấy giá trị **Name** của **Relation** hoặc lấy trong danh sách **Keywords** sao cho ý nghĩa phù hợp giữa 2 khái niệm).

    - Ngoài ra còn có thể có thêm các thuộc tính (**attributes**): Cung cấp thông tin bổ sung về các nút và cạnh, ví dụ: loại khái niệm, ý nghĩa mối quan hệ, hoặc trọng số.

<br>
<br>

## 2. Đồ thị tri thức (Knowledge Graphics)

  - **Đồ thị tri thức (Knowledge Graph)** là một cách tổ chức và biểu diễn tri thức dưới dạng các nút (nodes) và cạnh (edges), trong đó:

    - Các **node là các khái niệm** $ Conc $ (có thể lấy giá trị **Name** của **Concept** hoặc lấy trong danh sách **Keyphrases**).

    - Các **cạnh là các quan hệ** giữa các khái niệm $ Rel $ (có thể lấy giá trị **Name** của **Relation** hoặc lấy trong danh sách **Keywords** sao cho ý nghĩa phù hợp giữa 2 khái niệm).

    - Các thuộc tính (**attributes**): Cung cấp thông tin bổ sung về các nút và cạnh, ví dụ: loại khái niệm, ý nghĩa mối quan hệ, hoặc trọng số.


  - Ví dụ về sơ đồ tri thức:
  
     ![Knowledge Graphics Example](/images/Knowledge-Graphics-Example.jpg)









  






