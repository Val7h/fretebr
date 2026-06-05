import React, { useState } from 'react';
import { CreateFretePayload } from '../services/api';

const CIDADES = [
  'São Paulo (SP)',
  'Rio de Janeiro (RJ)',
  'Minas Gerais (MG)',
  'Bahia (BA)',
  'Pernambuco (PE)',
  'Ceará (CE)',
  'Pará (PA)',
  'Santa Catarina (SC)',
  'Rio Grande do Sul (RS)',
  'Goiás (GO)',
  'Distrito Federal (DF)',
  'Espírito Santo (ES)',
  'Paraná (PR)',
  'Maranhão (MA)',
  'Paraíba (PB)',
  'Rio Grande do Norte (RN)',
  'Piauí (PI)',
  'Alagoas (AL)',
  'Sergipe (SE)',
  'Mato Grosso (MT)',
  'Mato Grosso do Sul (MS)',
  'Tocantins (TO)',
  'Amapá (AP)',
  'Roraima (RR)',
  'Amazonas (AM)',
];

interface FreteFormProps {
  onSubmit: (data: CreateFretePayload) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
  error?: string;
}

export const FreteForm: React.FC<FreteFormProps> = ({
  onSubmit,
  onCancel,
  isLoading = false,
  error = '',
}) => {
  const [formData, setFormData] = useState<CreateFretePayload>({
    origem: '',
    destino: '',
    peso_kg: 0.1,
    valor_r: 1,
    descricao: '',
  });

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateForm = () => {
    const errors: Record<string, string> = {};

    if (!formData.origem.trim()) {
      errors.origem = 'Origem é obrigatória';
    }
    if (!formData.destino.trim()) {
      errors.destino = 'Destino é obrigatório';
    }
    if (formData.peso_kg < 0.1) {
      errors.peso_kg = 'Peso deve ser no mínimo 0,1 kg';
    }
    if (formData.valor_r < 1) {
      errors.valor_r = 'Valor deve ser no mínimo R$ 1,00';
    }
    if ((formData.descricao || '').length > 500) {
      errors.descricao = 'Descrição não pode exceder 500 caracteres';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;

    if (name === 'peso_kg' || name === 'valor_r') {
      setFormData(prev => ({
        ...prev,
        [name]: parseFloat(value) || 0,
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value,
      }));
    }

    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Origem */}
      <div>
        <label htmlFor="origem" className="block text-sm font-medium text-gray-700 mb-2">
          Origem *
        </label>
        <select
          id="origem"
          name="origem"
          value={formData.origem}
          onChange={handleChange}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
            validationErrors.origem ? 'border-red-500' : 'border-gray-300'
          }`}
        >
          <option value="">Selecione uma cidade</option>
          {CIDADES.map(cidade => (
            <option key={cidade} value={cidade}>
              {cidade}
            </option>
          ))}
        </select>
        {validationErrors.origem && (
          <p className="text-red-500 text-sm mt-1">{validationErrors.origem}</p>
        )}
      </div>

      {/* Destino */}
      <div>
        <label htmlFor="destino" className="block text-sm font-medium text-gray-700 mb-2">
          Destino *
        </label>
        <select
          id="destino"
          name="destino"
          value={formData.destino}
          onChange={handleChange}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
            validationErrors.destino ? 'border-red-500' : 'border-gray-300'
          }`}
        >
          <option value="">Selecione uma cidade</option>
          {CIDADES.map(cidade => (
            <option key={cidade} value={cidade}>
              {cidade}
            </option>
          ))}
        </select>
        {validationErrors.destino && (
          <p className="text-red-500 text-sm mt-1">{validationErrors.destino}</p>
        )}
      </div>

      {/* Peso em kg */}
      <div>
        <label htmlFor="peso_kg" className="block text-sm font-medium text-gray-700 mb-2">
          Peso em kg *
        </label>
        <input
          type="number"
          id="peso_kg"
          name="peso_kg"
          min="0.1"
          step="0.1"
          value={formData.peso_kg}
          onChange={handleChange}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
            validationErrors.peso_kg ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="0.0"
        />
        {validationErrors.peso_kg && (
          <p className="text-red-500 text-sm mt-1">{validationErrors.peso_kg}</p>
        )}
      </div>

      {/* Valor em R$ */}
      <div>
        <label htmlFor="valor_r" className="block text-sm font-medium text-gray-700 mb-2">
          Valor em R$ *
        </label>
        <input
          type="number"
          id="valor_r"
          name="valor_r"
          min="1"
          step="0.01"
          value={formData.valor_r}
          onChange={handleChange}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
            validationErrors.valor_r ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="0.00"
        />
        {validationErrors.valor_r && (
          <p className="text-red-500 text-sm mt-1">{validationErrors.valor_r}</p>
        )}
      </div>

      {/* Descrição */}
      <div>
        <label htmlFor="descricao" className="block text-sm font-medium text-gray-700 mb-2">
          Descrição (máx 500 caracteres)
        </label>
        <textarea
          id="descricao"
          name="descricao"
          value={formData.descricao || ''}
          onChange={handleChange}
          maxLength={500}
          rows={4}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition resize-none ${
            validationErrors.descricao ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Descreva detalhes sobre o frete..."
        />
        <p className="text-xs text-gray-500 mt-1">
          {(formData.descricao || '').length}/500
        </p>
        {validationErrors.descricao && (
          <p className="text-red-500 text-sm mt-1">{validationErrors.descricao}</p>
        )}
      </div>

      {/* Buttons */}
      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          disabled={isSubmitting || isLoading}
          className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition duration-200"
        >
          {isSubmitting || isLoading ? 'Postando...' : 'Postar Frete'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting || isLoading}
          className="flex-1 bg-gray-300 hover:bg-gray-400 disabled:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition duration-200"
        >
          Voltar
        </button>
      </div>
    </form>
  );
};
