import React from 'react';

/**
 * A reusable Input component for forms.
 * @param {object} props - The component props.
 * @param {string} props.label - The label for the input field.
 * @param {string} props.id - The unique ID for the input field.
 * @param {string} [props.type='text'] - The type of the input field (e.g., 'text', 'number').
 * @param {string|number} props.value - The current value of the input field.
 * @param {function} props.onChange - The event handler for input changes.
 * @param {string} [props.description] - Optional description text for accessibility.
 * @param {object} props - Additional props to pass to the input element.
 */
const Input = ({ label, id, type = 'text', value, onChange, description, ...props }) => {
  const descriptionId = description ? `${id}-description` : undefined;

  return (
    <div className="mb-4">
      <label htmlFor={id} className="block text-gray-700 text-sm font-bold mb-2">
        {label}
      </label>
      <input
        type={type}
        id={id}
        name={id}
        value={value}
        onChange={onChange}
        className="shadow-sm appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition duration-200"
        aria-label={label}
        aria-describedby={descriptionId}
        {...props}
      />
      {description && (
        <p id={descriptionId} className="text-medium-contrast text-xs mt-1">
          {description}
        </p>
      )}
    </div>
  );
};

export default Input;
