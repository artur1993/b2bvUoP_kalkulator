import React from 'react';

/**
 * A reusable Checkbox component for forms.
 * @param {object} props - The component props.
 * @param {string} props.label - The label for the checkbox.
 * @param {string} props.id - The unique ID for the checkbox.
 * @param {boolean} props.checked - The current checked state of the checkbox.
 * @param {function} props.onChange - The event handler for checkbox changes.
 * @param {string} [props.description] - Optional description text for accessibility.
 * @param {object} props - Additional props to pass to the checkbox element.
 */
const Checkbox = ({ label, id, checked, onChange, description, ...props }) => {
  const descriptionId = description ? `${id}-description` : undefined;

  return (
    <div className="mb-4 flex items-center">
      <input
        type="checkbox"
        id={id}
        name={id}
        checked={!!checked}
        onChange={onChange}
        className="mr-2 h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded transition duration-200"
        aria-label={label}
        aria-describedby={descriptionId}
        {...props}
      />
      <label htmlFor={id} className="text-gray-700 text-sm">
        {label}
      </label>
      {description && (
        <p id={descriptionId} className="text-medium-contrast text-xs ml-2">
          {description}
        </p>
      )}
    </div>
  );
};

export default Checkbox;
