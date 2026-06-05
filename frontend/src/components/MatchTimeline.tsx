import React from 'react';
import type { MatchStatus } from '../services/matchesApi';

interface MatchTimelineProps {
  currentStatus: MatchStatus;
}

export const MatchTimeline: React.FC<MatchTimelineProps> = ({ currentStatus }) => {
  const steps: { key: MatchStatus; label: string; number: number }[] = [
    { key: 'pendente', label: 'Pendente', number: 1 },
    { key: 'aceito', label: 'Aceito', number: 2 },
    { key: 'em_entrega', label: 'Em Entrega', number: 3 },
    { key: 'finalizado', label: 'Finalizado', number: 4 },
  ];

  const getStepIndex = (status: MatchStatus) => {
    return steps.findIndex((s) => s.key === status);
  };

  const currentStepIndex = getStepIndex(currentStatus);

  return (
    <div className="py-8">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <React.Fragment key={step.key}>
            {/* Circle and Label */}
            <div className="flex flex-col items-center flex-1">
              <div
                className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg transition-all ${
                  index <= currentStepIndex
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {step.number}
              </div>
              <p
                className={`mt-2 text-sm font-medium text-center ${
                  index <= currentStepIndex ? 'text-blue-600' : 'text-gray-600'
                }`}
              >
                {step.label}
              </p>
            </div>

            {/* Connector Line */}
            {index < steps.length - 1 && (
              <div
                className={`h-1 flex-1 mx-2 transition-all ${
                  index < currentStepIndex ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};
