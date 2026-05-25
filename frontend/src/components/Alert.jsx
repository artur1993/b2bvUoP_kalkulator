import React from "react";

const Alert = ({ message, type }) => {
  if (!message) return null; // Do not render if message is null or empty

  let bgColor = "bg-blue-100";
  let textColor = "text-blue-700";
  let iconColor = "text-blue-500";
  let borderColor = "border-blue-400";

  switch (type) {
    case "error":
      bgColor = "bg-red-100";
      textColor = "text-red-700";
      iconColor = "text-red-500";
      borderColor = "border-red-400";
      break;
    case "success":
      bgColor = "bg-green-100";
      textColor = "text-green-700";
      iconColor = "text-green-500";
      borderColor = "border-green-400";
      break;
    case "warning":
      bgColor = "bg-yellow-100";
      textColor = "text-yellow-700";
      iconColor = "text-yellow-500";
      borderColor = "border-yellow-400";
      break;
    default:
      // Default to info (blue)
      break;
  }

  return (
    <div
      className={`p-4 mb-4 text-sm rounded-lg ${bgColor} ${textColor} border ${borderColor}`}
      role="alert"
      data-testid="alert-message"
    >
      <div className="flex items-center">
        {type === "error" && (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={`h-5 w-5 mr-3 ${iconColor}`}
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        )}
        {(type === "success" ||
          type === "warning" ||
          type === "info" ||
          !type) && (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={`h-5 w-5 mr-3 ${iconColor}`}
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clipRule="evenodd"
            />
          </svg>
        )}
        <div>{message}</div>
      </div>
    </div>
  );
};

export default Alert;
