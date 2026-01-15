import React from 'react';
import { Check, Loader2 } from 'lucide-react';

interface Step {
  id: number;
  title: string;
  description: string;
}

interface StepIndicatorProps {
  steps: Step[];
  currentStep: number;
  completedSteps: number[];
}

export default function StepIndicator({ steps, currentStep, completedSteps }: StepIndicatorProps) {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <React.Fragment key={step.id}>
            <div className="flex flex-col items-center flex-1">
              <div
                className={`step-indicator ${
                  completedSteps.includes(step.id)
                    ? 'step-completed'
                    : currentStep === step.id
                    ? 'step-active'
                    : 'step-pending'
                }`}
              >
                {completedSteps.includes(step.id) ? (
                  <Check className="w-6 h-6" />
                ) : currentStep === step.id ? (
                  <Loader2 className="w-6 h-6 animate-spin" />
                ) : (
                  step.id
                )}
              </div>
              <div className="mt-2 text-center">
                <div className="text-sm font-medium text-gray-900">{step.title}</div>
                <div className="text-xs text-gray-500">{step.description}</div>
              </div>
            </div>
            
            {index < steps.length - 1 && (
              <div
                className={`flex-1 h-1 mx-4 rounded-full transition-all ${
                  completedSteps.includes(steps[index + 1].id)
                    ? 'bg-green-600'
                    : currentStep >= steps[index + 1].id
                    ? 'bg-blue-600'
                    : 'bg-gray-300'
                }`}
              />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}