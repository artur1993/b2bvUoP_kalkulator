import React from "react";
import { render, screen } from "@testing-library/react";
import Alert from "./Alert";
import { describe, it, expect } from "vitest";

describe("Alert", () => {
  it("renders nothing when message is not provided", () => {
    render(<Alert message="" type="info" />);
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("renders an info alert correctly", () => {
    render(<Alert message="This is an info message." type="info" />);
    const alert = screen.getByRole("alert");
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveTextContent("This is an info message.");
    expect(alert).toHaveClass("bg-blue-100");
  });

  it("renders an error alert correctly", () => {
    render(<Alert message="This is an error message." type="error" />);
    const alert = screen.getByRole("alert");
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveTextContent("This is an error message.");
    expect(alert).toHaveClass("bg-red-100");
  });

  it("renders a success alert correctly", () => {
    render(<Alert message="This is a success message." type="success" />);
    const alert = screen.getByRole("alert");
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveTextContent("This is a success message.");
    expect(alert).toHaveClass("bg-green-100");
  });

  it("renders a warning alert correctly", () => {
    render(<Alert message="This is a warning message." type="warning" />);
    const alert = screen.getByRole("alert");
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveTextContent("This is a warning message.");
    expect(alert).toHaveClass("bg-yellow-100");
  });
});
