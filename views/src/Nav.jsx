import React, { useState } from "react";
import ConversationItem from "./ConversationItem";
import "./Nav.css";

// Icon ví dụ (bạn có thể dùng thư viện react-icons hoặc icon riêng)
import { FaBars, FaTimes, FaSearch, FaPlus } from "react-icons/fa";

const Naviagtion = () => {
  // State quản lý việc mở/đóng sidebar
  const [isOpen, setIsOpen] = useState(true);

  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className={`sidebar ${isOpen ? "open" : "close"}`}>
      {/* Header của Sidebar */}
      <div className="sidebar-header">
        <button className="toggle-button" onClick={handleToggle}>
          {isOpen ? <FaTimes /> : <FaBars />}
        </button>
        {/* Chỉ hiển thị tiêu đề khi đang mở */}
        {isOpen && <h2>Law Searching</h2>}
      </div>

      {/* Phần nội dung của Sidebar (chỉ hiển thị khi mở) */}
      {isOpen && (
        <div className="sidebar-content">
          {/* Khu vực tìm kiếm */}
          <div className="search-section">
            <FaSearch />
            <input type="text" placeholder="Tìm kiếm cuộc trò chuyện..." />
          </div>

          {/* Nút tạo đoạn chat mới */}
          <button className="new-chat-button">
            <FaPlus />
            Tạo đoạn chat mới
          </button>

          {/* Danh sách các cuộc trò chuyện */}
          <div className="conversation-list">
            <ConversationItem title="Cuộc trò chuyện A" />
            {/* Có thể thêm nhiều ConversationItem khác tại đây */}
          </div>
        </div>
      )}
    </div>
  );
};

export default Naviagtion;


