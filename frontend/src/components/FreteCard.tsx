import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Frete } from '../services/api';

interface FreteCardProps {
  frete: Frete;
  motoristaName?: string;
  onSelect?: () => void;
}

export const FreteCard: React.FC<FreteCardProps> = ({ frete, motoristaName, onSelect }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    if (onSelect) {
      onSelect();
    } else {
      navigate(`/frete/${frete.id}`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'disponível':
        return 'bg-green-100 text-green-800';
      case 'aceito':
        return 'bg-blue-100 text-blue-800';
      case 'entregue':
        return 'bg-gray-100 text-gray-800';
      case 'cancelado':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div
      onClick={handleClick}
      className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-lg transition cursor-pointer overflow-hidden h-full flex flex-col"
    >
      {/* Status Badge */}
      <div className="px-6 pt-4 flex justify-between items-start">
        <div className="flex-1">
          <p className="text-xs text-gray-600 font-medium mb-1">ROTA</p>
          <p className="text-sm font-semibold text-gray-900">
            {frete.origem.split('(')[0].trim()} → {frete.destino.split('(')[0].trim()}
          </p>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap ml-2 ${getStatusColor(frete.status)}`}>
          {frete.status}
        </span>
      </div>

      {/* Details Section */}
      <div className="px-6 py-4 flex-1">
        {/* Weight and Value Grid */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-blue-50 rounded p-3">
            <p className="text-xs text-gray-600 font-medium mb-1">PESO</p>
            <p className="text-lg font-bold text-blue-600">{frete.peso_kg}</p>
            <p className="text-xs text-gray-600">kg</p>
          </div>
          <div className="bg-green-50 rounded p-3">
            <p className="text-xs text-gray-600 font-medium mb-1">VALOR</p>
            <p className="text-lg font-bold text-green-600">
              R$ {frete.valor_r.toFixed(2)}
            </p>
          </div>
        </div>

        {/* Description */}
        {frete.descricao && (
          <div className="mb-4">
            <p className="text-xs text-gray-600 font-medium mb-1">DESCRIÇÃO</p>
            <p className="text-sm text-gray-700 line-clamp-2">{frete.descricao}</p>
          </div>
        )}

        {/* Motorista Name */}
        {motoristaName && (
          <div className="mb-4">
            <p className="text-xs text-gray-600 font-medium mb-1">MOTORISTA</p>
            <p className="text-sm font-semibold text-gray-900">{motoristaName}</p>
          </div>
        )}

        {/* Rating Placeholder */}
        <div className="flex items-center">
          <span className="text-sm text-yellow-500">★★★★★</span>
          <span className="text-sm text-gray-600 ml-2">5.0</span>
        </div>
      </div>

      {/* Button */}
      <div className="px-6 pb-4 pt-2 border-t border-gray-100">
        <button
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition text-sm"
          onClick={e => {
            e.stopPropagation();
            handleClick();
          }}
        >
          Ver Detalhes
        </button>
      </div>
    </div>
  );
};
