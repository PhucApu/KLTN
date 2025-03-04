import React from 'react';
// import './ConversationItem.css'; // Tùy chọn, nếu bạn muốn style riêng

const ConversationItem = ({ title }) => {
  return (
    <div className="conversation-item">
      <span>{title}</span>
    </div>
  );
};

export default ConversationItem;
