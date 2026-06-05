import React from 'react';
import type { Message } from '../services/matchesApi';

interface ChatMessageProps {
  message: Message;
  isOwn: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, isOwn }) => {
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div
      className={`flex ${isOwn ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-2 rounded-lg ${
          isOwn
            ? 'bg-blue-600 text-white rounded-br-none'
            : 'bg-gray-200 text-gray-900 rounded-bl-none'
        }`}
      >
        {!isOwn && (
          <p className="text-xs font-semibold mb-1 opacity-75">
            {message.sender_nome}
          </p>
        )}
        <p className="break-words text-sm">{message.content}</p>
        <p
          className={`text-xs mt-1 ${
            isOwn ? 'text-blue-100' : 'text-gray-600'
          }`}
        >
          {formatTime(message.created_at)}
        </p>
      </div>
    </div>
  );
};
